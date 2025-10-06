import { Controller, Get, Post, Delete, Body, Param } from '@nestjs/common';
import { CacheService } from './cache.service';

@Controller('cache')
export class CacheController {
  constructor(private readonly cacheService: CacheService) {}

  @Get(':key')
  async getCache(@Param('key') key: string) {
    return await this.cacheService.get(key);
  }

  @Post(':key')
  async setCache(@Param('key') key: string, @Body() body: { value: string; ttl?: number }) {
    return await this.cacheService.set(key, body.value, body.ttl);
  }

  @Delete(':key')
  async deleteCache(@Param('key') key: string) {
    return await this.cacheService.delete(key);
  }
}
