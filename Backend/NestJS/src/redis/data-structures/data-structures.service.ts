"""
Advanced Data Structures for NestJS
Redis advanced data structures utilities
"""
import { Injectable } from '@nestjs/common';
import { InjectRedis } from '@nestjs-modules/ioredis';
import Redis from 'ioredis';

@Injectable()
export class AdvancedDataStructuresService {
  constructor(@InjectRedis() private readonly redis: Redis) {}

  // Hash operations
  async hashSet(key: string, field: string, value: any): Promise<number> {
    return await this.redis.hset(`nestjs:hash:${key}`, field, JSON.stringify(value));
  }

  async hashGet(key: string, field: string): Promise<any> {
    const value = await this.redis.hget(`nestjs:hash:${key}`, field);
    return value ? JSON.parse(value) : null;
  }

  async hashGetAll(key: string): Promise<Record<string, any>> {
    const values = await this.redis.hgetall(`nestjs:hash:${key}`);
    const result: Record<string, any> = {};

    for (const [field, value] of Object.entries(values)) {
      result[field] = JSON.parse(value);
    }

    return result;
  }

  // Set operations
  async setAdd(key: string, ...members: any[]): Promise<number> {
    const jsonMembers = members.map(member => JSON.stringify(member));
    return await this.redis.sadd(`nestjs:set:${key}`, ...jsonMembers);
  }

  async setMembers(key: string): Promise<Set<any>> {
    const members = await this.redis.smembers(`nestjs:set:${key}`);
    return new Set(members.map(member => JSON.parse(member)));
  }

  async setIsMember(key: string, member: any): Promise<boolean> {
    return await this.redis.sismember(`nestjs:set:${key}`, JSON.stringify(member));
  }

  // Sorted Set operations (Leaderboards)
  async sortedSetAdd(key: string, member: any, score: number): Promise<number> {
    return await this.redis.zadd(`nestjs:zset:${key}`, score, JSON.stringify(member));
  }

  async sortedSetGetRange(key: string, start: number = 0, stop: number = -1): Promise<Array<{member: any; score: number}>> {
    const results = await this.redis.zrange(`nestjs:zset:${key}`, start, stop, 'WITHSCORES');

    const formattedResults = [];
    for (let i = 0; i < results.length; i += 2) {
      formattedResults.push({
        member: JSON.parse(results[i]),
        score: parseFloat(results[i + 1])
      });
    }

    return formattedResults;
  }

  async sortedSetIncrementScore(key: string, member: any, increment: number): Promise<number> {
    return await this.redis.zincrby(`nestjs:zset:${key}`, increment, JSON.stringify(member));
  }

  // List operations (Queues)
  async listPush(key: string, ...values: any[]): Promise<number> {
    const jsonValues = values.map(value => JSON.stringify(value));
    return await this.redis.rpush(`nestjs:list:${key}`, ...jsonValues);
  }

  async listPop(key: string): Promise<any | null> {
    const value = await this.redis.lpop(`nestjs:list:${key}`);
    return value ? JSON.parse(value) : null;
  }

  async listLength(key: string): Promise<number> {
    return await this.redis.llen(`nestjs:list:${key}`);
  }

  // HyperLogLog operations
  async hyperloglogAdd(key: string, ...elements: any[]): Promise<number> {
    return await this.redis.pfadd(`nestjs:hll:${key}`, ...elements);
  }

  async hyperloglogCount(key: string): Promise<number> {
    return await this.redis.pfcount(`nestjs:hll:${key}`);
  }

  // Geospatial operations
  async geoAdd(key: string, longitude: number, latitude: number, member: string): Promise<number> {
    return await this.redis.geoadd(`nestjs:geo:${key}`, longitude, latitude, member);
  }

  async geoSearch(
    key: string,
    longitude: number,
    latitude: number,
    radiusKm: number,
    unit: 'km' | 'm' | 'mi' | 'ft' = 'km'
  ): Promise<Array<{member: string; distance: number}>> {
    const results = await this.redis.georadius(
      `nestjs:geo:${key}`,
      longitude,
      latitude,
      radiusKm,
      unit,
      'WITHDIST'
    );

    return results.map(([member, distance]) => ({
      member,
      distance: parseFloat(distance)
    }));
  }

  // Utility methods
  async getStats() {
    const patterns = [
      'nestjs:hash:*',
      'nestjs:set:*',
      'nestjs:zset:*',
      'nestjs:list:*',
      'nestjs:hll:*',
      'nestjs:geo:*'
    ];

    const stats = {};

    for (const pattern of patterns) {
      const keys = await this.redis.keys(pattern);
      const type = pattern.split(':')[1];

      stats[type] = {
        count: keys.length,
        totalSize: 0
      };

      // Calculate total size for sample keys
      for (const key of keys.slice(0, 10)) {
        stats[type].totalSize += await this.redis.strlen(key);
      }
    }

    return stats;
  }

  async cleanupExpired() {
    // Cleanup expired keys (TTL-based cleanup)
    const patterns = [
      'nestjs:hash:*',
      'nestjs:set:*',
      'nestjs:zset:*',
      'nestjs:list:*'
    ];

    let cleaned = 0;

    for (const pattern of patterns) {
      const keys = await this.redis.keys(pattern);

      for (const key of keys) {
        const ttl = await this.redis.ttl(key);
        if (ttl === -2) { // Key doesn't exist
          continue;
        }
        if (ttl === -1 || ttl === 0) { // No expiration or expired
          await this.redis.del(key);
          cleaned++;
        }
      }
    }

    return cleaned;
  }
}
