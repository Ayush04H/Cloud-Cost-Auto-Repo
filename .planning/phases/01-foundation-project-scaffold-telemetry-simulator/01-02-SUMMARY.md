# Plan 01-02 Summary: Domain Models, EC2 Catalog & Telemetry Simulator

- **Completed:** 2026-11-25
- **Key Deliverables:**
  - `backend/app/domain/schemas.py` defines `PodSpec`, `NodeSpec`, `ClusterPolicy`, `ClusterSnapshot`, and `PackingResult` using integer millicores, MB, and micro-dollars.
  - `backend/app/domain/pricing.py` defines heterogeneous AWS EC2 `c5`, `m5`, `c6g`, and `m6g` Spot/On-Demand profiles (`hourly_price_micros`).
  - `backend/app/solver/baseline.py` implements deterministic `generate_cluster_snapshot` and greedy `run_naive_kube_scheduler`.
  - `POST /api/v1/cluster/simulate` wired in `backend/app/main.py`.
- **Verification:** `pytest backend/tests -v` (4/4 passed in 0.31s); `ruff check` passed with 0 errors.
