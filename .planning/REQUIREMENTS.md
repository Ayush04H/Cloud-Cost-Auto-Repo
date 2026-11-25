# Requirements: CloudCost-Autopilot

## v1.0 Scope

### Core Solver & Domain
- **SOLV-01**: Define immutable/lean `PodSpec`, `NodeSpec`, `ClusterPolicy`, and `PackingResult` Pydantic v2 models using integer micro-dollars (`hourly_price_micros`) and integer millicores/MB.
- **SOLV-02**: Implement CP-SAT bin-packing solver with pre-pruned `(pod, node)` boolean variables for `spot_tolerant`, `arch`, and `allowed_zones`.
- **SOLV-03**: Enforce hard constraints: exact single-node assignment, CPU capacity, Memory capacity, $O(N)$ grouped Pod Anti-Affinity (`sum <= 1` per `replica_group_id`), and `spot_allocation_ratio`.
- **SOLV-04**: Enforce soft objectives: minimize total hourly node cost + penalize cross-AZ service spread.
- **SOLV-05**: Bound solver execution (`max_time_in_seconds=3.0`, `num_search_workers=2`) and run inside a bounded `ProcessPoolExecutor` / `ThreadPoolExecutor` (`max_workers=2`) so FastAPI's async loop never blocks.

### AI Policy Compiler
- **AI-01**: Compile natural-language SLO directives into `ClusterPolicy` via Gemini 2.5 Flash using `response_schema=ClusterPolicy`.
- **AI-02**: Cache compiled policies by normalized SHA-256 prompt hash in memory + Postgres to stay well within Gemini's 15 RPM free limit.
- **AI-03**: Provide a deterministic keyword/regex fallback parser if Gemini is rate-limited or offline.

### API, Persistence & Streaming
- **API-01**: Async Neon Postgres integration (`asyncpg` + SQLAlchemy 2.0, `-pooler` URL, `pool_size=3`, `max_overflow=2`).
- **API-02**: `POST /api/v1/optimize` returns `202 Accepted` with `job_id`; `GET /api/v1/optimize/{job_id}/stream` streams progress and final packing diff via SSE.
- **API-03**: In-memory TTL cache (`cachetools`) for AWS EC2 pricing profiles and baseline naive `kube-scheduler` simulation.

### Frontend Dashboard
- **UI-01**: Interactive Node Packing Grid showing EC2 instances (`c6g.xlarge`, `m5.large`, etc.), Spot/On-Demand badges, and pod blocks with CPU/Memory fill bars.
- **UI-02**: Before vs. After Cost Optimization Meter (Naive `kube-scheduler` vs. OR-Tools CP-SAT) with monthly savings % and optimality status.
- **UI-03**: Natural Language Policy Input Bar with example presets, live compiled JSON preview, and SSE solve progress indicator.

### Quality, Testing & Deployment
- **OPS-01**: Unit & property tests (0 capacity/anti-affinity/arch violations across 50+ randomized 500-pod stress runs).
- **OPS-02**: Memory profiling verifying RSS `< 350 MB` under load.
- **OPS-03**: Multi-stage slim Docker build + $0 deploy to Render/Fly.io (backend) + Cloudflare Pages/Vercel (frontend).
