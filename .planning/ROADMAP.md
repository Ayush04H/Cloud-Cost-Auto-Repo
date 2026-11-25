# Roadmap: CloudCost-Autopilot

## Overview

A 6-phase, ~30–45 day build plan taking **CloudCost-Autopilot** from an empty repository to a $0-deployed, memory-optimized (<350 MB RSS) Kubernetes FinOps & Pod Bin-Packing platform powered by **React 18 + Python FastAPI + Google OR-Tools (CP-SAT) + Gemini 2.5 Flash + Neon Postgres**.

## Phases

- [ ] **Phase 1: Foundation, Project Scaffold & Telemetry Simulator** (Days 1–5) — Repo layout, FastAPI + Vite/React setup, lean Pydantic domain models, EC2 pricing matrix, and 500-pod naive `kube-scheduler` baseline simulator.
- [ ] **Phase 2: OR-Tools CP-SAT Bin-Packing Engine** (Days 6–14) — Exact mathematical model, pre-pruned variables, $O(N)$ anti-affinity, Spot/ARM64/Cross-AZ constraints, and 50-seed stress tests.
- [ ] **Phase 3: Gemini 2.5 Flash Policy Compiler & Caching** (Days 15–20) — Structured output (`response_schema`), SHA-256 prompt cache, token-bucket rate limiter, and deterministic fallback parser.
- [ ] **Phase 4: Neon Postgres Persistence & Async SSE Job Pipeline** (Days 21–27) — Async SQLAlchemy + `asyncpg` pooled schema, bounded worker pool, `202 Accepted` job queue, and SSE live streaming.
- [ ] **Phase 5: Interactive React 18 FinOps Dashboard** (Days 28–36) — Node Packing Grid, Before/After Cost Gauge, Natural Language Policy Bar, and SSE real-time updates.
- [ ] **Phase 6: Memory Profiling, Load Testing & $0 Production Deploy** (Days 37–45) — RSS `< 350 MB` verification, multi-stage Docker build, Neon + Render/Fly + Cloudflare Pages deployment, and documentation.

## Phase Details

### Phase 1: Foundation, Project Scaffold & Telemetry Simulator
**Goal**: Establish the monorepo structure, strict coding/linting rules, lean Pydantic domain models, AWS EC2 pricing catalog, and a realistic 500-pod / 35-node naive `kube-scheduler` baseline simulator.
**Estimated Time**: 4–5 days
**Depends on**: Nothing (first phase)
**Requirements**: [REQ-01, REQ-02, SOLV-01, SCALE-01]
**Success Criteria** (what must be TRUE):
  1. `uvicorn app.main:app` starts cleanly in `< 2s` with `< 65 MB` idle RSS and `/health` returns `200 OK`.
  2. Simulator deterministically generates 500 pods + 35 heterogeneous nodes (`c5`, `m5`, `c6g`, Spot/On-Demand) and computes the naive `kube-scheduler` placement + monthly baseline cost.
  3. React 18 + Vite + Tailwind + TypeScript frontend builds cleanly and proxies `/api` to FastAPI locally.
**Plans**: 2 plans

Plans:
- [ ] 01-01: Monorepo scaffold, Protocol seams (JobBus, BlobStore, RateLimiter), FastAPI health, React 18 shell
- [ ] 01-02: Lean Pydantic domain models, EC2 micro-dollar catalog, 500-pod simulator & naive baseline

### Phase 2: OR-Tools CP-SAT Bin-Packing Engine
**Goal**: Build the deterministic CP-SAT optimization engine with variable pre-pruning, integer micro-dollar arithmetic, $O(N)$ anti-affinity grouping, and dynamic `ClusterPolicy` enforcement.
**Estimated Time**: 7–9 days
**Depends on**: Phase 1
**Requirements**: [REQ-03, SOLV-02, SOLV-03, SOLV-04, SOLV-05, OPS-01]
**Success Criteria** (what must be TRUE):
  1. Solver packs 500 pods across 35 nodes in `<= 3.0s` achieving `>= 40%` cost reduction vs. the naive baseline.
  2. Stress test across 50 randomized cluster seeds passes with `0` CPU, Memory, Spot, Architecture, or Anti-Affinity violations.
  3. Solver runs in a bounded worker (`max_workers=2`) without blocking FastAPI's asyncio event loop.
