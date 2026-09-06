import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { Header } from '../components/Header';

export const DashboardLayout: React.FC = () => {
  const location = useLocation();

  const getPageMeta = (pathname: string) => {
    switch (pathname) {
      case '/dashboard':
        return { title: 'Executive Overview', subtitle: 'Real-time sales velocity, demand intelligence & risk indicators' };
      case '/forecast':
        return { title: 'Demand Forecasting', subtitle: 'Multi-horizon machine learning predictions with confidence intervals' };
      case '/inventory':
        return { title: 'Inventory Optimization', subtitle: 'Automated safety stock, reorder points (ROP) and replenishment matrix' };
      case '/scenario':
        return { title: 'What-If Simulation Sandbox', subtitle: 'Test demand growth shocks, pricing elasticity and supplier lead time delays' };
      case '/analytics':
        return { title: 'Sales Analytics', subtitle: 'Historical demand patterns, weekly seasonality and promotional lift' };
      case '/models':
        return { title: 'Model Intelligence', subtitle: 'Model benchmarks, validation metrics, and feature importance explainability' };
      case '/products':
        return { title: 'Product Catalog', subtitle: 'Master SKU attributes, lead times, MOQ, and packaging constraints' };
      case '/upload':
        return { title: 'Data Ingestion & Ingestion Status', subtitle: 'Upload custom sales CSV with automated schema and anomaly validation' };
      default:
        return { title: 'Inventory Intelligence', subtitle: 'AI-Powered Decision System' };
    }
  };

  const meta = getPageMeta(location.pathname);

  return (
    <div className="flex min-h-screen bg-[#090d16]">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header title={meta.title} subtitle={meta.subtitle} />
        <main className="flex-1 p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
