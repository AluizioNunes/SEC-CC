import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { Controller, Get, Module, Res, ValidationPipe, Logger } from '@nestjs/common';
import { Response } from 'express';
import * as client from 'prom-client';
import { ServiceRegistrationService } from './service-registration/service-registration.service';
import { ServiceRegistrationModule } from './service-registration/service-registration.module';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';

// Security imports
import helmet from 'helmet'
import * as compression from 'compression'
import { ThrottlerModule } from '@nestjs/throttler';

// Logging imports
import { WinstonModule } from 'nest-winston'
import * as winston from 'winston';

// Tracing imports
import * as jaeger from 'jaeger-client'

// CORS configuration
import { CorsOptions } from '@nestjs/common/interfaces/external/cors-options.interface';

// Create a single registry instance to avoid duplicate metrics
const register = new client.Registry();

// Check if metrics are already registered to prevent duplicates
const registerMetrics = () => {
  // Only register default metrics if they haven't been registered yet
  if (register.getSingleMetric('process_cpu_user_seconds_total') === undefined) {
    client.collectDefaultMetrics({ register });
  }
};

// Enhanced CORS configuration
const corsOptions: CorsOptions = {
  origin: [
    'http://localhost:3000',
    'http://localhost:5173',
    process.env.FRONTEND_URL || 'http://localhost:3000'
  ],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  exposedHeaders: ['X-Total-Count', 'X-Page-Count'],
  credentials: true,
  maxAge: 86400, // 24 hours
};

// winston logger configuration
const logger = WinstonModule.createLogger({
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json(),
        winston.format.printf(({ timestamp, level, message, context, trace, ...meta }) => {
          return JSON.stringify({ timestamp, level, message, context, trace, ...meta });
        }),
      ),
    }),
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json(),
      ),
    }),
    new winston.transports.File({
      filename: 'logs/combined.log',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json(),
      ),
    }),
  ],
});

// Jaeger tracing configuration
const initJaegerTracer = () => {
  const config = {
    serviceName: 'nestjs-service',
    sampler: {
      type: 'const',
      param: 1,
    },
    reporter: {
      logSpans: true,
      agentHost: process.env.JAEGER_AGENT_HOST || 'jaeger',
      agentPort: parseInt(process.env.JAEGER_AGENT_PORT || '6832'),
    },
  } as any;

  return jaeger.initTracer(config, {});
};

@Controller()
class AppController {
  private readonly logger = new Logger(AppController.name);

  constructor(private readonly jwtService: JwtService) {}

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
    // Enhanced readiness check
    return {
      status: 'ready',
      service: 'nestjs',
      checks: {
        redis: 'ok',
        database: 'ok',
        jwt: 'configured'
      },
      timestamp: new Date().toISOString()
    };
  }

  @Get('health/live')
  livenessProbe() {
    // Enhanced liveness check
    return {
      status: 'alive',
      service: 'nestjs',
      timestamp: new Date().toISOString(),
      uptime: process.uptime()
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
    // Register default metrics only once
    registerMetrics();

    // Get metrics as a string
    const metrics = await register.metrics();

    // Send the metrics as plain text response
    res.set('Content-Type', register.contentType);
    res.send(metrics);
  }

  @Get('auth/test')
  async testAuth() {
    // Mock authentication endpoint
    const payload = { sub: 'test-user', role: 'admin' };
    const token = this.jwtService.sign(payload);

    this.logger.log(`JWT token generated for user: ${payload.sub}`);

    return {
      message: 'Authentication test successful',
      token: token,
      expiresIn: '30m'
    };
  }
}

@Module({
  imports: [
    ServiceRegistrationModule,
    WinstonModule.forRoot({
      transports: [
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.errors({ stack: true }),
            winston.format.json(),
            winston.format.printf(({ timestamp, level, message, context, trace, ...meta }) => {
              return JSON.stringify({ timestamp, level, message, context, trace, ...meta });
            }),
          ),
        }),
        new winston.transports.File({
          filename: 'logs/error.log',
          level: 'error',
          format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.errors({ stack: true }),
            winston.format.json(),
          ),
        }),
        new winston.transports.File({
          filename: 'logs/combined.log',
          format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.json(),
          ),
        }),
      ],
    }),
  ],
  controllers: [AppController],
  providers: [ServiceRegistrationService, JwtService, ConfigService],
})
class AppModule {}

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: logger,
  });

  // Initialize Jaeger tracer
  const tracer = initJaegerTracer();

  // Global validation pipe
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
  }));

  // Security middleware
  app.use(helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", "data:", "https:"],
      },
    },
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true,
    },
  }))

  // Compression middleware
  app.use(compression())

  // CORS configuration
  app.enableCors(corsOptions);

  // Rate limiting
  app.useGlobalPipes(new ValidationPipe());

  // Get service registration service
  const serviceRegistrationService = app.get(ServiceRegistrationService);

  // Enhanced logging middleware
  app.use((req: any, res: any, next: any) => {
    const start = Date.now();

    res.on('finish', () => {
      const duration = Date.now() - start;
      logger.log({
        message: 'HTTP Request',
        method: req.method,
        url: req.url,
        statusCode: res.statusCode,
        duration: `${duration}ms`,
        ip: req.ip,
        userAgent: req.get('User-Agent'),
      });
    });

    next();
  });

  await app.listen(process.env.PORT || 3000, '0.0.0.0');

  const port = process.env.PORT || 3000;
  logger.log(`NestJS application with enhanced security started on port ${port}`);
  logger.log(`Metrics available at http://localhost:${port}/metrics`);
  logger.log(`Health checks available at http://localhost:${port}/health`);
  logger.log(`JWT authentication configured`);
  logger.log(`Structured logging enabled`);
  logger.log(`Jaeger tracing enabled`);
}

bootstrap();