import { Module } from '@nestjs/common';
import { RedisModule as IoRedisModule } from '@nestjs-modules/ioredis';
import { MongodbCacheService } from './mongodb-cache.service';

@Module({
  imports: [
    IoRedisModule.forRoot({
      type: 'single',
      url: `redis://:${process.env.REDIS_PASSWORD || 'redispassword2024'}@${process.env.REDIS_HOST || 'redis'}:${process.env.REDIS_PORT || '6379'}`,
    }),
  ],
  providers: [MongodbCacheService],
  exports: [MongodbCacheService],
})
export class MongodbCacheModule {}
