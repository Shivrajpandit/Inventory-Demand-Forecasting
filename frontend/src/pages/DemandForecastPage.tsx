import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
  Legend,
} from 'recharts';
import {
  Calendar,
  Sparkles,
  SlidersHorizontal,
  TrendingUp,
  Tag,
  Percent,
} from 'lucide-react';
import { api } from '../services/api';
import { Product, Store, ForecastResponse } from '../types';

export const DemandForecastPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  const [selectedStore, setSelectedStore] = useState<string>('STR_01');
  const [selectedProduct, setSelectedProduct] = useState<string>('PRD_01');
  const [horizonDays, setHorizonDays] = useState<number>(14);
  const [demandGrowth, setDemandGrowth] = useState<number>(0);
  const [priceChange, setPriceChange] = useState<number>(0);

  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Load initial dropdown catalogs
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

  // Fetch forecast whenever parameters change
  useEffect(() => {
    const runForecast = async () => {
      if (!selectedStore || !selectedProduct) return;
      setLoading(true);
      try {
        const [fRes, hRes] = await Promise.all([
          api.generateForecast({
            store_id: selectedStore,
            product_id: selectedProduct,
            horizon_days: horizonDays,
            demand_growth_pct: demandGrowth,
            price_change_pct: priceChange,
          }),
          api.getHistoricalDemand(selectedStore, selectedProduct, 30),
        ]);
        setForecast(fRes);
        setHistory(hRes.history || []);
      } catch (err) {
        console.error('Forecast error:', err);
      } finally {
        setLoading(false);
      }
    };
    runForecast();
  }, [selectedStore, selectedProduct, horizonDays, demandGrowth, priceChange]);

  // Combine history + future forecast for the continuous chart
  const combinedChartData = [
    ...history.map((h) => ({
      date: h.date,
      actual_demand: h.units_sold,
      predicted_demand: null,
      lower_bound: null,
      upper_bound: null,
    })),
    ...(forecast?.daily_forecasts || []).map((f) => ({
      date: f.date,
      actual_demand: null,
      predicted_demand: f.predicted_demand,
      lower_bound: f.lower_bound,
      upper_bound: f.upper_bound,
    })),
  ];

  return (
    <div className="space-y-8">
      {/* Control Ribbon */}
      <div className="glass-card rounded-2xl p-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 items-center">
          {/* Store Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
              Store Location
            </label>
            <select
              value={selectedStore}
              onChange={(e) => setSelectedStore(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-sm font-medium text-white focus:outline-none focus:border-emerald-500"
            >
              {stores.map((s) => (
                <option key={s.store_id} value={s.store_id}>
                  {s.store_name} ({s.store_id})
                </option>
              ))}
            </select>
          </div>

          {/* Product Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
              Product SKU
            </label>
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-sm font-medium text-white focus:outline-none focus:border-emerald-500"
            >
              {products.map((p) => (
                <option key={p.product_id} value={p.product_id}>
                  {p.product_name}
                </option>
              ))}
            </select>
          </div>

          {/* Forecast Horizon */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
              Forecast Horizon
            </label>
            <div className="grid grid-cols-3 gap-1.5 bg-slate-900 p-1 rounded-xl border border-slate-700">
              {[7, 14, 30].map((days) => (
                <button
                  key={days}
                  onClick={() => setHorizonDays(days)}
                  className={`py-1.5 text-xs font-bold rounded-lg transition ${
                    horizonDays === days
                      ? 'bg-emerald-600 text-white shadow-md'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {days}d
                </button>
              ))}
            </div>
          </div>

          {/* Growth % Slider */}
          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-400 mb-1.5">
              <span className="uppercase tracking-wider">Demand Shock</span>
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
          </div>

          {/* Price Change % Slider */}
          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-400 mb-1.5">
              <span className="uppercase tracking-wider">Price Delta</span>
              <span className="text-amber-400 font-bold">{priceChange > 0 ? `+${priceChange}%` : `${priceChange}%`}</span>
            </div>
            <input
              type="range"
              min="-30"
              max="30"
              step="5"
              value={priceChange}
              onChange={(e) => setPriceChange(Number(e.target.value))}
              className="w-full accent-amber-500 bg-slate-900 rounded-lg cursor-pointer"
            />
          </div>
        </div>
      </div>

      {/* Main Forecast Visualizer */}
      <div className="glass-card rounded-2xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-bold text-lg text-white">
                {forecast?.product_name || 'Demand Forecast'}
              </h3>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-medium border border-slate-700">
                {forecast?.category}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              30-Day Historical Actuals + Next {horizonDays}-Day Forward Machine Learning Projection with 95% Confidence Interval
            </p>
          </div>

          {forecast && (
            <div className="flex items-center gap-6 bg-slate-900/80 px-4 py-2 rounded-xl border border-slate-700/80">
              <div>
                <p className="text-[10px] text-slate-400 uppercase">Total Forecast</p>
                <p className="text-base font-bold text-white">{forecast.total_forecast_demand} units</p>
              </div>
              <div className="border-l border-slate-700 pl-4">
                <p className="text-[10px] text-slate-400 uppercase">Daily Average</p>
                <p className="text-base font-bold text-emerald-400">{forecast.avg_daily_demand} u/d</p>
              </div>
              <div className="border-l border-slate-700 pl-4">
                <p className="text-[10px] text-slate-400 uppercase">Engine</p>
                <p className="text-xs font-bold text-slate-300">{forecast.model_used}</p>
              </div>
            </div>
          )}
        </div>

        {/* Chart */}
        <div className="h-96 w-full">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={combinedChartData}>
                <defs>
                  <linearGradient id="ciGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                />
                <Legend verticalAlign="top" height={36} />

                {/* Upper Confidence Area */}
                <Area
                  name="95% Upper Bound"
                  type="monotone"
                  dataKey="upper_bound"
                  stroke="#06b6d4"
                  strokeDasharray="3 3"
                  fill="url(#ciGrad)"
                />

                {/* Lower Confidence Area */}
                <Area
                  name="95% Lower Bound"
                  type="monotone"
                  dataKey="lower_bound"
                  stroke="#06b6d4"
                  strokeDasharray="3 3"
                  fill="transparent"
                />

                {/* Actual Historical Demand */}
                <Line
                  name="Historical Actual Demand"
                  type="monotone"
                  dataKey="actual_demand"
                  stroke="#94a3b8"
                  strokeWidth={2}
                  dot={{ r: 2 }}
                />

                {/* Predicted Forward Demand */}
                <Line
                  name="Predicted Demand"
                  type="monotone"
                  dataKey="predicted_demand"
                  stroke="#10b981"
                  strokeWidth={3}
                  dot={{ r: 3, fill: '#10b981' }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Daily Breakdown Table */}
      {forecast && (
        <div className="glass-card rounded-2xl p-6">
          <h4 className="font-bold text-base text-white mb-4">Daily Forecast Schedule</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Day</th>
                  <th className="py-3 px-4 text-right">Predicted Units</th>
                  <th className="py-3 px-4 text-right">95% Lower CI</th>
                  <th className="py-3 px-4 text-right">95% Upper CI</th>
                  <th className="py-3 px-4 text-center">Event / Promo</th>
                  <th className="py-3 px-4 text-right">Unit Price</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {forecast.daily_forecasts.map((d) => (
                  <tr key={d.date} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 font-mono font-medium text-slate-200">{d.date}</td>
                    <td className="py-3 px-4 text-slate-400">{d.day_of_week}</td>
                    <td className="py-3 px-4 text-right font-bold text-emerald-400">{d.predicted_demand.toFixed(1)}</td>
                    <td className="py-3 px-4 text-right text-slate-400">{d.lower_bound.toFixed(1)}</td>
                    <td className="py-3 px-4 text-right text-slate-400">{d.upper_bound.toFixed(1)}</td>
                    <td className="py-3 px-4 text-center">
                      {d.promotion === 1 ? (
                        <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20 text-[10px]">
                          PROMO ACTIVE
                        </span>
                      ) : (
                        <span className="text-slate-500">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-300">${d.price.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
