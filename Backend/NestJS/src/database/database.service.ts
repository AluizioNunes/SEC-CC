import { Injectable, Inject, OnModuleDestroy } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { InjectModel } from '@nestjs/mongoose';
import { Repository } from 'typeorm';
import { Model } from 'mongoose';
import { RedisService } from '../redis/redis.service';
import { User } from './entities/user.entity';
import { UserDocument } from './schemas/user.schema';

@Injectable()
export class DatabaseService implements OnModuleDestroy {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
    @InjectModel(User.name)
    private userModel: Model<UserDocument>,
    private redisService: RedisService,
  ) {}

  async onModuleDestroy() {
    // Cleanup connections if needed
  }

  // PostgreSQL operations with Redis cache
  async getUserFromPostgres(userId: string) {
    const cacheKey = `postgres_user:${userId}`;

    // Try cache first
    const cached = await this.redisService.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    // Get from PostgreSQL
    const user = await this.userRepository.findOne({ where: { id: userId } });
    if (user) {
      await this.redisService.set(cacheKey, JSON.stringify(user), 600);
      return user;
    }

    return null;
  }

  async createUserInPostgres(username: string, email: string) {
    const user = this.userRepository.create({ username, email });
    const savedUser = await this.userRepository.save(user);

    // Invalidate cache
    await this.redisService.delete(`postgres_user:${savedUser.id}`);

    return savedUser;
  }

  // MongoDB operations with Redis cache
  async getUserFromMongo(userId: string) {
    const cacheKey = `mongo_user:${userId}`;

    // Try cache first
    const cached = await this.redisService.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    // Get from MongoDB
    const user = await this.userModel.findOne({ userId }).exec();
    if (user) {
      await this.redisService.set(cacheKey, JSON.stringify(user.toObject()), 300);
      return user.toObject();
    }

    return null;
  }

  async createUserInMongo(userId: string, preferences: any = {}) {
    const user = new this.userModel({ userId, preferences });
    const savedUser = await user.save();

    // Invalidate cache
    await this.redisService.delete(`mongo_user:${userId}`);

    return savedUser.toObject();
  }

  // Combined operations
  async getCompleteUserData(userId: string) {
    const cacheKey = `complete_user:${userId}`;

    // Try cache first
    const cached = await this.redisService.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    // Get from both databases
    const [postgresUser, mongoUser] = await Promise.all([
      this.getUserFromPostgres(userId),
      this.getUserFromMongo(userId)
    ]);

    const completeData = {
      ...postgresUser,
      preferences: mongoUser?.preferences || {}
    };

    if (completeData.id) {
      await this.redisService.set(cacheKey, JSON.stringify(completeData), 300);
    }

    return completeData;
  }

  async createCompleteUser(username: string, email: string, preferences: any = {}) {
    // Create in PostgreSQL
    const postgresUser = await this.createUserInPostgres(username, email);

    // Create in MongoDB
    await this.createUserInMongo(postgresUser.id, preferences);

    // Invalidate combined cache
    await this.redisService.delete(`complete_user:${postgresUser.id}`);

    return {
      id: postgresUser.id,
      username: postgresUser.username,
      email: postgresUser.email,
      preferences
    };
  }

  // Cache invalidation
  async invalidateUserCache(userId: string) {
    await Promise.all([
      this.redisService.delete(`postgres_user:${userId}`),
      this.redisService.delete(`mongo_user:${userId}`),
      this.redisService.delete(`complete_user:${userId}`)
    ]);
  }

  // Health check
  async getDatabaseStatus() {
    const results = await Promise.allSettled([
      this.redisService.get('health_check'),
      this.userRepository.count(),
      this.userModel.countDocuments()
    ]);

    return {
      redis: results[0].status === 'fulfilled',
      postgresql: results[1].status === 'fulfilled',
      mongodb: results[2].status === 'fulfilled'
    };
  }
}
