# CloudCost-Autopilot: HLD, LLD & Engineering Rules

## 1. High-Level Design (HLD)

```text
┌──────────────────────────────────────────────────────────────────────┐
│               React 18 + TypeScript + Tailwind (Vite)                │
│         Hosted on Cloudflare Pages / Vercel ($0 Static CDN)          │
└───────────────────┬──────────────────────────────────┬───────────────┘
                    │ HTTPS REST (POST /optimize)      │ SSE (GET /stream)
                    ▼                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│              Python 3.12 + FastAPI Modular Monolith                  │
│             Hosted on Render / Fly.io (512 MB RAM, $0)               │
│                                                                      │
│  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐  │
│  │  API & SSE Layer │   │  Policy Compiler │   │  Bounded Worker  │  │
│  │  (AsyncIO,       │──▶│  (Gemini 2.5     │──▶│  Pool (max=2)    │  │
│  │   Rate Limiter)  │   │   + SHA256 Cache)│   │  OR-Tools CP-SAT │  │
│  └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘  │
│           │                      │                      │            │
│           ▼                      ▼                      ▼            │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │         In-Memory LRU/TTL Cache (cachetools: EC2 Rates, Jobs)  │  │
│  └───────────────────────────────┬────────────────────────────────┘  │
└──────────────────────────────────┼───────────────────────────────────┘
                                   │ asyncpg (pool_size=3, -pooler)
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                Neon Serverless Postgres ($0, 0.5 GB)                 │
│        Tables: clusters, policies, optimization_runs                 │
└──────────────────────────────────────────────────────────────────────┘
```

### Request & Data Flow
1. **Cluster Load / Simulation:** FastAPI loads EC2 pricing profiles from an in-memory TTL cache (`cachetools`) and generates/fetches a 500-pod, 35-node cluster snapshot + naive `kube-scheduler` baseline.
2. **Submit Optimization (`POST /api/v1/optimize`):**
   - Validates request & checks token-bucket rate limit.
   - Normalizes prompt -> checks SHA-256 policy cache -> calls Gemini 2.5 Flash (`response_schema=ClusterPolicy`) only on cache miss (with deterministic regex fallback on 429/error).
   - Enqueues solve job into bounded `asyncio.Queue` / `ThreadPoolExecutor(max_workers=2)` and immediately returns `202 Accepted` with `job_id`.
3. **Stream Progress (`GET /api/v1/optimize/{job_id}/stream`):**
   - Streams SSE events: `queued` -> `compiling_policy` -> `solving` -> `completed` (with full packing diff, savings %, and optimality status).
4. **Persistence:** Completed `optimization_runs` and `policies` are persisted asynchronously to Neon Postgres.

---

## 2. Low-Level Design (LLD)

### A. Directory Structure
```text
cloudcost-autopilot/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI lifespan, CORS, routers
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic BaseSettings (env vars, limits)
│   │   │   ├── cache.py             # TTLCache for EC2 rates, policies, jobs
│   │   │   └── rate_limit.py        # Lightweight in-memory token bucket
│   │   ├── domain/
│   │   │   ├── schemas.py           # PodSpec, NodeSpec, ClusterPolicy, PackingResult
│   │   │   └── pricing.py           # AWS EC2 catalog (c5, m5, c6g) in micro-USD
│   │   ├── solver/
│   │   │   ├── baseline.py          # Greedy kube-scheduler simulator
│   │   │   ├── cpsat_solver.py      # OR-Tools CP-SAT model + variable pruning
│   │   │   └── worker.py            # Bounded executor + SSE event emitter
│   │   ├── ai/
│   │   │   ├── policy_compiler.py   # Gemini 2.5 Flash + response_schema
│   │   │   └── fallback_parser.py   # Deterministic regex/keyword fallback
│   │   └── db/
│   │       ├── session.py           # asyncpg engine (pool_size=3, max_overflow=2)
│   │       └── models.py            # SQLAlchemy 2.0 ORM tables
│   ├── tests/
│   │   ├── test_solver_constraints.py
│   │   └── test_policy_compiler.py
│   ├── Dockerfile                   # Multi-stage python:3.12-slim
│   └── pyproject.toml
└── frontend/
    ├── src/
    │   ├── api/client.ts            # Typed fetch + EventSource SSE hook
    │   ├── components/
    │   │   ├── NodeGrid.tsx         # Memoized EC2 node + pod block grid
    │   │   ├── CostGauge.tsx        # Before vs After monthly cost & savings
    │   │   └── PolicyBar.tsx        # Natural language prompt + JSON preview
    │   └── App.tsx
    └── package.json
```

