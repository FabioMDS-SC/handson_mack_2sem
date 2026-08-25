from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from minio import Minio

BASE = Path(__file__).resolve().parents[1]
load_dotenv(BASE / ".env")


def _as_bool(value: str | None) -> bool:
    return str(value or "false").strip().lower() in {"1", "true", "yes", "y"}


def get_client() -> Minio:
    return Minio(
        os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINIO_ROOT_USER", "mackenzie"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD", "mackenzie123"),
        secure=_as_bool(os.getenv("MINIO_SECURE", "false")),
    )


def ensure_bucket(client: Minio, bucket: str) -> None:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


def upload_file(local_path: Path, bucket: str, object_name: str) -> None:
    client = get_client()
    ensure_bucket(client, bucket)
    client.fput_object(bucket, object_name.replace("\\", "/"), str(local_path))
