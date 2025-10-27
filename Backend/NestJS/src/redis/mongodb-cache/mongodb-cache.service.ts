/**
 * MongoDB Cache Integration for NestJS
 * Advanced MongoDB aggregation caching with Redis
 */
import { Injectable } from '@nestjs/common';
import { InjectRedis } from '@nestjs-modules/ioredis';
import { InjectConnection } from '@nestjs/mongoose';
import Redis from 'ioredis';
import mongoose, { Connection } from 'mongoose';

@Injectable()
export class MongodbCacheService {
  constructor(
    @InjectRedis() private readonly redis: Redis,
    @InjectConnection() private readonly mongooseConn: Connection,
  ) {}

  private dbConn: Connection | null = null;

  private async ensureMongoConnected(): Promise<void> {
    const dbName = process.env.MONGODB_DB || 'secmongo';

    // Wait until the Nest-managed Mongoose connection is ready
    const timeoutMs = 5000;
    const start = Date.now();
    while (this.mongooseConn.readyState !== 1) {
      if (Date.now() - start > timeoutMs) {
        throw new Error('MongoDB not connected (timeout waiting for MongooseModule connection)');
      }
      await new Promise((r) => setTimeout(r, 100));
    }

    this.dbConn = this.mongooseConn.useDb(dbName);
  }

  private async executeAggregation<T>(collection: string, pipeline: any[]): Promise<T[]> {
    await this.ensureMongoConnected();
    const db = (this.dbConn || this.mongooseConn).db;
    if (!db) throw new Error('MongoDB connection not initialized');
    const col = db.collection(collection);
    const cursor = col.aggregate(pipeline, { allowDiskUse: true });
    const result = await cursor.toArray();
    return result as T[];
  }

  private async executeFindOne<T>(collection: string, query: any): Promise<T | null> {
    await this.ensureMongoConnected();
    const db = (this.dbConn || this.mongooseConn).db;
    if (!db) throw new Error('MongoDB connection not initialized');
    const col = db.collection(collection);
    const doc = await col.findOne(query);
    return (doc as unknown as T) || null;
  }

  async mongoPing(): Promise<any> {
    await this.ensureMongoConnected();
    const db = (this.dbConn || this.mongooseConn).db;
    if (!db) throw new Error('MongoDB connection not initialized');
    const admin = db.admin();
    const res = await admin.command({ ping: 1 });
    return res;
  }

  async cachedAggregation<T>(
    collection: string,
    pipeline: any[],
    options: { ttl?: number; key?: string } = {}
  ): Promise<T[]> {
    const { ttl = 600, key } = options;
    const cacheKey = key || this.generateAggregationKey(collection, pipeline);
    const cached = await this.redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }
    const result = await this.executeAggregation<T>(collection, pipeline);
    await this.redis.setex(cacheKey, ttl, JSON.stringify(result));
    return result;
  }

  async cachedFindOne<T>(
    collection: string,
    query: any,
    options: { ttl?: number; key?: string } = {}
  ): Promise<T | null> {
    const { ttl = 300, key } = options;
    const cacheKey = key || this.generateQueryKey(collection, query);
    const cached = await this.redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }
    const result = await this.executeFindOne<T>(collection, query);
    if (result) {
      await this.redis.setex(cacheKey, ttl, JSON.stringify(result));
    }
    return result;
  }

  async invalidateCollectionCache(collection: string): Promise<number> {
    const pattern = `mongodb:collection:${collection}:*`;
    const keys = await this.redis.keys(pattern);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
    return keys.length;
  }

  private generateAggregationKey(collection: string, pipeline: any[]): string {
    const keyData = { collection, pipeline: JSON.stringify(pipeline) };
    const keyString = JSON.stringify(keyData);
    return `mongodb:aggregation:${Buffer.from(keyString).toString('base64')}`;
  }

  private generateQueryKey(collection: string, query: any): string {
    const keyData = { collection, query: JSON.stringify(query) };
    const keyString = JSON.stringify(keyData);
    return `mongodb:query:${Buffer.from(keyString).toString('base64')}`;
  }
}