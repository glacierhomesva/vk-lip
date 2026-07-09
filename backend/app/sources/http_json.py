from __future__ import annotations

import json
from typing import Any, Iterable
from urllib.request import Request, urlopen
from urllib.parse import urlencode, urlsplit, parse_qsl, urlunsplit

from app.core.source_config import SourceSyncSettings
from app.sources.base import SourceClient, SourceRecord


class HttpJsonSourceClient(SourceClient):
    def __init__(self, settings: SourceSyncSettings):
        self.settings = settings

    def available_datasets(self) -> dict[str, bool]:
        return {
            name: config.enabled
            for name, config in self.settings.dataset_map().items()
        }

    def fetch(self, dataset_name: str) -> Iterable[SourceRecord]:
        config = self.settings.dataset_map().get(dataset_name)
        if config is None or not config.enabled or config.url is None:
            return []

        if "/query" in config.url:
            return self._fetch_arcgis_records(config.url)

        payload = self._fetch_payload(config.url)
        records = self._extract_records(payload, config.root_key)
        return [record for record in records if isinstance(record, dict)]

    def _fetch_payload(self, url: str) -> Any:
        request = Request(url, headers=self._headers())
        with urlopen(request, timeout=self.settings.timeout_seconds) as response:
            return json.load(response)

    def _fetch_arcgis_records(self, url: str) -> Iterable[SourceRecord]:
        # ArcGIS query endpoints require pagination when transfer limits are exceeded.
        split = urlsplit(url)
        params = dict(parse_qsl(split.query, keep_blank_values=True))
        if "f" not in params:
            params["f"] = "json"
        if "where" not in params:
            params["where"] = "1=1"
        if "outFields" not in params:
            params["outFields"] = "*"
        if "returnGeometry" not in params:
            params["returnGeometry"] = "false"

        offset = 0
        page_size = int(params.get("resultRecordCount") or 2000)

        while True:
            paged = dict(params)
            paged["resultOffset"] = str(offset)
            paged["resultRecordCount"] = str(page_size)
            query = urlencode(paged)
            paged_url = urlunsplit((split.scheme, split.netloc, split.path, query, split.fragment))

            request = Request(paged_url, headers=self._headers())
            with urlopen(request, timeout=self.settings.timeout_seconds) as response:
                payload = json.load(response)

            if "error" in payload:
                return []

            features = payload.get("features") or []
            if not isinstance(features, list):
                break

            for item in features:
                if not isinstance(item, dict):
                    continue
                attributes = item.get("attributes")
                properties = item.get("properties")
                if isinstance(attributes, dict):
                    yield attributes
                elif isinstance(properties, dict):
                    yield properties
                else:
                    yield item

            exceeded = bool(payload.get("exceededTransferLimit"))
            if not exceeded or len(features) < page_size:
                break

            offset += page_size

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.settings.api_key:
            headers["X-API-Key"] = self.settings.api_key
        if self.settings.bearer_token:
            headers["Authorization"] = f"Bearer {self.settings.bearer_token}"
        return headers

    def _extract_records(self, payload: Any, root_key: str | None) -> list[Any]:
        if isinstance(payload, list):
            return payload

        if not isinstance(payload, dict):
            return []

        if root_key:
            rooted = payload.get(root_key, [])
            return rooted if isinstance(rooted, list) else []

        for key in ("items", "results", "records", "data", "features"):
            value = payload.get(key)
            if isinstance(value, list):
                if key == "features":
                    extracted: list[Any] = []
                    for item in value:
                        if not isinstance(item, dict):
                            continue
                        if isinstance(item.get("attributes"), dict):
                            extracted.append(item.get("attributes"))
                        elif isinstance(item.get("properties"), dict):
                            extracted.append(item.get("properties"))
                        else:
                            extracted.append(item)
                    return extracted
                return value

        return []