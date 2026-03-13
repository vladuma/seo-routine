#!/usr/bin/env python3
"""
Google Search Console data collector
Usage: python3 scripts/gsc.py --days 7
       python3 scripts/gsc.py --days 7 --compare    # 7d vs previous 7d
       python3 scripts/gsc.py --days 28 --page "/blog/example"
"""
import argparse
import sys
from datetime import date, timedelta

from credential import get_google_credentials, get_gsc_site_url

GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def build_service():
    """Build authenticated Search Console service."""
    from googleapiclient.discovery import build
    creds = get_google_credentials(GSC_SCOPES)
    return build("searchconsole", "v1", credentials=creds)


def query_gsc(service, site_url: str, start: str, end: str,
              dimensions: list, row_limit: int = 1000,
              page_filter: str = None) -> list:
    """Run a Search Analytics query and return rows."""
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": dimensions,
        "rowLimit": row_limit,
    }
    if page_filter:
        body["dimensionFilterGroups"] = [{
            "filters": [{
                "dimension": "page",
                "operator": "contains",
                "expression": page_filter,
            }]
        }]

    resp = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    return resp.get("rows", [])


def print_page_rows(rows: list):
    """Print page-level performance data."""
    print(f"pages[{len(rows)}]{{page,clicks,impressions,ctr,position}}:")
    for row in rows:
        page = row["keys"][0]
        # Strip domain to keep output compact
        if "://" in page:
            page = "/" + page.split("://", 1)[1].split("/", 1)[-1]
        clicks = int(row["clicks"])
        impressions = int(row["impressions"])
        ctr = f"{row['ctr'] * 100:.1f}%"
        position = f"{row['position']:.1f}"
        print(f"  {page},{clicks},{impressions},{ctr},{position}")


def print_query_rows(rows: list):
    """Print query-level performance data."""
    print(f"queries[{len(rows)}]{{query,clicks,impressions,ctr,position}}:")
    for row in rows:
        query = row["keys"][0][:60]
        clicks = int(row["clicks"])
        impressions = int(row["impressions"])
        ctr = f"{row['ctr'] * 100:.1f}%"
        position = f"{row['position']:.1f}"
        print(f"  {query},{clicks},{impressions},{ctr},{position}")


def print_comparison(current: list, previous: list, dimension: str):
    """Print current vs previous period with deltas."""
    prev_map = {}
    for row in previous:
        key = row["keys"][0]
        prev_map[key] = row

    label = "pages" if dimension == "page" else "queries"
    print(f"{label}_comparison[{len(current)}]{{key,clicks,delta_clicks,position,delta_position}}:")
    for row in current:
        key = row["keys"][0]
        if dimension == "page" and "://" in key:
            key = "/" + key.split("://", 1)[1].split("/", 1)[-1]
        clicks = int(row["clicks"])
        position = row["position"]

        prev = prev_map.get(row["keys"][0])
        if prev:
            d_clicks = clicks - int(prev["clicks"])
            d_pos = position - prev["position"]
            d_clicks_s = f"+{d_clicks}" if d_clicks >= 0 else str(d_clicks)
            d_pos_s = f"{d_pos:+.1f}"
        else:
            d_clicks_s = "new"
            d_pos_s = "new"

        print(f"  {key[:60]},{clicks},{d_clicks_s},{position:.1f},{d_pos_s}")


def main():
    parser = argparse.ArgumentParser(description="Google Search Console data")
    parser.add_argument("--days", "-d", type=int, default=7,
                        help="Number of days to query (default: 7)")
    parser.add_argument("--compare", "-c", action="store_true",
                        help="Compare with previous period")
    parser.add_argument("--page", "-p", type=str, default=None,
                        help="Filter to a specific page path")
    parser.add_argument("--dimension", choices=["page", "query"], default="page",
                        help="Primary dimension (default: page)")
    parser.add_argument("--limit", "-l", type=int, default=50,
                        help="Max rows (default: 50)")
    args = parser.parse_args()

    site_url = get_gsc_site_url()
    service = build_service()

    # GSC data has ~3 day lag
    end = date.today() - timedelta(days=3)
    start = end - timedelta(days=args.days)

    print(f"site: {site_url}")
    print(f"period: {start} to {end}")

    rows = query_gsc(service, site_url, str(start), str(end),
                     [args.dimension], args.limit, args.page)
    if not rows:
        print("No data found for this period.")
        sys.exit(0)

    if args.compare:
        prev_end = start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=args.days)
        print(f"compare: {prev_start} to {prev_end}")
        prev_rows = query_gsc(service, site_url, str(prev_start), str(prev_end),
                              [args.dimension], args.limit, args.page)
        print_comparison(rows, prev_rows, args.dimension)
    else:
        if args.dimension == "page":
            print_page_rows(rows)
        else:
            print_query_rows(rows)

    # Striking distance summary (positions 5-20 with impressions >= 10)
    striking = [r for r in rows
                if 5 <= r["position"] <= 20 and r["impressions"] >= 10]
    if striking:
        print(f"\nstriking_distance[{len(striking)}]:")
        for row in sorted(striking, key=lambda r: r["position"]):
            key = row["keys"][0]
            if args.dimension == "page" and "://" in key:
                key = "/" + key.split("://", 1)[1].split("/", 1)[-1]
            print(f"  {key[:60]},{row['position']:.1f},{int(row['impressions'])}imp")


if __name__ == "__main__":
    main()
