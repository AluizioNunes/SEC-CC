"""
PostgreSQL Cache Integration for NestJS
Advanced PostgreSQL query caching with Redis
"""
import { Injectable } from '@nestjs/common';
import { InjectRedis } from '@nestjs-modules/ioredis';
import Redis from 'ioredis';

@Injectable()
export class PostgresCacheService {
  constructor(@InjectRedis() private readonly redis: Redis) {}

  async cachedQuery<T>(
    query: string,
    params: any[] = [],
    options: {
      ttl?: number;
      tableDependencies?: string[];
      key?: string;
    } = {}
  ): Promise<T[]> {
    const { ttl = 300, tableDependencies = [], key } = options;

    // Generate cache key
    const cacheKey = key || this.generateQueryKey(query, params);

    // Check cache first
    const cached = await this.redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    // Execute query (placeholder - would use actual TypeORM)
    const result = await this.executeQuery<T>(query, params);

    // Cache result
    await this.redis.setex(cacheKey, ttl, JSON.stringify(result));

    // Store table dependencies
    for (const table of tableDependencies) {
      await this.redis.sadd(`postgres:table:${table}`, cacheKey);
    }

    return result;
  }

  async invalidateTableCache(table: string): Promise<number> {
    const cacheKeys = await this.redis.smembers(`postgres:table:${table}`);

    if (cacheKeys.length > 0) {
      await this.redis.del(...cacheKeys);
      await this.redis.del(`postgres:table:${table}`);
    }

    return cacheKeys.length;
  }

  private generateQueryKey(query: string, params: any[]): string {
    const keyData = { query, params: JSON.stringify(params) };
    const keyString = JSON.stringify(keyData);
    return `postgres:${Buffer.from(keyString).toString('base64')}`;
  }

  private async executeQuery<T>(query: string, params: any[]): Promise<T[]> {
    // Placeholder for actual database query
    // In real implementation, this would use TypeORM or similar
    return [];
  }
}
