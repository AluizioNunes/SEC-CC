import { Controller, Get, Post, Delete, Body, Param, Query } from '@nestjs/common';
import { RedisService } from './redis.service';
import { PostgresCacheService } from './postgres-cache/postgres-cache.service';
import { MongodbCacheService } from './mongodb-cache/mongodb-cache.service';
import { HybridBrokerService, MessagePriority, MessageBrokerType } from './hybrid-broker/hybrid-broker.service';
import { EventSourcingService, EventType } from './event-sourcing/event-sourcing.service';
import { GrafanaCacheService } from './grafana-cache/grafana-cache.service';
import { PrometheusCacheService } from './prometheus-cache/prometheus-cache.service';
import { AdvancedDataStructuresService } from './data-structures/data-structures.service';

@Controller('redis')
export class RedisController {
  constructor(
    private readonly redisService: RedisService,
    private readonly postgresCacheService: PostgresCacheService,
    private readonly mongodbCacheService: MongodbCacheService,
    private readonly hybridBrokerService: HybridBrokerService,
    private readonly eventSourcingService: EventSourcingService,
    private readonly grafanaCacheService: GrafanaCacheService,
    private readonly prometheusCacheService: PrometheusCacheService,
    private readonly dataStructuresService: AdvancedDataStructuresService,
  ) {}

  // Basic Redis operations
  @Get('get/:key')
  async get(@Param('key') key: string) {
    const value = await this.redisService.get(key);
    return { key, value };
  }

  @Post('set/:key')
  async set(@Param('key') key: string, @Body() body: { value: string; ttl?: number }) {
    const result = await this.redisService.set(key, body.value, body.ttl);
    return { success: result === 'OK', key, ttl: body.ttl || 300 };
  }

  @Delete('delete/:key')
  async delete(@Param('key') key: string) {
    const deleted = await this.redisService.delete(key);
    return { deleted, key };
  }

  @Get('exists/:key')
  async exists(@Param('key') key: string) {
    const exists = await this.redisService.exists(key);
    return { key, exists };
  }

  @Post('expire/:key')
  async expire(@Param('key') key: string, @Body() body: { seconds: number }) {
    const expired = await this.redisService.expire(key, body.seconds);
    return { key, expired, seconds: body.seconds };
  }

  @Get('ttl/:key')
  async ttl(@Param('key') key: string) {
    const ttl = await this.redisService.ttl(key);
    return { key, ttl };
  }

  // PostgreSQL Cache endpoints
  @Post('postgres/query')
  async postgresQuery(@Body() body: {
    query: string;
    params?: any[];
    ttl?: number;
    tableDependencies?: string[];
  }) {
    const result = await this.postgresCacheService.cachedQuery(
      body.query,
      body.params,
      { ttl: body.ttl, tableDependencies: body.tableDependencies }
    );
    return { query: body.query, result, cached: true };
  }

  @Post('postgres/invalidate')
  async invalidatePostgresTable(@Body() body: { table: string }) {
    const invalidated = await this.postgresCacheService.invalidateTableCache(body.table);
    return { table: body.table, invalidated };
  }

  // MongoDB Cache endpoints
  @Post('mongodb/aggregation')
  async mongodbAggregation(@Body() body: {
    collection: string;
    pipeline: any[];
    ttl?: number;
  }) {
    const result = await this.mongodbCacheService.cachedAggregation(
      body.collection,
      body.pipeline,
      { ttl: body.ttl }
    );
    return { collection: body.collection, result, cached: true };
  }

  @Get('mongodb/ping')
  async mongodbPing() {
    const res = await this.mongodbCacheService.mongoPing();
    return { ping: res };
  }

  @Post('mongodb/find')
  async mongodbFind(@Body() body: {
    collection: string;
    query: any;
    ttl?: number;
  }) {
    const result = await this.mongodbCacheService.cachedFindOne(
      body.collection,
      body.query,
      { ttl: body.ttl }
    );
    return { collection: body.collection, query: body.query, result, cached: true };
  }

  // Message Broker endpoints
  @Post('broker/publish')
  async publishMessage(@Body() body: {
    message: any;
    routingKey?: string;
    priority?: string;
    brokerType?: string;
  }) {
    const priority = body.priority ? MessagePriority[body.priority as keyof typeof MessagePriority] : MessagePriority.NORMAL;
    const brokerType = body.brokerType ? MessageBrokerType[body.brokerType as keyof typeof MessageBrokerType] : MessageBrokerType.HYBRID;
    
    const messageId = await this.hybridBrokerService.publishMessage(
      body.message,
      body.routingKey,
      priority,
      brokerType
    );
    return { messageId, routingKey: body.routingKey, priority: body.priority };
  }

