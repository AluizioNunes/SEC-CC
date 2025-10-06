import { Controller, Get, Param } from '@nestjs/common';
import { RateLimitService } from './rate-limit.service';

@Controller('rate-limit')
export class RateLimitController {
  constructor(private readonly rateLimitService: RateLimitService) {}

  @Get(':userId')
  async checkRateLimit(@Param('userId') userId: string) {
    return await this.rateLimitService.check(userId);
  }
}
