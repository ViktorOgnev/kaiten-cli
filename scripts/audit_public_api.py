#!/usr/bin/env python3
"""Refresh official documentation evidence explicitly; check registry parity offline by default.

No Kaiten credentials or tenant requests are used. Snapshot hashes identify source
pages; raw HTML is kept only in the optional local download cache.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import subprocess
import time
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BASE = "https://developers.kaiten.ru"
SNAPSHOT = ROOT / "docs/public-api/contracts.json"


class Page(HTMLParser):
    """Retain text, links, and top-level table cells without executing page scripts."""

    def __init__(self, html: str):
        super().__init__()
        self.parts = []
        self.links = []
        self.sections = {}
        self.heading = None
        self.heading_parts = []
        self.section = ""
        self.skip = 0
        self.table_depth = 0
        self.row = None
        self.cell = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if self.skip:
            return
        if tag == "a":
            self.links.extend(v for k, v in attrs if k == "href")
        if re.fullmatch("h[1-6]", tag):
            self.heading = tag
            self.heading_parts = []
        if tag == "table":
            self.table_depth += 1
        if self.table_depth == 1:
            if tag == "tr":
                self.row = []
            if tag in ("td", "th"):
                self.cell = []

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1
            return
        if self.skip:
            return
        if tag == self.heading:
            self.section = "".join(self.heading_parts).strip()
            self.sections.setdefault(self.section, {"text": [], "rows": []})
            self.heading = None
        if self.table_depth == 1:
            if tag in ("td", "th") and self.cell is not None:
                if self.row is not None:
                    self.row.append("".join(self.cell).strip())
                self.cell = None
            if tag == "tr" and self.row is not None:
                self.sections.setdefault(self.section, {"text": [], "rows": []})["rows"].append(
                    self.row
                )
                self.row = None
        if tag == "table":
            self.table_depth -= 1

    def handle_data(self, data):
        if self.skip:
            return
        self.parts.append(data)
        if self.heading:
            self.heading_parts.append(data)
        else:
            self.sections.setdefault(self.section, {"text": [], "rows": []})["text"].append(data)
        if self.cell is not None:
            self.cell.append(data)


def schema_type(label: str) -> dict:
    if not isinstance(label, str):
        return {"x-documentation-type": label}
    label = label.split("Schema", 1)[0]
    parts = [x.strip().lower() for x in label.split("|")]
    types = []
    result = {}
    for part in parts:
        if part.startswith("array"):
            types.append("array")
            item = part.removeprefix("array").strip().removeprefix("of").strip().rstrip("s")
            if item in ("integer", "string", "object", "number"):
                result["items"] = {"type": item}
        elif part in ("integer", "string", "object", "number", "boolean", "null"):
            types.append(part)
        elif part == "enum":
            pass
    if types:
        result["type"] = types[0] if len(types) == 1 else types
    return result


def section_schema(section: dict | None) -> dict | None:
    if not section:
        return None
    text = "".join(section["text"])
    pos = text.find("{")
    if pos >= 0:
        try:
            value, _ = json.JSONDecoder().raw_decode(text[pos:])
            if isinstance(value, dict) and ("properties" in value or "$schema" in value):
                return value
        except ValueError:
            pass
    rows = section["rows"]
    if not rows or "Name" not in rows[0]:
        return None
    headers = rows[0]
    props = {}
    required = []
    for row in rows[1:]:
        if len(row) != len(headers):
            continue
        values = dict(zip(headers, row))
        name = re.sub(r"(required|BETA|DEPRECATED|Deprecated)", "", values["Name"]).strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9.\[\]-]*", name):
            continue
        field = schema_type(values.get("Type", ""))
        field["description"] = values.get("Description", values.get("Reference", ""))
        constraint = values.get("Constraints", "")
        if constraint:
            field["x-documentation-constraints"] = constraint
        props[name] = field
        if "required" in values["Name"]:
            required.append(name)
    return {"type": "object", "properties": props, "required": required} if props else None


def parse_page(url: str, html: str, section: str) -> dict:
    page = Page(html)
    record = {"url": url, "section": section, "sha256": hashlib.sha256(html.encode()).hexdigest()}
    endpoint = None
    method = None
    for part in page.parts:
        value = part.strip()
        if value in ("GET", "POST", "PUT", "PATCH", "DELETE"):
            method = value
        if re.match(r"https://example\.kaiten\.ru/(?:api|scim)/", value):
            endpoint = value
            break
    if endpoint and method:
        record.update(kind="http", method=method, path=urlparse(endpoint).path)
        record["request_headers"] = page.sections.get("Headers", {}).get("rows", [])
        for heading, key in [
            ("Attributes", "body"),
            ("Query", "query"),
            ("Path parameters", "path_parameters"),
        ]:
            record[key] = section_schema(page.sections.get(heading))
        record["response_tables"] = page.sections.get("Response Attributes", {}).get("rows", [])
        record["notes"] = [p.strip() for p in page.parts if "⚠" in p or "Deprecated" in p]
    else:
        expected_operation = (
            section == "REST API" and len(urlparse(url).path.strip("/").split("/")) >= 2
        ) or (section == "SCIM" and len(urlparse(url).path.strip("/").split("/")) >= 3)
        record["kind"] = "unparsed" if expected_operation else "reference"
        if expected_operation:
            record["error"] = "Expected an HTTP operation page but no endpoint could be parsed."
        record["headings"] = [s for s in page.sections if s]
    return record


def refresh(cache: Path) -> None:
    import httpx

    cache.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=30, follow_redirects=True) as client:

        def fetch(url):
            path = cache / (hashlib.sha256(url.encode()).hexdigest() + ".html")
            if path.exists():
                return path.read_text()
            for attempt in range(4):
                try:
                    response = client.get(url)
                    response.raise_for_status()
                    path.write_text(response.text)
                    return response.text
                except httpx.HTTPError:
                    if attempt == 3:
                        raise
                    time.sleep(attempt + 1)

        index = fetch(BASE + "/llms.txt")
        sources = {}
        section = ""
        for line in index.splitlines():
            if line.startswith("## "):
                section = line[3:]
            for url in re.findall(r"\]\((https://[^)]+)\)", line):
                sources[url] = section
        # llms.txt may lag the navigation. Inspect every section overview too.
        for suffix in ("/", "/scim", "/external-webhooks", "/webhooks", "/imports", "/addons"):
            for href in Page(fetch(BASE + suffix)).links:
                url = urljoin(BASE, href).split("#")[0].rstrip("/")
                if url == BASE:
                    url += "/"
                if urlparse(url).netloc == urlparse(BASE).netloc and not any(
                    token in url
                    for token in (
                        "/_next/",
                        "/login",
                        "/terms",
                        "/policy",
                        "addon-terms",
                        "personal-data-processing-policy",
                        ".json",
                        ".ico",
                        ".png",
                    )
                ):
                    sources.setdefault(url or BASE, "navigation")

        def collect(item):
            url, section = item
            try:
                return parse_page(url, fetch(url), section)
            except (httpx.HTTPError, ValueError) as exc:
                return {"url": url, "section": section, "kind": "unparsed", "error": str(exc)}

        with ThreadPoolExecutor(max_workers=4) as pool:
            pages = list(pool.map(collect, sorted(sources.items())))
        automation_html = fetch(BASE + "/automations/create-automation")
    # The automation request schemas live in client-side modal tables, not in SSR HTML.
    automation_source = {}
    try:
        with httpx.Client(timeout=30) as modal_client:
            bundle_path = re.search(r'src="([^\"]*/pages/_app-[^\"]+)"', automation_html).group(1)
            bundle_url = BASE + bundle_path
            bundle_file = cache / (hashlib.sha256(bundle_url.encode()).hexdigest() + ".html")
            if not bundle_file.exists():
                response = modal_client.get(bundle_url)
                response.raise_for_status()
                bundle_file.write_text(response.text)
            run = subprocess.run(
                ["node", str(ROOT / "scripts/extract_automation_docs.cjs"), str(bundle_file)],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )
            tables = json.loads(run.stdout)
            table_path = SNAPSHOT.with_name("automation-tables.json")
            table_path.write_text(json.dumps(tables, ensure_ascii=False, indent=2) + "\n")
            automation_source = {
                "url": bundle_url,
                "sha256": hashlib.sha256(bundle_file.read_bytes()).hexdigest(),
                "tables_sha256": hashlib.sha256(table_path.read_bytes()).hexdigest(),
            }
    except (
        OSError,
        ValueError,
        AttributeError,
        subprocess.SubprocessError,
        httpx.HTTPError,
    ) as exc:
        automation_source = {"error": str(exc)}

    snapshot = {
        "checked_at": datetime.now(UTC).isoformat(),
        "index_sha256": hashlib.sha256(index.encode()).hexdigest(),
        "automation_source": automation_source,
        "pages": pages,
    }
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
    print(f"Saved {len(pages)} pages to {SNAPSHOT}")


# Source-path mappings for public routes implemented through compatible shapers.
SPECIAL_ROUTES = {
    "space-boards/get-board": "boards.get",
    "card-checklist-items/add-item-to-checklist": "checklist-items.create",
    "card-checklist-items/update-checklist-item": "checklist-items.update",
    "card-checklist-items/remove-checklist-item": "checklist-items.delete",
}
PREFERRED = {
    ("PATCH", "/cards/{}"): "cards.update",
    ("PATCH", "/spaces/{}/boards/{}"): "boards.update",
}


def normalize_path(path):
    return re.sub(r"\{[^}]+\}", "{}", path.removeprefix("/api/latest"))


def matching_tool(page):
    from kaiten_cli.registry import iter_tools, resolve_tool

    slug = page["url"].split(".ru/")[-1]
    if slug in SPECIAL_ROUTES:
        return resolve_tool(SPECIAL_ROUTES[slug])
    key = page["method"], normalize_path(page["path"])
    if key in PREFERRED:
        return resolve_tool(PREFERRED[key])
    candidates = [
        t
        for t in iter_tools()
        if (t.operation.method, normalize_path(t.operation.path_template)) == key
    ]
    return candidates[0] if candidates else None


def types(schema):
    if "type" in schema:
        value = schema["type"]
        return set(value if isinstance(value, list) else [value])
    variants = schema.get("oneOf", schema.get("anyOf", []))
    if variants:
        return set().union(*(types(v) for v in variants))
    if "enum" in schema:
        return {
            (
                "null"
                if v is None
                else "boolean"
                if isinstance(v, bool)
                else "integer"
                if isinstance(v, int)
                else "number"
                if isinstance(v, float)
                else "string"
            )
            for v in schema["enum"]
        }
    return set()


def schema_fields(schema):
    result = dict(schema.get("properties", {}))
    for v in schema.get("oneOf", schema.get("anyOf", [])):
        result.update(schema_fields(v))
    return result


def schema_items(schema):
    if isinstance(schema.get("items"), dict):
        return schema["items"]
    for v in schema.get("oneOf", schema.get("anyOf", [])):
        if schema_items(v):
            return schema_items(v)
    return {}


def differences(documented, cli, path):
    result = []
    wanted, supported = types(documented), types(cli)
    if "number" in supported:
        supported.add("integer")
    if wanted and supported and not wanted <= supported:
        result.append(
            {"field": path, "issue": "type", "documented": sorted(wanted), "cli": sorted(supported)}
        )
    if documented.get("enum") and cli.get("enum"):
        rejected = [v for v in documented["enum"] if v not in cli["enum"]]
        if rejected:
            result.append({"field": path, "issue": "enum", "rejected": rejected})
    for keyword in ("minimum", "exclusiveMinimum", "minLength", "minItems"):
        if keyword in cli and keyword in documented and cli[keyword] > documented[keyword]:
            result.append(
                {
                    "field": path,
                    "issue": "constraint",
                    "keyword": keyword,
                    "documented": documented[keyword],
                    "cli": cli[keyword],
                }
            )
    for keyword in ("maximum", "exclusiveMaximum", "maxLength", "maxItems"):
        if keyword in cli and keyword in documented and cli[keyword] < documented[keyword]:
            result.append(
                {
                    "field": path,
                    "issue": "constraint",
                    "keyword": keyword,
                    "documented": documented[keyword],
                    "cli": cli[keyword],
                }
            )
    extra_required = set(cli.get("required", [])) - set(documented.get("required", []))
    if extra_required and not documented.get("anyOf") and not documented.get("oneOf"):
        result.append({"field": path, "issue": "required", "extra": sorted(extra_required)})
    for name, definition in schema_fields(documented).items():
        child = cli.get("properties", {}).get(name)
        if child is None:
            result.append(
                {
                    "field": path + "." + name,
                    "issue": "opaque"
                    if cli.get("additionalProperties") is not False
                    else "missing",
                }
            )
        else:
            result.extend(differences(definition, child, path + "." + name))
    child = schema_items(documented)
    if child:
        result.extend(differences(child, cli.get("items", {}), path + "[]"))
    return result


def audit(snapshot):
    decisions = json.loads(SNAPSHOT.with_name("decisions.json").read_text())
    results = []
    for page in snapshot["pages"]:
        record = {"url": page["url"], "kind": page["kind"]}
        if page["kind"] != "http":
            record["status"] = "unparsed" if page["kind"] == "unparsed" else "reference_only"
            results.append(record)
            continue
        tool = matching_tool(page)
        if tool is None:
            record.update(status="missing", method=page["method"], path=page["path"])
            results.append(record)
            continue
        issues = []
        props = tool.input_schema.get("properties", {})
        for location in ("body", "query"):
            for field, definition in schema_fields(page.get(location) or {}).items():
                local = (
                    "start_index"
                    if tool.canonical_name.startswith("scim.") and field == "startIndex"
                    else field
                )
                cli = props.get(local)
                if cli is None:
                    issues.append(
                        {
                            "field": location + "." + field,
                            "issue": "payload_only" if "payload" in props else "missing",
                        }
                    )
                else:
                    issues.extend(differences(definition, cli, location + "." + field))
                    fields = (
                        tool.operation.body_fields
                        if location == "body"
                        else tool.operation.query_fields
                    )
                    if local not in fields:
                        issues.append({"field": location + "." + field, "issue": "wire_mapping"})
        resolved = []
        pending = []
        for issue in issues:
            decision = next(
                (
                    d
                    for d in decisions
                    if d["url"] == page["url"]
                    and d["tool"] == tool.canonical_name
                    and d["expected_issue"] == issue
                ),
                None,
            )
            if decision:
                resolved.append(decision)
            else:
                pending.append(issue)
        record.update(
            tool=tool.canonical_name,
            status="covered" if not pending else "review",
            issues=pending,
            decisions=resolved,
        )
        if resolved and not pending:
            record["status"] = "accounted_with_notes"
        if tool.canonical_name.startswith("automations.") and tool.action in ("create", "update"):
            record["modal_schemas"] = "automation-tables.json"
            if snapshot.get("automation_source", {}).get("error") or not snapshot.get(
                "automation_source"
            ):
                record["status"] = "unparsed"
                record["issues"].append({"field": "modal schemas", "issue": "unparsed"})
        if tool.canonical_name.startswith("private-") and tool.action == "get":
            if record["status"] == "covered":
                record["status"] = "accounted_with_notes"
            record["notes"] = [
                "redirect=true is rejected: JSON metadata commands do not follow storage redirects. Use files.download for binary downloads."
            ]
        results.append(record)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    if args.refresh:
        if args.cache_dir is None:
            import tempfile

            with tempfile.TemporaryDirectory(prefix="kaiten-docs-") as directory:
                refresh(Path(directory))
        else:
            refresh(args.cache_dir)
    else:
        snapshot = json.loads(SNAPSHOT.read_text())
        from normalize_automation_docs import normalize, OUTPUT

        table_path = SNAPSHOT.with_name("automation-tables.json")
        source = snapshot.get("automation_source", {})
        if source.get("tables_sha256") != hashlib.sha256(table_path.read_bytes()).hexdigest():
            raise SystemExit("Automation source table hash mismatch; refresh/review the snapshot.")
        if normalize(json.loads(table_path.read_text())) != json.loads(OUTPUT.read_text()):
            raise SystemExit(
                "Normalized automation schemas are stale; review sources and run scripts/normalize_automation_docs.py."
            )
        results = audit(snapshot)
        if args.write_report:
            SNAPSHOT.with_name("coverage.json").write_text(
                json.dumps(results, ensure_ascii=False, indent=2) + "\n"
            )
        counts = {
            status: sum(p["status"] == status for p in results)
            for status in sorted({p["status"] for p in results})
        }
        print(json.dumps(counts))
        failures = [p for p in results if p["status"] in ("missing", "review", "unparsed")]
        if failures:
            print(json.dumps(failures, ensure_ascii=False, indent=2))
            raise SystemExit(1)


if __name__ == "__main__":
    main()
