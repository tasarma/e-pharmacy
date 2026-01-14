import { useEffect, useState } from 'react';
import { getHealthStatus } from './api/health';
import { HealthCheckResponse } from './types/api';

function App() {
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
    console.log(health);

  useEffect(() => {
    getHealthStatus()
      .then(setHealth)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">System Status</h1>
        
        {error && (
          <div className="p-3 bg-red-100 text-red-700 rounded-md">
            Connection Failed: {error}
          </div>
        )}

        {health ? (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-green-500 rounded-full"></span>
              <span className="font-medium text-green-700">Backend Online</span>
            </div>
            <p className="text-sm text-gray-500">Version: {health.version}</p>
            <p className="text-sm text-gray-500">Time: {new Date(health.timestamp).toLocaleString()}</p>
          </div>
        ) : !error && (
          <p className="text-gray-500 animate-pulse">Checking connection...</p>
        )}
      </div>
    </div>
  );
}

export default App;
