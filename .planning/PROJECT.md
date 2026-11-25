# CloudCost-Autopilot

## What This Is

**CloudCost-Autopilot** is a Kubernetes FinOps & Pod Bin-Packing Optimization platform. It uses **Gemini 2.5 Flash** to compile natural-language DevOps SLO directives into strict, validated JSON policy schemas, and **Google OR-Tools (CP-SAT)** inside a single **Python FastAPI** service to deterministically pack microservice pods onto heterogeneous AWS Spot, On-Demand, and Graviton (ARM64) instances—slashing simulated cloud compute bills by 40%–60% with zero SLO violations.

## Core Value

**Deterministic, policy-compliant pod bin-packing in under 3 seconds per solve, running within a $0 / 512 MB RAM single-backend deployment.**

## Requirements

### Validated

(None yet — greenfield project)

### Active

- [ ] **REQ-01**: Single Python FastAPI backend (`<= 90 MB` idle RAM) serving REST, SSE streaming, OR-Tools CP-SAT solver, and Gemini 2.5 Flash policy compiler
- [ ] **REQ-02**: Realistic K8s cluster telemetry & AWS EC2 pricing matrix simulator (500+ pods, 35+ heterogeneous node profiles: c5, m5, c6g Graviton, Spot vs On-Demand, multi-AZ)
- [ ] **REQ-03**: Exact CP-SAT bin-packing solver enforcing CPU/Memory capacity, Spot tolerance, ARM64/x86_64 architecture match, $O(N)$ grouped Pod Anti-Affinity, Cross-AZ minimization, and dynamic `ClusterPolicy` constraints
- [ ] **REQ-04**: Gemini 2.5 Flash natural-language SLO policy compiler using strict `response_schema` (Pydantic), normalized prompt caching, and deterministic fallback parser
- [ ] **REQ-05**: Neon Serverless Postgres persistence (pooled `-pooler` connection, SQLAlchemy async + `asyncpg`, `pool_size=3`) for cluster snapshots, policies, and optimization runs
- [ ] **REQ-06**: Async bounded worker queue + Server-Sent Events (SSE) progress streaming so concurrent solves never starve the event loop or exceed 512 MB RAM
- [ ] **REQ-07**: Interactive React 18 + TypeScript + Tailwind dashboard (Node Packing Grid, Before/After Cost Gauge, Natural Language Policy Bar, Live Diff)
- [ ] **REQ-08**: $0 production deployment (Cloudflare Pages / Vercel for frontend, Render/Fly 512 MB container for FastAPI, Neon Postgres) + load/stress test suite

### Out of Scope

- **Java / JVM / Timefold runtime** — Eliminated to keep idle RAM under 90 MB on 512 MB free-tier containers and avoid dual-backend cold starts.
- **Live AWS EKS cluster mutation in v1** — v1 uses a high-fidelity simulated K8s cluster & AWS pricing matrix so it can run safely at $0 without paid AWS accounts.
- **Upstash Redis for per-tick diffs** — Replaced by in-process `asyncio` + `cachetools` LRU cache + SSE to avoid exhausting the 10k/day free-tier command cap.

## Context

- **Timeline:** 6 phases over ~30–45 days.
- **Architecture:** Single-process modular monolith (FastAPI + OR-Tools C++ bindings + Gemini REST/SDK + Neon Postgres) designed to scale cleanly to async worker pools later.
- **Reference Docs:** Full HLD, LLD, and optimization rules live in `.planning/ARCHITECTURE.md`.

## Constraints

- **Tech Stack**: React 18 (Vite + TS + Tailwind) + Python 3.12 + FastAPI + Google OR-Tools (CP-SAT) + Gemini 2.5 Flash + Neon Postgres.
- **Memory Budget**: Container RSS must stay `< 350 MB` under concurrent solves (512 MB hard container limit).
- **Solver Latency**: Bounded `max_time_in_seconds = 3.0` for 500-pod topologies.
- **Cost**: $0.00/month infrastructure cost.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Replace Java + Timefold with Python + OR-Tools CP-SAT | Eliminates JVM ~300 MB idle RAM, unifies AI + Solver in one service, provides exact optimality gaps | — Pending |
| Use SSE instead of WebSockets + Upstash Redis | Lighter one-way streaming, zero Redis command quota burn, cleaner proxy/CDN behavior | — Pending |
| Pre-prune invalid `(pod, node)` variables before CP-SAT | Shrinks search space dramatically vs runtime constraint filtering | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

---
*Last updated: 2026-11-25 after project initialization*
