import React, { useEffect, useState } from 'react';
import { Package, Search, Tag, DollarSign, Clock, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';
import { Product } from '../types';

export const ProductsPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [search, setSearch] = useState<string>('');
  const [selectedCat, setSelectedCat] = useState<string>('ALL');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchProds = async () => {
      try {
        const res = await api.getProducts();
        setProducts(res);
      } catch (err) {
        console.error('Failed to load products:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProds();
  }, []);

  const categories = ['ALL', ...Array.from(new Set(products.map((p) => p.category)))];

  const filtered = products.filter((p) => {
    const matchCat = selectedCat === 'ALL' || p.category === selectedCat;
    const matchSearch =
      p.product_name.toLowerCase().includes(search.toLowerCase()) ||
      p.product_id.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  return (
    <div className="space-y-8">
      {/* Control Bar */}
      <div className="glass-card rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search product catalog..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCat(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  selectedCat === cat
                    ? 'bg-emerald-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <span className="text-xs text-slate-400 font-semibold">
          Showing {filtered.length} SKUs
        </span>
      </div>

      {/* Catalog Table */}
      <div className="glass-card rounded-2xl p-6 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                <th className="py-3 px-4">SKU ID</th>
                <th className="py-3 px-4">Product Name</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4 text-right">Unit Price</th>
                <th className="py-3 px-4 text-right">Unit Cost</th>
                <th className="py-3 px-4 text-right">Gross Margin</th>
                <th className="py-3 px-4 text-right">Supplier Lead Time</th>
                <th className="py-3 px-4 text-right">Min Order Qty (MOQ)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((p) => {
                const marginPct = (((p.unit_price - p.unit_cost) / p.unit_price) * 100).toFixed(1);
                return (
                  <tr key={p.product_id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-emerald-400">{p.product_id}</td>
                    <td className="py-3.5 px-4 font-bold text-white">{p.product_name}</td>
                    <td className="py-3.5 px-4 text-slate-400">{p.category}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-200">${p.unit_price.toFixed(2)}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-400">${p.unit_cost.toFixed(2)}</td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-emerald-400">+{marginPct}%</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-300">{p.lead_time_days} days</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-300">{p.min_order_qty} units</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