### B. Database Schema (Neon Postgres)
- `clusters` (`id UUID PK`, `name TEXT`, `pod_count INT`, `node_count INT`, `snapshot_json JSONB`, `created_at TIMESTAMPTZ`)
- `policies` (`prompt_hash CHAR(64) PK`, `raw_prompt TEXT`, `compiled_json JSONB`, `source TEXT` [`gemini`|`fallback`], `created_at TIMESTAMPTZ`)
- `optimization_runs` (`id UUID PK`, `cluster_id UUID FK`, `policy_hash CHAR(64)`, `status TEXT`, `baseline_monthly_usd NUMERIC(10,2)`, `optimized_monthly_usd NUMERIC(10,2)`, `savings_pct NUMERIC(5,2)`, `solve_ms INT`, `solver_status TEXT`, `result_json JSONB`, `created_at TIMESTAMPTZ`)

### C. Core API Contracts
- `GET /api/v1/health` -> `{"status": "ok", "rss_mb": 74.2}`
- `POST /api/v1/cluster/simulate?pods=500&nodes=35&seed=42` -> returns cluster + naive baseline cost
- `POST /api/v1/optimize` -> body `{cluster_id, prompt}` -> `202 {"job_id": "..."}`
- `GET /api/v1/optimize/{job_id}/stream` -> `text/event-stream` emitting `progress` and `result` events

---

## 3. Coding & Optimization Rules (Mandatory)

### Rule 1: Memory Discipline (< 350 MB Peak RSS)
- **No heavy data libraries:** Never import `pandas`, `numpy`, `scipy`, or `langchain`. Use pure Python dataclasses/`__slots__`, Pydantic v2, and `ortools`.
- **Single worker process:** Run `uvicorn app.main:app --workers 1` on 512 MB containers; concurrency is handled by `asyncio` + bounded `ThreadPoolExecutor(max_workers=2)` (OR-Tools C++ releases the GIL!).
- **Explicit cleanup:** Drop `CpModel` and `CpSolver` references immediately after extracting `PackingResult` so C++ memory is freed before the next job.

### Rule 2: CP-SAT Modeling Discipline
- **Integer-only arithmetic:** Represent all costs in `hourly_price_micros: int` (`$0.0384 -> 38400`) and resources in `cpu_milli: int`, `mem_mb: int`. Never use floats in `CpModel`.
- **Pre-prune invalid variables:** Never add a `BoolVar x[p, n]` if `node.az not in policy.allowed_zones`, `not pod.spot_tolerant and node.is_spot`, or `pod.arch != node.arch`.
- **$O(N)$ Anti-Affinity:** Group pods by `replica_group_id` per node and emit `sum(x[p, n]) <= 1`. Never write $O(N^2)$ pairwise constraints.
- **Strict time bounds:** Always set `solver.parameters.max_time_in_seconds = 3.0` and `num_search_workers = 2`.

### Rule 3: Async & Database Discipline
- **Never block the event loop:** All CP-SAT solves and synchronous SDK calls run via `asyncio.to_thread` / bounded executor.
- **Neon connection limits:** Always use Neon's `-pooler` URL, `pool_size=3`, `max_overflow=2`, `pool_pre_ping=True`, `pool_recycle=300`.
- **Never query DB inside solve loops:** Fetch snapshot once before solving; persist result once after solving.

### Rule 4: AI & Rate-Limit Discipline
- **Always use Structured Outputs:** Pass `response_schema=ClusterPolicy` to Gemini 2.5 Flash.
- **Cache before calling:** Normalize prompt (`strip().lower()` + collapse whitespace), SHA-256 hash, check cache before hitting Gemini.
- **Graceful degradation:** If Gemini returns `429` or times out (`> 4s`), transparently fall back to `fallback_parser.py` and tag `source="fallback"`.

### Rule 5: Frontend Rendering Discipline
- **Memoize grid nodes:** Wrap `NodeCard` in `React.memo` so SSE status ticks don't re-render 35 node cards × 500 pod blocks unnecessarily.
- **Clean SSE lifecycle:** Always close `EventSource` on unmount or completion.
