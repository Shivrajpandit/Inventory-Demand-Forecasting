import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell,
} from 'recharts';
import { TrendingUp, Calendar, Zap, Sparkles, Award } from 'lucide-react';
import { api } from '../services/api';

const DOW_DATA = [
  { day: 'Mon', avg_units: 30.8, fill: '#3b82f6' },
  { day: 'Tue', avg_units: 32.4, fill: '#3b82f6' },
  { day: 'Wed', avg_units: 34.1, fill: '#3b82f6' },
  { day: 'Thu', avg_units: 37.6, fill: '#3b82f6' },
  { day: 'Fri', avg_units: 46.2, fill: '#10b981' },
  { day: 'Sat', avg_units: 51.5, fill: '#10b981' },
  { day: 'Sun', avg_units: 42.9, fill: '#10b981' },
];

const PROMO_LIFT_DATA = [
  { name: 'Standard Day (No Promo)', units: 32.81, fill: '#64748b' },
  { name: 'Active Promotion', units: 47.96, fill: '#10b981' },
];

const HOLIDAY_LIFT_DATA = [
  { name: 'Regular Weekday', units: 34.45, fill: '#64748b' },
  { name: 'Holiday Surge', units: 45.72, fill: '#f59e0b' },
];

export const SalesAnalyticsPage: React.FC = () => {
  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="glass-card rounded-2xl p-6 bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950/40 border border-indigo-500/20">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-white">Exploratory Demand & Seasonality Insights</h3>
              <p className="text-xs text-slate-400">Deep-dive empirical analysis across 21,900 daily retail sales records</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-bold border border-emerald-500/20">
              +46.19% Promotional Lift
            </span>
          </div>
        </div>
      </div>

      {/* Grid: DOW Seasonality & Promo Lift */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Day of Week */}
        <div className="glass-card rounded-2xl p-6">
          <h4 className="font-bold text-base text-white mb-1">Weekly Demand Rhythm (Day of Week)</h4>
          <p className="text-xs text-slate-400 mb-6">Average daily units sold showing weekend retail surges</p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={DOW_DATA}>
                <XAxis dataKey="day" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
                <Tooltip
                  formatter={(val: any) => [`${val} units/day`, 'Avg Demand']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                />
                <Bar dataKey="avg_units" radius={[6, 6, 0, 0]}>
                  {DOW_DATA.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Promotional Uplift */}
        <div className="glass-card rounded-2xl p-6">
          <h4 className="font-bold text-base text-white mb-1">Promotional Elasticity & Uplift</h4>
          <p className="text-xs text-slate-400 mb-6">Comparative daily velocity during active promo campaigns</p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={PROMO_LIFT_DATA} layout="vertical">
                <XAxis type="number" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis dataKey="name" type="category" stroke="#64748b" fontSize={11} tickLine={false} width={150} />
                <Tooltip
                  formatter={(val: any) => [`${val} units/day`, 'Average Velocity']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                />
                <Bar dataKey="units" radius={[0, 6, 6, 0]}>
                  {PROMO_LIFT_DATA.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
