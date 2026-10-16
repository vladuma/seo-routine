"""
GEO citation panel via DataForSEO LLM responses.

Runs a fixed prompt panel against an LLM with optional web search and writes a raw JSON
receipt plus a markdown summary, so a reading is reproducible from a committed command
and a file instead of terminal scrollback.

Endpoint: POST /v3/ai_optimization/chat_gpt/llm_responses/live
Panel, brand and domain come from a JSON file (see templates/geo-panel.json):

  {"panel_version": "2026-01-01-v1", "brand_regex": "acme", "domain": "acme.com",
   "prompts": [{"id": "C1", "intent": "commercial", "prompt": "best ... tool"}]}

Usage:
  python3 scripts/geo_panel.py --panel docs/seo/geo-panel.json --prompts C1,C4 --samples 3 \
      --raw-out <run>/inputs/geo-raw.json --out <run>/inputs/geo.md
"""

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

ENDPOINT = "https://api.dataforseo.com/v3/ai_optimization/chat_gpt/llm_responses/live"

# Panel 2026-09-13-v1, copied from docs/seo/seo-config.md geo.panel.
LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
SCHEME_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
HOSTLIKE_RE = re.compile(r"^[\w-]+(?:\.[\w-]+)+$")


def _link_text(match):
    """
    Keep a prose link's visible text, drop a citation link whole.

    Citations render as ([example.com](https://example.com/...)) — the visible text
    is a bare host, so keeping it would put our brand inside a RIVAL's entry and
    score that entry as ours. A link whose text is real prose ("see Acme's docs")
    is kept. Bare hosts are only removed in this link position, never from prose:
    an earlier version stripped every domain-shaped token and deleted the competitor
    competitor's name from a heading, which would understate our own list rank.
    """
    text = (match.group(1) or "").strip()
    return "" if HOSTLIKE_RE.match(text) else text


def strip_urls(text):
    """Drop citation links and absolute URLs, keeping human-visible prose."""
    return SCHEME_URL_RE.sub("", LINK_RE.sub(_link_text, text or ""))


def call_once(login, password, prompt, model, web_search, timeout=180):
    payload = json.dumps([{"user_prompt": prompt, "model_name": model,
                           "web_search": web_search}]).encode()
    token = base64.b64encode(f"{login}:{password}".encode()).decode()
    req = urllib.request.Request(ENDPOINT, data=payload, method="POST", headers={
        "Authorization": f"Basic {token}", "Content-Type": "application/json"})
    # HTTP errors raise: a failed call must never be scored as "brand absent".
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def extract(body):
    """Pull the fields the panel scores out of one live response."""
    task = (body.get("tasks") or [{}])[0]
    res = (task.get("result") or [{}])[0]
    item = (res.get("items") or [{}])[0]
    sections = item.get("sections") or []
    text = "\n".join(s.get("text") or "" for s in sections)
    annotations = []
    for s in sections:
        for a in s.get("annotations") or []:
            url = a.get("url") or ""
            if url:
                annotations.append(url)
    return {
        "task_id": task.get("id"),
        "status_code": body.get("status_code"),
        "status_message": body.get("status_message"),
        "datetime_utc": task.get("data", {}).get("datetime") or res.get("datetime"),
        "model_name": res.get("model_name"),
        "web_search": res.get("web_search"),
        "input_tokens": res.get("input_tokens"),
        "output_tokens": res.get("output_tokens"),
        "cost": task.get("cost"),
        "annotations": annotations,
        "text": text,
    }


def _norm_title(title):
    """
    Normalise one entry title for comparison across samples.

    Answers mix `### LeapSync`, `### 3. **LeapSync**` and
    `### 2calendars - Google-only, real-time`, so the bare name has to be recovered
    before counting who outranks us; otherwise the same rival tallies three ways.
    """
    t = (title or "").strip().strip("*").strip()
    t = re.sub(r"^\d+[.)]\s*", "", t)          # leading list number
    t = t.strip().strip("*").strip()
    t = re.split(r"\s+[\u2014\u2013-]\s+", t)[0]  # trailing " - description"
    return t.strip().strip("*").strip(":").strip()


def entry_titles(text):
    """
    Ordered titles of the answer's ranked entries.

    Answers arrive in three shapes: `### Tool` heading blocks, `1. Tool` numbered
    items, and `- **Tool**:` bullets. Headings win when present, because an answer
    using headings also carries per-entry sub-bullets that are not themselves
    ranked entries.

    KNOWN LIMITATION: a section header one level ABOVE the entries is excluded by the
    deepest-enumerating-level rule, but a non-enumerating header at the SAME level as
    the entries is not. Observed in practice, where `## Quick Comparison
    Table` and `## Recommendations by Scenario` sat at the entries' own level and were
    counted, inflating `entries` from 9 to 11. `list_rank` is unaffected whenever the
    spurious headers sort below us, which is the usual case because they close the
    answer — but do NOT build a competitor count on `entries` without re-reading the
    raw text, and treat its length as an upper bound.
    """
    lines = (text or "").splitlines()

    by_level = {}
    for line in lines:
        m = re.match(r"^(#{2,6})\s+(.*?)\s*$", line.strip())
        if m:
            title = m.group(2).strip().strip("*").strip()
            title = _norm_title(title)
            if title:
                by_level.setdefault(len(m.group(1)), []).append(title)
    # Entries sit at the deepest level that actually enumerates; shallower levels are
    # the answer's own section headers ("Quick Comparison Table", "Final Recommendations").
    headings = []
    for level in sorted(by_level, reverse=True):
        if len(by_level[level]) >= 2:
            headings = by_level[level]
            break

    numbered = []
    for line in lines:
        m = re.match(r"^(?:\*\*)?\d+[.)]\s+(.*)$", line.strip())
        if m:
            numbered.append(_norm_title(m.group(1)))
    bullets = []
    for line in lines:
        m = re.match(r"^[-*\u2022]\s+\*\*([^*:]+)", line.strip())
        if m:
            bullets.append(_norm_title(m.group(1)))

    # A heading-shaped answer still has sub-bullets; prefer the coarsest real list.
    for candidate in (headings, numbered, bullets):
        if len(candidate) >= 2:
            return candidate
    return headings or numbered or bullets


