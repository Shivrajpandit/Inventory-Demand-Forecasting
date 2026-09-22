# 🤖 AI-Powered Inventory Demand Forecasting & Optimization System

<p align="center">

[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![LightGBM](https://img.shields.io/badge/ML-LightGBM%20%7C%20XGBoost-4CAF50.svg)](https://lightgbm.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</p>

> **An end-to-end AI and Operations Intelligence platform that forecasts product demand, detects stockout and overstock risks, and generates data-driven replenishment recommendations.**

---

## 📌 Overview

The **AI-Powered Inventory Demand Forecasting & Optimization System** combines machine learning, time-series forecasting, and inventory optimization to help businesses make smarter inventory decisions.

Instead of relying only on static spreadsheets, simple moving averages, or manual inventory rules, the platform uses historical sales data, machine learning models, demand uncertainty, lead times, and current inventory levels to generate actionable recommendations.

### 🎯 The system helps answer:

- 📈 **How much demand should we expect?**
- 📦 **How much inventory should we maintain?**
- ⚠️ **Which products are at risk of stockout?**
- 🔴 **Which products are overstocked?**
- 🚚 **When should we reorder?**
- 🧮 **How much should we order?**
- 🔮 **What happens if demand suddenly increases?**
- ⏱️ **What happens if supplier lead time increases?**

---

# 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Business Impact](#-business-impact)
- [System Workflow](#-system-workflow)
- [Architecture](#️-architecture)
- [Machine Learning Methodology](#-machine-learning-methodology)
- [Model Benchmark Results](#-model-benchmark-results)
- [Inventory Optimization](#-inventory-optimization)
- [Risk Classification](#-risk-classification)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Docker Deployment](#-docker-deployment)
- [API](#-api)
- [Testing](#-testing)
- [Repository Structure](#-repository-structure)
- [Use Cases](#-use-cases)
- [Future Enhancements](#-future-enhancements)
- [License](#-license)

---

# 🌟 Key Features

## 📈 1. AI Demand Forecasting

Forecast future product demand using multiple machine learning approaches.

The system evaluates:

- Naive forecasting
- Moving averages
- Ridge Regression
- Random Forest
- XGBoost
- LightGBM

The best-performing model is selected based on validation performance.

---

## 🧠 2. Intelligent Feature Engineering

The forecasting pipeline generates time-series features such as:

### Lag Features

```text
t-1
t-7
t-14
t-28

                 ┌──────────────────────┐
                 │ Historical Sales Data│
                 │ Promotions & Inventory│
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Data Validation &    │
                 │ Cleaning             │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Feature Engineering  │
                 │ Lag + Rolling + Time │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Model Training       │
                 │ Ridge / RF / XGB /   │
                 │ LightGBM             │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Model Evaluation     │
                 │ & Champion Selection │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Demand Forecasting   │
                 │ Multi-Horizon        │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Inventory Optimizer  │
                 │ Safety Stock + ROP   │
                 └──────────┬───────────┘
                            │
                 ┌──────────┴───────────┐
                 ▼                      ▼
        ┌─────────────────┐    ┌──────────────────┐
        │ Risk Detection  │    │ Replenishment   │
        │ Stockout /      │    │ Recommendation  │
        │ Overstock       │    │                 │
        └─────────────────┘    └──────────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Dashboard &          │
                 │ What-If Simulator    │
                 └──────────────────────┘
