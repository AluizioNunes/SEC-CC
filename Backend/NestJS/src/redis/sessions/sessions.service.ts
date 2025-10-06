import { Injectable } from '@nestjs/common';
import { RedisService } from '../redis.service';

@Injectable()
export class SessionsService {
  constructor(private readonly redisService: RedisService) {}

  async create(userId: string, data: any): Promise<{ sessionId: string; userId: string }> {
    const sessionId = `session:${userId}:${Date.now()}`;
    await this.redisService.set(sessionId, JSON.stringify(data), 3600);
    return { sessionId, userId };
  }

  async get(sessionId: string): Promise<{ sessionId: string; data?: any; error?: string }> {
    try {
      const data = await this.redisService.get(sessionId);
      if (data) {
        return { sessionId, data: JSON.parse(data) };
      }
      return { sessionId, error: 'Session not found' };
    } catch (error) {
      return { sessionId, error: 'Failed to get session' };
    }
  }
}
