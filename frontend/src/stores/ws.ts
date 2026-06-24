import { ref, onUnmounted } from "vue";
import { useAuthStore } from "./auth";

interface PresenceUser {
  user_id: string;
  user_name: string;
}

export function useTripSocket(tripId: string) {
  const auth = useAuthStore();
  const connected = ref(false);
  const users = ref<PresenceUser[]>([]);
  let ws: WebSocket | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  function connect() {
    if (!auth.token) return;
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host; // proxied by Vite
    const url = `${protocol}//${host}/ws/trip/${tripId}`;

    ws = new WebSocket(url);

    ws.onopen = () => {
      connected.value = true;
      // Send auth as first message (not in URL to avoid logging)
      ws!.send(JSON.stringify({ type: "auth", token: auth.token }));
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "presence") {
          users.value = msg.users || [];
        }
        // Other message types can be handled by the caller via callback
        if (onMessageCallback) {
          onMessageCallback(msg);
        }
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      connected.value = false;
      // Reconnect after 3s
      reconnectTimer = setTimeout(() => connect(), 3000);
    };

    ws.onerror = () => {
      ws?.close();
    };
  }

  let onMessageCallback: ((msg: any) => void) | null = null;

  function onMessage(cb: (msg: any) => void) {
    onMessageCallback = cb;
  }

  function send(data: any) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  }

  function disconnect() {
    if (reconnectTimer) clearTimeout(reconnectTimer);
    if (ws) {
      ws.onclose = null;
      ws.close();
      ws = null;
    }
    connected.value = false;
    users.value = [];
  }

  onUnmounted(() => disconnect());

  return { connected, users, connect, disconnect, send, onMessage };
}