  // Event Sourcing endpoints
  @Post('events/publish')
  async publishEvent(@Body() body: {
    eventType: string;
    data: any;
    userId?: string;
    entityId?: string;
    entityType?: string;
  }) {
    const eventType = EventType[body.eventType as keyof typeof EventType];
    const eventId = await this.eventSourcingService.publishEvent(
      eventType,
      body.data,
      body.userId,
      body.entityId,
      body.entityType
    );
    return { eventId, eventType: body.eventType };
  }

  // Grafana Cache endpoints
  @Post('grafana/cache-dashboard')
  async cacheGrafanaDashboard(@Body() body: {
    dashboardId: string;
    data: any;
    timeRange: { start: string; end: string };
    variables?: Record<string, any>;
    ttl?: number;
  }) {
    const success = await this.grafanaCacheService.cacheDashboard(
      body.dashboardId,
      body.data,
      body.timeRange,
      body.variables,
      body.ttl
    );
    return { dashboardId: body.dashboardId, cached: success };
  }

  @Post('grafana/cache-query')
  async cacheGrafanaQuery(@Body() body: {
    queryHash: string;
    result: any;
    timeRange: { start: string; end: string };
    variables?: Record<string, any>;
    ttl?: number;
  }) {
    const success = await this.grafanaCacheService.cacheQueryResult(
      body.queryHash,
      body.result,
      body.timeRange,
      body.variables,
      body.ttl
    );
    return { queryHash: body.queryHash, cached: success };
  }

  // Prometheus Cache endpoints
  @Post('prometheus/cache-query')
  async cachePrometheusQuery(@Body() body: {
    query: string;
    result: any;
    startTime: number;
    endTime: number;
    step?: number;
    ttl?: number;
  }) {
    const success = await this.prometheusCacheService.cacheQueryResult(
      body.query,
      body.result,
      body.startTime,
      body.endTime,
      body.step,
      body.ttl
    );
    return { query: body.query, cached: success };
  }

  @Post('prometheus/cache-metric')
  async cachePrometheusMetric(@Body() body: {
    metricName: string;
    data: any[];
    labels?: Record<string, string>;
    ttl?: number;
  }) {
    const success = await this.prometheusCacheService.cacheMetricData(
      body.metricName,
      body.data,
      body.labels,
      body.ttl
    );
    return { metricName: body.metricName, cached: success };
  }

  // Advanced Data Structures endpoints
  @Post('hash/set')
  async hashSet(@Body() body: { key: string; field: string; value: any }) {
    const result = await this.dataStructuresService.hashSet(body.key, body.field, body.value);
    return { key: body.key, field: body.field, set: result > 0 };
  }

  @Get('hash/get')
  async hashGet(@Query() query: { key: string; field: string }) {
    const value = await this.dataStructuresService.hashGet(query.key, query.field);
    return { key: query.key, field: query.field, value };
  }

  @Post('set/add')
  async setAdd(@Body() body: { key: string; members: any[] }) {
    const added = await this.dataStructuresService.setAdd(body.key, ...body.members);
    return { key: body.key, added, members: body.members };
  }

  @Get('set/members')
  async setMembers(@Query() query: { key: string }) {
    const members = await this.dataStructuresService.setMembers(query.key);
    return { key: query.key, members: Array.from(members) };
  }

  @Post('zset/add')
  async sortedSetAdd(@Body() body: { key: string; member: any; score: number }) {
    const added = await this.dataStructuresService.sortedSetAdd(body.key, body.member, body.score);
    return { key: body.key, member: body.member, score: body.score, added: added > 0 };
  }

  @Get('zset/range')
  async sortedSetRange(@Query() query: { key: string; start?: number; stop?: number }) {
    const results = await this.dataStructuresService.sortedSetGetRange(
      query.key,
      query.start || 0,
      query.stop || -1
    );
    return { key: query.key, results };
  }

  @Post('list/push')
  async listPush(@Body() body: { key: string; values: any[] }) {
    const length = await this.dataStructuresService.listPush(body.key, ...body.values);
    return { key: body.key, length, values: body.values };
  }

  @Get('list/pop')
  async listPop(@Query() query: { key: string }) {
    const value = await this.dataStructuresService.listPop(query.key);
    return { key: query.key, value };
  }

  // Statistics endpoints
  @Get('stats/postgres')
  async getPostgresStats() {
    // This would need to be implemented in the service
    return { status: 'Postgres cache stats endpoint' };
  }

  @Get('stats/mongodb')
  async getMongodbStats() {
    // This would need to be implemented in the service
    return { status: 'MongoDB cache stats endpoint' };
  }

  @Get('stats/broker')
  async getBrokerStats() {
    // This would need to be implemented in the service
    return { status: 'Message broker stats endpoint' };
  }

  @Get('stats/events')
  async getEventStats() {
    return await this.eventSourcingService.getEventStats();
  }

  @Get('stats/data-structures')
  async getDataStructuresStats() {
    return await this.dataStructuresService.getStats();
  }
}