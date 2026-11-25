from fastapi.testclient import TestClient

from app.main import app
from app.solver.baseline import generate_cluster_snapshot, run_naive_kube_scheduler


def test_simulator_is_deterministic() -> None:
    """Same seed must yield identical pod and node specs."""
    snap1 = generate_cluster_snapshot(pod_count=500, node_count=35, seed=42)
    snap2 = generate_cluster_snapshot(pod_count=500, node_count=35, seed=42)
    assert snap1.cluster_id == snap2.cluster_id
    assert snap1.pods == snap2.pods
    assert snap1.nodes == snap2.nodes


def test_naive_kube_scheduler_respects_capacity_arch_and_spot() -> None:
    """Baseline scheduler must place all 500 pods without violating hard node limits."""
    snap = generate_cluster_snapshot(pod_count=500, node_count=35, seed=42)
    result = run_naive_kube_scheduler(snap)

    assert len(result.assignments) == 500
    assert result.monthly_cost_usd > 0

    node_map = {n.id: n for n in snap.nodes}
    cpu_used = {n.id: 0 for n in snap.nodes}
    mem_used = {n.id: 0 for n in snap.nodes}

    for pod in snap.pods:
        nid = result.assignments[pod.id]
        node = node_map[nid]
        assert pod.arch == node.arch
        assert pod.spot_tolerant or not node.is_spot
        cpu_used[nid] += pod.cpu_milli
        mem_used[nid] += pod.mem_mb

    for node in snap.nodes:
        assert cpu_used[node.id] <= node.cpu_cap_milli
        assert mem_used[node.id] <= node.mem_cap_mb


def test_simulate_endpoint() -> None:
    """POST /api/v1/cluster/simulate returns 200 with 500 pods and baseline cost."""
    client = TestClient(app)
    resp = client.post("/api/v1/cluster/simulate?pods=500&nodes=35&seed=42")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["snapshot"]["pods"]) == 500
    assert len(data["snapshot"]["nodes"]) == 35
    assert data["baseline"]["monthly_cost_usd"] > 0
