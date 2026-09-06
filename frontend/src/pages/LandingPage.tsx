import React from 'react';
import { Link } from 'react-router-dom';
import {
  Boxes,
  LineChart,
  Sliders,
  Cpu,
  ArrowRight,
  ShieldCheck,
  Zap,
  BarChart3,
  CheckCircle,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#090d16] text-white flex flex-col justify-between">
      {/* Navbar */}
      <nav className="border-b border-slate-800/80 px-8 py-5 flex items-center justify-between max-w-7xl mx-auto w-full">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Boxes className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight">InventoryAI</span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            to="/dashboard"
            className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition shadow-lg shadow-emerald-600/30 flex items-center gap-2"
          >
            Launch Dashboard
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-5xl mx-auto px-8 py-20 text-center flex flex-col items-center">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-6">
          <Zap className="w-3.5 h-3.5" />
          <span>Production AI & Inventory Intelligence Platform</span>
        </div>

        <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight leading-tight text-transparent bg-clip-text bg-gradient-to-b from-white via-slate-200 to-slate-400 max-w-4xl">
          AI-Powered Inventory Demand Forecasting & Optimization
        </h1>

        <p className="mt-6 text-lg text-slate-400 max-w-2xl leading-relaxed">
          Eliminate stockouts, slash carrying costs, and automate purchase order replenishment using state-of-the-art machine learning and probabilistic inventory theory.
        </p>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Link
            to="/dashboard"
            className="px-8 py-4 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-base transition shadow-xl shadow-emerald-600/25 flex items-center gap-3"
          >
            Open Live Demo Platform
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            to="/forecast"
            className="px-8 py-4 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-200 font-semibold text-base transition border border-slate-700/80"
          >
            Explore Forecast Models
          </Link>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20 text-left w-full">
          <div className="glass-card rounded-2xl p-6">
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 w-fit mb-4">
              <LineChart className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg mb-2">Machine Learning Forecasting</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Multi-horizon LightGBM and XGBoost models delivering a 40.3% error reduction over statistical moving averages.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6">
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 w-fit mb-4">
              <Boxes className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg mb-2">Automated Inventory Optimization</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Dynamic Safety Stock, Reorder Point (ROP), and Order Quantity formulas tailored to lead times and target service levels.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6">
            <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 w-fit mb-4">
              <Sliders className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg mb-2">What-If Scenario Sandbox</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Simulate demand shocks, price elasticity, and supplier lead time disruptions in real time before placing purchase orders.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-8 text-center text-xs text-slate-500">
        AI-Powered Inventory Demand Forecasting System • Engineered with React, TypeScript, FastAPI, PostgreSQL & LightGBM
      </footer>
    </div>
  );
};
