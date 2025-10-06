import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { Controller, Get, Module } from '@nestjs/common';

@Controller()
class AppController {
  @Get()
  getHello(): string {
    return 'NestJS funcionando!';
  }

  @Get('health')
  health() {
    return { status: 'ok', service: 'nestjs' };
  }

  @Get('redis-status')
  redisStatus() {
    return {
      status: 'connected',
      host: process.env.REDIS_HOST || 'redis',
      port: process.env.REDIS_PORT || '6379'
    };
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
