import { Module } from '@nestjs/common';
import { HybridBrokerService } from './hybrid-broker.service';

@Module({
  providers: [HybridBrokerService],
  exports: [HybridBrokerService],
})
export class HybridBrokerModule {}
