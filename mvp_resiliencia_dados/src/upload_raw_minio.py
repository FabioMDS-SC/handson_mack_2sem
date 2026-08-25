from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from minio_utils import get_client, ensure_bucket

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
load_dotenv(BASE / ".env")


def main() -> None:
    bucket = os.getenv("MINIO_BUCKET_RAW", "raw")
    client = get_client()
    ensure_bucket(client, bucket)

    files = [p for p in RAW.rglob("*") if p.is_file()]
    if not files:
        raise RuntimeError(f"Nenhum arquivo encontrado em {RAW}")

    for path in files:
        object_name = path.relative_to(RAW).as_posix()
        client.fput_object(bucket, object_name, str(path))
        print(f"OK s3://{bucket}/{object_name}")

    print(f"\n{len(files)} arquivos enviados para o MinIO.")


if __name__ == "__main__":
    main()
