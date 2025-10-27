/**
 * Hybrid Message Broker for NestJS
 * RabbitMQ + Redis Streams integration
 */
import { Injectable, OnModuleDestroy, OnModuleInit } from '@nestjs/common';
import { InjectRedis } from '@nestjs-modules/ioredis';
import Redis from 'ioredis';
import * as amqp from 'amqplib';

export enum MessagePriority {
  LOW = 1,
  NORMAL = 2,
  HIGH = 3,
  CRITICAL = 4,
}

export enum MessageBrokerType {
  RABBITMQ = 'rabbitmq',
  REDIS = 'redis',
  HYBRID = 'hybrid',
}

@Injectable()
export class HybridBrokerService implements OnModuleInit, OnModuleDestroy {
  private rabbitmqConnection: any = null;
  private rabbitmqChannel: any = null;
  private readonly redisStreamsPrefix = 'nestjs_messages';

  constructor(@InjectRedis() private readonly redis: Redis) {}

  async onModuleDestroy() {
    if (this.rabbitmqConnection && this.rabbitmqConnection.close) {
      await this.rabbitmqConnection.close();
    }
  }

  async onModuleInit() {
    await this.initialize();
  }

  async initialize() {
    try {
      // Initialize RabbitMQ connection using env vars with sensible defaults
      const rmqUser = process.env.RABBITMQ_USER || 'admin';
      const rmqPass = process.env.RABBITMQ_PASSWORD || 'admin123';
      const rmqHost = process.env.RABBITMQ_HOST || 'rabbitmq';
      const rmqPort = process.env.RABBITMQ_PORT || '5672';
      const rmqUrl = process.env.RABBITMQ_URL || `amqp://${rmqUser}:${rmqPass}@${rmqHost}:${rmqPort}/`;

      this.rabbitmqConnection = await amqp.connect(rmqUrl);
      if (this.rabbitmqConnection) {
        this.rabbitmqChannel = await this.rabbitmqConnection.createChannel();

        // Declare exchange
        if (this.rabbitmqChannel && this.rabbitmqChannel.assertExchange) {
          await this.rabbitmqChannel.assertExchange('nestjs_exchange', 'direct', { durable: true });
        }
      }
    } catch (error) {
      console.error('Failed to initialize RabbitMQ connection:', error);
    }
  }

  async publishMessage(
    message: any,
    routingKey: string = 'default',
    priority: MessagePriority = MessagePriority.NORMAL,
    brokerType: MessageBrokerType = MessageBrokerType.HYBRID
  ): Promise<string> {
    const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const enrichedMessage = {
      id: messageId,
      timestamp: Date.now(),
      priority: priority,
      routingKey,
      brokerType,
      data: message,
      source: 'nestjs'
    };

    if (brokerType === MessageBrokerType.REDIS || brokerType === MessageBrokerType.HYBRID) {
      // Publish to Redis Streams (field-value pairs required)
      await this.redis.xadd(`${this.redisStreamsPrefix}:${routingKey}`, '*', 'payload', JSON.stringify(enrichedMessage));
    }

    if (brokerType === MessageBrokerType.RABBITMQ || brokerType === MessageBrokerType.HYBRID) {
      // Publish to RabbitMQ
      if (this.rabbitmqChannel && this.rabbitmqChannel.publish) {
        this.rabbitmqChannel.publish(
          'nestjs_exchange',
          routingKey,
          Buffer.from(JSON.stringify(enrichedMessage)),
          { persistent: true, priority: priority }
        );
      }
    }

    return messageId;
  }

  async consumeMessages(
    routingKey: string,
    callback: (message: any) => Promise<void>,
    brokerType: MessageBrokerType = MessageBrokerType.REDIS
  ) {
    if (brokerType === MessageBrokerType.REDIS || brokerType === MessageBrokerType.HYBRID) {
      await this.consumeRedisStream(routingKey, callback);
    }

    if (brokerType === MessageBrokerType.RABBITMQ || brokerType === MessageBrokerType.HYBRID) {
      await this.consumeRabbitMQQueue(routingKey, callback);
    }
  }

  private async consumeRedisStream(routingKey: string, callback: (message: any) => Promise<void>) {
    const streamKey = `${this.redisStreamsPrefix}:${routingKey}`;
    const groupName = 'nestjs_consumers';
    const consumerName = `consumer_${Date.now()}`;

    try {
      // Create consumer group
      await this.redis.xgroup('CREATE', streamKey, groupName, '0', 'MKSTREAM');
    } catch (error) {
      // Group already exists
    }

    while (true) {
      try {
        const messages: any = await this.redis.xreadgroup(
          'GROUP', groupName, consumerName,
          'STREAMS', streamKey, '>'
        );

        if (messages && messages[0] && messages[0][1]) {
          for (const [messageId, messageData] of messages[0][1]) {
            try {
              const parsedMessage = JSON.parse(messageData[1]);
              await callback(parsedMessage);
              await this.redis.xack(streamKey, groupName, messageId);
            } catch (error) {
              console.error('Error processing Redis message:', error);
            }
          }
        }

        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        console.error('Redis stream consumption error:', error);
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }
  }

  private async consumeRabbitMQQueue(routingKey: string, callback: (message: any) => Promise<void>) {
    if (!this.rabbitmqChannel) return;

    const queueName = `nestjs_${routingKey}`;

    // Declare queue
    const queue = await this.rabbitmqChannel.assertQueue(queueName, {
      durable: true,
      arguments: { 'x-max-priority': 4 }
    });

    // Bind to exchange
    await this.rabbitmqChannel.bindQueue(queue.queue, 'nestjs_exchange', routingKey);

    // Start consuming
    await this.rabbitmqChannel.consume(queue.queue, async (msg: amqp.ConsumeMessage | null) => {
      if (msg) {
        try {
          const messageData = JSON.parse(msg.content.toString());
          await callback(messageData);
          this.rabbitmqChannel.ack(msg);
        } catch (error) {
          console.error('Error processing RabbitMQ message:', error);
          this.rabbitmqChannel.nack(msg, false, true); // Requeue
        }
      }
    });
  }
}