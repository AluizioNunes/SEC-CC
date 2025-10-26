import { Module } from '@nestjs/common';
import { RedisModule as IoRedisModule } from '@nestjs-modules/ioredis';
import { AdvancedDataStructuresService } from './data-structures.service';

@Module({
  imports: [
    IoRedisModule.forRoot({
      type: 'single',
      url: `redis://:${process.env.REDIS_PASSWORD || 'redispassword2024'}@${process.env.REDIS_HOST || 'redis'}:${process.env.REDIS_PORT || '6379'}`,
    }),
  ],
  providers: [AdvancedDataStructuresService],
  exports: [AdvancedDataStructuresService],
})
export class AdvancedDataStructuresModule {}
