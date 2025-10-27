import { Module, Logger, OnModuleInit } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { MongooseModule, InjectConnection } from '@nestjs/mongoose';
import { Connection } from 'mongoose';
import { RedisModule } from '../redis/redis.module';
import { DatabaseService } from './database.service';
import { User, UserSchema } from './schemas/user.schema';
import { DatabaseController } from './database.controller';
import { User as UserEntity } from './entities/user.entity';

class DatabaseConnectionLogger implements OnModuleInit {
  private readonly logger = new Logger('DatabaseConnectionLogger');
  constructor(@InjectConnection() private readonly conn: Connection) {}
  async onModuleInit() {
    try {
      const host = process.env.MONGODB_HOST || 'mongodb';
      const dbName = process.env.MONGODB_DB || 'secmongo';
      const authSource = process.env.MONGODB_AUTH_SOURCE || 'admin';
      // Wait briefly if not ready
      const start = Date.now();
      while (this.conn.readyState !== 1 && Date.now() - start < 3000) {
        await new Promise((r) => setTimeout(r, 100));
      }
      this.logger.log(`MongoDB connection state=${this.conn.readyState} host=${host} db=${dbName} authSource=${authSource}`);
    } catch (e) {
      this.logger.error(`MongoDB connection logger error: ${e instanceof Error ? e.message : e}`);
    }
  }
}

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'postgres',
      host: process.env.POSTGRES_HOST || 'postgres',
      port: parseInt(process.env.POSTGRES_PORT || '5432'),
      username: process.env.POSTGRES_USER || 'sec',
      password: process.env.POSTGRES_PASSWORD || 'secpass',
      database: process.env.POSTGRES_DB || 'secdb',
      entities: [__dirname + '/entities/*.entity{.ts,.js}'],
      synchronize: true, // Only for development
      logging: false,
    }),
    TypeOrmModule.forFeature([UserEntity]),
    MongooseModule.forRoot(
      `mongodb://${process.env.MONGODB_HOST || 'mongodb'}:27017/${process.env.MONGODB_DB || 'secmongo'}`,
      {
        user: process.env.MONGODB_USER || 'secmongo',
        pass: process.env.MONGODB_PASSWORD || 'mongopass2024',
        authSource: process.env.MONGODB_AUTH_SOURCE || 'admin',
      }
    ),
    MongooseModule.forFeature([{ name: User.name, schema: UserSchema }]),
    RedisModule,
  ],
  controllers: [DatabaseController],
  providers: [DatabaseService, DatabaseConnectionLogger],
  exports: [DatabaseService],
})
export class DatabaseModule {}
