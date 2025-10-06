import { Module } from '@nestjs/common';
import { PostgresCacheService } from './postgres-cache.service';

@Module({
  providers: [PostgresCacheService],
  exports: [PostgresCacheService],
})
export class PostgresCacheModule {}
