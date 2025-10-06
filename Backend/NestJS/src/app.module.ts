import { Module } from '@nestjs/common';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { RedisModule } from './redis/redis.module';
import { DatabaseModule } from './database/database.module';

@Module({
  imports: [
    RedisModule,
    DatabaseModule,
    ClientsModule.register([
      {
        name: 'REDIS_SERVICE',
        transport: Transport.REDIS,
        options: {
          host: process.env.REDIS_HOST || 'redis',
          port: parseInt(process.env.REDIS_PORT || '6379'),
        }
      },
    ]),
  ],
})
export class AppModule {}
