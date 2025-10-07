import { Module } from '@nestjs/common';
import { MessageHandlerService } from './message-handler.service';
import { RedisModule } from '../redis/redis.module';

@Module({
  imports: [RedisModule],
  providers: [MessageHandlerService],
  exports: [MessageHandlerService],
})
export class MessageHandlerModule {}