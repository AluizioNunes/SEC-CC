import { Controller, Get, Post, Delete, Body, Param, Query } from '@nestjs/common';
import { RedisService } from './redis.service';

@Controller('redis')
export class RedisController {
  constructor(private readonly redisService: RedisService) {}

  @Get('get/:key')
  async get(@Param('key') key: string) {
    const value = await this.redisService.get(key);
    return { key, value };
  }

  @Post('set/:key')
  async set(@Param('key') key: string, @Body() body: { value: string; ttl?: number }) {
    const result = await this.redisService.set(key, body.value, body.ttl);
    return { success: result === 'OK', key, ttl: body.ttl || 300 };
  }

  @Delete('delete/:key')
  async delete(@Param('key') key: string) {
    const deleted = await this.redisService.delete(key);
    return { deleted, key };
  }

  @Get('exists/:key')
  async exists(@Param('key') key: string) {
    const exists = await this.redisService.exists(key);
    return { key, exists };
  }

  @Post('expire/:key')
  async expire(@Param('key') key: string, @Body() body: { seconds: number }) {
    const expired = await this.redisService.expire(key, body.seconds);
    return { key, expired, seconds: body.seconds };
  }

  @Get('ttl/:key')
  async ttl(@Param('key') key: string) {
    const ttl = await this.redisService.ttl(key);
    return { key, ttl };
  }
}
