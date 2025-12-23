/**
 * MCP请求批处理器
 * 
 * 实现请求批处理、批量转换、结果分发等功能
 */

export interface BatchRequest {
  id: string;
  tool: string;
  args: any;
  resolve: (result: any) => void;
  reject: (error: Error) => void;
  timestamp: number;
}

export interface BatchProcessorConfig {
  batchSize: number;
  batchWindow: number; // ms
  maxWaitTime: number; // ms
}

export class BatchProcessor {
  private queue: BatchRequest[] = [];
  private config: BatchProcessorConfig;
  private timer?: NodeJS.Timeout;
  private processing = false;

  constructor(config: Partial<BatchProcessorConfig> = {}) {
    this.config = {
      batchSize: config.batchSize ?? 10,
      batchWindow: config.batchWindow ?? 100, // 100ms
      maxWaitTime: config.maxWaitTime ?? 1000, // 1秒
    };
  }

  /**
   * 添加请求到批处理队列
   */
  async addRequest(
    tool: string,
    args: any
  ): Promise<any> {
    return new Promise((resolve, reject) => {
      const request: BatchRequest = {
        id: `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        tool,
        args,
        resolve,
        reject,
        timestamp: Date.now(),
      };

      this.queue.push(request);

      // 检查是否达到批处理大小
      if (this.queue.length >= this.config.batchSize) {
        this.processBatch();
      } else if (!this.timer && !this.processing) {
        // 设置时间窗口定时器
        this.timer = setTimeout(() => {
          this.processBatch();
        }, this.config.batchWindow);
      }

      // 检查最大等待时间
      setTimeout(() => {
        const index = this.queue.findIndex((r) => r.id === request.id);
        if (index !== -1) {
          this.queue.splice(index, 1);
          reject(new Error('请求处理超时'));
        }
      }, this.config.maxWaitTime);
    });
  }

  /**
   * 处理批处理队列
   */
  private async processBatch(): Promise<void> {
    if (this.processing || this.queue.length === 0) {
      return;
    }

    this.processing = true;

    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = undefined;
    }

    // 取出批处理请求
    const batch = this.queue.splice(0, this.config.batchSize);

    try {
      // 按工具分组
      const groupedRequests = this.groupByTool(batch);

      // 批量处理每个工具组
      const results = await Promise.all(
        Array.from(groupedRequests.entries()).map(([tool, requests]) =>
          this.processToolBatch(tool, requests)
        )
      );

      // 分发结果
      this.distributeResults(batch, results.flat());
    } catch (error) {
      // 处理错误
      batch.forEach((req) => {
        req.reject(
          error instanceof Error ? error : new Error(String(error))
        );
      });
    } finally {
      this.processing = false;

      // 如果队列中还有请求，继续处理
      if (this.queue.length > 0) {
        if (this.queue.length >= this.config.batchSize) {
          this.processBatch();
        } else {
          this.timer = setTimeout(() => {
            this.processBatch();
          }, this.config.batchWindow);
        }
      }
    }
  }

  /**
   * 按工具分组请求
   */
  private groupByTool(
    requests: BatchRequest[]
  ): Map<string, BatchRequest[]> {
    const grouped = new Map<string, BatchRequest[]>();

    for (const req of requests) {
      if (!grouped.has(req.tool)) {
        grouped.set(req.tool, []);
      }
      grouped.get(req.tool)!.push(req);
    }

    return grouped;
  }

  /**
   * 处理工具批处理
   */
  private async processToolBatch(
    tool: string,
    requests: BatchRequest[]
  ): Promise<any[]> {
    // 这里应该调用实际的工具处理函数
    // 简化实现：返回模拟结果
    return requests.map((req) => ({
      id: req.id,
      result: { tool, args: req.args },
    }));
  }

  /**
   * 分发结果
   */
  private distributeResults(
    requests: BatchRequest[],
    results: any[]
  ): void {
    const resultMap = new Map(
      results.map((r) => [r.id, r.result])
    );

    for (const req of requests) {
      const result = resultMap.get(req.id);
      if (result) {
        req.resolve(result);
      } else {
        req.reject(new Error('批处理结果缺失'));
      }
    }
  }

  /**
   * 获取批处理统计信息
   */
  getStats() {
    return {
      queueSize: this.queue.length,
      batchSize: this.config.batchSize,
      batchWindow: this.config.batchWindow,
      processing: this.processing,
    };
  }

  /**
   * 清空队列
   */
  clear(): void {
    this.queue.forEach((req) => {
      req.reject(new Error('批处理队列已清空'));
    });
    this.queue = [];
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = undefined;
    }
  }
}
