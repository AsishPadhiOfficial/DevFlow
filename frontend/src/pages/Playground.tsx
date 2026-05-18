import { useState } from 'react';

export function Playground() {
  const [userName, setUserName] = useState('');
  const [userEmail, setUserEmail] = useState('');
  
  const [orderUserId, setOrderUserId] = useState('');
  const [orderProduct, setOrderProduct] = useState('');
  const [orderAmount, setOrderAmount] = useState('');

  const [response, setResponse] = useState<any>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [rateLimitResults, setRateLimitResults] = useState<{id: number, status: number, text: string}[]>([]);

  const apiBase = import.meta.env.VITE_API_URL || 'http://localhost';

  const showToast = () => {
    setToastMessage("Rate limit hit! Nginx blocked this request. This demonstrates production-grade rate limiting.");
    setTimeout(() => setToastMessage(null), 5000);
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${apiBase}/api/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: userName, email: userEmail })
      });
      if (res.status === 429) showToast();
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      setResponse({ error: String(err) });
    }
  };

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${apiBase}/api/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_id: parseInt(orderUserId), 
          product: orderProduct, 
          amount: parseFloat(orderAmount) 
        })
      });
      if (res.status === 429) showToast();
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      setResponse({ error: String(err) });
    }
  };

  const handleTestRateLimit = async () => {
    setRateLimitResults([]);
    const promises = [];
    for (let i = 1; i <= 15; i++) {
      promises.push((async () => {
        try {
          const res = await fetch(`${apiBase}/api/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: `Test ${i}`, email: `test${i}@example.com` })
          });
          return { 
            id: i, 
            status: res.status, 
            text: res.status === 429 ? '❌ 429 Rate Limited' : (res.ok ? '✅ 201 Created' : `❌ ${res.status} Error`) 
          };
        } catch (e) {
          return { id: i, status: 500, text: '❌ Error' };
        }
      })());
    }
    const results = await Promise.all(promises);
    setRateLimitResults(results.sort((a, b) => a.id - b.id));
  };

  return (
    <div className="relative">
      {toastMessage && (
        <div className="absolute top-0 right-0 bg-red-500 text-white px-4 py-2 rounded shadow-lg z-50 transition-opacity">
          {toastMessage}
        </div>
      )}

      <h1 className="text-2xl font-bold mb-6">API Playground</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        <div className="space-y-8">
          {/* User Form */}
          <div className="bg-[#151520] p-6 rounded-xl border border-gray-800">
            <h2 className="text-lg font-semibold mb-4 text-white">Create User</h2>
            <form onSubmit={handleCreateUser} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Name</label>
                <input 
                  required
                  type="text" 
                  value={userName} 
                  onChange={e => setUserName(e.target.value)}
                  className="w-full bg-black/50 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-accent"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Email</label>
                <input 
                  required
                  type="email" 
                  value={userEmail} 
                  onChange={e => setUserEmail(e.target.value)}
                  className="w-full bg-black/50 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-accent"
                />
              </div>
              <button type="submit" className="bg-accent text-white px-4 py-2 rounded hover:bg-indigo-600 transition-colors">
                Send Request
              </button>
            </form>
          </div>

          {/* Order Form */}
          <div className="bg-[#151520] p-6 rounded-xl border border-gray-800">
            <h2 className="text-lg font-semibold mb-4 text-white">Create Order</h2>
            <form onSubmit={handleCreateOrder} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">User ID</label>
                <input 
                  required
                  type="number" 
                  value={orderUserId} 
                  onChange={e => setOrderUserId(e.target.value)}
                  className="w-full bg-black/50 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-accent"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Product Name</label>
                <input 
                  required
                  type="text" 
                  value={orderProduct} 
                  onChange={e => setOrderProduct(e.target.value)}
                  className="w-full bg-black/50 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-accent"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Amount</label>
                <input 
                  required
                  type="number" 
                  step="0.01"
                  value={orderAmount} 
                  onChange={e => setOrderAmount(e.target.value)}
                  className="w-full bg-black/50 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-accent"
                />
              </div>
              <button type="submit" className="bg-accent text-white px-4 py-2 rounded hover:bg-indigo-600 transition-colors">
                Send Request
              </button>
            </form>
          </div>
        </div>

        {/* Response & Tests */}
        <div className="space-y-8">
          <div className="bg-[#151520] p-6 rounded-xl border border-gray-800">
            <h2 className="text-lg font-semibold mb-4 text-white">Response</h2>
            <pre className="bg-black/50 p-4 rounded overflow-x-auto text-sm font-mono text-gray-300 min-h-[200px]">
              {response ? JSON.stringify(response, null, 2) : 'No requests sent yet.'}
            </pre>
          </div>

          <div className="bg-[#151520] p-6 rounded-xl border border-gray-800">
            <h2 className="text-lg font-semibold mb-4 text-white">Rate Limit Testing</h2>
            <button 
              onClick={handleTestRateLimit}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors mb-4"
            >
              Test Rate Limit (15 rapid requests)
            </button>
            
            {rateLimitResults.length > 0 && (
              <div className="bg-black/50 rounded overflow-hidden">
                <table className="w-full text-sm text-left text-gray-300">
                  <thead className="text-xs text-gray-400 bg-gray-900 uppercase">
                    <tr>
                      <th className="px-4 py-2">Request</th>
                      <th className="px-4 py-2">Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rateLimitResults.map((res) => (
                      <tr key={res.id} className="border-b border-gray-800">
                        <td className="px-4 py-2">Request {res.id}</td>
                        <td className={`px-4 py-2 ${res.status === 429 ? 'text-red-400' : 'text-green-400'}`}>
                          {res.text}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
