import React from 'react';
import { Bell, ShieldCheck, Database, RefreshCw } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  return (
    <header className="h-16 px-8 border-b border-slate-800/80 bg-[#0c121e]/80 backdrop-blur-md flex items-center justify-between sticky top-0 z-20">
      <div>
        <h2 className="text-lg font-bold text-white tracking-tight">{title}</h2>
        {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* System Health Badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-medium text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Engine Online</span>
        </div>

        {/* Database Status */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/60 text-xs text-slate-300 border border-slate-700/50">
          <Database className="w-3.5 h-3.5 text-slate-400" />
          <span>21,900 Records</span>
        </div>

        {/* User Pill */}
        <div className="flex items-center gap-2.5 pl-3 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center font-bold text-xs text-white">
            DP
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-semibold text-slate-200">Demo Planner</p>
            <p className="text-[10px] text-slate-400">demo@inventoryai.com</p>
          </div>
        </div>
      </div>
    </header>
  );
};
