"""Hardware tier detection and classification for Ollama model selection."""

import os
import platform
import subprocess
from dataclasses import dataclass
from typing import Literal

HardwareTierId = Literal["1", "2", "3", "4"]

TIER_IDS: list[HardwareTierId] = ["1", "2", "3", "4"]

TIER_LABELS: dict[HardwareTierId, str] = {
    "1": "Light local inference",
    "2": "Balanced local inference",
    "3": "Strong local inference",
    "4": "Premium local inference",
}

TIER_DESCRIPTIONS: dict[HardwareTierId, str] = {
    "1": "Modest server, prioritize responsiveness and stability, smaller models only",
    "2": "Strong general-purpose server, good day-to-day writing, balanced quality and speed",
    "3": "High-memory/VRAM server, higher-quality drafting, heavier workloads acceptable",
    "4": "Very strong server, large model usage acceptable, premium drafting prioritized",
}


@dataclass
class HardwareProfile:
    """Detected or configured hardware profile."""

    tier: HardwareTierId
    source: Literal["config", "detected"]
    total_ram_gb: float | None = None
    vram_gb: float | None = None
    cpu_cores: int | None = None
    detection_message: str | None = None


def _get_ram_gb() -> float | None:
    """Detect total RAM in GB. Cross-platform where possible."""
    try:
        import psutil
        return round(psutil.virtual_memory().total / (1024**3), 1)
    except ImportError:
        pass

    if platform.system() == "Linux":
        try:
            with open("/proc/meminfo", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        return round(kb / (1024 * 1024), 1)
        except (OSError, ValueError):
            pass

    return None


def _get_vram_gb() -> float | None:
    """Detect GPU VRAM in GB via nvidia-smi if available."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Sum if multiple GPUs
            total_mb = sum(int(x.strip().split()[0]) for x in result.stdout.strip().split("\n") if x.strip())
            return round(total_mb / 1024, 1)
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass
    return None


def _classify_tier_from_profile(ram_gb: float | None, vram_gb: float | None) -> HardwareTierId:
    """Classify tier from RAM/VRAM. Prefer VRAM for GPU-heavy workloads."""
    effective = vram_gb if vram_gb and vram_gb >= 4 else ram_gb
    if effective is None:
        return "1"  # Unknown = conservative
    if effective >= 48:
        return "4"
    if effective >= 24:
        return "3"
    if effective >= 12:
        return "2"
    return "1"


def get_hardware_tier(configured_tier: str | None = None) -> HardwareProfile:
    """
    Get hardware tier. Uses OLLAMA_HARDWARE_TIER if set, else auto-detects.
    Returns HardwareProfile with tier, source, and optional detection details.
    """
    if configured_tier and str(configured_tier).strip() in TIER_IDS:
        return HardwareProfile(
            tier=str(configured_tier).strip(),
            source="config",
            detection_message="Tier set via OLLAMA_HARDWARE_TIER",
        )

    ram_gb = _get_ram_gb()
    vram_gb = _get_vram_gb()
    cpu_cores = os.cpu_count()

    tier = _classify_tier_from_profile(ram_gb, vram_gb)
    msg_parts = []
    if ram_gb is not None:
        msg_parts.append(f"{ram_gb} GB RAM")
    if vram_gb is not None:
        msg_parts.append(f"{vram_gb} GB VRAM")
    if msg_parts:
        msg = f"Auto-detected from {', '.join(msg_parts)}"
    else:
        msg = "Auto-detected (limited info, defaulting to Tier 1)"

    return HardwareProfile(
        tier=tier,
        source="detected",
        total_ram_gb=ram_gb,
        vram_gb=vram_gb,
        cpu_cores=cpu_cores,
        detection_message=msg,
    )
