import type { DevEvent } from '../hooks/useWebSocket';
import { format } from 'date-fns';

export function EventCard({ event }: { event: DevEvent }) {
  const isUser = event.event_type.startsWith('user.');
  const color = isUser ? 'border-blue-500' : 'border-green-500';
  const badgeColor = isUser ? 'bg-blue-500/10 text-blue-400' : 'bg-green-500/10 text-green-400';

  return (
    <div className={`p-4 mb-4 rounded-lg bg-[#151520] border-l-4 ${color} shadow-lg event-enter-active`}>
      <div className="flex justify-between items-center mb-2">
        <span className={`px-2 py-1 rounded text-xs font-semibold ${badgeColor}`}>
          {event.event_type}
        </span>
        <span className="text-xs text-gray-500">
          {format(new Date(event.timestamp), 'HH:mm:ss.SSS')}
        </span>
      </div>
      <pre className="text-xs font-mono bg-black/50 p-3 rounded overflow-x-auto text-gray-300">
        {JSON.stringify(event.payload, null, 2)}
      </pre>
    </div>
  );
}
