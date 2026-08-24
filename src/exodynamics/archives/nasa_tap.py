"""Small, provenance-aware NASA Exoplanet Archive TAP client."""

from __future__ import annotations

import hashlib
import io
import json
import time
import urllib.parse
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

TAP_SYNC = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"


@dataclass(frozen=True)
class Acquisition:
    archive: str
    table: str
    query: str
    target: str
    retrieval_timestamp_utc: str
    row_count: int
    source_url_or_identifier: str
    dataset_version: str
    checksum_sha256: str
    doi_reference: str
    processing_version: str
    output_path: str


class NasaTapClient:
    """Synchronous TAP client with retries and immutable acquisition manifests."""

    def __init__(self, timeout: int = 180, retries: int = 3) -> None:
        self.timeout = timeout
        self.retries = retries

    def url(self, query: str, output_format: str = "csv") -> str:
        return f"{TAP_SYNC}?{urllib.parse.urlencode({'query': query, 'format': output_format})}"

    def fetch_bytes(self, query: str, output_format: str = "csv") -> bytes:
        url = self.url(query, output_format)
        error: Exception | None = None
        for attempt in range(self.retries):
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "EXODYNAMICS/0.1"})
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    return response.read()
            except (urllib.error.URLError, TimeoutError, OSError) as exc:  # pragma: no cover
                error = exc
                time.sleep(2**attempt)
        raise RuntimeError(f"NASA TAP query failed after {self.retries} attempts") from error

    def query(self, adql: str) -> pd.DataFrame:
        return pd.read_csv(io.BytesIO(self.fetch_bytes(adql)))

    def table_columns(self, table: str) -> list[str]:
        frame = self.query(
            "select column_name from TAP_SCHEMA.columns "
            f"where table_name='{table}' order by column_index"
        )
        return frame["column_name"].astype(str).tolist()

    def acquire(
        self,
        *,
        table: str,
        adql: str,
        destination: Path,
        manifest_destination: Path,
    ) -> Acquisition:
        raw = self.fetch_bytes(adql)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        frame = pd.read_csv(io.BytesIO(raw))
        acquisition = Acquisition(
            archive="NASA Exoplanet Archive",
            table=table,
            query=adql,
            target="population survey",
            retrieval_timestamp_utc=datetime.now(UTC).isoformat(),
            row_count=len(frame),
            source_url_or_identifier=self.url(adql),
            dataset_version="live TAP response; timestamped snapshot",
            checksum_sha256=hashlib.sha256(raw).hexdigest(),
            doi_reference="10.26133/NEA12",
            processing_version="exodynamics-0.1.0",
            output_path=destination.as_posix(),
        )
        manifest_destination.parent.mkdir(parents=True, exist_ok=True)
        manifest_destination.write_text(json.dumps(asdict(acquisition), indent=2), encoding="utf-8")
        return acquisition
