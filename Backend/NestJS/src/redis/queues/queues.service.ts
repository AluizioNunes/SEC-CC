import { Injectable } from '@nestjs/common';
import { RedisService } from '../redis.service';

@Injectable()
export class QueuesService {
  constructor(private readonly redisService: RedisService) {}

  async enqueue(queueName: string, jobData: any): Promise<{ success: boolean; queue: string }> {
    try {
      const client = this.redisService.getClient();
      await client.lpush(`queue:${queueName}`, JSON.stringify(jobData));
      return { success: true, queue: queueName };
    } catch (error) {
      return { success: false, queue: queueName };
    }
  }

  async dequeue(queueName: string): Promise<{ job?: any; queue: string; error?: string }> {
    try {
      const client = this.redisService.getClient();
      const job = await client.rpop(`queue:${queueName}`);
      if (job) {
        return { job: JSON.parse(job), queue: queueName };
      }
      return { queue: queueName, error: 'No jobs in queue' };
    } catch (error) {
      return { queue: queueName, error: 'Failed to dequeue job' };
    }
  }
}
