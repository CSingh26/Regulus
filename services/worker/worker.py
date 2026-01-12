from __future__ import annotations

import sys
from pathlib import Path

from redis import Redis
from rq import Queue, Worker


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    api_src = root / "api" / "src"
    sys.path.insert(0, str(api_src))

    from regulus_api.core.config import get_settings

    settings = get_settings()
    connection = Redis.from_url(settings.redis_url)
    queue = Queue("default", connection=connection)
    worker = Worker([queue], connection=connection)
    worker.work()


if __name__ == "__main__":
    main()
