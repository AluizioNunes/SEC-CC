import { Injectable } from '@nestjs/common';
import { RedisService } from '../redis.service';

@Injectable()
export class RateLimitService {
  constructor(private readonly redisService: RedisService) {}

  async check(userId: string): Promise<{ allowed: boolean; userId: string }> {
    try {
      const client = this.redisService.getClient();
      const key = `ratelimit:${userId}`;
      const current = await client.get(key);

      if (!current) {
        await client.setex(key, 60, '1');
        return { allowed: true, userId };
      }

      const count = parseInt(current);
      if (count >= 100) {
        return { allowed: false, userId };
      }

      await client.incr(key);
      return { allowed: true, userId };
    } catch (error) {
      return { allowed: true, userId };
    }
  }
}
