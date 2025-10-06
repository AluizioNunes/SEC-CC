import { Controller, Get, Post, Body, Param } from '@nestjs/common';
import { SessionsService } from './sessions.service';

@Controller('session')
export class SessionsController {
  constructor(private readonly sessionsService: SessionsService) {}

  @Post(':userId')
  async createSession(@Param('userId') userId: string, @Body() data: any) {
    return await this.sessionsService.create(userId, data);
  }

  @Get(':sessionId')
  async getSession(@Param('sessionId') sessionId: string) {
    return await this.sessionsService.get(sessionId);
  }
}
