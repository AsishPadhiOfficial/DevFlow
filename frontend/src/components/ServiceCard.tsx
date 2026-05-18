import { CheckCircle2, XCircle } from 'lucide-react';

export function ServiceCard({ name, status }: { name: string, status: 'UP' | 'DOWN' | 'UNKNOWN' }) {
  const isUp = status === 'UP';
  return (
    <div className="p-6 rounded-xl bg-[#151520] border border-gray-800 flex flex-col items-center justify-center shadow-lg">
      <h3 className="text-lg font-semibold text-white mb-4">{name}</h3>
      <div className="flex items-center gap-2">
        {isUp ? (
          <CheckCircle2 className="text-green-500 h-6 w-6" />
        ) : (
          <XCircle className="text-red-500 h-6 w-6" />
        )}
        <span className={`font-bold ${isUp ? 'text-green-500' : 'text-red-500'}`}>
          {status}
        </span>
      </div>
    </div>
  );
}
