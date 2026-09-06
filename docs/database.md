# Database Schema Specification

## Relational Database Design (PostgreSQL)

The system uses a normalized PostgreSQL relational database to store business entities, granular daily sales records, current inventory positions, forecasting runs, and generated recommendations.

```mermaid
erDiagram
    USERS ||--o{ SCENARIOS : creates
    STORES ||--o{ SALES : records
    STORES ||--o{ INVENTORY : maintains
    STORES ||--o{ FORECASTS : targets
    PRODUCTS ||--o{ SALES : includes
    PRODUCTS ||--o{ INVENTORY : tracked_in
    PRODUCTS ||--o{ FORECASTS : predicted_for
    PRODUCTS ||--o{ INVENTORY_RECOMMENDATIONS : generated_for
    MODEL_RUNS ||--o{ FORECASTS : produces

    USERS {
        uuid id PK
        varchar email UK
        varchar hashed_password
        varchar full_name
        varchar role
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    STORES {
        varchar store_id PK
        varchar store_name
        varchar location
        varchar region
        timestamp created_at
    }

    PRODUCTS {
        varchar product_id PK
        varchar product_name
        varchar category
        varchar subcategory
        numeric unit_price
        numeric unit_cost
        integer lead_time_days
        integer min_order_qty
        timestamp created_at
    }

    SALES {
        bigserial id PK
        date sale_date
        varchar store_id FK
        varchar product_id FK
        integer units_sold
        numeric revenue
        numeric discount_rate
        boolean is_promotion
        boolean is_holiday
        timestamp created_at
    }

    INVENTORY {
        bigserial id PK
        varchar store_id FK
        varchar product_id FK
        integer current_stock
        integer safety_stock
        integer reorder_point
        integer max_capacity
        date last_restock_date
        timestamp updated_at
    }

    MODEL_RUNS {
        uuid id PK
        varchar model_name
        varchar model_version
        varchar algorithm
        jsonb hyperparameters
        jsonb metrics
        jsonb feature_importances
        varchar artifact_path
        timestamp trained_at
    }

    FORECASTS {
        bigserial id PK
        uuid model_run_id FK
        varchar store_id FK
        varchar product_id FK
        date forecast_date
        numeric predicted_demand
        numeric lower_bound
        numeric upper_bound
        timestamp created_at
    }

    INVENTORY_RECOMMENDATIONS {
        bigserial id PK
        varchar store_id FK
        varchar product_id FK
        date recommendation_date
        integer current_stock
        numeric projected_demand_lead_time
        integer safety_stock
        integer reorder_point
        integer recommended_reorder_qty
        varchar risk_status
        text recommendation_reason
        timestamp created_at
    }

    SCENARIOS {
        uuid id PK
        uuid user_id FK
        varchar name
        varchar product_id FK
        varchar store_id FK
        jsonb input_parameters
        jsonb simulation_results
        timestamp created_at
    }
```

---

## Table Definitions & Indexing Strategy

### 1. `users`
- Stores user accounts for dashboard access and API authentication.
- **Indexes**: `UNIQUE INDEX idx_users_email (email)`.

### 2. `stores` & `products`
- Master entity catalogs representing physical/virtual storefronts and SKU metadata (costs, prices, default lead times, packaging constraints).
- **Indexes**: `INDEX idx_products_category (category)`.

### 3. `sales`
- High-volume transaction log containing historical daily aggregate unit sales per product and store.
- **Indexes**:
  - `UNIQUE INDEX idx_sales_date_store_prod (sale_date, store_id, product_id)`
  - `INDEX idx_sales_store_prod (store_id, product_id)`
  - `INDEX idx_sales_date (sale_date)`

### 4. `inventory`
- Real-time stock levels, current inventory buffer metrics, and storage capacities.
- **Indexes**: `UNIQUE INDEX idx_inventory_store_prod (store_id, product_id)`.

### 5. `model_runs` & `forecasts`
- Full lineage tracking of trained ML models, evaluation metrics (MAE, RMSE, sMAPE), and multi-horizon point forecasts.
- **Indexes**:
  - `INDEX idx_forecasts_lookup (store_id, product_id, forecast_date)`
  - `INDEX idx_forecasts_model_run (model_run_id)`

### 6. `inventory_recommendations`
- Actionable business intelligence derived from model forecasts combined with inventory business rules.
- **Risk Statuses**: `HEALTHY`, `LOW_STOCK`, `STOCKOUT_RISK`, `OVERSTOCK_RISK`.
- **Indexes**: `INDEX idx_recommendations_store_risk (store_id, risk_status)`.

### 7. `scenarios`
- Sandbox simulations allowing business planners to test demand shocks, price elasticity, and lead time disruptions.