**Plans**: TBD

### Phase 3: Gemini 2.5 Flash Policy Compiler & Caching
**Goal**: Compile natural-language DevOps SLOs into validated `ClusterPolicy` JSON via Gemini 2.5 Flash with `response_schema`, prompt-hash caching, and a deterministic fallback.
**Estimated Time**: 5–6 days
**Depends on**: Phase 2
**Requirements**: [REQ-04, AI-01, AI-02, AI-03]
**Success Criteria** (what must be TRUE):
  1. Natural-language prompts compile into 100% schema-valid `ClusterPolicy` objects and feed directly into the CP-SAT solver.
  2. Repeated or normalized prompts hit the cache (`0` redundant Gemini calls).
  3. Simulated Gemini `429` / timeout triggers the deterministic fallback parser cleanly without failing the request.
**Plans**: TBD

### Phase 4: Neon Postgres Persistence & Async SSE Job Pipeline
**Goal**: Persist clusters, policies, and optimization runs in Neon Serverless Postgres and stream solve progress via `202 Accepted` + Server-Sent Events (SSE).
**Estimated Time**: 6–7 days
**Depends on**: Phase 3
**Requirements**: [REQ-05, REQ-06, API-01, API-02, API-03]
**Success Criteria** (what must be TRUE):
  1. Alembic migrations run cleanly against Neon Postgres using the `-pooler` endpoint with `pool_size=3`.
  2. `POST /api/v1/optimize` returns `202` immediately and `GET /api/v1/optimize/{job_id}/stream` streams status transitions (`queued -> compiling -> solving -> completed`).
  3. 20 concurrent optimization requests queue cleanly without OOM or DB connection exhaustion.
**Plans**: TBD

### Phase 5: Interactive React 18 FinOps Dashboard
**Goal**: Build the interactive UI with Node Packing Grid, Cost Optimization Meter, Natural Language Policy Bar, and live SSE diff updates.
**Estimated Time**: 7–9 days
**Depends on**: Phase 4
**Requirements**: [REQ-07, UI-01, UI-02, UI-03]
**Success Criteria** (what must be TRUE):
  1. User can type a natural-language SLO (or pick a preset), watch SSE progress, and see the packed EC2 grid update live.
  2. Dashboard displays Before vs. After monthly cost, savings percentage, Spot/Graviton breakdown, and CP-SAT optimality status.
  3. UI handles 500+ pod blocks smoothly (memoized rendering, zero layout lag).
**Plans**: TBD

### Phase 6: Memory Profiling, Load Testing & $0 Production Deploy
**Goal**: Verify `< 350 MB` peak RSS under load, package slim Docker image, deploy to $0 cloud platforms, and finalize README/interview metrics.
**Estimated Time**: 5–9 days
**Depends on**: Phase 5
**Requirements**: [REQ-08, OPS-02, OPS-03]
**Success Criteria** (what must be TRUE):
  1. Peak container RSS stays `< 350 MB` during concurrent 500-pod solves.
  2. Live public URLs work end-to-end on $0 tiers (Cloudflare Pages/Vercel + Render/Fly + Neon + Gemini).
  3. Automated test suite + Locust/k6 load test report passes and is documented.
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation, Scaffold & Simulator | 0/TBD | Not started | - |
| 2. OR-Tools CP-SAT Engine | 0/TBD | Not started | - |
| 3. Gemini Policy Compiler | 0/TBD | Not started | - |
| 4. Neon Postgres & Async SSE | 0/TBD | Not started | - |
| 5. React 18 FinOps Dashboard | 0/TBD | Not started | - |
| 6. Profiling & $0 Production Deploy | 0/TBD | Not started | - |
