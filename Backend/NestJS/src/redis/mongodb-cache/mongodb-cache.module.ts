import { Module } from '@nestjs/common';
import { MongodbCacheService } from './mongodb-cache.service';

@Module({
  providers: [MongodbCacheService],
  exports: [MongodbCacheService],
})
export class MongodbCacheModule {}
