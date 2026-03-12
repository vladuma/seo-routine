#!/usr/bin/env python3
"""
Google Analytics 4 data collector
Usage: python3 scripts/ga4.py --property 123456789 --days 7
       python3 scripts/ga4.py --property 123456789 --days 7 --compare
"""
import argparse
import sys
from datetime import date, timedelta

from credential import get_google_credentials

GA4_SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]


def build_service():
    """Build authenticated GA4 Data API service."""
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric, OrderBy,
    )
    creds = get_google_credentials(GA4_SCOPES)
    client = BetaAnalyticsDataClient(credentials=creds)
    return client, RunReportRequest, DateRange, Dimension, Metric, OrderBy


def run_page_report(client, types, property_id: str,
                    start: str, end: str, limit: int = 50):
    """Run a page-level report returning pageviews, sessions, bounce rate, avg duration."""
    RunReportRequest, DateRange, Dimension, Metric, OrderBy = types

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="pagePath")],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="sessions"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration"),
        ],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"),
                           desc=True)],
        limit=limit,
    )
    return client.run_report(request)


def print_report(response, label: str = "pages"):
    """Print GA4 report in compact format."""
    rows = response.rows if response.rows else []
    print(f"{label}[{len(rows)}]{{page,views,sessions,bounce_rate,avg_duration}}:")
    for row in rows:
        page = row.dimension_values[0].value[:60]
        views = row.metric_values[0].value
        sessions = row.metric_values[1].value
        bounce = f"{float(row.metric_values[2].value) * 100:.1f}%"
        duration = f"{float(row.metric_values[3].value):.0f}s"
        print(f"  {page},{views},{sessions},{bounce},{duration}")


def print_comparison(current, previous):
    """Print current vs previous with deltas."""
    prev_map = {}
    if previous.rows:
        for row in previous.rows:
            prev_map[row.dimension_values[0].value] = row

    rows = current.rows if current.rows else []
    print(f"pages_comparison[{len(rows)}]{{page,views,delta_views,bounce,delta_bounce}}:")
    for row in rows:
        page = row.dimension_values[0].value[:60]
        views = int(row.metric_values[0].value)
        bounce = float(row.metric_values[2].value) * 100

        prev = prev_map.get(row.dimension_values[0].value)
        if prev:
            prev_views = int(prev.metric_values[0].value)
            prev_bounce = float(prev.metric_values[2].value) * 100
            d_views = views - prev_views
            d_bounce = bounce - prev_bounce
            d_views_s = f"+{d_views}" if d_views >= 0 else str(d_views)
            d_bounce_s = f"{d_bounce:+.1f}%"
        else:
            d_views_s = "new"
            d_bounce_s = "new"

        print(f"  {page},{views},{d_views_s},{bounce:.1f}%,{d_bounce_s}")


def main():
    parser = argparse.ArgumentParser(description="Google Analytics 4 data")
    parser.add_argument("--property", "-pid", required=True,
                        help="GA4 property ID (numeric, e.g. 123456789)")
    parser.add_argument("--days", "-d", type=int, default=7,
                        help="Number of days to query (default: 7)")
    parser.add_argument("--compare", "-c", action="store_true",
                        help="Compare with previous period")
    parser.add_argument("--limit", "-l", type=int, default=50,
                        help="Max rows (default: 50)")
    args = parser.parse_args()

    client, RunReportRequest, DateRange, Dimension, Metric, OrderBy = build_service()
    types = (RunReportRequest, DateRange, Dimension, Metric, OrderBy)

    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=args.days)

    print(f"property: {args.property}")
    print(f"period: {start} to {end}")

    response = run_page_report(client, types, args.property,
                               str(start), str(end), args.limit)
    if not response.rows:
        print("No data found for this period.")
        sys.exit(0)

    if args.compare:
        prev_end = start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=args.days)
        print(f"compare: {prev_start} to {prev_end}")
        prev_response = run_page_report(client, types, args.property,
                                        str(prev_start), str(prev_end), args.limit)
        print_comparison(response, prev_response)
    else:
        print_report(response)


if __name__ == "__main__":
    main()
