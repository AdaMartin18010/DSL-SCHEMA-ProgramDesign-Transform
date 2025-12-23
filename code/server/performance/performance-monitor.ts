/**
 * MCP性能监控器
 * 
 * 实现性能指标收集、分析、告警等功能
 */

export interface PerformanceMetrics {
  requestCount: number;
  successCount: number;
  errorCount: number;
  avgResponseTime: number; // ms
  minResponseTime: number; // ms
  maxResponseTime: number; // ms
  p50ResponseTime: number; // ms
  p95ResponseTime: number; // ms
  p99ResponseTime: number; // ms
  throughput: number; // requests/second
  errorRate: number; // percentage
}

export interface PerformanceSnapshot {
  timestamp: number;
  metrics: PerformanceMetrics;
}

export class PerformanceMonitor {
  private responseTimes: number[] = [];
  private requestCount = 0;
  private successCount = 0;
  private errorCount = 0;
  private snapshots: PerformanceSnapshot[] = [];
  private maxSnapshots = 1000;
  private windowSize = 100; // 保留最近100个响应时间

  /**
   * 记录请求开始
   */
  recordRequestStart(): () => void {
    const startTime = Date.now();
    this.requestCount++;

    return () => {
      const responseTime = Date.now() - startTime;
      this.recordResponseTime(responseTime, true);
    };
  }

  /**
   * 记录请求成功
   */
  recordSuccess(): void {
    this.successCount++;
  }

  /**
   * 记录请求失败
   */
  recordError(): void {
    this.errorCount++;
  }

  /**
   * 记录响应时间
   */
  private recordResponseTime(responseTime: number, success: boolean): void {
    this.responseTimes.push(responseTime);

    // 保持窗口大小
    if (this.responseTimes.length > this.windowSize) {
      this.responseTimes.shift();
    }

    if (success) {
      this.successCount++;
    } else {
      this.errorCount++;
    }

    // 定期创建快照
    if (this.requestCount % 100 === 0) {
      this.createSnapshot();
    }
  }

  /**
   * 创建性能快照
   */
  createSnapshot(): PerformanceSnapshot {
    const metrics = this.getMetrics();
    const snapshot: PerformanceSnapshot = {
      timestamp: Date.now(),
      metrics,
    };

    this.snapshots.push(snapshot);

    // 保持快照数量限制
    if (this.snapshots.length > this.maxSnapshots) {
      this.snapshots.shift();
    }

    return snapshot;
  }

  /**
   * 获取当前性能指标
   */
  getMetrics(): PerformanceMetrics {
    const sortedTimes = [...this.responseTimes].sort((a, b) => a - b);
    const count = sortedTimes.length;

    const avgResponseTime =
      count > 0
        ? sortedTimes.reduce((sum, t) => sum + t, 0) / count
        : 0;

    const minResponseTime = count > 0 ? sortedTimes[0] : 0;
    const maxResponseTime = count > 0 ? sortedTimes[count - 1] : 0;
    const p50ResponseTime =
      count > 0 ? sortedTimes[Math.floor(count * 0.5)] : 0;
    const p95ResponseTime =
      count > 0 ? sortedTimes[Math.floor(count * 0.95)] : 0;
    const p99ResponseTime =
      count > 0 ? sortedTimes[Math.floor(count * 0.99)] : 0;

    const totalRequests = this.successCount + this.errorCount;
    const errorRate =
      totalRequests > 0 ? (this.errorCount / totalRequests) * 100 : 0;

    // 计算吞吐量（简化实现，基于最近1分钟）
    const recentSnapshots = this.snapshots.filter(
      (s) => Date.now() - s.timestamp < 60000
    );
    const throughput =
      recentSnapshots.length > 0
        ? recentSnapshots.reduce(
            (sum, s) => sum + s.metrics.throughput,
            0
          ) / recentSnapshots.length
        : 0;

    return {
      requestCount: this.requestCount,
      successCount: this.successCount,
      errorCount: this.errorCount,
      avgResponseTime,
      minResponseTime,
      maxResponseTime,
      p50ResponseTime,
      p95ResponseTime,
      p99ResponseTime,
      throughput,
      errorRate,
    };
  }

  /**
   * 获取性能快照历史
   */
  getSnapshots(limit?: number): PerformanceSnapshot[] {
    const snapshots = [...this.snapshots];
    if (limit) {
      return snapshots.slice(-limit);
    }
    return snapshots;
  }

  /**
   * 重置统计信息
   */
  reset(): void {
    this.responseTimes = [];
    this.requestCount = 0;
    this.successCount = 0;
    this.errorCount = 0;
    this.snapshots = [];
  }

  /**
   * 检查性能告警
   */
  checkAlerts(): Array<{ level: string; message: string }> {
    const metrics = this.getMetrics();
    const alerts: Array<{ level: string; message: string }> = [];

    // 检查响应时间告警
    if (metrics.p95ResponseTime > 1000) {
      alerts.push({
        level: 'warning',
        message: `P95响应时间过高: ${metrics.p95ResponseTime.toFixed(2)}ms`,
      });
    }

    if (metrics.p99ResponseTime > 2000) {
      alerts.push({
        level: 'error',
        message: `P99响应时间过高: ${metrics.p99ResponseTime.toFixed(2)}ms`,
      });
    }

    // 检查错误率告警
    if (metrics.errorRate > 5) {
      alerts.push({
        level: 'warning',
        message: `错误率过高: ${metrics.errorRate.toFixed(2)}%`,
      });
    }

    if (metrics.errorRate > 10) {
      alerts.push({
        level: 'error',
        message: `错误率严重: ${metrics.errorRate.toFixed(2)}%`,
      });
    }

    return alerts;
  }
}
