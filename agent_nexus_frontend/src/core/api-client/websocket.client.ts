const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL;

if (!WS_BASE_URL) {
  throw new Error("NEXT_PUBLIC_WS_URL is not defined in the environment.");
}

let socket: WebSocket | null = null;
let reconnectAttempt = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY_MS = 3000;

export const initWebSocket = () => {
  if (socket) {
    console.log("WebSocket already initialized.");
    return;
  }
  
  const url = WS_BASE_URL.endsWith('/') ? WS_BASE_URL.slice(0, -1) : WS_BASE_URL;

  try {
    socket = new WebSocket(url);
  } catch (error) {
    console.error("Failed to create WebSocket instance:", error);
    return;
  }

  socket.onopen = () => {
    console.log(`[WS] Connection opened successfully to ${url}`);
    reconnectAttempt = 0;
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log("[WS] Message received:", data);
      
    } catch (e) {
      console.error("[WS] Error parsing JSON message:", event.data);
    }
  };

  socket.onclose = (event) => {
    console.warn(`[WS] Connection closed. Code: ${event.code}. Reason: ${event.reason}`);
    socket = null;

    if (reconnectAttempt < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempt++;
      setTimeout(() => {
        console.log(`[WS] Attempting reconnect ${reconnectAttempt}/${MAX_RECONNECT_ATTEMPTS}...`);
        initWebSocket();
      }, RECONNECT_DELAY_MS);
    } else {
      console.error("[WS] Max reconnect attempts reached. Connection permanently lost.");
    }
  };

  socket.onerror = (error) => {
    console.error("[WS] Error encountered:", error);
  };
};

export const sendWebSocketMessage = (message: any) => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
    return true;
  } else {
    console.warn("[WS] Cannot send message: Connection is not open.");
    return false;
  }
};