import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { HybridBrokerService } from '../redis/hybrid-broker/hybrid-broker.service';

@Injectable()
export class MessageHandlerService implements OnModuleInit, OnModuleDestroy {
  private handlers: Map<string, (message: any) => Promise<void>> = new Map();

  constructor(private readonly hybridBroker: HybridBrokerService) {}

  async onModuleInit() {
    try {
      // Initialize the hybrid broker
      await this.hybridBroker.initialize();
      
      // Start consuming messages
      this.consumeMessages();
      
      console.log('✅ Message handler service initialized');
    } catch (error) {
      console.error('❌ Message handler service initialization failed:', error);
    }
  }

  async onModuleDestroy() {
    // Cleanup if needed
    console.log('✅ Message handler service destroyed');
  }

  registerHandler(messageType: string, handler: (message: any) => Promise<void>) {
    this.handlers.set(messageType, handler);
  }

  private async consumeMessages() {
    // Consume messages from Redis Streams
    this.hybridBroker.consumeMessages('default', async (message: any) => {
      try {
        const messageType = message.routingKey || 'default';
        const handler = this.handlers.get(messageType);
        
        if (handler) {
          await handler(message);
        } else {
          console.warn(`⚠️  No handler found for message type: ${messageType}`);
        }
      } catch (error) {
        console.error('❌ Error processing message:', error);
      }
    });
  }

  async publishEvent(eventType: string, data: any, priority: string = 'NORMAL') {
    try {
      const message = {
        eventType,
        data,
        source: 'nestjs',
        timestamp: Date.now()
      };

      const messageId = await this.hybridBroker.publishMessage(
        message,
        eventType,
        this.getPriorityEnum(priority)
      );

      console.log(`✅ Event ${eventType} published with ID: ${messageId}`);
      return messageId;
    } catch (error) {
      console.error('❌ Error publishing event:', error);
      throw error;
    }
  }

  private getPriorityEnum(priority: string) {
    switch (priority) {
      case 'LOW': return 1;
      case 'HIGH': return 3;
      case 'CRITICAL': return 4;
      default: return 2; // NORMAL
    }
  }
}