import random
import time
import uuid

from app.domain.pricing import AVAILABILITY_ZONES, EC2_CATALOG, HOURS_PER_MONTH
from app.domain.schemas import ClusterSnapshot, NodeSpec, PackingResult, PodSpec

_SERVICES: tuple[tuple[str, bool, bool], ...] = (
    # (service_name, spot_tolerant, requires_anti_affinity)
    ("auth-service", False, True),
    ("payments-api", False, True),
    ("checkout-service", False, True),
    ("catalog-worker", True, False),
    ("analytics-ingest", True, False),
    ("image-resizer", True, False),
    ("notification-fanout", True, False),
    ("search-indexer", True, True),
)


def generate_cluster_snapshot(
    pod_count: int = 500,
    node_count: int = 35,
    seed: int = 42,
    tenant_id: str = "demo",
) -> ClusterSnapshot:
    """Deterministically generate a heterogeneous K8s cluster & workload."""
    rng = random.Random(seed)
    nodes: list[NodeSpec] = []

    # Ensure sufficient On-Demand capacity across both architectures
    od_x86 = [
        p for p in EC2_CATALOG
        if not p.is_spot and p.arch == "X86_64" and p.cpu_cap_milli >= 8000
    ]
    od_arm = [
        p for p in EC2_CATALOG
        if not p.is_spot and p.arch == "ARM64" and p.cpu_cap_milli >= 8000
    ]
    spot_profiles = [p for p in EC2_CATALOG if p.is_spot]

    on_demand_target = max(6, (node_count * 3) // 5)  # ~60% On-Demand, ~40% Spot
    for i in range(node_count):
        if i < on_demand_target:
            if i % 2 == 0:
                profile = od_x86[i % len(od_x86)]
            else:
                profile = od_arm[i % len(od_arm)]
        else:
            profile = spot_profiles[i % len(spot_profiles)]
        az = AVAILABILITY_ZONES[i % len(AVAILABILITY_ZONES)]
        nodes.append(
            NodeSpec(
                id=f"node-{i + 1:02d}-{az[-1]}",
                instance_type=profile.instance_type,
                cpu_cap_milli=profile.cpu_cap_milli,
                mem_cap_mb=profile.mem_cap_mb,
                is_spot=profile.is_spot,
                hourly_price_micros=profile.hourly_price_micros,
                az=az,
                arch=profile.arch,
            )
        )

    pods: list[PodSpec] = []
    for i in range(pod_count):
        svc_name, spot_tolerant, anti_affinity = _SERVICES[i % len(_SERVICES)]
        arch = "ARM64" if rng.random() < 0.45 else "X86_64"
        cpu_milli = rng.choice((100, 150, 200, 250, 300))
        mem_mb = rng.choice((128, 256, 384, 512))
        replica_group = f"rg-{svc_name}-{i // 8}" if anti_affinity else None
        pods.append(
            PodSpec(
                id=f"pod-{i + 1:04d}",
                service_name=svc_name,
                cpu_milli=cpu_milli,
                mem_mb=mem_mb,
                spot_tolerant=spot_tolerant,
                arch=arch,
                replica_group_id=replica_group,
            )
        )

    cluster_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cluster-{seed}-{pod_count}-{node_count}"))
    return ClusterSnapshot(
        cluster_id=cluster_id,
        tenant_id=tenant_id,
        pods=pods,
        nodes=nodes,
    )


def run_naive_kube_scheduler(snapshot: ClusterSnapshot) -> PackingResult:
    """Simulate greedy single-pod kube-scheduler (spreads pods across On-Demand nodes)."""
    start = time.perf_counter()
    remaining_cpu = {n.id: n.cpu_cap_milli for n in snapshot.nodes}
    remaining_mem = {n.id: n.mem_cap_mb for n in snapshot.nodes}
    node_map = {n.id: n for n in snapshot.nodes}

    assignments: dict[str, str] = {}
    active_nodes: set[str] = set()
    spot_pods = 0

    for pod in snapshot.pods:
        # Naive kube-scheduler LeastRequestedPriority spreads pods onto On-Demand/least-full nodes
        candidates = [
            n
            for n in snapshot.nodes
            if n.arch == pod.arch
            and (pod.spot_tolerant or not n.is_spot)
            and remaining_cpu[n.id] >= pod.cpu_milli
            and remaining_mem[n.id] >= pod.mem_mb
        ]
        if not candidates:
            raise ValueError(f"Insufficient capacity for pod {pod.id} in naive scheduler")

        # Prefer least-utilized (spread) and non-spot first, mimicking unoptimized K8s clusters
        chosen = max(
            candidates,
            key=lambda n: (
                0 if n.is_spot else 1,
                remaining_cpu[n.id] / n.cpu_cap_milli + remaining_mem[n.id] / n.mem_cap_mb,
            ),
        )
        assignments[pod.id] = chosen.id
        remaining_cpu[chosen.id] -= pod.cpu_milli
        remaining_mem[chosen.id] -= pod.mem_mb
        active_nodes.add(chosen.id)
        if chosen.is_spot:
            spot_pods += 1

    total_hourly_micros = sum(node_map[nid].hourly_price_micros for nid in active_nodes)
    monthly_cost_usd = round((total_hourly_micros * HOURS_PER_MONTH) / 1_000_000, 2)
    elapsed_ms = max(1, int((time.perf_counter() - start) * 1000))

    return PackingResult(
        assignments=assignments,
        active_node_ids=sorted(active_nodes),
        monthly_cost_usd=monthly_cost_usd,
        spot_pod_ratio=round(spot_pods / max(1, len(snapshot.pods)), 4),
        solve_ms=elapsed_ms,
        status="BASELINE_GREEDY",
    )
