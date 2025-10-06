"""
Grafana Cache Integration for NestJS
Dashboard and query caching
"""
import { Injectable } from '@nestjs/common';
import { InjectRedis } from '@nestjs-modules/ioredis';
import Redis from 'ioredis';

@Injectable()
export class GrafanaCacheService {
  constructor(@InjectRedis() private readonly redis: Redis) {}

  async cacheDashboard(
    dashboardId: string,
    dashboardData: any,
    timeRange: { start: string; end: string },
    variables?: Record<string, any>,
    ttl: number = 300
  ): Promise<boolean> {
    try {
      const cacheKey = this.generateDashboardKey(dashboardId, timeRange, variables);

      const cacheData = {
        dashboardId,
        data: dashboardData,
        timeRange,
        variables,
        cachedAt: Date.now(),
        ttl
      };

      await this.redis.setex(cacheKey, ttl, JSON.stringify(cacheData));
      return true;
    } catch (error) {
      console.error('Grafana dashboard cache error:', error);
      return false;
    }
  }

  async getCachedDashboard(
    dashboardId: string,
    timeRange: { start: string; end: string },
    variables?: Record<string, any>
  ): Promise<any | null> {
    try {
      const cacheKey = this.generateDashboardKey(dashboardId, timeRange, variables);
      const cached = await this.redis.get(cacheKey);

      if (cached) {
        const cacheData = JSON.parse(cached);

        // Check if expired
        if (Date.now() - cacheData.cachedAt < cacheData.ttl * 1000) {
          return cacheData.data;
        }

        // Expired, remove from cache
        await this.redis.del(cacheKey);
      }

      return null;
    } catch (error) {
      console.error('Grafana dashboard retrieval error:', error);
      return null;
    }
  }

  async cacheQueryResult(
    queryHash: string,
    result: any,
    timeRange: { start: string; end: string },
    variables?: Record<string, any>,
    ttl: number = 300
  ): Promise<boolean> {
    try {
      const cacheKey = this.generateQueryKey(queryHash, timeRange, variables);

      const cacheData = {
        queryHash,
        result,
        timeRange,
        variables,
        cachedAt: Date.now(),
        ttl
      };

      await this.redis.setex(cacheKey, ttl, JSON.stringify(cacheData));
      return true;
    } catch (error) {
      console.error('Grafana query cache error:', error);
      return false;
    }
  }

  async getCachedQueryResult(
    queryHash: string,
    timeRange: { start: string; end: string },
    variables?: Record<string, any>
  ): Promise<any | null> {
    try {
      const cacheKey = this.generateQueryKey(queryHash, timeRange, variables);
      const cached = await this.redis.get(cacheKey);

      if (cached) {
        const cacheData = JSON.parse(cached);

        if (Date.now() - cacheData.cachedAt < cacheData.ttl * 1000) {
          return cacheData.result;
        }

        await this.redis.del(cacheKey);
      }

      return null;
    } catch (error) {
      console.error('Grafana query result retrieval error:', error);
      return null;
    }
  }

  async invalidateDashboard(dashboardId: string): Promise<number> {
    const pattern = `grafana:dashboard:${dashboardId}:*`;
    const keys = await this.redis.keys(pattern);

    if (keys.length > 0) {
      await this.redis.del(...keys);
    }

    return keys.length;
  }

  async preloadDashboard(dashboardId: string, timeRanges: Array<{ start: string; end: string }>): Promise<number> {
    let preloaded = 0;

    for (const timeRange of timeRanges) {
      // Simulate dashboard data (in real implementation, call Grafana API)
      const dashboardData = {
        id: dashboardId,
        title: `Dashboard ${dashboardId}`,
        panels: [
          { id: 1, title: 'CPU Usage', data: 'preloaded' },
          { id: 2, title: 'Memory Usage', data: 'preloaded' }
        ]
      };

      const success = await this.cacheDashboard(dashboardId, dashboardData, timeRange, undefined, 600);
      if (success) preloaded++;
    }

    return preloaded;
  }

  private generateDashboardKey(
    dashboardId: string,
    timeRange: { start: string; end: string },
    variables?: Record<string, any>
  ): string {
    const keyData = { dashboardId, timeRange, variables };
    const keyString = JSON.stringify(keyData);
    return `grafana:dashboard:${Buffer.from(keyString).toString('base64')}`;
  }

  private generateQueryKey(
    queryHash: string,
    timeRange: { start: string; end: string },
    variables?: Record<string, any>
  ): string {
    const keyData = { queryHash, timeRange, variables };
    const keyString = JSON.stringify(keyData);
    return `grafana:query:${Buffer.from(keyString).toString('base64')}`;
  }
}
