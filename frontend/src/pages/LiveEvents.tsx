import { useWebSocket } from '../hooks/useWebSocket';
import { EventCard } from '../components/EventCard';

export function LiveEvents() {
  const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost/ws';
  const { events, isConnected } = useWebSocket(wsUrl);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Live Event Stream</h1>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Connection Status:</span>
          <span className={`h-3 w-3 rounded-full ${isConnected ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.6)]' : 'bg-red-500'}`}></span>
        </div>
      </div>
      
      <div className="space-y-4">
        {events.length === 0 ? (
          <div className="text-center text-gray-500 py-12">
            No events received yet. Try creating some from the Playground.
          </div>
        ) : (
          events.map((evt, idx) => (
            <EventCard key={`${evt.timestamp}-${idx}`} event={evt} />
          ))
        )}
      </div>
    </div>
  );
}
