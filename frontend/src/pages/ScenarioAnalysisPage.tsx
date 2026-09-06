import React, { useEffect, useState } from 'react';
import {
  Sliders,
  Play,
  RotateCcw,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Shield,
  Clock,
  Percent,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { api } from '../services/api';
import { Product, Store, ScenarioSimulationResult } from '../types';
import { RiskBadge } from '../components/RiskBadge';

export const ScenarioAnalysisPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  const [selectedStore, setSelectedStore] = useState<string>('STR_01');
  const [selectedProduct, setSelectedProduct] = useState<string>('PRD_01');

  // Scenario Controls
  const [demandGrowth, setDemandGrowth] = useState<number>(20);
  const [priceChange, setPriceChange] = useState<number>(0);
  const [leadTime, setLeadTime] = useState<number>(7);
  const [serviceLevel, setServiceLevel] = useState<number>(0.99);

  const [result, setResult] = useState<ScenarioSimulationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const init = async () => {
      try {
        const [prods, strs] = await Promise.all([api.getProducts(), api.getStores()]);
        setProducts(prods);
        setStores(strs);
        if (prods.length > 0) setSelectedProduct(prods[0].product_id);
        if (strs.length > 0) setSelectedStore(strs[0].store_id);
      } catch (err) {
        console.error('Failed to load initial catalog:', err);
      }
    };
    init();
  }, []);

  const runSimulation = async () => {
    if (!selectedStore || !selectedProduct) return;
    setLoading(true);
    try {
      const res = await api.simulateScenario({
        store_id: selectedStore,
        product_id: selectedProduct,
        demand_growth_pct: demandGrowth,
        price_change_pct: priceChange,
        lead_time_days: leadTime,
        service_level: serviceLevel,
        horizon_days: 14,
      });
      setResult(res);
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, [selectedStore, selectedProduct, demandGrowth, priceChange, leadTime, serviceLevel]);

  const resetDefaults = () => {
    setDemandGrowth(0);
    setPriceChange(0);
    setLeadTime(5);
    setServiceLevel(0.95);
  };

  const chartData = (result?.daily_forecast_curves.dates || []).map((d, i) => ({
    date: d,
    baseline_demand: result?.daily_forecast_curves.baseline_demand[i],
    scenario_demand: result?.daily_forecast_curves.scenario_demand[i],
  }));

  const comp = result?.comparison;

  return (
    <div className="space-y-8">
      {/* Simulation Playground Controls */}
      <div className="glass-card rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-emerald-400" />
            <h3 className="font-bold text-base text-white">What-If Sensitivity Simulation Controls</h3>
          </div>
          <button
            onClick={resetDefaults}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 border border-slate-700 transition"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Baseline</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Target SKU */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
              Product SKU & Store
            </label>
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs font-medium text-white focus:outline-none focus:border-emerald-500 mb-2"
            >
              {products.map((p) => (
                <option key={p.product_id} value={p.product_id}>
                  {p.product_name}
                </option>
              ))}
            </select>
            <select
              value={selectedStore}
              onChange={(e) => setSelectedStore(e.target.value)}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs font-medium text-white focus:outline-none focus:border-emerald-500"
            >
              {stores.map((s) => (
                <option key={s.store_id} value={s.store_id}>
                  {s.store_name}
                </option>
              ))}
            </select>
          </div>

          {/* Demand Growth % */}
          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-400 mb-2">
              <span className="uppercase tracking-wider">Demand Growth %</span>
              <span className="text-emerald-400 font-bold">{demandGrowth > 0 ? `+${demandGrowth}%` : `${demandGrowth}%`}</span>
            </div>
            <input
              type="range"
              min="-50"
              max="50"
              step="5"
              value={demandGrowth}
              onChange={(e) => setDemandGrowth(Number(e.target.value))}
              className="w-full accent-emerald-500 bg-slate-900 rounded-lg cursor-pointer"
            />
            <p className="text-[11px] text-slate-400 mt-1">Simulate seasonal market shocks</p>
          </div>

          {/* Supplier Lead Time */}
          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-400 mb-2">
              <span className="uppercase tracking-wider">Lead Time (Days)</span>
              <span className="text-amber-400 font-bold">{leadTime} days</span>
            </div>
            <input
              type="range"
              min="1"
              max="21"
              step="1"
              value={leadTime}
              onChange={(e) => setLeadTime(Number(e.target.value))}
              className="w-full accent-amber-500 bg-slate-900 rounded-lg cursor-pointer"
            />
            <p className="text-[11px] text-slate-400 mt-1">Simulate supply chain delivery delays</p>
          </div>

          {/* Target Service Level */}
          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-400 mb-2">
              <span className="uppercase tracking-wider">Service Level (Z-score)</span>
              <span className="text-cyan-400 font-bold">{(serviceLevel * 100).toFixed(1)}%</span>
            </div>
            <select
              value={serviceLevel}
              onChange={(e) => setServiceLevel(Number(e.target.value))}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs font-medium text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="0.90">90.0% Service Level (Z = 1.282)</option>
              <option value="0.95">95.0% Standard Service Level (Z = 1.645)</option>
              <option value="0.98">98.0% High Availability (Z = 2.054)</option>
              <option value="0.99">99.0% Critical SLA (Z = 2.326)</option>
              <option value="0.999">99.9% Zero Stockout SLA (Z = 3.090)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Side-by-Side Comparative Impact Table */}
      {comp && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Total Demand */}
          <div className="glass-card rounded-2xl p-5">
            <span className="text-xs text-slate-400 font-semibold uppercase">14-Day Demand</span>
            <div className="flex items-baseline justify-between mt-2">
              <span className="text-sm text-slate-400">Base: {comp.total_forecast_demand.baseline}u</span>
              <span className="text-xl font-bold text-white">{comp.total_forecast_demand.scenario}u</span>
            </div>
            <span className="text-xs font-bold text-emerald-400 mt-1 block">
              {comp.total_forecast_demand.delta_percentage > 0 ? `+${comp.total_forecast_demand.delta_percentage}%` : `${comp.total_forecast_demand.delta_percentage}%`}
            </span>
          </div>

          {/* Safety Stock */}
          <div className="glass-card rounded-2xl p-5">
            <span className="text-xs text-slate-400 font-semibold uppercase">Safety Stock Required</span>
            <div className="flex items-baseline justify-between mt-2">
              <span className="text-sm text-slate-400">Base: {comp.safety_stock.baseline}u</span>
              <span className="text-xl font-bold text-cyan-400">{comp.safety_stock.scenario}u</span>
            </div>
            <span className="text-xs font-bold text-cyan-400 mt-1 block">
              +{comp.safety_stock.delta_units} buffer units
            </span>
          </div>

          {/* Reorder Point */}
          <div className="glass-card rounded-2xl p-5">
            <span className="text-xs text-slate-400 font-semibold uppercase">Reorder Point (ROP)</span>
            <div className="flex items-baseline justify-between mt-2">
              <span className="text-sm text-slate-400">Base: {comp.reorder_point.baseline}u</span>
              <span className="text-xl font-bold text-amber-400">{comp.reorder_point.scenario}u</span>
            </div>
            <span className="text-xs font-bold text-amber-400 mt-1 block">
              +{comp.reorder_point.delta_units} units threshold
            </span>
          </div>

          {/* Reorder Quantity */}
          <div className="glass-card rounded-2xl p-5">
            <span className="text-xs text-slate-400 font-semibold uppercase">Order Qty Recommended</span>
            <div className="flex items-baseline justify-between mt-2">
              <span className="text-sm text-slate-400">Base: {comp.recommended_order_qty.baseline}u</span>
              <span className="text-xl font-bold text-emerald-400">{comp.recommended_order_qty.scenario}u</span>
            </div>
            <span className="text-xs font-bold text-emerald-400 mt-1 block">
              +{comp.recommended_order_qty.delta_units} units PO
            </span>
          </div>
        </div>
      )}

      {/* Comparative Forecast Curves Chart */}
      <div className="glass-card rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="font-bold text-base text-white">Baseline vs Scenario Forward Demand Projection</h3>
            <p className="text-xs text-slate-400">Overlaying simulated demand growth curves against the baseline model</p>
          </div>
        </div>

        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
              />
              <Legend verticalAlign="top" height={36} />
              <Line
                name="Baseline Forecast"
                type="monotone"
                dataKey="baseline_demand"
                stroke="#64748b"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={{ r: 3 }}
              />
              <Line
                name="What-If Scenario Demand"
                type="monotone"
                dataKey="scenario_demand"
                stroke="#10b981"
                strokeWidth={3}
                dot={{ r: 4, fill: '#10b981' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
