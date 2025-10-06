import { Module } from '@nestjs/common';
import { RedisController } from './redis.controller';
import { RedisService } from './redis.service';

// Advanced modules
import { PostgresCacheModule } from './postgres-cache/postgres-cache.module';
import { MongodbCacheModule } from './mongodb-cache/mongodb-cache.module';
import { HybridBrokerModule } from './hybrid-broker/hybrid-broker.module';
import { EventSourcingModule } from './event-sourcing/event-sourcing.module';
import { GrafanaCacheModule } from './grafana-cache/grafana-cache.module';
import { PrometheusCacheModule } from './prometheus-cache/prometheus-cache.module';
import { AdvancedDataStructuresModule } from './data-structures/data-structures.module';

@Module({
  imports: [
    PostgresCacheModule,
    MongodbCacheModule,
    HybridBrokerModule,
    EventSourcingModule,
    GrafanaCacheModule,
    PrometheusCacheModule,
    AdvancedDataStructuresModule,
  ],
  controllers: [RedisController],
  providers: [RedisService],
  exports: [
    RedisService,
    PostgresCacheModule,
    MongodbCacheModule,
    HybridBrokerModule,
    EventSourcingModule,
    GrafanaCacheModule,
    PrometheusCacheModule,
    AdvancedDataStructuresModule,
  ],
})
export class RedisModule {}
