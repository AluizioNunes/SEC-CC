import { Controller, Get, Post, Body, Param } from '@nestjs/common';
import { QueuesService } from './queues.service';

@Controller('queue')
export class QueuesController {
  constructor(private readonly queuesService: QueuesService) {}

  @Post(':queueName')
  async enqueue(@Param('queueName') queueName: string, @Body() jobData: any) {
    return await this.queuesService.enqueue(queueName, jobData);
  }

  @Get(':queueName')
  async dequeue(@Param('queueName') queueName: string) {
    return await this.queuesService.dequeue(queueName);
  }
}
