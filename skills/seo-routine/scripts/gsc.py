#!/usr/bin/env python3
"""
Google Search Console API data fetcher.

Finalized web-search data with comparable property totals, a transparent query
partition and explicit coverage, so a failed or truncated pull can never look like
zero traffic. See references/measurement.md for how to interpret each field.

Usage:
  python3 scripts/gsc.py --days 7 --compare --dimension property --json
  python3 scripts/gsc.py --days 28 --compare --dimension query,page --limit 25000 \
      --brand-regex "(?i)acme" --json

Brand classification is optional. Pass --brand-regex (or set GSC_BRAND_REGEX) to split
visible queries into brand / nonbrand. Without it, only the visible-vs-unreported
query split is computed. A regex is a text classifier, not proof of brand awareness.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta


SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def _resolve_creds_path():
    """Resolve the credentials file path from env."""
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set")
    if not os.path.isabs(creds_path):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(project_root, creds_path)
    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Credentials file not found: {creds_path}")
    return creds_path


def _load_credentials(creds_path, allow_interactive=False):
    """Load credentials, supporting both service account and OAuth client types."""
    from google.auth.transport.requests import Request

    with open(creds_path) as f:
        creds_data = json.load(f)

    # Service account credentials
    if creds_data.get("type") == "service_account":
        from google.oauth2.service_account import Credentials
        return Credentials.from_service_account_file(creds_path, scopes=SCOPES)

    # OAuth installed/web app credentials — use token cache
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials as OAuthCredentials

    token_path = os.path.join(os.path.dirname(creds_path), ".seo-token.json")
    creds = None

    if os.path.exists(token_path):
        creds = OAuthCredentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif allow_interactive:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        else:
            raise RuntimeError("No reusable Google authorization; run once with --authorize interactively")
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def get_gsc_client(allow_interactive=False):
    """Initialize Google Search Console API client."""
    from googleapiclient.discovery import build

    creds_path = _resolve_creds_path()
    credentials = _load_credentials(creds_path, allow_interactive)
    return build("webmasters", "v3", credentials=credentials)


def query_result(service, site_url, start_date, end_date, dimensions, limit=25000,
                 start_row=0, query_filter=None):
    request = {
        "startDate": str(start_date), "endDate": str(end_date),
        "dimensions": dimensions, "rowLimit": limit, "startRow": start_row,
        "type": "web", "dataState": "final",
        "aggregationType": "byProperty" if not dimensions else "auto",
    }
    if query_filter:
        request["dimensionFilterGroups"] = [{"filters": [query_filter]}]
    # Errors propagate: a failed collection must never look like zero traffic.
    return service.searchanalytics().query(siteUrl=site_url, body=request).execute(num_retries=3)


def latest_data_date(service, site_url, lookback=15):
    """Discover the latest FINAL day, never assume a fixed reporting lag."""
    today = datetime.now().date()
    rows = query_result(service, site_url, today - timedelta(days=lookback), today,
                        ["date"], lookback + 1).get("rows", [])
    if not rows:
        raise RuntimeError("No finalized GSC dates available; collection is incomplete")
    return datetime.strptime(max(row["keys"][0] for row in rows), "%Y-%m-%d").date()


def fetch_rows(service, site_url, start_date, end_date, dimension, limit=100):
    dimensions = [] if dimension == "property" else dimension.split(",")
    rows = []
    while len(rows) < limit:
        page_size = min(25000, limit - len(rows))
        batch = query_result(service, site_url, start_date, end_date, dimensions,
                             page_size, len(rows)).get("rows", [])
        rows.extend(batch)
        if len(batch) < page_size or not dimensions:
            return rows, False
    # Conservative: hitting the requested cap does not prove the remaining set is empty.
    return rows, True


def fetch_gsc_data(service, site_url, start_date, end_date, dimension, limit=100):
    """Compatibility interface for callers; API failures now propagate."""
    return fetch_rows(service, site_url, start_date, end_date, dimension, limit)[0]


def metric_row(response):
    rows = response.get("rows", [])
    return rows[0] if rows else {"clicks": 0, "impressions": 0, "ctr": 0, "position": None}


def collect_period(service, site_url, start_date, end_date, dimension, limit, brand_regex):
    total = metric_row(query_result(service, site_url, start_date, end_date, []))
    segments = {}
    if brand_regex:
        for label, operator in [("visible_brand", "includingRegex"),
                                ("visible_nonbrand", "excludingRegex")]:
            segments[label] = metric_row(query_result(
                service, site_url, start_date, end_date, [],
                query_filter={"dimension": "query", "operator": operator,
                              "expression": brand_regex}))
    else:
        # Any non-empty query text: what remains is anonymized or otherwise unreturned.
        segments["visible_queries"] = metric_row(query_result(
            service, site_url, start_date, end_date, [],
            query_filter={"dimension": "query", "operator": "includingRegex",
                          "expression": ".+"}))
    residual = {metric: total[metric] - sum(row[metric] for row in segments.values())
                for metric in ["clicks", "impressions"]}
    if any(value < 0 for value in residual.values()):
        raise RuntimeError("GSC query partition exceeds property totals; do not publish this comparison")
    segments["unreported"] = residual
    coverage = {metric: ((total[metric] - residual[metric]) / total[metric]
                         if total[metric] else None) for metric in residual}
    if dimension == "property":
        rows, capped = [total], False
    else:
        rows, capped = fetch_rows(service, site_url, start_date, end_date, dimension, limit)
    return {"start": str(start_date), "end": str(end_date), "property": total,
            "query_partition": segments, "query_coverage": coverage,
            "dimension": dimension, "rows": rows, "row_limit_reached": capped}


def format_data(rows, dimension):
    """Format GSC rows into readable format."""
    if not rows:
        return "No data available"

    dims = [d.strip() for d in dimension.split(",")]
    output = []
    output.append(f"# GSC {dimension.upper()} Data\n")
    output.append(
        "| " + " | ".join(d.title() for d in dims) + " | Clicks | Impressions | CTR | Avg Position |"
    )
    output.append("|" + "|".join(["---"] * (len(dims) + 4)) + "|")

    for row in rows:
        keys = row.get("keys", [""])
        key_value = " | ".join(f"`{str(k).replace(chr(124), chr(92) + chr(124))}`" for k in keys) if keys else "Property"
        clicks = row.get("clicks", 0)
        impressions = row.get("impressions", 0)
        ctr = row.get("ctr", 0)
        position = row.get("position", 0)

        # Format CTR as percentage
        ctr_pct = f"{ctr * 100:.2f}%" if ctr else "0%"
        avg_pos = f"{position:.2f}" if position else "-"

        output.append(
            f"| {key_value} | {clicks} | {impressions} | {ctr_pct} | {avg_pos} |"
        )

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Finalized GSC traffic with comparable property totals")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--dimension", default="page", choices=[
        "property", "page", "query", "country", "device", "date", "query,page", "page,query",
        "page,date", "date,page"])
    parser.add_argument("--limit", type=int, default=100, help="Maximum dimension rows; cap is reported")
    parser.add_argument("--end-date", type=lambda v: datetime.strptime(v, "%Y-%m-%d").date())
    parser.add_argument("--brand-regex", default=os.environ.get("GSC_BRAND_REGEX"),
                        help="Optional transparent query classifier (RE2 syntax); default $GSC_BRAND_REGEX")
    parser.add_argument("--json", action="store_true", help="Emit reproducible metrics and metadata")
    parser.add_argument("--authorize", action="store_true", help="Allow interactive Google consent setup")
    args = parser.parse_args()
    if not 1 <= args.days <= 365 or not 1 <= args.limit <= 100000:
        parser.error("days must be 1..365 and limit must be 1..100000")
    site_url = os.environ.get("GSC_SITE_URL")
    if not site_url:
        parser.error("GSC_SITE_URL is required")
    service = get_gsc_client(args.authorize)
    latest = latest_data_date(service, site_url)
    end_date = args.end_date or latest
    if end_date > latest:
        parser.error(f"end-date exceeds latest finalized date {latest}")
    periods = {}
    for index, label in enumerate(["current", "previous"] if args.compare else ["current"]):
        end = end_date - timedelta(days=args.days * index)
        start = end - timedelta(days=args.days - 1)
        periods[label] = collect_period(service, site_url, start, end,
                                        args.dimension, args.limit, args.brand_regex)
    report = {"schema_version": 1, "site": site_url, "search_type": "web",
              "data_state": "final", "latest_finalized_date": str(latest),
              "timezone": "America/Los_Angeles", "days": args.days,
              "collected_at": datetime.now().astimezone().isoformat(),
              "brand_regex": args.brand_regex, "periods": periods,
              "caveats": ["Query filtering omits anonymized queries; unreported is not nonbrand.",
                          "Page/query rows must not be summed as property totals.",
                          "API-internal privacy and row limits apply even below the requested cap."]}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"GSC Web, finalized through {latest}; dates use America/Los_Angeles.\n")
        for label, period in periods.items():
            print(f"## {label.title()}: {period['start']} to {period['end']} ({args.days}d)\n")
            print(format_data([period["property"]], "property"))
            print("\nQuery partition (visible brand / visible nonbrand / unreported; "
                  "or visible queries / unreported when no brand regex is set):")
            print(json.dumps(period["query_partition"], indent=2))
            if args.dimension != "property":
                print(format_data(period["rows"], args.dimension))
            if period["row_limit_reached"]:
                print("\nROW LIMIT REACHED: dimension rows are a bounded subset.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"GSC collection failed ({type(exc).__name__}); no valid report produced.", file=sys.stderr)
        sys.exit(1)
