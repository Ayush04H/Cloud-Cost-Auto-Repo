import os

import psutil
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.core.cache import cluster_cache
from app.core.config import get_settings
from app.domain.schemas import ClusterSnapshot, PackingResult
from app.solver.baseline import generate_cluster_snapshot, run_naive_kube_scheduler

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Kubernetes FinOps & Pod Bin-Packing Optimization Engine",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_rss_mb() -> float:
    """Return current process resident set size in megabytes."""
    process = psutil.Process(os.getpid())
    return round(process.memory_info().rss / (1024 * 1024), 2)


@app.get("/api/v1/health")
async def health_check() -> dict[str, object]:
    """Lightweight health check reporting process RSS memory."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "rss_mb": get_rss_mb(),
    }


@app.post("/api/v1/cluster/simulate")
async def simulate_cluster(
    pods: int = Query(default=500, ge=10, le=2000),
    nodes: int = Query(default=35, ge=3, le=200),
    seed: int = Query(default=42),
) -> dict[str, ClusterSnapshot | PackingResult]:
    """Generate a deterministic cluster snapshot and naive kube-scheduler baseline."""
    snapshot = generate_cluster_snapshot(pod_count=pods, node_count=nodes, seed=seed)
    baseline = run_naive_kube_scheduler(snapshot)
    cluster_cache[snapshot.cluster_id] = snapshot
    return {"snapshot": snapshot, "baseline": baseline}
