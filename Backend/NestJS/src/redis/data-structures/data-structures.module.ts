import { Module } from '@nestjs/common';
import { AdvancedDataStructuresService } from './data-structures.service';

@Module({
  providers: [AdvancedDataStructuresService],
  exports: [AdvancedDataStructuresService],
})
export class AdvancedDataStructuresModule {}
