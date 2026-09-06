import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  DollarSign,
  Package,
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  Layers,
  ArrowUpRight,
  Activity,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts';
import { KPICard } from '../components/KPICard';
import { api } from '../services/api';
import { DashboardSummaryResponse } from '../types';

const CATEGORY_COLORS = ['#10b981', '#06b6d4', '#8b5cf6', '#f59e0b', '#ec4899'];

export const DashboardPage: React.FC = () => {
  const [data, setData] = useState<DashboardSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await api.getDashboardSummary();
        setData(res);
      } catch (err) {
        console.error('Error fetching dashboard summary:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm text-slate-400">Loading live business metrics...</span>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-8">
      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <KPICard
          title="Total Revenue (2-Yr)"
          value={`$${(data.total_revenue / 1000000).toFixed(2)}M`}
          subtitle={`${data.total_sales_volume.toLocaleString()} units sold`}
          icon={DollarSign}
          color="emerald"
        />
        <KPICard
          title="Daily System Demand"
          value={`${data.avg_daily_system_demand.toLocaleString()} u/d`}
          subtitle="Across all active store locations"
          icon={TrendingUp}
          color="blue"
        />
        <KPICard
          title="Stockout Risk"
          value={data.stockout_risk_count}
          subtitle="SKUs below lead-time demand"
          icon={AlertCircle}
          color="red"
          badge="Action Required"
        />
        <KPICard
          title="Low Stock Warning"
          value={data.low_stock_count}
          subtitle="SKUs at or below Reorder Point"
          icon={AlertTriangle}
          color="amber"
          badge="Reorder Trigger"
        />
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sales Trend Chart */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-bold text-base text-white">Daily Sales Velocity (Recent 30 Days)</h3>
              <p className="text-xs text-slate-400">Aggregated unit volume across all product categories</p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-slate-800/80 text-xs font-semibold text-emerald-400 border border-slate-700">
              <Activity className="w-3.5 h-3.5" />
              <span>Real-Time Ingestion</span>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.recent_sales_trend}>
                <defs>
                  <linearGradient id="salesGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                  labelStyle={{ color: '#94a3b8' }}
                />
                <Area type="monotone" dataKey="units_sold" stroke="#10b981" strokeWidth={2.5} fillOpacity={1} fill="url(#salesGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Contribution Share */}
        <div className="glass-card rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-base text-white mb-1">Revenue by Category</h3>
            <p className="text-xs text-slate-400 mb-4">Volume and monetary split across catalog</p>
          </div>

          <div className="h-56 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.category_distribution}
                  dataKey="revenue"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                >
                  {data.category_distribution.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Revenue']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 gap-2 mt-2 pt-3 border-t border-slate-800">
            {data.category_distribution.map((cat, idx) => (
              <div key={cat.category} className="flex items-center gap-2 text-xs">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: CATEGORY_COLORS[idx % CATEGORY_COLORS.length] }} />
                <span className="text-slate-300 truncate">{cat.category}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Model Benchmark & AI Status Card */}
      <div className="glass-card rounded-2xl p-6 bg-gradient-to-r from-slate-900 via-slate-800/90 to-emerald-950/30 border border-emerald-500/20">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="font-bold text-white text-base">Active Champion Model: {data.champion_model_name}</h4>
                <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">PRODUCTION</span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Outperforming statistical baselines with a 40.3% error reduction on out-of-time test partitions.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-6 text-sm">
            <div className="text-right">
              <p className="text-xs text-slate-400">Mean Absolute Error</p>
              <p className="text-lg font-bold text-white">{data.champion_model_mae} units</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-400">Holdout WAPE</p>
              <p className="text-lg font-bold text-emerald-400">{data.champion_model_wape_pct}%</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
