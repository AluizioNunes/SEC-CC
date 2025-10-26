import { Module } from '@nestjs/common';
import { RedisModule as IoRedisModule } from '@nestjs-modules/ioredis';
import { HybridBrokerService } from './hybrid-broker.service';

@Module({
  imports: [
    IoRedisModule.forRoot({
      type: 'single',
      url: `redis://:${process.env.REDIS_PASSWORD || 'redispassword2024'}@${process.env.REDIS_HOST || 'redis'}:${process.env.REDIS_PORT || '6379'}`,
    }),
  ],
  providers: [HybridBrokerService],
  exports: [HybridBrokerService],
})
export class HybridBrokerModule {}
