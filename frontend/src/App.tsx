import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from './layouts/DashboardLayout';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { DemandForecastPage } from './pages/DemandForecastPage';
import { InventoryOptimizationPage } from './pages/InventoryOptimizationPage';
import { ScenarioAnalysisPage } from './pages/ScenarioAnalysisPage';
import { SalesAnalyticsPage } from './pages/SalesAnalyticsPage';
import { ModelPerformancePage } from './pages/ModelPerformancePage';
import { ProductsPage } from './pages/ProductsPage';
import { DataUploadPage } from './pages/DataUploadPage';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/forecast" element={<DemandForecastPage />} />
          <Route path="/inventory" element={<InventoryOptimizationPage />} />
          <Route path="/scenario" element={<ScenarioAnalysisPage />} />
          <Route path="/analytics" element={<SalesAnalyticsPage />} />
          <Route path="/models" element={<ModelPerformancePage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/upload" element={<DataUploadPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
