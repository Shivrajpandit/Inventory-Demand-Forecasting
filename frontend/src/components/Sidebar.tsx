import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  LineChart,
  Boxes,
  Sliders,
  Cpu,
  Package,
  UploadCloud,
  ChevronRight,
  Sparkles,
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Demand Forecast', path: '/forecast', icon: LineChart },
  { name: 'Inventory & Reorders', path: '/inventory', icon: Boxes },
  { name: 'What-If Simulation', path: '/scenario', icon: Sliders },
  { name: 'Sales Analytics', path: '/analytics', icon: TrendingUp },
  { name: 'Model Intelligence', path: '/models', icon: Cpu },
  { name: 'Product Catalog', path: '/products', icon: Package },
  { name: 'Data Ingestion', path: '/upload', icon: UploadCloud },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-[#0c121e] border-r border-slate-800/80 flex flex-col shrink-0 min-h-screen">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
          <Boxes className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-sm tracking-tight text-white flex items-center gap-1.5">
            InventoryAI
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20">
              PRO
            </span>
          </h1>
          <p className="text-xs text-slate-400">Demand & Optimization</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
          Platform Menu
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 opacity-40" />
            </NavLink>
          );
        })}
      </nav>

      {/* Model Status Card */}
      <div className="p-3 m-3 rounded-xl bg-gradient-to-br from-slate-900 to-slate-800/80 border border-slate-700/50">
        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 mb-1">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Active Champion</span>
        </div>
        <p className="text-xs font-bold text-white">LightGBM Regressor</p>
        <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-700/50 pt-2">
          <span>Test MAE: 5.34</span>
          <span className="text-emerald-400 font-medium">16.09% WAPE</span>
        </div>
      </div>
    </aside>
  );
};
