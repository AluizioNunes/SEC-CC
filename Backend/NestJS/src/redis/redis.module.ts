import { Module } from '@nestjs/common';
import { RedisService } from './redis.service';
import { CacheController } from './cache/cache.controller';
import { CacheService } from './cache/cache.service';
import { SessionsController } from './sessions/sessions.controller';
import { SessionsService } from './sessions/sessions.service';
import { QueuesController } from './queues/queues.controller';
import { QueuesService } from './queues/queues.service';
import { RateLimitController } from './rate-limit/rate-limit.controller';
import { RateLimitService } from './rate-limit/rate-limit.service';

@Module({
  controllers: [CacheController, SessionsController, QueuesController, RateLimitController],
  providers: [RedisService, CacheService, SessionsService, QueuesService, RateLimitService],
  exports: [RedisService, CacheService, SessionsService, QueuesService, RateLimitService],
})
export class RedisModule {}
