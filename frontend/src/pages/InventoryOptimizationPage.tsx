import React, { useEffect, useState } from 'react';
import {
  Boxes,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  PackageX,
  Search,
  Filter,
  ShoppingCart,
  ArrowUpDown,
  Download,
} from 'lucide-react';
import { api } from '../services/api';
import { InventorySummaryResponse, InventoryStatusItem, Store } from '../types';
import { RiskBadge } from '../components/RiskBadge';

export const InventoryOptimizationPage: React.FC = () => {
  const [data, setData] = useState<InventorySummaryResponse | null>(null);
  const [stores, setStores] = useState<Store[]>([]);
  const [selectedStore, setSelectedStore] = useState<string>('');
  const [filterRisk, setFilterRisk] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchStores = async () => {
      try {
        const res = await api.getStores();
        setStores(res);
      } catch (err) {
        console.error('Failed to load stores:', err);
      }
    };
    fetchStores();
  }, []);

  useEffect(() => {
    const fetchInventory = async () => {
      setLoading(true);
      try {
        const res = await api.getInventoryStatus(selectedStore || undefined);
        setData(res);
      } catch (err) {
        console.error('Failed to load inventory status:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchInventory();
  }, [selectedStore]);

  const filteredItems = (data?.items || []).filter((item) => {
    const matchesRisk = filterRisk === 'ALL' || item.risk_status === filterRisk;
    const matchesSearch =
      item.product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.product_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesRisk && matchesSearch;
  });

  return (
    <div className="space-y-8">
      {/* Top Filter & Summary Tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <button
          onClick={() => setFilterRisk('ALL')}
          className={`glass-card rounded-xl p-4 text-left transition ${
            filterRisk === 'ALL' ? 'border-emerald-500/50 bg-emerald-500/10' : ''
          }`}
        >
          <span className="text-xs text-slate-400 font-medium">All SKUs Tracked</span>
          <p className="text-xl font-bold text-white mt-1">{data?.total_products_tracked || 0}</p>
        </button>

        <button
          onClick={() => setFilterRisk('STOCKOUT_RISK')}
          className={`glass-card rounded-xl p-4 text-left transition ${
            filterRisk === 'STOCKOUT_RISK' ? 'border-red-500/50 bg-red-500/10' : ''
          }`}
        >
          <div className="flex items-center gap-1.5 text-xs text-red-400 font-medium">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Stockout Risk</span>
          </div>
          <p className="text-xl font-bold text-red-400 mt-1">{data?.stockout_risk_count || 0}</p>
        </button>

        <button
          onClick={() => setFilterRisk('LOW_STOCK')}
          className={`glass-card rounded-xl p-4 text-left transition ${
            filterRisk === 'LOW_STOCK' ? 'border-amber-500/50 bg-amber-500/10' : ''
          }`}
        >
          <div className="flex items-center gap-1.5 text-xs text-amber-400 font-medium">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Low Stock</span>
          </div>
          <p className="text-xl font-bold text-amber-400 mt-1">{data?.low_stock_count || 0}</p>
        </button>

        <button
          onClick={() => setFilterRisk('OVERSTOCK_RISK')}
          className={`glass-card rounded-xl p-4 text-left transition ${
            filterRisk === 'OVERSTOCK_RISK' ? 'border-blue-500/50 bg-blue-500/10' : ''
          }`}
        >
          <div className="flex items-center gap-1.5 text-xs text-blue-400 font-medium">
            <PackageX className="w-3.5 h-3.5" />
            <span>Overstock Risk</span>
          </div>
          <p className="text-xl font-bold text-blue-400 mt-1">{data?.overstock_risk_count || 0}</p>
        </button>
      </div>

      {/* Control Bar */}
      <div className="glass-card rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          {/* Search */}
          <div className="relative flex-1 sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search SKU or Category..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          {/* Store Filter */}
          <select
            value={selectedStore}
            onChange={(e) => setSelectedStore(e.target.value)}
            className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Stores</option>
            {stores.map((s) => (
              <option key={s.store_id} value={s.store_id}>
                {s.store_name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
          <ShoppingCart className="w-4 h-4 text-emerald-400" />
          <span>Total Recommended Reorders:</span>
          <span className="text-emerald-400 font-bold text-sm">
            {data?.total_recommended_reorder_units.toLocaleString() || 0} units
          </span>
        </div>
      </div>

      {/* Inventory & Reorders Table */}
      <div className="glass-card rounded-2xl p-6 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                <th className="py-3 px-4">Store</th>
                <th className="py-3 px-4">Product Name</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4 text-right">Current Stock</th>
                <th className="py-3 px-4 text-right">Days of Supply</th>
                <th className="py-3 px-4 text-right">Safety Stock</th>
                <th className="py-3 px-4 text-right">Reorder Point (ROP)</th>
                <th className="py-3 px-4 text-right">Recommended Reorder</th>
                <th className="py-3 px-4 text-center">Risk Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                    Calculating replenishment positions...
                  </td>
                </tr>
              ) : filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    No SKUs match the current filter criteria.
                  </td>
                </tr>
              ) : (
                filteredItems.map((item) => (
                  <tr key={`${item.store_id}-${item.product_id}`} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-slate-300">{item.store_id}</td>
                    <td className="py-3.5 px-4 font-bold text-white">{item.product_name}</td>
                    <td className="py-3.5 px-4 text-slate-400">{item.category}</td>
                    <td className="py-3.5 px-4 text-right font-mono font-semibold text-slate-200">
                      {item.current_stock.toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-400">
                      {item.days_of_supply} days
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-400">
                      {item.safety_stock}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-amber-400">
                      {item.reorder_point}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-extrabold text-emerald-400">
                      {item.recommended_reorder_qty > 0 ? (
                        <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          +{item.recommended_reorder_qty.toLocaleString()}
                        </span>
                      ) : (
                        <span className="text-slate-500">0</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <RiskBadge status={item.risk_status} />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
