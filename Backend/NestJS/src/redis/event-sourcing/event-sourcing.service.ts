/**
 * Event Sourcing for NestJS
 * Redis Streams-based event sourcing
 */
import { Injectable } from '@nestjs/common';
import { InjectRedis } from '@nestjs-modules/ioredis';
import Redis from 'ioredis';

export enum EventType {
  USER_CREATED = 'user_created',
  USER_UPDATED = 'user_updated',
  USER_DELETED = 'user_deleted',
  ORDER_CREATED = 'order_created',
  ORDER_UPDATED = 'order_updated',
  PAYMENT_PROCESSED = 'payment_processed',
  INVENTORY_UPDATED = 'inventory_updated',
  SYSTEM_ALERT = 'system_alert',
}

export interface Event {
  eventId: string;
  eventType: EventType;
  timestamp: number;
  userId?: string;
  entityId?: string;
  entityType?: string;
  data: any;
  metadata?: any;
}

@Injectable()
export class EventSourcingService {
  private readonly eventsPrefix = 'nestjs_events';

  constructor(@InjectRedis() private readonly redis: Redis) {}

  async publishEvent(
    eventType: EventType,
    data: any,
    userId?: string,
    entityId?: string,
    entityType?: string,
    metadata?: any
  ): Promise<string> {
    const event: Event = {
      eventId: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      eventType,
      timestamp: Date.now(),
      userId,
      entityId,
      entityType,
      data,
      metadata
    };

    // Publish to main events stream
    await this.redis.xadd(`${this.eventsPrefix}:main`, '*', JSON.stringify(event));

    // Publish to entity-specific stream if entity info provided
    if (entityId && entityType) {
      await this.redis.xadd(
        `${this.eventsPrefix}:entity:${entityType}:${entityId}`,
        '*',
        JSON.stringify(event)
      );
    }

    // Publish to user-specific stream if user info provided
    if (userId) {
      await this.redis.xadd(`${this.eventsPrefix}:user:${userId}`, '*', JSON.stringify(event));
    }

    return event.eventId;
  }

  async consumeEvents(
    callback: (event: Event) => Promise<void>,
    eventTypes?: EventType[],
    entityType?: string,
    entityId?: string
  ) {
    const streamKey = entityId && entityType
      ? `${this.eventsPrefix}:entity:${entityType}:${entityId}`
      : `${this.eventsPrefix}:main`;

    const groupName = 'nestjs_event_processors';
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
              const event: Event = JSON.parse(messageData[1]); // Parse the JSON string
              
              // Filter by event type if specified
              if (eventTypes && !eventTypes.includes(event.eventType)) {
                await this.redis.xack(streamKey, groupName, messageId);
                continue;
              }

              await callback(event);
              await this.redis.xack(streamKey, groupName, messageId);
            } catch (error) {
              console.error('Error processing event:', error);
            }
          }
        }

        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        console.error('Event consumption error:', error);
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }
  }

  async replayEvents(
    entityType: string,
    entityId: string,
    startTime: number = 0
  ): Promise<Event[]> {
    const streamKey = `${this.eventsPrefix}:entity:${entityType}:${entityId}`;

    try {
      const events = await this.redis.xrange(streamKey, startTime.toString(), '+');
      return events.map(([_, eventData]) => JSON.parse(eventData[1]) as Event);
    } catch (error) {
      console.error('Event replay error:', error);
      return [];
    }
  }

  async getEventStats() {
    const pattern = `${this.eventsPrefix}:*`;
    const streams = await this.redis.keys(pattern);

    const stats: { totalStreams: number; eventsPublished: number; streams: Record<string, { length: number }> } = {
      totalStreams: streams.length,
      eventsPublished: 0,
      streams: {}
    };

    for (const stream of streams) {
      const length = await this.redis.xlen(stream);
      stats.eventsPublished += length;
      stats.streams[stream] = { length };
    }

    return stats;
  }
}