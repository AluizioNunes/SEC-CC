/**
 * Advanced Collaborative State Management for Frontend
 * Real-time collaborative editing with Operational Transformation
 */

import { RedisWebSocketClient } from './redisIntegration';

// Operational Transformation for conflict resolution
export class OperationalTransformation {
  private operations: Map<string, any[]> = new Map();
  private pendingOps: Map<string, any[]> = new Map();

  transform(operation: any, concurrentOps: any[]): any {
    let transformedOp = { ...operation };

    for (const concurrentOp of concurrentOps) {
      if (this.operationsOverlap(transformedOp, concurrentOp)) {
        transformedOp = this.transformOperation(transformedOp, concurrentOp);
      }
    }

    return transformedOp;
  }

  private operationsOverlap(op1: any, op2: any): boolean {
    // Check if operations affect the same part of the document
    return op1.position <= op2.position + op2.length &&
           op2.position <= op1.position + op1.length;
  }

  private transformOperation(op1: any, op2: any): any {
    // Transform operation based on concurrent operation
    if (op1.type === 'insert' && op2.type === 'insert') {
      if (op1.position <= op2.position) {
        return { ...op1, position: op1.position + op2.content.length };
      }
    } else if (op1.type === 'delete' && op2.type === 'delete') {
      if (op1.position < op2.position) {
        return { ...op1, position: Math.max(0, op1.position - op2.length) };
      }
    }

    return op1;
  }
}

// Conflict-free Replicated Data Types (CRDT)
export class CRDTManager {
  private document = '';
  private operations: any[] = [];
  private siteId: string;

  constructor(siteId?: string) {
    this.siteId = siteId || `site_${Date.now()}_${Math.random()}`;
  }

