#!/usr/bin/env python3
"""
competitor_intel.py -- Reads gap analysis keywords, searches Google for top-ranking
competitors, assesses threat levels, and generates actionable intelligence reports.
"""

import os
import json
import time
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def get_latest_gap_analysis():
    """Get the most recent gap analysis JSON from reports/."""
    reports = sorted(Path("reports").glob("gap-analysis-*.json"), reverse=True)
    if not reports:
        return None
    with open(reports[0]) as f:
        return json.load(f)


def search_google(query, num_results=3):
    """Search for competitors -- uses DataForSEO if available, else fallback."""
    login = os.getenv("DATAFORSEO_LOGIN")
    password = os.getenv("DATAFORSEO_PASSWORD")

    if login and password:
        return search_dataforseo(query, login, password, num_results)
    return search_basic(query, num_results)


def search_dataforseo(query, login, password, num_results=3):
    """Use DataForSEO SERP API for real competitor data."""
    import requests

    url = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
    payload = [
        {
            "keyword": query,
            "location_code": 2840,  # United States
            "language_code": "en",
            "depth": 10,
        }
    ]

    try:
        response = requests.post(url, json=payload, auth=(login, password))
        response.raise_for_status()
        data = response.json()

        results = []
        tasks = data.get("tasks", [])
        if tasks and tasks[0].get("result"):
            items = tasks[0]["result"][0].get("items", [])
            for item in items:
                if item.get("type") == "organic" and len(results) < num_results:
                    results.append({
                        "url": item.get("url", ""),
                        "title": item.get("title", ""),
                        "domain": item.get("domain", ""),
                        "position": item.get("rank_group", 0),
                        "description": item.get("description", ""),
                    })
        return results
    except Exception as e:
        print(f"  DataForSEO error: {e}. Falling back to basic search.")
        return search_basic(query, num_results)


def search_basic(query, num_results=3):
    """Fallback: return placeholder results when no API is available."""
    return [
        {
            "url": f"https://example.com/{query.replace(' ', '-')}-{i}",
            "title": f"Top result for {query} (demo #{i})",
            "domain": f"competitor{i}.com",
            "position": i,
            "description": f"Demo competitor result for '{query}'. Enable DataForSEO for real data.",
        }
        for i in range(1, num_results + 1)
    ]


def analyze_competitor(competitor, keyword):
    """Assess threat level and generate actionable insight."""
    domain = competitor.get("domain", "").lower()
    title = competitor.get("title", "").lower()
    desc = competitor.get("description", "").lower()
    position = competitor.get("position", 0)

    # High-authority domains
    high_authority = [
        "google.com", "microsoft.com", "apple.com", "support.google.com",
        "support.microsoft.com", "zapier.com", "notion.so", "wikipedia.org",
    ]

    current_year = str(datetime.date.today().year)

    if any(d in domain for d in high_authority):
        threat = "HIGH"
        reason = f"Massive domain authority. {domain} is a recognized brand in this space. Hard to displace with content alone."
    elif current_year in title or current_year in desc:
        threat = "MEDIUM"
        reason = f"Recency signal in title/URL ({current_year}). Fix: update your title with current year, add 'What changed in {current_year}' section."
    elif any(w in title for w in ["vs", "compare", "comparison", "alternative"]):
        threat = "MEDIUM"
        reason = "Comparison content ranking well. Fix: create a structured comparison table -- Google AI Overview pulls from tables."
    elif any(w in title for w in ["guide", "how to", "tutorial", "step"]):
        threat = "MEDIUM"
        reason = "Guide/tutorial format ranking. Fix: match content depth and add numbered steps with clear headings."
    elif position <= 3:
        threat = "MEDIUM"
        reason = f"Ranking position {position} without obvious authority signals. Likely strong content -- analyze their structure."
    else:
        threat = "LOW"
        reason = "Appears to be thin content or ranking on coincidence. A single solid article can outrank them."

    return threat, reason


def run_competitor_intel():
    print("Loading gap analysis data...")
    gap_data = get_latest_gap_analysis()

    if not gap_data:
        raise FileNotFoundError("No gap analysis found. Run gap_finder.py first.")

    keywords = gap_data.get("keywords", [])[:8]
    if not keywords:
        print("No keywords in gap analysis. Run gap_finder.py first.")
        return

    print(f"Analyzing competitors for {len(keywords)} keywords...")

    results = []
    quick_wins = []
    avoid = []

    for kw_data in keywords:
        keyword = kw_data["keyword"]
        print(f"  Searching: {keyword}")

        competitors = search_google(keyword)
        time.sleep(1)  # Rate limit

        for comp in competitors:
            threat, reason = analyze_competitor(comp, keyword)
            entry = {
                "keyword": keyword,
                "competitor": comp["domain"],
                "url": comp["url"],
                "title": comp["title"],
                "threat": threat,
                "reason": reason,
            }
            results.append(entry)

            if threat == "LOW":
                quick_wins.append(entry)
            elif threat == "HIGH":
                avoid.append(entry)

    # -- Save outputs ---------------------------------------------------------
    today = datetime.date.today().isoformat()
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    json_path = reports_dir / f"competitive-{today}.json"
    output_data = {
        "date": today,
        "keywords_analyzed": len(keywords),
        "results": results,
        "quick_wins": quick_wins,
        "avoid": avoid,
    }
    with open(json_path, "w") as f:
        json.dump(output_data, f, indent=2)

    md_path = reports_dir / f"competitive-{today}.md"
    with open(md_path, "w") as f:
        f.write(f"# Competitive Intelligence Report\n")
        f.write(f"**Date:** {today} | **Keywords analyzed:** {len(keywords)}\n\n")
        f.write("## Competitor Analysis\n\n")
        f.write("| Keyword | Competitor | Threat | Why They Win |\n")
        f.write("|---------|-----------|--------|-------------|\n")
        for r in results:
            f.write(f"| {r['keyword']} | {r['competitor']} | {r['threat']} | {r['reason']} |\n")

        if quick_wins:
            f.write("\n## Quick Wins (LOW threat)\n\n")
            for qw in quick_wins:
                f.write(f"- **{qw['keyword']}** vs {qw['competitor']}: {qw['reason']}\n")

        if avoid:
            f.write("\n## Keywords to Avoid (HIGH threat)\n\n")
            for a in avoid:
                f.write(f"- **{a['keyword']}** -- {a['competitor']}: {a['reason']}\n")

    print(f"\nReports saved:")
    print(f"   {md_path}")
    print(f"   {json_path}")
    print(f"\nQuick wins: {len(quick_wins)} | High threat: {len(avoid)}")

    return output_data


if __name__ == "__main__":
    run_competitor_intel()
