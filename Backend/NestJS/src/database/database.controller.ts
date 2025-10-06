import { Controller, Get, Post, Body, Param } from '@nestjs/common';
import { DatabaseService } from '../database/database.service';

@Controller('database')
export class DatabaseController {
  constructor(private readonly databaseService: DatabaseService) {}

  @Get('status')
  async getDatabaseStatus() {
    return await this.databaseService.getDatabaseStatus();
  }

  @Get('user/:userId')
  async getUser(@Param('userId') userId: string) {
    return await this.databaseService.getCompleteUserData(userId);
  }

  @Post('user')
  async createUser(@Body() body: { username: string; email: string; preferences?: any }) {
    return await this.databaseService.createCompleteUser(
      body.username,
      body.email,
      body.preferences
    );
  }

  @Post('user/:userId/invalidate-cache')
  async invalidateCache(@Param('userId') userId: string) {
    await this.databaseService.invalidateUserCache(userId);
    return { success: true, message: 'Cache invalidated' };
  }
}
