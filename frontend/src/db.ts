export class OfflineDB {
  private dbName = "TravelMateOffline";
  private version = 1;
  private db: IDBDatabase | null = null;

  async open(): Promise<IDBDatabase> {
    if (this.db) return this.db;
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains("trips")) {
          const store = db.createObjectStore("trips", { keyPath: "id" });
          store.createIndex("updated_at", "updated_at", { unique: false });
        }
        if (!db.objectStoreNames.contains("days")) {
          const store = db.createObjectStore("days", { keyPath: "id" });
          store.createIndex("trip_id", "trip_id", { unique: false });
        }
        if (!db.objectStoreNames.contains("activities")) {
          const store = db.createObjectStore("activities", { keyPath: "id" });
          store.createIndex("day_id", "day_id", { unique: false });
        }
        if (!db.objectStoreNames.contains("pois")) {
          const store = db.createObjectStore("pois", { keyPath: "id" });
          store.createIndex("trip_id", "trip_id", { unique: false });
        }
        if (!db.objectStoreNames.contains("expenses")) {
          const store = db.createObjectStore("expenses", { keyPath: "id" });
          store.createIndex("trip_id", "trip_id", { unique: false });
        }
        if (!db.objectStoreNames.contains("memories")) {
          const store = db.createObjectStore("memories", { keyPath: "id" });
          store.createIndex("trip_id", "trip_id", { unique: false });
        }
        if (!db.objectStoreNames.contains("pending_changes")) {
          db.createObjectStore("pending_changes", {
            keyPath: "id",
            autoIncrement: true,
          });
        }
        if (!db.objectStoreNames.contains("sync_meta")) {
          db.createObjectStore("sync_meta", { keyPath: "id" });
        }
      };
      request.onsuccess = (event) => {
        this.db = (event.target as IDBOpenDBRequest).result;
        resolve(this.db!);
      };
      request.onerror = (event) => {
        reject(
          new Error(
            `Failed to open IndexedDB: ${(event.target as IDBOpenDBRequest).error?.message}`
          )
        );
      };
    });
  }

  private async withStore(
    storeName: string,
    mode: IDBTransactionMode,
    callback: (store: IDBObjectStore) => IDBRequest
  ): Promise<any> {
    const db = await this.open();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(storeName, mode);
      const store = transaction.objectStore(storeName);
      const request = callback(store);
      transaction.oncomplete = () => resolve(request.result);
      transaction.onerror = () =>
        reject(
          new Error(
            `IndexedDB transaction error on '${storeName}': ${transaction.error?.message}`
          )
        );
      request.onerror = () =>
        reject(
          new Error(
            `IndexedDB request error on '${storeName}': ${request.error?.message}`
          )
        );
    });
  }

  async save(store: string, data: Record<string, any>): Promise<void> {
    await this.withStore(store, "readwrite", (s) => s.put(data));
  }

  async get(store: string, id: string): Promise<any> {
    return this.withStore(store, "readonly", (s) => s.get(id));
  }

  async getAll(store: string): Promise<any[]> {
    return this.withStore(store, "readonly", (s) => s.getAll());
  }

  async delete(store: string, id: string): Promise<void> {
    await this.withStore(store, "readwrite", (s) => s.delete(id));
  }

  async clear(store: string): Promise<void> {
    await this.withStore(store, "readwrite", (s) => s.clear());
  }

  async getAllByIndex(
    store: string,
    index: string,
    value: any
  ): Promise<any[]> {
    const db = await this.open();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(store, "readonly");
      const objectStore = transaction.objectStore(store);
      const indexRef = objectStore.index(index);
      const request = indexRef.getAll(value);
      transaction.oncomplete = () => resolve(request.result);
      transaction.onerror = () =>
        reject(
          new Error(
            `IndexedDB transaction error on '${store}': ${transaction.error?.message}`
          )
        );
      request.onerror = () =>
        reject(
          new Error(
            `IndexedDB index query error on '${store}.${index}': ${request.error?.message}`
          )
        );
    });
  }
}

export const offlineDB = new OfflineDB();

export default offlineDB;