def rank_of_brand(text, brand_re):
    """
    1-based rank of the entry whose SUBJECT is the brand, or None.

    Reads URL-stripped prose so a rival entry citing one of the brand's own pages is not
    mistaken for our own entry. None means either absent or no enumerable list;
    the committed raw text stays authoritative for every reading.
    """
    clean = strip_urls(text)
    if not brand_re.search(clean):
        return None
    for i, title in enumerate(entry_titles(clean), start=1):
        if brand_re.search(title):
            return i
    return None


def main():
    ap = argparse.ArgumentParser(description="GEO citation panel via DataForSEO LLM responses")
    ap.add_argument("--panel", required=True, help="Panel definition JSON (see module docstring)")
    ap.add_argument("--prompts", default="all",
                    help="Comma-separated panel ids, or 'all'")
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--model", default="gpt-4.1")
    ap.add_argument("--no-web-search", action="store_true")
    ap.add_argument("--sleep", type=float, default=2.0, help="Seconds between calls")
    ap.add_argument("--raw-out", required=True, help="Raw JSON receipt path")
    ap.add_argument("--out", help="Markdown summary path (default: stdout)")
    args = ap.parse_args()

    login = os.getenv("DATAFORSEO_LOGIN")
    password = os.getenv("DATAFORSEO_PASSWORD")
    if not login or not password:
        sys.exit("DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD must be set")

    with open(args.panel, encoding="utf-8") as f:
        definition = json.load(f)
    brand_re = re.compile(definition["brand_regex"], re.IGNORECASE)
    domain = definition["domain"].lower()
    panel_version = definition["panel_version"]
    PANEL = {p["id"]: (p["intent"], p["prompt"]) for p in definition["prompts"]}

    ids = list(PANEL) if args.prompts == "all" else [p.strip() for p in args.prompts.split(",")]
    unknown = [p for p in ids if p not in PANEL]
    if unknown:
        sys.exit(f"Unknown panel id(s): {unknown}")
    if not 1 <= args.samples <= 10:
        sys.exit("samples must be 1..10")

    web_search = not args.no_web_search
    started = datetime.now(timezone.utc).isoformat()
    records = []
    for pid in ids:
        intent, prompt = PANEL[pid]
        for s in range(1, args.samples + 1):
            tag = f"{pid}-s{s}"
            body = call_once(login, password, prompt, args.model, web_search)
            rec = extract(body)
            rec.update({"tag": tag, "panel_id": pid, "intent": intent, "prompt": prompt,
                        "named": bool(brand_re.search(strip_urls(rec["text"]))),
                        "cited_url": any(domain in u.lower() for u in rec["annotations"]),
                        "list_rank": rank_of_brand(rec["text"], brand_re),
                        "entries": entry_titles(strip_urls(rec["text"])),
                        "raw": body})
            records.append(rec)
            print(f"{tag}: status={rec['status_code']} named={rec['named']} "
                  f"cited={rec['cited_url']} rank={rec['list_rank']} "
                  f"entries={len(rec['entries'])} cost={rec['cost']}", file=sys.stderr)
            time.sleep(args.sleep)

    receipt = {
        "schema_version": 1,
        "panel_version": panel_version,
        "endpoint": ENDPOINT,
        "model_requested": args.model,
        "web_search_requested": web_search,
        "samples_per_prompt": args.samples,
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "total_cost_usd": round(sum(r["cost"] or 0 for r in records), 6),
        "records": records,
    }
    with open(args.raw_out, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, ensure_ascii=False)

    lines = [f"# GEO panel {started[:10]} — panel {receipt['panel_version']}", "",
             f"Endpoint `{ENDPOINT}`, model requested `{args.model}`, "
             f"`web_search={str(web_search).lower()}`, {args.samples} samples per prompt.",
             f"Raw receipt: `{os.path.basename(args.raw_out)}`. "
             f"Total cost {receipt['total_cost_usd']} USD.", "",
             "| tag | prompt | status | web_search | named | cited | list rank | entries | annotations | cost |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in records:
        lines.append(
            f"| {r['tag']} | {r['panel_id']} | {r['status_code']} | {r['web_search']} | "
            f"{'yes' if r['named'] else 'NO'} | {'yes' if r['cited_url'] else 'NO'} | "
            f"{r['list_rank'] if r['list_rank'] else '-'} | {len(r['entries'])} | "
            f"{len(r['annotations'])} | {r['cost']} |")
    lines.append("")
    for pid in ids:
        rs = [r for r in records if r["panel_id"] == pid]
        named = sum(1 for r in rs if r["named"])
        first = sum(1 for r in rs if r["list_rank"] == 1)
        ranks = ", ".join(str(r["list_rank"]) if r["list_rank"] else "-" for r in rs)
        cited = sum(1 for r in rs if r["cited_url"])
        lines.append(f"- **{pid}** ({PANEL[pid][1]}): named {named}/{len(rs)}, "
                     f"cited {cited}/{len(rs)}, #1 in {first}/{len(rs)}, ranks [{ranks}]")
        for r in rs:
            lines.append(f"    - {r['tag']} entries: " +
                         (" > ".join(r["entries"]) if r["entries"] else "(no enumerable list)"))
    out = "\n".join(lines) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        print(out)


if __name__ == "__main__":
    main()