  // Generate unique operation ID
  generateOperationId(): string {
    return `${this.siteId}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Apply local operation
  applyLocalOperation(operation: any): string {
    const opId = this.generateOperationId();
    operation.id = opId;
    operation.timestamp = Date.now();

    // Apply to local document
    this.applyOperationToDocument(operation);

    // Add to operations history
    this.operations.push(operation);

    return opId;
  }

  // Merge remote operation
  mergeRemoteOperation(operation: any): boolean {
    // Check if operation is already applied
    if (this.operations.some(op => op.id === operation.id)) {
      return false;
    }

    // Apply operation to document
    this.applyOperationToDocument(operation);
    this.operations.push(operation);

    return true;
  }

  private applyOperationToDocument(operation: any) {
    switch (operation.type) {
      case 'insert':
        const before = this.document.slice(0, operation.position);
        const after = this.document.slice(operation.position);
        this.document = before + operation.content + after;
        break;

      case 'delete':
        const start = operation.position;
        const end = operation.position + operation.length;
        this.document = this.document.slice(0, start) + this.document.slice(end);
        break;

      case 'replace':
        this.document = this.document.slice(0, operation.position) +
                       operation.content +
                       this.document.slice(operation.position + operation.length);
        break;
    }
  }

  getDocument(): string {
    return this.document;
  }

  getOperations(): any[] {
    return [...this.operations];
  }

  // Synchronize with remote state
  async synchronize(remoteOperations: any[]): Promise<boolean> {
    try {
      // Find operations that need to be applied
      const operationsToApply = remoteOperations.filter(
        remoteOp => !this.operations.some(localOp => localOp.id === remoteOp.id)
      );

      for (const operation of operationsToApply) {
        this.mergeRemoteOperation(operation);
      }

      return true;
    } catch (error) {
      console.error('Synchronization error:', error);
      return false;
    }
  }
}

// Real-time collaborative editing manager
export class CollaborativeEditingManager {
  private redisClient: RedisWebSocketClient;
  private crdtManager: CRDTManager;
  private ot: OperationalTransformation;
  private documentSubscribers: Set<(document: string, operations: any[]) => void> = new Set();
  private userCursors: Map<string, { position: number; color: string }> = new Map();

  constructor(documentId: string, userId: string) {
    this.redisClient = new RedisWebSocketClient();
    this.crdtManager = new CRDTManager(`${userId}_${documentId}`);
    this.ot = new OperationalTransformation();
  }

  async initialize() {
    await this.redisClient.connect();

    // Subscribe to document updates
    this.redisClient.onCacheUpdate = (data) => {
      if (data.type === 'document_update') {
        this.handleDocumentUpdate(data);
      } else if (data.type === 'cursor_update') {
        this.handleCursorUpdate(data);
      }
    };

    // Send initial subscription
    this.redisClient.send({
      type: 'subscribe_document',
      documentId: this.crdtManager['siteId'],
      userId: this.crdtManager['siteId'].split('_')[0]
    });
  }

  // Apply local operation
  async applyLocalOperation(operation: any): Promise<string> {
    const opId = this.crdtManager.applyLocalOperation(operation);

    // Broadcast to other users
    this.redisClient.send({
      type: 'operation',
      operation: { ...operation, id: opId },
      documentId: this.crdtManager['siteId']
    });

    // Notify local subscribers
    this.notifyDocumentUpdate();

    return opId;
  }

  private async handleDocumentUpdate(data: any) {
    const { operation, userId } = data;

    // Transform operation if needed
    const concurrentOps = this.crdtManager.getOperations()
      .filter(op => op.timestamp > operation.timestamp - 1000); // Last second

    const transformedOp = this.ot.transform(operation, concurrentOps);

    // Apply operation
    this.crdtManager.mergeRemoteOperation(transformedOp);

    // Notify subscribers
    this.notifyDocumentUpdate();
  }

  private handleCursorUpdate(data: any) {
    const { userId, position, color } = data;
    this.userCursors.set(userId, { position, color });
    this.notifyCursorUpdate();
  }

  // Update cursor position
  async updateCursor(position: number, color: string = '#3b82f6') {
    this.redisClient.send({
      type: 'cursor_update',
      userId: this.crdtManager['siteId'].split('_')[0],
      position,
      color,
      documentId: this.crdtManager['siteId']
    });
  }

  // Subscribe to document changes
  subscribe(callback: (document: string, operations: any[]) => void): () => void {
    this.documentSubscribers.add(callback);

    // Send current document state
    callback(this.crdtManager.getDocument(), this.crdtManager.getOperations());

    return () => {
      this.documentSubscribers.delete(callback);
    };
  }

  // Subscribe to cursor changes
  subscribeToCursors(callback: (cursors: Map<string, { position: number; color: string }>) => void): () => void {
    const wrappedCallback = () => callback(this.userCursors);
    this.cursorSubscribers.add(wrappedCallback);

    // Send current cursor state
    callback(this.userCursors);

    return () => {
      this.cursorSubscribers.delete(wrappedCallback);
    };
  }

  private cursorSubscribers: Set<() => void> = new Set();

  private notifyDocumentUpdate() {
    const document = this.crdtManager.getDocument();
    const operations = this.crdtManager.getOperations();

    this.documentSubscribers.forEach(callback => {
      callback(document, operations);
    });
  }

  private notifyCursorUpdate() {
    this.cursorSubscribers.forEach(callback => callback());
  }

  // Document locking
  async lockSection(start: number, end: number, userId: string): Promise<boolean> {
    const lockKey = `document_lock:${this.crdtManager['siteId']}:${start}_${end}`;

    try {
      // Try to acquire lock
      const lockAcquired = await this.redisClient.redisClient?.set(
        lockKey,
        userId,
        'EX', 300, // 5 minutes
        'NX'
      );

      if (lockAcquired) {
        // Broadcast lock acquisition
        this.redisClient.send({
          type: 'section_locked',
          userId,
          start,
          end,
          documentId: this.crdtManager['siteId']
        });

        return true;
      }

      return false;
    } catch (error) {
      console.error('Lock acquisition error:', error);
      return false;
    }
  }

  async unlockSection(start: number, end: number, userId: string): Promise<boolean> {
    const lockKey = `document_lock:${this.crdtManager['siteId']}:${start}_${end}`;

    try {
      const currentOwner = await this.redisClient.redisClient?.get(lockKey);

      if (currentOwner === userId) {
        await this.redisClient.redisClient?.del(lockKey);

        // Broadcast lock release
        this.redisClient.send({
          type: 'section_unlocked',
          userId,
          start,
          end,
          documentId: this.crdtManager['siteId']
        });

        return true;
      }

      return false;
    } catch (error) {
      console.error('Lock release error:', error);
      return false;
    }
  }

  // Version control integration
  async saveVersion(versionName: string, description?: string): Promise<string> {
    const versionId = `version_${Date.now()}`;

    const versionData = {
      id: versionId,
      name: versionName,
      description,
      document: this.crdtManager.getDocument(),
      operations: this.crdtManager.getOperations(),
      timestamp: Date.now()
    };

    // Save version in Redis
    await this.redisClient.redisClient?.setex(
      `document_versions:${this.crdtManager['siteId']}:${versionId}`,
      86400 * 30, // 30 days
      JSON.stringify(versionData)
    );

    return versionId;
  }

  async loadVersion(versionId: string): Promise<boolean> {
    try {
      const versionData = await this.redisClient.redisClient?.get(
        `document_versions:${this.crdtManager['siteId']}:${versionId}`
      );

      if (versionData) {
        const version = JSON.parse(versionData);

        // Reset document to version state
        this.crdtManager = new CRDTManager(this.crdtManager['siteId']);
        this.crdtManager['document'] = version.document;
        this.crdtManager['operations'] = version.operations;

        // Notify subscribers
        this.notifyDocumentUpdate();

        return true;
      }

      return false;
    } catch (error) {
      console.error('Version load error:', error);
      return false;
    }
  }

  disconnect() {
    this.redisClient.disconnect();
  }
}

// React hooks for collaborative editing
export function useCollaborativeDocument(documentId: string, userId: string) {
  const [document, setDocument] = useState('');
  const [operations, setOperations] = useState<any[]>([]);
  const [cursors, setCursors] = useState<Map<string, { position: number; color: string }>>(new Map());
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const manager = new CollaborativeEditingManager(documentId, userId);

    manager.initialize().then(() => {
      setIsConnected(true);

      // Subscribe to document changes
      const unsubscribeDocument = manager.subscribe((doc, ops) => {
        setDocument(doc);
        setOperations(ops);
      });

      // Subscribe to cursor changes
      const unsubscribeCursors = manager.subscribeToCursors(setCursors);

      return () => {
        unsubscribeDocument();
        unsubscribeCursors();
        manager.disconnect();
      };
    }).catch((error) => {
      console.error('Failed to initialize collaborative editing:', error);
    });
  }, [documentId, userId]);

  const applyOperation = async (operation: any) => {
    // This would be implemented to use the manager
    console.log('Apply operation:', operation);
  };

  const updateCursor = async (position: number, color?: string) => {
    // This would be implemented to use the manager
    console.log('Update cursor:', position, color);
  };

  return {
    document,
    operations,
    cursors,
    isConnected,
    applyOperation,
    updateCursor
  };
}
