import { Module } from '@nestjs/common';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { RedisModule } from './redis/redis.module';
import { DatabaseModule } from './database/database.module';
import { ServiceRegistrationModule } from './service-registration/service-registration.module';
import { MessageHandlerModule } from './message-handler/message-handler.module';

@Module({
  imports: [
    RedisModule,
    DatabaseModule,
    ServiceRegistrationModule,
    MessageHandlerModule,
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
