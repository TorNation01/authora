"""Worker entry point - processes jobs from Redis queues."""

import asyncio
import os
import sys
from pathlib import Path

# Add api to path for shared code
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "api"))

# Set default env for worker
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")


async def run_export_job(payload: dict) -> None:
    """Process export job."""
    # Placeholder - would call export engine, store to storage, update export_jobs
    print(f"Export job: {payload}")


async def process_queue(queue_name: str) -> None:
    """Process jobs from queue. Uses Redis BRPOP or BullMQ."""
    import redis.asyncio as redis

    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    r = redis.from_url(url)
    key = f"authora:queue:{queue_name}"

    while True:
        try:
            result = await r.brpop(key, timeout=30)
            if result:
                _, data = result
                import json
                payload = json.loads(data)
                job_type = payload.get("type", "")
                if job_type == "export.generate":
                    await run_export_job(payload.get("payload", {}))
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)


async def main() -> None:
    """Run worker."""
    print("AUTHORA Worker starting...")
    await process_queue("export")


if __name__ == "__main__":
    asyncio.run(main())
