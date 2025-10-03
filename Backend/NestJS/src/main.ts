import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { Controller, Get, Module } from '@nestjs/common';
import { collectDefaultMetrics, Counter, Histogram, register } from 'prom-client';

collectDefaultMetrics();
const httpCounter = new Counter({ name: 'http_requests_total', help: 'Total HTTP requests', labelNames: ['method', 'path', 'status'] });
const httpDuration = new Histogram({ name: 'http_request_duration_seconds', help: 'Duration of HTTP requests', labelNames: ['method', 'path'] });

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
    return { service: 'nestjs' };
  }
}

@Module({ controllers: [AppController] })
class AppModule {}

async function bootstrap() {
  const app = await NestFactory.create(AppModule, { bufferLogs: true });

  // Simple middleware to collect metrics
  app.use(async (req: any, res: any, next: any) => {
    const end = (httpDuration.labels as any)(req.method, req.path).startTimer();
    res.on('finish', () => {
      end();
      (httpCounter.labels as any)(req.method, req.path, String(res.statusCode)).inc();
    });
    next();
  });

  await app.listen(process.env.PORT || 3000, '0.0.0.0');
}

bootstrap();
