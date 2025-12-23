/**
 * MCP缓存管理器
 * 
 * 实现多级缓存、缓存策略、缓存失效等功能
 */

export interface CacheEntry<T = any> {
  key: string;
  value: T;
  timestamp: number;
  ttl?: number; // ms
  accessCount: number;
  lastAccessed: number;
}

export interface CacheConfig {
  maxSize: number;
  defaultTTL?: number; // ms
  strategy: 'LRU' | 'LFU' | 'TTL';
}

export class CacheManager {
  private cache: Map<string, CacheEntry> = new Map();
  private config: CacheConfig;
  private accessOrder: string[] = []; // LRU顺序
  private accessCounts: Map<string, number> = new Map(); // LFU计数

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      maxSize: config.maxSize ?? 1000,
      defaultTTL: config.defaultTTL ?? 3600000, // 1小时
      strategy: config.strategy ?? 'LRU',
    };

    // 启动清理定时器
    this.startCleanupTimer();
  }

  /**
   * 获取缓存值
   */
  get<T = any>(key: string): T | null {
    const entry = this.cache.get(key);

    if (!entry) {
      return null;
    }

    // 检查TTL
    if (entry.ttl && Date.now() - entry.timestamp > entry.ttl) {
      this.delete(key);
      return null;
    }

    // 更新访问信息
    entry.accessCount++;
    entry.lastAccessed = Date.now();
    this.updateAccessOrder(key);

    return entry.value as T;
  }

  /**
   * 设置缓存值
   */
  set<T = any>(
    key: string,
    value: T,
    ttl?: number
  ): void {
    // 检查缓存大小
    if (this.cache.size >= this.config.maxSize) {
      this.evict();
    }

    const entry: CacheEntry<T> = {
      key,
      value,
      timestamp: Date.now(),
      ttl: ttl ?? this.config.defaultTTL,
      accessCount: 1,
      lastAccessed: Date.now(),
    };

    this.cache.set(key, entry);
    this.updateAccessOrder(key);
    this.accessCounts.set(key, 1);
  }

  /**
   * 删除缓存
   */
  delete(key: string): boolean {
    const deleted = this.cache.delete(key);
    if (deleted) {
      const index = this.accessOrder.indexOf(key);
      if (index !== -1) {
        this.accessOrder.splice(index, 1);
      }
      this.accessCounts.delete(key);
    }
    return deleted;
  }

  /**
   * 清空缓存
   */
  clear(): void {
    this.cache.clear();
    this.accessOrder = [];
    this.accessCounts.clear();
  }

  /**
   * 更新访问顺序（LRU）
   */
  private updateAccessOrder(key: string): void {
    const index = this.accessOrder.indexOf(key);
    if (index !== -1) {
      this.accessOrder.splice(index, 1);
    }
    this.accessOrder.push(key);
  }

  /**
   * 淘汰缓存（根据策略）
   */
  private evict(): void {
    if (this.cache.size === 0) {
      return;
    }

    let keyToEvict: string | null = null;

    switch (this.config.strategy) {
      case 'LRU':
        // 移除最久未使用的
        keyToEvict = this.accessOrder[0];
        break;

      case 'LFU':
        // 移除访问次数最少的
        let minCount = Infinity;
        for (const [key, count] of this.accessCounts.entries()) {
          if (count < minCount) {
            minCount = count;
            keyToEvict = key;
          }
        }
        break;

      case 'TTL':
        // 移除最早过期的
        let earliestExpiry = Infinity;
        for (const [key, entry] of this.cache.entries()) {
          if (entry.ttl) {
            const expiry = entry.timestamp + entry.ttl;
            if (expiry < earliestExpiry) {
              earliestExpiry = expiry;
              keyToEvict = key;
            }
          }
        }
        // 如果没有TTL，回退到LRU
        if (!keyToEvict) {
          keyToEvict = this.accessOrder[0];
        }
        break;
    }

    if (keyToEvict) {
      this.delete(keyToEvict);
    }
  }

  /**
   * 启动清理定时器
   */
  private startCleanupTimer(): void {
    setInterval(() => {
      this.cleanup();
    }, 60000); // 每分钟清理一次
  }

  /**
   * 清理过期缓存
   */
  private cleanup(): void {
    const now = Date.now();
    const toDelete: string[] = [];

    for (const [key, entry] of this.cache.entries()) {
      if (entry.ttl && now - entry.timestamp > entry.ttl) {
        toDelete.push(key);
      }
    }

    for (const key of toDelete) {
      this.delete(key);
    }
  }

  /**
   * 生成缓存键
   */
  static generateKey(tool: string, args: any): string {
    const argsStr = JSON.stringify(args);
    return `${tool}:${Buffer.from(argsStr).toString('base64')}`;
  }

  /**
   * 获取缓存统计信息
   */
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.config.maxSize,
      strategy: this.config.strategy,
      hitRate: this.calculateHitRate(),
    };
  }

  /**
   * 计算命中率（简化实现）
   */
  private calculateHitRate(): number {
    // 这里应该维护命中/未命中统计
    // 简化实现返回0
    return 0;
  }
}
