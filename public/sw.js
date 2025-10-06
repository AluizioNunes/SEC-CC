/**
 * Service Worker with Redis Integration
 * Advanced PWA features with Redis caching
 */

const CACHE_NAME = 'redis-pwa-cache';
const REDIS_WS_URL = 'ws://localhost:8000/redis-ws';

// Redis WebSocket client for service worker
class ServiceWorkerRedisClient {
  private ws: WebSocket | null = null;

  constructor(private url: string) {}

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('Service Worker Redis WebSocket connected');
        resolve();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(JSON.parse(event.data));
      };

      this.ws.onerror = (error) => {
        console.error('Service Worker Redis WebSocket error:', error);
        reject(error);
      };
    });
  }

  private handleMessage(message: any) {
    switch (message.type) {
      case 'asset_update':
        this.handleAssetUpdate(message.data);
        break;
      case 'config_update':
        this.handleConfigUpdate(message.data);
        break;
    }
  }

  private async handleAssetUpdate(data: any) {
    const { url, content, contentType } = data;

    // Update cache with new asset
    const cache = await caches.open(CACHE_NAME);
    const response = new Response(content, {
      headers: { 'Content-Type': contentType }
    });

    await cache.put(url, response);

    // Notify clients
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'asset_updated',
        url,
        contentType
      });
    });
  }

  private async handleConfigUpdate(data: any) {
    // Update configuration in cache
    const cache = await caches.open(CACHE_NAME);
    await cache.put('/config.json', new Response(JSON.stringify(data)));
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }
}

// Install event - cache assets
self.addEventListener('install', (event: ExtendableEvent) => {
  console.log('Service Worker installing');

  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);

      // Cache essential assets
      const assetsToCache = [
        '/',
        '/index.html',
        '/manifest.json',
        '/config.json'
      ];

      await cache.addAll(assetsToCache);

      // Initialize Redis connection for service worker
      const redisClient = new ServiceWorkerRedisClient(REDIS_WS_URL);
      await redisClient.connect();

      // Subscribe to asset updates
      redisClient.send({
        type: 'subscribe_asset_updates',
        serviceWorker: true
      });
    })()
  );
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event: ExtendableEvent) => {
  console.log('Service Worker activating');

  event.waitUntil(
    (async () => {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map(name => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    })()
  );
});

// Fetch event - serve from cache with Redis fallback
self.addEventListener('fetch', (event: FetchEvent) => {
  event.respondWith(
    (async () => {
      const request = event.request;
      const url = new URL(request.url);

      // Handle API requests with Redis cache
      if (url.pathname.startsWith('/api/')) {
        return handleApiRequest(request);
      }

      // Handle asset requests
      if (url.pathname.match(/\.(css|js|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot)$/)) {
        return handleAssetRequest(request);
      }

      // Handle configuration requests
      if (url.pathname === '/config.json') {
        return handleConfigRequest(request);
      }

      // Default: try network first, then cache
      return fetch(request).catch(async () => {
        const cached = await caches.match(request);
        return cached || new Response('Offline', { status: 503 });
      });
    })()
  );
});

async function handleApiRequest(request: Request): Promise<Response> {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);

  if (cached) {
    // Check if cache is still valid
    const cacheTime = new Date(cached.headers.get('date') || 0).getTime();
    const now = Date.now();
    const maxAge = 5 * 60 * 1000; // 5 minutes

    if (now - cacheTime < maxAge) {
      return cached;
    }
  }

  try {
    const response = await fetch(request);

    // Cache successful responses
    if (response.ok) {
      const responseToCache = response.clone();
      cache.put(request, responseToCache);
    }

    return response;
  } catch (error) {
    // Return cached version if available
    return cached || new Response('Offline', { status: 503 });
  }
}

async function handleAssetRequest(request: Request): Promise<Response> {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);

  if (cached) {
    return cached;
  }

  try {
    const response = await fetch(request);

    if (response.ok) {
      const responseToCache = response.clone();
      cache.put(request, responseToCache);
    }

    return response;
  } catch (error) {
    return new Response('Asset not available offline', { status: 404 });
  }
}

async function handleConfigRequest(request: Request): Promise<Response> {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);

  if (cached) {
    return cached;
  }

  try {
    const response = await fetch(request);

    if (response.ok) {
      const responseToCache = response.clone();
      cache.put(request, responseToCache);
    }

    return response;
  } catch (error) {
    return new Response('Configuration not available offline', { status: 404 });
  }
}

// Background sync for offline actions
self.addEventListener('sync', (event: SyncEvent) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(handleBackgroundSync());
  }
});

async function handleBackgroundSync() {
  // Handle offline actions when back online
  const offlineActions = await getOfflineActions();

  for (const action of offlineActions) {
    try {
      await syncAction(action);
      await removeOfflineAction(action.id);
    } catch (error) {
      console.error('Failed to sync action:', action, error);
    }
  }
}

// IndexedDB for offline storage
async function getOfflineActions(): Promise<any[]> {
  // Implementation would use IndexedDB
  return [];
}

async function syncAction(action: any) {
  // Sync action with server
  await fetch('/api/sync', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(action)
  });
}

async function removeOfflineAction(actionId: string) {
  // Remove from IndexedDB
}

// Push notifications with Redis
self.addEventListener('push', (event: PushEvent) => {
  if (event.data) {
    const data = event.data.json();

    const options = {
      body: data.body,
      icon: '/icon-192x192.png',
      badge: '/badge-72x72.png',
      data: data.data,
      actions: data.actions || []
    };

    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// Notification click handling
self.addEventListener('notificationclick', (event: NotificationEvent) => {
  event.notification.close();

  if (event.action) {
    // Handle action buttons
    handleNotificationAction(event.action, event.notification.data);
  } else {
    // Default action
    event.waitUntil(
      clients.openWindow(event.notification.data?.url || '/')
    );
  }
});

async function handleNotificationAction(action: string, data: any) {
  // Handle notification actions
  switch (action) {
    case 'view':
      await clients.openWindow(data.url);
      break;
    case 'dismiss':
      // Just close notification (already done)
      break;
  }
}
