/**
 * MCP连接池管理器
 * 
 * 实现连接复用、健康检查、动态调整等功能
 */

export interface Connection {
  id: string;
  createdAt: number;
  lastUsedAt: number;
  isHealthy: boolean;
  metadata?: Record<string, any>;
}

export interface ConnectionPoolConfig {
  minSize: number;
  maxSize: number;
  idleTimeout: number; // ms
  healthCheckInterval: number; // ms
  connectionTimeout: number; // ms
}

export class ConnectionPool {
  private connections: Map<string, Connection> = new Map();
  private activeConnections: Set<string> = new Set();
  private config: ConnectionPoolConfig;
  private healthCheckTimer?: NodeJS.Timeout;

  constructor(config: Partial<ConnectionPoolConfig> = {}) {
    this.config = {
      minSize: config.minSize ?? 5,
      maxSize: config.maxSize ?? 20,
      idleTimeout: config.idleTimeout ?? 30000, // 30秒
      healthCheckInterval: config.healthCheckInterval ?? 10000, // 10秒
      connectionTimeout: config.connectionTimeout ?? 5000, // 5秒
    };

    this.startHealthCheck();
  }

  /**
   * 获取连接
   */
  async acquire(): Promise<Connection> {
    // 尝试复用现有连接
    for (const [id, conn] of this.connections.entries()) {
      if (!this.activeConnections.has(id) && conn.isHealthy) {
        this.activeConnections.add(id);
        conn.lastUsedAt = Date.now();
        return conn;
      }
    }

    // 创建新连接
    if (this.connections.size < this.config.maxSize) {
      const conn = await this.createConnection();
      this.connections.set(conn.id, conn);
      this.activeConnections.add(conn.id);
      return conn;
    }

    // 等待连接释放
    return this.waitForConnection();
  }

  /**
   * 释放连接
   */
  release(connectionId: string): void {
    this.activeConnections.delete(connectionId);
    const conn = this.connections.get(connectionId);
    if (conn) {
      conn.lastUsedAt = Date.now();
    }
  }

  /**
   * 创建新连接
   */
  private async createConnection(): Promise<Connection> {
    const conn: Connection = {
      id: `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: Date.now(),
      lastUsedAt: Date.now(),
      isHealthy: true,
    };

    // 模拟连接创建（实际应该建立真实连接）
    await new Promise((resolve) => setTimeout(resolve, 10));

    return conn;
  }

  /**
   * 等待连接释放
   */
  private async waitForConnection(): Promise<Connection> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < this.config.connectionTimeout) {
      for (const [id, conn] of this.connections.entries()) {
        if (!this.activeConnections.has(id) && conn.isHealthy) {
          this.activeConnections.add(id);
          conn.lastUsedAt = Date.now();
          return conn;
        }
      }
      await new Promise((resolve) => setTimeout(resolve, 100));
    }

    throw new Error('连接获取超时');
  }

  /**
   * 启动健康检查
   */
  private startHealthCheck(): void {
    this.healthCheckTimer = setInterval(() => {
      this.performHealthCheck();
    }, this.config.healthCheckInterval);
  }

  /**
   * 执行健康检查
   */
  private async performHealthCheck(): Promise<void> {
    const now = Date.now();
    const toRemove: string[] = [];

    for (const [id, conn] of this.connections.entries()) {
      // 检查空闲超时
      if (
        !this.activeConnections.has(id) &&
        now - conn.lastUsedAt > this.config.idleTimeout
      ) {
        // 如果连接数超过最小值，移除空闲连接
        if (this.connections.size > this.config.minSize) {
          toRemove.push(id);
        }
      }

      // 检查连接健康状态（简化实现）
      if (!conn.isHealthy) {
        toRemove.push(id);
      }
    }

    // 移除不健康的连接
    for (const id of toRemove) {
      this.connections.delete(id);
      this.activeConnections.delete(id);
    }

    // 确保连接池大小满足最小值
    while (this.connections.size < this.config.minSize) {
      const conn = await this.createConnection();
      this.connections.set(conn.id, conn);
    }
  }

  /**
   * 获取连接池统计信息
   */
  getStats() {
    return {
      totalConnections: this.connections.size,
      activeConnections: this.activeConnections.size,
      idleConnections: this.connections.size - this.activeConnections.size,
      minSize: this.config.minSize,
      maxSize: this.config.maxSize,
    };
  }

  /**
   * 关闭连接池
   */
  async close(): Promise<void> {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
    }

    // 清理所有连接
    this.connections.clear();
    this.activeConnections.clear();
  }
}
