import { Module } from '@nestjs/common';
import { GrafanaCacheService } from './grafana-cache.service';

@Module({
  providers: [GrafanaCacheService],
  exports: [GrafanaCacheService],
})
export class GrafanaCacheModule {}
