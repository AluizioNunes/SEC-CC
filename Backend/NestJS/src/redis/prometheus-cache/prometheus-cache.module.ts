import { Module } from '@nestjs/common';
import { PrometheusCacheService } from './prometheus-cache.service';

@Module({
  providers: [PrometheusCacheService],
  exports: [PrometheusCacheService],
})
export class PrometheusCacheModule {}
