import { Injectable } from '@nestjs/common';
import { RedisService } from '../redis.service';

@Injectable()
export class CacheService {
  constructor(private readonly redisService: RedisService) {}

  async get(key: string): Promise<{ key: string; value?: string; error?: string }> {
    try {
      const value = await this.redisService.get(key);
      if (value) {
        return { key, value };
      }
      return { key, error: 'Key not found' };
    } catch (error) {
      return { key, error: 'Failed to get cache value' };
    }
  }

  async set(key: string, value: string, ttl?: number): Promise<{ success: boolean; key: string; ttl?: number }> {
    try {
      await this.redisService.set(key, value, ttl);
      return { success: true, key, ttl };
    } catch (error) {
      return { success: false, key };
    }
  }

  async delete(key: string): Promise<{ success: boolean; key: string }> {
    try {
      await this.redisService.delete(key);
      return { success: true, key };
    } catch (error) {
      return { success: false, key };
    }
  }
}
