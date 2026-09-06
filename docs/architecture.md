# System Architecture

## AI-Powered Inventory Demand Forecasting & Optimization System

```mermaid
flowchart TD
    subgraph DataLayer [Data Ingestion & Storage]
        CSV[Retail Sales Data / CSV Upload] --> Ingestion[Data Ingestion & Validation Pipeline]
        Ingestion --> Preproc[Preprocessing & Data Cleaning]
        Preproc --> DB[(PostgreSQL Database)]
        DB --> CleanData[Cleaned Daily Store-Product Sales]
    end

    subgraph MLLayer [Machine Learning & Forecasting Engine]
        CleanData --> FE[Feature Engineering Engine\n- Lags: 1, 7, 14, 28\n- Rolling Stats: Mean/Std 7, 14, 28\n- Temporal: Day, Week, Month, Season\n- Promo, Price, Holiday]
        FE --> Split[Chronological Train / Val / Test Split\nStrict No-Leakage Time Boundary]
        Split --> Models[Forecasting Models\n- Baseline: Naive, Moving Avg\n- ML: Ridge, Random Forest, XGBoost\n- Time Series: SARIMAX]
        Models --> Eval[Model Evaluation & Walk-Forward Validation\nMetrics: MAE, RMSE, WAPE, sMAPE]
        Eval --> Registry[Model Registry & Serializer\nMetadata, Metrics & Feature Importance]
    end

    subgraph InventoryLayer [Inventory Optimization Engine]
        Registry --> Inference[Multi-Horizon Demand Forecast Engine]
        Inference --> InvEngine[Inventory Decision Engine]
        DB -. Current Stock & Lead Time .-> InvEngine
        InvEngine --> OptRules[Safety Stock & Reorder Point Calculation\n- Demand Uncertainty (Std Dev)\n- Target Service Level (Z-score)\n- Lead Time Demand\n- Economic Reorder Quantity]
        OptRules --> RiskClass[Risk Classification\n🟢 Healthy | 🟠 Low Stock\n🔴 Stockout Risk | 🔵 Overstock Risk]
        OptRules --> ScenarioEngine[What-If Scenario Simulation Engine\n- Demand shifts, Lead time changes, Price/Promo changes]
    end

    subgraph BackendLayer [FastAPI REST API]
        InvEngine --> APIServices[FastAPI Backend Services]
        APIServices --> Auth[JWT Auth & RBAC]
        APIServices --> Endpoints[REST Endpoints\n/api/products, /api/forecast\n/api/inventory/recommendations\n/api/scenario, /api/models/performance]
    end

    subgraph FrontendLayer [React + TypeScript Dashboard]
        Endpoints --> UI[Modern SaaS Web Application\n- Executive KPI Cards\n- Interactive Forecast Charts (Recharts)\n- Inventory Matrix & Risk Table\n- What-If Scenario Sandbox\n- Model Explainability & Feature Importance]
    end
```

---

## 1. Architectural Highlights

### A. Separation of Concerns
1. **Data Engineering Layer (`ml/preprocessing`)**:
   - Ingests raw sales logs, validates schemas, eliminates duplicates, handles missing records and zero-sales padding per store-SKU combination.
2. **Feature Store / Feature Engineering (`ml/features`)**:
   - Computes causal historical lag features and rolling aggregations. All calculations use strictly backward-looking windows to prevent lookahead bias.
3. **Forecasting Engine (`ml/forecasting` & `ml/models`)**:
   - Trains and compares baselines against machine learning models. Serializes top-performing models with full lineage metadata into `models/`.
4. **Inventory Intelligence (`ml/inference` & `backend/app/services`)**:
   - Bridges raw machine learning point forecasts with probabilistic inventory theory (Safety Stock, Reorder Point, Economic Order Quantity, Stockout/Overstock Risk scoring).
5. **Backend REST API (`backend/app`)**:
   - High-throughput asynchronous FastAPI framework with SQLAlchemy ORM, Pydantic v2 schemas, JWT authentication, and automated OpenAPI documentation.
6. **Frontend Dashboard (`frontend`)**:
   - React 18, TypeScript, Tailwind CSS, Lucide icons, and Recharts delivering an executive-ready business intelligence platform.

---

## 2. Component Directory Mapping

| Layer / Component | Workspace Directory | Key Responsibilities |
| :--- | :--- | :--- |
| **Data Ingestion** | `ml/preprocessing/` | Schema validation, outlier handling, chronological consistency |
| **Feature Engineering** | `ml/features/` | Causal lags, rolling statistics, calendar seasonality encoding |
| **Model Training & Registry**| `ml/models/`, `ml/forecasting/` | Model training, hyperparameter tuning, model artifact serialization |
| **Evaluation Suite** | `ml/evaluation/` | MAE, RMSE, WAPE, sMAPE, walk-forward time-series CV |
| **Inventory Optimization** | `ml/inference/`, `backend/app/services/` | Safety stock formulas, risk classification, reorder recommendations |
| **Backend REST API** | `backend/app/` | API routing, database persistence, authentication, scenario calculations |
| **Web Dashboard** | `frontend/src/` | Executive dashboard, forecast visualizer, what-if simulator |
