"""
Hybrid Message Broker for NestJS
RabbitMQ + Redis Streams integration
"""
import { Injectable, OnModuleDestroy } from '@nestjs/common';
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
export class HybridBrokerService implements OnModuleDestroy {
  private rabbitmqConnection: amqp.Connection | null = null;
  private rabbitmqChannel: amqp.Channel | null = null;
  private readonly redisStreamsPrefix = 'nestjs_messages';

  constructor(@InjectRedis() private readonly redis: Redis) {}

  async onModuleDestroy() {
    if (this.rabbitmqConnection) {
      await this.rabbitmqConnection.close();
    }
  }

  async initialize() {
    // Initialize RabbitMQ connection
    this.rabbitmqConnection = await amqp.connect('amqp://admin:admin123@rabbitmq:5672/');
    this.rabbitmqChannel = await this.rabbitmqConnection.createChannel();

    // Declare exchange
    await this.rabbitmqChannel.assertExchange('nestjs_exchange', 'direct', { durable: true });
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
      // Publish to Redis Streams
      await this.redis.xadd(`${this.redisStreamsPrefix}:${routingKey}`, '*', enrichedMessage);
    }

    if (brokerType === MessageBrokerType.RABBITMQ || brokerType === MessageBrokerType.HYBRID) {
      // Publish to RabbitMQ
      await this.rabbitmqChannel!.publish(
        'nestjs_exchange',
        routingKey,
        Buffer.from(JSON.stringify(enrichedMessage)),
        { persistent: true, priority: priority }
      );
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
        const messages = await this.redis.xreadgroup(
          'GROUP', groupName, consumerName,
          'STREAMS', streamKey, '>'
        );

        if (messages && messages[0] && messages[0][1]) {
          for (const [messageId, messageData] of messages[0][1]) {
            try {
              await callback(messageData);
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
    const queueName = `nestjs_${routingKey}`;

    // Declare queue
    const queue = await this.rabbitmqChannel!.assertQueue(queueName, {
      durable: true,
      arguments: { 'x-max-priority': 4 }
    });

    // Bind to exchange
    await this.rabbitmqChannel!.bindQueue(queue.queue, 'nestjs_exchange', routingKey);

    // Start consuming
    await this.rabbitmqChannel!.consume(queue.queue, async (msg) => {
      if (msg) {
        try {
          const messageData = JSON.parse(msg.content.toString());
          await callback(messageData);
          this.rabbitmqChannel!.ack(msg);
        } catch (error) {
          console.error('Error processing RabbitMQ message:', error);
          this.rabbitmqChannel!.nack(msg, false, true); // Requeue
        }
      }
    });
  }
}
