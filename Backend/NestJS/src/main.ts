import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { Controller, Get, Post, Delete, Body, Param, Module } from '@nestjs/common';
import { collectDefaultMetrics, Counter, Histogram, register } from 'prom-client';
import * as Redis from 'ioredis';

collectDefaultMetrics();

// Redis client
const redis = new Redis({
  host: process.env.REDIS_HOST || 'redis',
  port: parseInt(process.env.REDIS_PORT || '6379'),
});

// Metrics
const httpCounter = new Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'path', 'status']
});

const httpDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests',
  labelNames: ['method', 'path']
});

const redisCounter = new Counter({
  name: 'redis_operations_total',
  help: 'Redis operations',
  labelNames: ['operation', 'status']
});

// Redis utilities
async function getCache(key: string): Promise<string | null> {
  try {
    const value = await redis.get(key);
    redisCounter.labels('get', 'success').inc();
    return value;
  } catch (error) {
    redisCounter.labels('get', 'error').inc();
    console.error('Redis get error:', error);
    return null;
  }
}

async function setCache(key: string, value: string, ttl: number = 300): Promise<boolean> {
  try {
    await redis.setex(key, ttl, value);
    redisCounter.labels('set', 'success').inc();
    return true;
  } catch (error) {
    redisCounter.labels('set', 'error').inc();
    console.error('Redis set error:', error);
    return false;
  }
}

async function deleteCache(key: string): Promise<boolean> {
  try {
    await redis.del(key);
    redisCounter.labels('delete', 'success').inc();
    return true;
  } catch (error) {
    redisCounter.labels('delete', 'error').inc();
    console.error('Redis delete error:', error);
    return false;
  }
}

@Controller()
class AppController {
  @Get('health')
  health() {
    return { status: 'ok' };
  }

  @Get('metrics')
  async metrics() {
    return register.metrics();
  }

  @Get('api/node/info')
  info() {
    return {
      service: 'nestjs',
      redis_host: process.env.REDIS_HOST || 'redis',
      redis_port: process.env.REDIS_PORT || '6379'
    };
  }

  // Cache endpoints
  @Get('cache/:key')
  async getCache(@Param('key') key: string) {
    const value = await getCache(key);
    if (value) {
      return { key, value };
    }
    return { error: 'Key not found' };
  }

  @Post('cache/:key')
  async setCache(@Param('key') key: string, @Body() body: { value: string; ttl?: number }) {
    const success = await setCache(key, body.value, body.ttl);
    return { success, key, ttl: body.ttl || 300 };
  }

  @Delete('cache/:key')
  async deleteCache(@Param('key') key: string) {
    const success = await deleteCache(key);
    return { success, key };
  }

  // Session management
  @Post('session/:userId')
  async createSession(@Param('userId') userId: string, @Body() data: any) {
    const sessionId = `session:${userId}:${Date.now()}`;
    await setCache(sessionId, JSON.stringify(data), 3600);
    return { sessionId, userId };
  }

  @Get('session/:sessionId')
  async getSession(@Param('sessionId') sessionId: string) {
    const data = await getCache(sessionId);
    if (data) {
      return { sessionId, data: JSON.parse(data) };
    }
    return { error: 'Session not found' };
  }

  // Queue operations
  @Post('queue/:queueName')
  async enqueue(@Param('queueName') queueName: string, @Body() jobData: any) {
    try {
      await redis.lpush(`queue:${queueName}`, JSON.stringify(jobData));
      redisCounter.labels('enqueue', 'success').inc();
      return { success: true, queue: queueName };
    } catch (error) {
      redisCounter.labels('enqueue', 'error').inc();
      return { success: false, error };
    }
  }

  @Get('queue/:queueName')
  async dequeue(@Param('queueName') queueName: string) {
    try {
      const job = await redis.rpop(`queue:${queueName}`);
      if (job) {
        redisCounter.labels('dequeue', 'success').inc();
        return { job: JSON.parse(job), queue: queueName };
      }
      return { error: 'No jobs in queue' };
    } catch (error) {
      redisCounter.labels('dequeue', 'error').inc();
      return { success: false, error };
    }
  }

  // Rate limiting
  @Get('rate-limit/:userId')
  async checkRateLimit(@Param('userId') userId: string) {
    try {
      const key = `ratelimit:${userId}`;
      const current = await redis.get(key);

      if (!current) {
        await redis.setex(key, 60, '1');
        return { allowed: true, userId };
      }

      const count = parseInt(current);
      if (count >= 100) {
        return { allowed: false, userId };
      }

      await redis.incr(key);
      return { allowed: true, userId };
    } catch (error) {
      return { allowed: true, userId, error: 'Rate limit check failed' };
    }
  }

  // Redis statistics
  @Get('redis/stats')
  async getRedisStats() {
    try {
      const info = await redis.info();
      const lines = info.split('\r\n');
      const stats: any = {};

      lines.forEach(line => {
        if (line && !line.startsWith('#')) {
          const [key, value] = line.split(':');
          if (key && value) {
            stats[key] = value;
          }
        }
      });

      return {
        connected_clients: parseInt(stats.connected_clients || '0'),
        used_memory_human: stats.used_memory_human || '0B',
        keyspace_hits: parseInt(stats.keyspace_hits || '0'),
        keyspace_misses: parseInt(stats.keyspace_misses || '0'),
        uptime_days: parseInt(stats.uptime_in_days || '0')
      };
    } catch (error) {
      return { error: 'Failed to get Redis stats' };
    }
  }
}

@Module({ controllers: [AppController] })
class AppModule {}

async function bootstrap() {
  const app = await NestFactory.create(AppModule, { bufferLogs: true });

  // Metrics middleware
  app.use(async (req: any, res: any, next: any) => {
    const end = (httpDuration.labels as any)(req.method, req.path).startTimer();
    res.on('finish', () => {
      end();
      (httpCounter.labels as any)(req.method, req.path, String(res.statusCode)).inc();
    });
    next();
  });

  // Graceful shutdown
  process.on('SIGTERM', async () => {
    await redis.quit();
    await app.close();
  });

  await app.listen(process.env.PORT || 3000, '0.0.0.0');
  console.log(`NestJS Redis application running on port ${process.env.PORT || 3000}`);
}

bootstrap();
