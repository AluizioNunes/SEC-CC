import { Module } from '@nestjs/common';
import { ServiceRegistrationService } from './service-registration.service';

@Module({
  providers: [ServiceRegistrationService],
  exports: [ServiceRegistrationService],
})
export class ServiceRegistrationModule {}