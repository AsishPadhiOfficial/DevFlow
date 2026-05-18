import { useState, useEffect, useRef } from 'react';

export interface DevEvent {
  event_type: string;
  payload: any;
  timestamp: string;
}

export function useWebSocket(url: string) {
  const [events, setEvents] = useState<DevEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      setIsConnected(true);
      console.log("WS Connected to", url);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      console.log("WS Disconnected from", url);
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as DevEvent;
        setEvents(prev => [data, ...prev].slice(0, 100)); // keep last 100
      } catch (err) {
        console.error("Failed to parse event", err);
      }
    };

    return () => {
      ws.current?.close();
    };
  }, [url]);

  return { events, isConnected };
}
