import { offlineDB, OfflineDB } from "./db";

export interface PendingChange {
  id?: number;
  store: string;
  action: "create" | "update" | "delete";
  endpoint: string;
  method: string;
  body?: any;
  timestamp: number;
  retry_count: number;
}

const DEFAULT_AUTO_FLUSH_INTERVAL = 30_000;
const MAX_RETRIES = 3;

export class SyncQueue {
  private db: OfflineDB;
  private flushing = false;
  private maxRetries = MAX_RETRIES;
  private autoFlushTimer: ReturnType<typeof setInterval> | null = null;
  private onlineHandler: (() => void) | null = null;

  constructor(db: OfflineDB) {
    this.db = db;
  }

  async enqueue(
    change: Omit<PendingChange, "id" | "timestamp" | "retry_count">
  ): Promise<void> {
    const entry: PendingChange = {
      ...change,
      timestamp: Date.now(),
      retry_count: 0,
    };
    await this.db.save("pending_changes", entry);
  }

  async flush(): Promise<{ success: number; failed: number }> {
    if (this.flushing) return { success: 0, failed: 0 };
    this.flushing = true;

    let success = 0;
    let failed = 0;

    try {
      const changes: PendingChange[] = await this.db.getAll("pending_changes");

      for (const change of changes) {
        try {
          const response = await fetch(change.endpoint, {
            method: change.method,
            headers: { "Content-Type": "application/json" },
            body: change.body ? JSON.stringify(change.body) : undefined,
          });

          if (response.ok || response.status === 404) {
            await this.db.delete("pending_changes", String(change.id));
            success++;
          } else {
            failed = await this.handleFailure(change, failed);
          }
        } catch {
          failed = await this.handleFailure(change, failed);
        }
      }
    } finally {
      this.flushing = false;
    }

    return { success, failed };
  }

  private async handleFailure(
    change: PendingChange,
    failed: number
  ): Promise<number> {
    change.retry_count++;
    if (change.retry_count >= this.maxRetries) {
      await this.db.save("pending_changes", change);
      return failed + 1;
    }
    await this.db.save("pending_changes", change);
    return failed + 1;
  }

  async getPendingCount(): Promise<number> {
    const changes = await this.db.getAll("pending_changes");
    return changes.length;
  }

  async clearCompleted(): Promise<void> {
    const changes: PendingChange[] = await this.db.getAll("pending_changes");
    const dead = changes.filter((c) => c.retry_count >= this.maxRetries);
    for (const change of dead) {
      await this.db.delete("pending_changes", String(change.id));
    }
  }

  startAutoFlush(intervalMs: number = DEFAULT_AUTO_FLUSH_INTERVAL): void {
    this.stopAutoFlush();

    this.onlineHandler = () => {
      this.flush();
    };
    window.addEventListener("online", this.onlineHandler);

    this.autoFlushTimer = setInterval(() => {
      if (navigator.onLine) {
        this.flush();
      }
    }, intervalMs);
  }

  stopAutoFlush(): void {
    if (this.autoFlushTimer !== null) {
      clearInterval(this.autoFlushTimer);
      this.autoFlushTimer = null;
    }
    if (this.onlineHandler !== null) {
      window.removeEventListener("online", this.onlineHandler);
      this.onlineHandler = null;
    }
  }
}

export const syncQueue = new SyncQueue(offlineDB);
