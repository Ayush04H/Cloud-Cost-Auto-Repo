from typing import Literal

from pydantic import BaseModel, Field

Arch = Literal["ARM64", "X86_64"]


class PodSpec(BaseModel):
    """Immutable-style pod resource & scheduling specification."""

    id: str
    service_name: str
    cpu_milli: int = Field(gt=0)
    mem_mb: int = Field(gt=0)
    spot_tolerant: bool
    arch: Arch
    replica_group_id: str | None = None


class NodeSpec(BaseModel):
    """Heterogeneous EC2 node profile using integer micro-dollars."""

    id: str
    instance_type: str
    cpu_cap_milli: int = Field(gt=0)
    mem_cap_mb: int = Field(gt=0)
    is_spot: bool
    hourly_price_micros: int = Field(gt=0)
    az: str
    arch: Arch


class ClusterPolicy(BaseModel):
    """Validated SLO policy compiled from natural language or defaults."""

    max_monthly_budget_usd: float = Field(gt=0)
    allowed_zones: list[str] = Field(min_length=1)
    spot_allocation_ratio: float = Field(ge=0.0, le=1.0)
    strict_anti_affinity_services: list[str] = Field(default_factory=list)
    require_graviton_arm64: bool = False


class ClusterSnapshot(BaseModel):
    """Complete cluster state for simulation or optimization."""

    cluster_id: str
    tenant_id: str = "demo"
    pods: list[PodSpec]
    nodes: list[NodeSpec]


class PackingResult(BaseModel):
    """Placement assignments and cost summary for baseline or CP-SAT solve."""

    assignments: dict[str, str]
    active_node_ids: list[str]
    monthly_cost_usd: float
    spot_pod_ratio: float
    solve_ms: int
    status: str
