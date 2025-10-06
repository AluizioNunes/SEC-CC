"""
Prometheus Cache Integration for NestJS
Metrics query caching and optimization
"""
import { Injectable } from '@nestjs/common';
import { InjectRedis } from '@nestjs-modules/ioredis';
import Redis from 'ioredis';

@Injectable()
export class PrometheusCacheService {
  constructor(@InjectRedis() private readonly redis: Redis) {}

  async cacheQueryResult(
    query: string,
    result: any,
    startTime: number,
    endTime: number,
    step: number = 60,
    ttl: number = 300
  ): Promise<boolean> {
    try {
      const cacheKey = this.generateQueryKey(query, startTime, endTime, step);

      const cacheData = {
        query,
        result,
        startTime,
        endTime,
        step,
        cachedAt: Date.now(),
        ttl
      };

      await this.redis.setex(cacheKey, ttl, JSON.stringify(cacheData));
      return true;
    } catch (error) {
      console.error('Prometheus query cache error:', error);
      return false;
    }
  }

  async getCachedQueryResult(
    query: string,
    startTime: number,
    endTime: number,
    step: number = 60
  ): Promise<any | null> {
    try {
      const cacheKey = this.generateQueryKey(query, startTime, endTime, step);
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
      console.error('Prometheus query retrieval error:', error);
      return null;
    }
  }

  async cacheMetricData(
    metricName: string,
    data: any[],
    labels?: Record<string, string>,
    ttl: number = 300
  ): Promise<boolean> {
    try {
      const cacheKey = this.generateMetricKey(metricName, labels);

      const cacheData = {
        metricName,
        data,
        labels,
        cachedAt: Date.now(),
        ttl
      };

      await this.redis.setex(cacheKey, ttl, JSON.stringify(cacheData));
      return true;
    } catch (error) {
      console.error('Prometheus metric cache error:', error);
      return false;
    }
  }

  async getCachedMetricData(
    metricName: string,
    labels?: Record<string, string>
  ): Promise<any[] | null> {
    try {
      const cacheKey = this.generateMetricKey(metricName, labels);
      const cached = await this.redis.get(cacheKey);

      if (cached) {
        const cacheData = JSON.parse(cached);

        if (Date.now() - cacheData.cachedAt < cacheData.ttl * 1000) {
          return cacheData.data;
        }

        await this.redis.del(cacheKey);
      }

      return null;
    } catch (error) {
      console.error('Prometheus metric retrieval error:', error);
      return null;
    }
  }

  async getHotMetrics(limit: number = 10): Promise<Array<{metric: string; accessCount: number}>> {
    try {
      const pattern = 'prometheus:metric:*';
      const keys = await this.redis.keys(pattern);

      const metricAccess: Record<string, number> = {};

      for (const key of keys) {
        const cached = await this.redis.get(key);
        if (cached) {
          const cacheData = JSON.parse(cached);
          const metricName = cacheData.metricName;

          metricAccess[metricName] = (metricAccess[metricName] || 0) + 1;
        }
      }

      return Object.entries(metricAccess)
        .map(([metric, accessCount]) => ({ metric, accessCount }))
        .sort((a, b) => b.accessCount - a.accessCount)
        .slice(0, limit);

    } catch (error) {
      console.error('Hot metrics error:', error);
      return [];
    }
  }

  async preloadCommonQueries(queries: Array<{query: string; timeRange: {start: number; end: number}}>): Promise<number> {
    let preloaded = 0;

    for (const queryInfo of queries) {
      // Simulate Prometheus query result
      const mockResult = {
        status: 'success',
        data: {
          resultType: 'matrix',
          result: [
            {
              metric: { __name__: 'up', job: 'prometheus' },
              values: [[Date.now() / 1000, '1'], [(Date.now() - 60) / 1000, '1']]
            }
          ]
        }
      };

      const success = await this.cacheQueryResult(
        queryInfo.query,
        mockResult,
        queryInfo.timeRange.start,
        queryInfo.timeRange.end,
        60,
        600
      );

      if (success) preloaded++;
    }

    return preloaded;
  }

  private generateQueryKey(query: string, startTime: number, endTime: number, step: number): string {
    const keyData = { query, startTime, endTime, step };
    const keyString = JSON.stringify(keyData);
    return `prometheus:query:${Buffer.from(keyString).toString('base64')}`;
  }

  private generateMetricKey(metricName: string, labels?: Record<string, string>): string {
    const keyData = { metricName, labels };
    const keyString = JSON.stringify(keyData);
    return `prometheus:metric:${Buffer.from(keyString).toString('base64')}`;
  }
}
