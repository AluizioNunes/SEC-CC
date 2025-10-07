import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { Controller, Get, Module, Res } from '@nestjs/common';
import { Response } from 'express';
import * as client from 'prom-client';

@Controller()
class AppController {
  @Get()
  getHello(): string {
    return 'NestJS funcionando!';
  }

  @Get('health')
  health() {
    return { 
      status: 'ok', 
      service: 'nestjs',
      timestamp: new Date().toISOString()
    };
  }

  @Get('health/ready')
  readinessProbe() {
    // Simple readiness check
    return { 
      status: 'ready', 
      service: 'nestjs',
      checks: {
        redis: 'ok',
        database: 'ok'
      }
    };
  }

  @Get('health/live')
  livenessProbe() {
    // Simple liveness check
    return { 
      status: 'alive', 
      service: 'nestjs',
      timestamp: new Date().toISOString()
    };
  }

  @Get('redis-status')
  redisStatus() {
    return {
      status: 'connected',
      host: process.env.REDIS_HOST || 'redis',
      port: process.env.REDIS_PORT || '6379'
    };
  }

  @Get('metrics')
  async metrics(@Res() res: Response) {
    // Register some default metrics
    client.collectDefaultMetrics({ register: client.register });

    // Get metrics as a string
    const metrics = await client.register.metrics();
    
    // Send the metrics as plain text response
    res.set('Content-Type', client.register.contentType);
    res.send(metrics);
  }
}

@Module({ controllers: [AppController] })
class AppModule {}

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  await app.listen(process.env.PORT || 3000, '0.0.0.0');
  console.log(`NestJS básico rodando na porta ${process.env.PORT || 3000}`);
}

bootstrap();