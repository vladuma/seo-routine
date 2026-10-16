#!/usr/bin/env python3
"""
content_plan.py -- Reads gap analysis + competitive intel, generates a
4-brief weekly content plan with titles, intent, and volume data.
"""

import os
import json
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def get_latest_report(pattern):
    """Get the most recent JSON report matching a pattern."""
    reports = sorted(Path("reports").glob(pattern), reverse=True)
    if not reports:
        return None
    with open(reports[0]) as f:
        return json.load(f)


def classify_intent(keyword):
    """Classify search intent from keyword signals."""
    kw = keyword.lower()
    if any(w in kw for w in ["how to", "how do", "tutorial", "guide", "steps", "setup"]):
        return "How-To"
    elif any(w in kw for w in ["best", "top", "vs", "versus", "compare", "alternative", "review"]):
        return "Commercial Investigation"
    elif any(w in kw for w in ["buy", "price", "cost", "cheap", "discount", "deal"]):
        return "Transactional"
    else:
        return "Informational"


def generate_title(keyword, intent, brand_context=""):
    """Generate a compelling SEO title for the keyword."""
    current_year = datetime.date.today().year
    kw_title = keyword.title()

    title_templates = {
        "How-To": [
            f"How to {kw_title}: Complete Setup Guide ({current_year})",
            f"{kw_title}: A Step-by-Step Guide for Busy Professionals",
        ],
        "Commercial Investigation": [
            f"Best {kw_title} Tools: Honest Comparison ({current_year})",
            f"{kw_title}: What Actually Works (And What Doesn't)",
        ],
        "Transactional": [
            f"{kw_title}: What to Look For Before You Choose ({current_year})",
        ],
        "Informational": [
            f"{kw_title}: The Complete Guide ({current_year})",
            f"What Is {kw_title}? A Practical Breakdown",
        ],
    }

    templates = title_templates.get(intent, title_templates["Informational"])
    return templates[0]


def generate_brief(keyword, intent, position, competitive_context=""):
    """Generate a one-sentence brief for the article."""
    briefs = {
        "How-To": (
            "Step-by-step walkthrough targeting the audience described in brand-voice.md -- "
            "lead with the outcome in the first paragraph, include a real setup example, "
            "and close with a CTA that matches the reader's decision stage."
        ),
        "Commercial Investigation": (
            "Neutral comparison post with a structured table above the fold -- "
            "Google AI Overview pulls from tables, and this keyword has commercial intent "
            "from buyers evaluating options."
        ),
        "Transactional": (
            "Buying guide with specific criteria and a clear recommendation -- "
            "readers are evaluating options and need a clear point of view to convert."
        ),
        "Informational": (
            "Definitive resource page targeting this keyword cluster -- build topical "
            "authority by covering the full topic, then link out to supporting how-to posts."
        ),
    }
    return briefs.get(intent, briefs["Informational"])


def run_content_plan():
    print("Loading gap analysis and competitive intel...")

    gap_data = get_latest_report("gap-analysis-*.json")
    comp_data = get_latest_report("competitive-*.json")

    if not gap_data:
        raise FileNotFoundError("No gap analysis found. Run gap_finder.py first.")

    brand_context = ""
    if Path("brand-voice.md").exists():
        with open("brand-voice.md") as f:
            brand_context = f.read()
        print("Brand voice loaded.")
    else:
        print("brand-voice.md not found. Run the brand interview first for better results.")

    keywords = gap_data.get("keywords", [])[:8]

    # Build competitive threat lookup
    threat_lookup = {}
    if comp_data:
        for result in comp_data.get("results", []):
            kw = result["keyword"]
            if kw not in threat_lookup:
                threat_lookup[kw] = result["threat"]

    # Score and select top 4 opportunities
    scored = []
    for kw_data in keywords:
        keyword = kw_data["keyword"]
        impressions = kw_data["impressions"]
        position = kw_data["position"]
        threat = threat_lookup.get(keyword, "MEDIUM")

        threat_score = {"LOW": 3, "MEDIUM": 2, "HIGH": 0}[threat]
        position_score = max(0, 20 - position)
        impression_score = min(impressions / 100, 10)
        total_score = threat_score * 3 + position_score + impression_score

        # Reframe HIGH threat keywords with a niche angle (optional: SEO_NICHE_ANGLE="for freelancers")
        niche_angle = os.environ.get("SEO_NICHE_ANGLE", "").strip()
        if threat == "HIGH" and niche_angle:
            keyword = f"{keyword} {niche_angle}"

        scored.append({
            "keyword": keyword,
            "original_keyword": kw_data["keyword"],
            "impressions": impressions,
            "position": position,
            "ctr": kw_data["ctr"],
            "threat": threat,
            "score": total_score,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top_4 = scored[:4]

    # Generate content plan
    plan = []
    for i, item in enumerate(top_4):
        intent = classify_intent(item["keyword"])
        title = generate_title(item["keyword"], intent, brand_context)
        brief = generate_brief(item["keyword"], intent, item["position"])
        priority = "P1" if i < 2 else "P2"

        plan.append({
            "priority": priority,
            "title": title,
            "keyword": item["keyword"],
            "estimated_volume": item["impressions"],
            "current_position": item["position"],
            "intent": intent,
            "brief": brief,
        })

    # -- Save outputs ---------------------------------------------------------
    today = datetime.date.today().isoformat()
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    json_path = reports_dir / f"content-plan-{today}.json"
    output_data = {"date": today, "articles": plan}
    with open(json_path, "w") as f:
        json.dump(output_data, f, indent=2)

    md_path = reports_dir / f"content-plan-{today}.md"
    with open(md_path, "w") as f:
        f.write("# Weekly Content Plan\n")
        f.write(f"**Date:** {today} | **Generated from:** gap analysis + competitive intel\n\n")
        for article in plan:
            f.write(f"## {article['priority']} -- {article['title']}\n")
            f.write(f"- **Target keyword:** {article['keyword']}\n")
            f.write(f"- **Est. volume:** {article['estimated_volume']:,} impressions/mo\n")
            f.write(f"- **Current position:** {article['current_position']}\n")
            f.write(f"- **Intent:** {article['intent']}\n")
            f.write(f"- **Brief:** {article['brief']}\n\n")

    print(f"\nContent plan saved:")
    print(f"   {md_path}")
    print(f"   {json_path}")
    print(f"\nThis week's plan:")
    for article in plan:
        print(f"\n  {article['priority']} -- {article['title']}")
        print(f"      Keyword: {article['keyword']} | Position: {article['current_position']} | Intent: {article['intent']}")

    return output_data


if __name__ == "__main__":
    run_content_plan()
