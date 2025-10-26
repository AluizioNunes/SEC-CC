import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { createClient, RedisClientType } from 'redis';

@Injectable()
export class ServiceRegistrationService implements OnModuleInit, OnModuleDestroy {
  private redisClient: RedisClientType;
  private instanceId: string;
  private serviceName: string;
  private isRegistered = false;
  private heartbeatInterval: NodeJS.Timeout;

  constructor() {
    // Initialize Redis client
    this.redisClient = createClient({
      socket: {
        host: process.env.REDIS_HOST || 'redis',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        connectTimeout: parseInt(process.env.REDIS_CONNECT_TIMEOUT || '3000'),
        reconnectStrategy: (retries) => Math.min(retries * 200, 2000),
      },
      password: process.env.REDIS_PASSWORD || 'redispassword2024',
    });

    this.redisClient.on('error', (err: any) => {
      console.error('Redis error:', err);
    });

    this.serviceName = 'nestjs'; // Default service name
    this.instanceId = '';
    this.heartbeatInterval = setTimeout(() => {}, 0) as NodeJS.Timeout;
  }

  async onModuleInit() {
    // Attempt Redis connection without blocking bootstrap
    this.redisClient
      .connect()
      .then(async () => {
        await this.registerService();
        this.startHeartbeat();
        console.log('✅ Service registration initialized');
      })
      .catch((error) => {
        console.error('❌ Service registration initialization failed:', error);
      });
  }

  async onModuleDestroy() {
    try {
      // Stop heartbeat
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval);
      }

      // Unregister service
      await this.unregisterService();

      // Disconnect from Redis (only if open)
      if (this.redisClient?.isOpen) {
        await this.redisClient.quit();
      }

      console.log('✅ Service unregistration completed');
    } catch (error) {
      console.error('❌ Service unregistration failed:', error);
    }
  }

  private async registerService() {
    try {
      this.instanceId = this.generateInstanceId();
      
      const registrationData = {
        service_id: this.instanceId,
        service_name: this.serviceName,
        host: process.env.HOST || 'nestjs',
        port: parseInt(process.env.PORT || '3000'),
        status: 'healthy',
        last_heartbeat: Date.now(),
        metadata: {
          startup_time: Date.now(),
          version: '1.0.0',
          environment: process.env.ENVIRONMENT || 'development'
        },
        tags: ['nestjs', 'auto-registered'],
        version: '1.0.0'
      };

      // Store in Redis with 24-hour expiration
      await this.redisClient.setEx(
        `service_registry:service:${this.instanceId}`,
        86400,
        JSON.stringify(registrationData)
      );

      // Add to service set
      await this.redisClient.sAdd(
        `service_registry:services:${this.serviceName}`,
        this.instanceId
      );

      // Register with service mesh
      await this.registerWithServiceMesh();

      this.isRegistered = true;
      console.log(`✅ Service ${this.serviceName} registered with ID: ${this.instanceId}`);
    } catch (error) {
      console.error('❌ Service registration failed:', error);
    }
  }

  private async registerWithServiceMesh() {
    try {
      const meshData = {
        service_name: this.serviceName,
        instance_id: this.instanceId,
        host: process.env.HOST || 'nestjs',
        port: parseInt(process.env.PORT || '3000'),
        status: 'healthy',
        last_heartbeat: Date.now(),
        metadata: {
          startup_time: Date.now(),
          version: '1.0.0'
          },
        load_score: 0.0
      };

      // Store in Redis with 24-hour expiration
      await this.redisClient.setEx(
        `service_mesh:instance:${this.instanceId}`,
        86400,
        JSON.stringify(meshData)
      );

      // Add to service registry
      await this.redisClient.sAdd(
        `service_mesh:service:${this.serviceName}`,
        this.instanceId
      );

      console.log(`✅ Service registered with service mesh`);
    } catch (error) {
      console.error('❌ Service mesh registration failed:', error);
    }
  }

  private async unregisterService() {
    try {
      if (!this.isRegistered || !this.instanceId) {
        return;
      }

      // Remove from service registry
      await this.redisClient.sRem(
        `service_registry:services:${this.serviceName}`,
        this.instanceId
      );

      // Remove instance data
      await this.redisClient.del(`service_registry:service:${this.instanceId}`);

      // Remove from service mesh
      await this.redisClient.sRem(
        `service_mesh:service:${this.serviceName}`,
        this.instanceId
      );

      // Remove service mesh instance data
      await this.redisClient.del(`service_mesh:instance:${this.instanceId}`);

      this.isRegistered = false;
      console.log(`✅ Service ${this.serviceName} unregistered`);
    } catch (error) {
      console.error('❌ Service unregistration failed:', error);
    }
  }

  private startHeartbeat() {
    this.heartbeatInterval = setInterval(async () => {
      try {
        if (this.isRegistered && this.instanceId) {
          // Update heartbeat in service registry
          const serviceData = await this.redisClient.get(`service_registry:service:${this.instanceId}`);
          if (serviceData) {
            const parsedData = JSON.parse(serviceData);
            parsedData.last_heartbeat = Date.now();
            await this.redisClient.setEx(
              `service_registry:service:${this.instanceId}`,
              86400,
              JSON.stringify(parsedData)
            );
          }

          // Update heartbeat in service mesh
          const meshData = await this.redisClient.get(`service_mesh:instance:${this.instanceId}`);
          if (meshData) {
            const parsedData = JSON.parse(meshData);
            parsedData.last_heartbeat = Date.now();
            parsedData.load_score = 0.0; // Default load score
            await this.redisClient.setEx(
              `service_mesh:instance:${this.instanceId}`,
              86400,
              JSON.stringify(parsedData)
            );
          }
        }
      } catch (error) {
        console.error('❌ Heartbeat update failed:', error);
      }
    }, 30000); // Send heartbeat every 30 seconds
  }

  private generateInstanceId(): string {
    return `${this.serviceName}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  async updateLoadScore(loadScore: number) {
    try {
      if (this.instanceId) {
        const meshData = await this.redisClient.get(`service_mesh:instance:${this.instanceId}`);
        if (meshData) {
          const parsedData = JSON.parse(meshData);
          parsedData.load_score = loadScore;
          await this.redisClient.setEx(
            `service_mesh:instance:${this.instanceId}`,
            86400,
            JSON.stringify(parsedData)
          );
        }
      }
    } catch (error) {
      console.error('❌ Load score update failed:', error);
    }
  }
}