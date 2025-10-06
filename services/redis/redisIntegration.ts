/**
 * Frontend Redis Integration Service
 * Client-side Redis integration for React/TypeScript
 */

// Redis WebSocket client for real-time features
export class RedisWebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 1000;

  constructor(private url: string = 'ws://localhost:8000/redis-ws') {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('Redis WebSocket connected');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(JSON.parse(event.data));
        };

        this.ws.onclose = () => {
          console.log('Redis WebSocket disconnected');
          this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('Redis WebSocket error:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleMessage(message: any) {
    // Handle different message types
    switch (message.type) {
      case 'user_update':
        this.onUserUpdate?.(message.data);
        break;
      case 'notification':
        this.onNotification?.(message.data);
        break;
      case 'cache_update':
        this.onCacheUpdate?.(message.data);
        break;
      default:
        console.log('Unhandled Redis message:', message);
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect().catch(() => {
          // Reconnection failed, will retry
        });
      }, this.reconnectInterval * this.reconnectAttempts);
    }
  }

  // Event handlers
  onUserUpdate?: (data: any) => void;
  onNotification?: (data: any) => void;
  onCacheUpdate?: (data: any) => void;

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected');
    }
  }
}

// Asset caching service
export class AssetCacheService {
  private cache: Map<string, { data: any; timestamp: number; ttl: number }> = new Map();

  set(key: string, data: any, ttl: number = 3600000) { // 1 hour default
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  get(key: string): any | null {
    const item = this.cache.get(key);

    if (!item) return null;

    // Check if expired
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  invalidate(key: string) {
    this.cache.delete(key);
  }

  clear() {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }
}

// State management with Redis
export class RedisStateManager {
  private redisClient: RedisWebSocketClient;
  private assetCache: AssetCacheService;
  private subscribers: Map<string, Set<(data: any) => void>> = new Map();

  constructor() {
    this.redisClient = new RedisWebSocketClient();
    this.assetCache = new AssetCacheService();
  }

  async initialize() {
    await this.redisClient.connect();

    // Subscribe to state updates
    this.redisClient.onCacheUpdate = (data) => {
      this.handleStateUpdate(data);
    };
  }

  // Subscribe to state changes
  subscribe(key: string, callback: (data: any) => void): () => void {
    if (!this.subscribers.has(key)) {
      this.subscribers.set(key, new Set());
    }

    this.subscribers.get(key)!.add(callback);

    // Send current cached value if available
    const cachedValue = this.assetCache.get(key);
    if (cachedValue !== null) {
      callback(cachedValue);
    }

    // Return unsubscribe function
    return () => {
      const callbacks = this.subscribers.get(key);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.subscribers.delete(key);
        }
      }
    };
  }

  // Update state
  async updateState(key: string, data: any, ttl: number = 3600000) {
    this.assetCache.set(key, data, ttl);

    // Notify subscribers
    this.notifySubscribers(key, data);

    // Send to Redis for cross-tab synchronization
    this.redisClient.send({
      type: 'state_update',
      key,
      data,
      timestamp: Date.now()
    });
  }

  private handleStateUpdate(data: any) {
    const { key, data: newData } = data;

    // Update local cache
    this.assetCache.set(key, newData);

    // Notify subscribers
    this.notifySubscribers(key, newData);
  }

  private notifySubscribers(key: string, data: any) {
    const callbacks = this.subscribers.get(key);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  // User preferences management
  async saveUserPreferences(userId: string, preferences: Record<string, any>) {
    const key = `user_preferences:${userId}`;
    await this.updateState(key, preferences, 86400000); // 24 hours

    // Also save to localStorage as backup
    localStorage.setItem(key, JSON.stringify(preferences));
  }

  async getUserPreferences(userId: string): Promise<Record<string, any> | null> {
    const key = `user_preferences:${userId}`;

    // Try cache first
    const cached = this.assetCache.get(key);
    if (cached) return cached;

    // Fallback to localStorage
    const stored = localStorage.getItem(key);
    if (stored) {
      const preferences = JSON.parse(stored);
      // Update cache
      await this.updateState(key, preferences, 86400000);
      return preferences;
    }

    return null;
  }

  // Real-time notifications
  async subscribeToNotifications(userId: string, callback: (notification: any) => void) {
    return this.subscribe(`notifications:${userId}`, callback);
  }

  async sendNotification(userId: string, notification: any) {
    const key = `notifications:${userId}`;
    await this.updateState(key, {
      ...notification,
      id: Date.now(),
      timestamp: Date.now()
    });
  }

  // Asset caching for CSS/JS
  async cacheAsset(url: string, content: string, contentType: string) {
    const key = `asset:${url}:${contentType}`;
    await this.updateState(key, {
      content,
      contentType,
      url,
      cachedAt: Date.now()
    }, 86400000 * 7); // 7 days
  }

  async getCachedAsset(url: string, contentType: string): Promise<string | null> {
    const key = `asset:${url}:${contentType}`;
    const asset = this.assetCache.get(key);
    return asset?.content || null;
  }

  // Configuration management
  async getConfiguration(key: string): Promise<any> {
    return this.assetCache.get(`config:${key}`);
  }

  async updateConfiguration(key: string, value: any) {
    await this.updateState(`config:${key}`, value, 3600000); // 1 hour
  }

  disconnect() {
    this.redisClient.disconnect();
  }
}

// React hook for Redis state management
export function useRedisState<T>(key: string, initialValue?: T) {
  const [state, setState] = useState<T | undefined>(initialValue);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const redisManager = new RedisStateManager();

    redisManager.initialize().then(() => {
      const unsubscribe = redisManager.subscribe(key, (data) => {
        setState(data);
        setLoading(false);
      });

      return unsubscribe;
    }).catch((error) => {
      console.error('Failed to initialize Redis state manager:', error);
      setLoading(false);
    });

    return () => {
      redisManager.disconnect();
    };
  }, [key]);

  const updateState = async (newValue: T) => {
    const redisManager = new RedisStateManager();
    await redisManager.initialize();
    await redisManager.updateState(key, newValue);
  };

  return { state, loading, updateState };
}
