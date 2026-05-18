import { NavLink, Outlet } from 'react-router-dom';
import { Activity, Server, BarChart3, Terminal } from 'lucide-react';

export function Layout() {
  return (
    <div className="min-h-screen bg-background text-gray-200 flex flex-col">
      <nav className="border-b border-gray-800 bg-[#111118]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <Activity className="h-6 w-6 text-accent" />
              <span className="font-bold text-xl text-white tracking-wider">DevFlow</span>
            </div>
            <div className="flex space-x-4">
              <NavLink to="/" className={({isActive}) => `flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'bg-gray-800 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'}`}>
                <Activity className="h-4 w-4" /> Live Events
              </NavLink>
              <NavLink to="/services" className={({isActive}) => `flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'bg-gray-800 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'}`}>
                <Server className="h-4 w-4" /> Services
              </NavLink>
              <NavLink to="/analytics" className={({isActive}) => `flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'bg-gray-800 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'}`}>
                <BarChart3 className="h-4 w-4" /> Analytics
              </NavLink>
              <NavLink to="/playground" className={({isActive}) => `flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'bg-gray-800 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'}`}>
                <Terminal className="h-4 w-4" /> API Playground
              </NavLink>
            </div>
          </div>
        </div>
      </nav>
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        <Outlet />
      </main>
    </div>
  );
}
