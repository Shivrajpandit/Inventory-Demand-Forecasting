import axios from 'axios';
import {
  Product,
  Store,
  ForecastResponse,
  InventorySummaryResponse,
  DashboardSummaryResponse,
  ScenarioSimulationResult,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Catalog
  getProducts: async (): Promise<Product[]> => {
    const res = await apiClient.get<Product[]>('/products');
    return res.data;
  },
  getStores: async (): Promise<Store[]> => {
    const res = await apiClient.get<Store[]>('/stores');
    return res.data;
  },

  // Dashboard
  getDashboardSummary: async (): Promise<DashboardSummaryResponse> => {
    const res = await apiClient.get<DashboardSummaryResponse>('/dashboard/summary');
    return res.data;
  },

  // Forecasting
  generateForecast: async (params: {
    store_id: string;
    product_id: string;
    horizon_days?: number;
    demand_growth_pct?: number;
    price_change_pct?: number;
    is_promotion?: boolean | null;
  }): Promise<ForecastResponse> => {
    const res = await apiClient.post<ForecastResponse>('/forecast', params);
    return res.data;
  },

  getHistoricalDemand: async (store_id: string, product_id: string, days: number = 60) => {
    const res = await apiClient.get('/forecast/history', {
      params: { store_id, product_id, days },
    });
    return res.data;
  },

  // Inventory
  getInventoryStatus: async (store_id?: string): Promise<InventorySummaryResponse> => {
    const res = await apiClient.get<InventorySummaryResponse>('/inventory/status', {
      params: store_id ? { store_id } : {},
    });
    return res.data;
  },

  // Scenarios
  simulateScenario: async (params: {
    store_id: string;
    product_id: string;
    demand_growth_pct?: number;
    price_change_pct?: number;
    lead_time_days?: number;
    service_level?: number;
    horizon_days?: number;
  }): Promise<ScenarioSimulationResult> => {
    const res = await apiClient.post<ScenarioSimulationResult>('/scenario/simulate', params);
    return res.data;
  },

  // Model Intelligence
  getModelPerformance: async () => {
    const res = await apiClient.get('/models/performance');
    return res.data;
  },
  getChampionDetails: async () => {
    const res = await apiClient.get('/models/champion');
    return res.data;
  },

  // CSV Upload
  uploadCSV: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post('/data/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },
};
