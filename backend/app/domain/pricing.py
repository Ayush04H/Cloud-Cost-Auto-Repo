from dataclasses import dataclass

from app.domain.schemas import Arch


@dataclass(frozen=True, slots=True)
class EC2Profile:
    """Static AWS EC2 instance profile with precomputed micro-USD pricing."""

    instance_type: str
    cpu_cap_milli: int
    mem_cap_mb: int
    is_spot: bool
    hourly_price_micros: int  # 1 USD = 1_000_000 micros
    arch: Arch


# Representative us-east-1 On-Demand & Spot pricing (micro-USD/hour)
EC2_CATALOG: tuple[EC2Profile, ...] = (
    # x86_64 On-Demand
    EC2Profile("c5.large", 2000, 4096, False, 85_000, "X86_64"),
    EC2Profile("c5.xlarge", 4000, 8192, False, 170_000, "X86_64"),
    EC2Profile("c5.2xlarge", 8000, 16384, False, 340_000, "X86_64"),
    EC2Profile("m5.large", 2000, 8192, False, 96_000, "X86_64"),
    EC2Profile("m5.xlarge", 4000, 16384, False, 192_000, "X86_64"),
    EC2Profile("m5.2xlarge", 8000, 32768, False, 384_000, "X86_64"),
    # x86_64 Spot (~68-72% discount)
    EC2Profile("c5.large", 2000, 4096, True, 26_000, "X86_64"),
    EC2Profile("c5.xlarge", 4000, 8192, True, 52_000, "X86_64"),
    EC2Profile("m5.large", 2000, 8192, True, 30_000, "X86_64"),
    EC2Profile("m5.xlarge", 4000, 16384, True, 60_000, "X86_64"),
    # ARM64 Graviton On-Demand (~20% cheaper than x86)
    EC2Profile("c6g.large", 2000, 4096, False, 68_000, "ARM64"),
    EC2Profile("c6g.xlarge", 4000, 8192, False, 136_000, "ARM64"),
    EC2Profile("c6g.2xlarge", 8000, 16384, False, 272_000, "ARM64"),
    EC2Profile("m6g.large", 2000, 8192, False, 77_000, "ARM64"),
    # ARM64 Graviton Spot (~72% discount off Graviton On-Demand)
    EC2Profile("c6g.large", 2000, 4096, True, 19_000, "ARM64"),
    EC2Profile("c6g.xlarge", 4000, 8192, True, 38_400, "ARM64"),
    EC2Profile("m6g.large", 2000, 8192, True, 22_000, "ARM64"),
)

AVAILABILITY_ZONES: tuple[str, ...] = ("us-east-1a", "us-east-1b", "us-east-1c")
HOURS_PER_MONTH: int = 730
