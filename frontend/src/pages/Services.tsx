import { useEffect, useState } from 'react';
import { ServiceCard } from '../components/ServiceCard';

type Status = 'UP' | 'DOWN' | 'UNKNOWN';

export function Services() {
  const [statuses, setStatuses] = useState<Record<string, Status>>({
    'User Service': 'UNKNOWN',
    'Order Service': 'UNKNOWN',
    'Notification Service': 'UNKNOWN',
    'Analytics Service': 'UNKNOWN',
  });
  
  const [cbState, setCbState] = useState<any[]>([]);

  const checkHealth = async () => {
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost';
    
    const endpoints = {
      'User Service': `${apiBase}/api/users/health`,
      'Order Service': `${apiBase}/api/orders/health`,
      'Notification Service': `${apiBase}/api/notifications/health`,
      'Analytics Service': `${apiBase}/api/analytics/health`,
    };

    const newStatuses: Record<string, Status> = {};

    for (const [name, url] of Object.entries(endpoints)) {
      try {
        const res = await fetch(url);
        newStatuses[name] = res.ok ? 'UP' : 'DOWN';
      } catch (err) {
        newStatuses[name] = 'DOWN';
      }
    }

    setStatuses(newStatuses);
    
    // Fetch circuit breaker status from order-service
    try {
      const cbRes = await fetch(`${apiBase}/api/orders/circuit-breakers`);
      if (cbRes.ok) {
         const cbData = await cbRes.json();
         setCbState(cbData.circuit_breakers || []);
      }
    } catch (err) {}
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Services Overview</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Object.entries(statuses).map(([name, status]) => (
          <div key={name} className="flex flex-col gap-2">
            <ServiceCard name={name} status={status} />
            {name === 'Order Service' && cbState.length > 0 && (
              <div className="mt-2 space-y-2">
                {cbState.map(cb => {
                   let pillColor = 'bg-green-500/20 text-green-400';
                   let pillText = 'Circuit: Closed';
                   if (cb.state === 'OPEN') { 
                     pillColor = 'bg-red-500/20 text-red-400'; 
                     pillText = 'Circuit: Open ⚠'; 
                   } else if (cb.state === 'HALF_OPEN') { 
                     pillColor = 'bg-yellow-500/20 text-yellow-400'; 
                     pillText = 'Circuit: Testing...'; 
                   }
                   return (
                     <div key={cb.name} className={`px-3 py-1 rounded-full text-xs font-semibold ${pillColor} text-center border border-current`}>
                       {cb.name} → {pillText}
                     </div>
                   );
                })}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
