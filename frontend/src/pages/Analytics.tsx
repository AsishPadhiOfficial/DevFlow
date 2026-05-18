import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';

export function Analytics() {
  const [data, setData] = useState<any>(null);

  const fetchSummary = async () => {
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost';
    try {
      const res = await fetch(`${apiBase}/api/analytics/summary`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchSummary();
    const interval = setInterval(fetchSummary, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Analytics Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-[#151520] p-6 rounded-xl border border-gray-800 flex flex-col items-center">
          <h2 className="text-gray-400 mb-2">Total Users</h2>
          <span className="text-5xl font-bold text-accent">{data.total_users}</span>
        </div>
        <div className="bg-[#151520] p-6 rounded-xl border border-gray-800 flex flex-col items-center">
          <h2 className="text-gray-400 mb-2">Total Orders</h2>
          <span className="text-5xl font-bold text-accent">{data.total_orders}</span>
        </div>
      </div>

      <div className="bg-[#151520] p-6 rounded-xl border border-gray-800 h-96">
        <h2 className="text-lg font-semibold mb-4 text-white">Events Per Minute</h2>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data.events_per_minute}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="time" 
              stroke="#888" 
              tickFormatter={(val) => format(parseISO(val), 'HH:mm')}
            />
            <YAxis stroke="#888" allowDecimals={false} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px', color: '#fff' }}
              labelFormatter={(val) => format(parseISO(val), 'HH:mm')}
            />
            <Line type="monotone" dataKey="count" stroke="#6366F1" strokeWidth={3} dot={{ fill: '#6366F1', r: 4 }} activeDot={{ r: 6 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
