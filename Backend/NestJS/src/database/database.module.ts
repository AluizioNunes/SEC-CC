import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { MongooseModule } from '@nestjs/mongoose';
import { RedisModule } from '../redis/redis.module';
import { DatabaseService } from './database.service';
import { User, UserSchema } from './schemas/user.schema';

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
    MongooseModule.forRoot(
      process.env.MONGODB_URL || 'mongodb://mongodb:27017/secmongo'
    ),
    MongooseModule.forFeature([{ name: User.name, schema: UserSchema }]),
    RedisModule,
  ],
  providers: [DatabaseService],
  exports: [DatabaseService],
})
export class DatabaseModule {}
