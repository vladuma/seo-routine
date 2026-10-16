# Implementation, publishing and live verification

## Implement within scope

Read the project's own instructions before editing (content rules, authored dates, redirect and removal
conventions). Use the existing task worktree, or create an isolated one when necessary, based on the
configured `base_branch`. Never hardcode `master` or `main`. Inspect concurrent state and preserve
unrelated edits. `--dry-run` produces a diff and plan with no commits, push or deployment.

Verify current competitor and product claims from authoritative sources and record the URL and check
date. Check every setup recipe and plan-limit claim against the code or documentation that *consumes* the
value, not only the table that stores it: an entitlement value is not a behavior, and a correctly read
number can still produce a false sentence. Preserve the original `published_at`. A meaningful edit gets
its real authored `updated_at`, and historical lastmod debt is fixed from evidence of actual edits, not a
bulk "today" bump. HTML, JSON-LD and generated AI text must agree. Structured-data strings are a second
rendering surface: markup that renders fine in the page can survive literally into the JSON-LD, so test
the schema output, not only the page. Keep implementation details out of reader copy.

Run the checks that fit the touched surfaces and the repository's required gates. Resolve failures inside
the scope. An unresolved QA failure stops publication. A local build proves local correctness, not
deployed state. Record the exact checked commit and the commands and results in `changes.md`.

## Independent review

Before publishing content changes, and before any autonomous publisher action, run a fresh read-only
adversarial reviewer that is independent of the author. Give it the current diff against the configured
base, the plan, the sources and the QA results. It checks factual accuracy, unsupported competitor
negatives, misleading comparison criteria, source quality, reader intent, counts and headings, date
integrity, scope, measurement claims and agreement between HTML, schema and generated text. The format
fits the task, not a mandatory verdict/table/FAQ recipe. Technical diffs also get the repository's
applicable code review.

Reviewer output is `PASS` or `BLOCK`, with evidence-backed blocking findings and nonblocking notes. Fix
real findings *and their sibling cases in the diff*, rerun the relevant checks, and use a fresh reviewer,
capped at three rounds. A reviewer failure or an unresolved blocker leaves the change `blocked_review`,
and it is not published. Reviewers cannot edit, commit or switch branches. Verify that branch and commit
state are unchanged after review, and report a violation instead of resetting another agent's work.
Passing review does not grant permission for an external action the user or workflow never authorized.

For a configured PR review, inspect the review on the **current** commit. Validate each finding against
the code, fix real P1/P2 issues and their related occurrences, and resume review on the new commit
(maximum three cycles). A pending review is `review_pending`, not clean. Content-only changes may use the
independent content review alone when repository rules permit. Code is never relabeled as content to
skip a gate, and authorizing implementation never means changing review requirements or merging a PR.

## Publish only the authorized action

Publisher configuration describes the intended workflow. Session instructions can restrict or override
it. `auto` means run the configured action when it is authorized and reviewed. `require` uses an
existing session authorization when that suffices, and otherwise presents the concrete reviewed result
for the missing action. `autonomous` mode does not expand permissions beyond the configured publisher. A
PR publisher creates a PR and stops at the merge boundary unless merge and deploy are also authorized.

If a push to the base branch deploys production, treat the push as the deployment. Follow the
repository's delivery rules, and never bypass hooks or push to the base branch because a config says
"autopilot". A request to commit only stays local. If push or PR is authorized, complete it and verify the
remote branch and PR URL. If it is not, report `local_only` with the reason, not success. Pass PR bodies
as a file or structured argument with an explicit base and head. Do not interpolate Markdown into a
shell string.

Record these milestones independently, each with evidence:

| Delivery state | Required evidence |
|---|---|
| `local_only` | Local branch and exact commit/diff, remaining action |
| `blocked_review` / `review_pending` | Findings, or the pending current-commit review |
| `pr_open` | Remote branch SHA and the actual PR URL; no deployment claimed |
| `merged` | Merge SHA; production job status is still separate |
| `deployed` | A successful applicable production run and the observed deployed SHA and time |
| Live verification `pending` / `passed` / `failed` | Timestamped checks of the changed production behavior |

A publisher's zero exit status proves its own action only. Changes that are not deployed or not
live-verified cannot start a post-deploy outcome window. Resume at the pending milestone rather than
reopening duplicate PRs or repeating mutations, and keep pending work in the ledger and the dated summary.

## Mandatory live verification after deployment

Inspect the changed public URLs and the dependent surfaces the change touches: status and redirect
destination, canonical, robots and indexability, body and title claims, JSON-LD, sitemap lastmod,
generated `llms` routes and CTA behavior. Use a live browser for viewport or click tracking changes, and
inspect the observed payloads and the collection response, not merely that the script is present. Never
fabricate signup or paid events to prove analytics. For content, verify the changed passage on the
deployed URL and in the rendered schema.

Record expected and observed values, `checked_at`, the deployed SHA and time, and the evidence in
`verify.md` and the ledger. A 404, 5xx, stale passage, wrong canonical or missing event is `failed`, with
the precise limitation. If deployment is not authorized or complete, record `pending` with the next
required action. A PR or local preview is never a live PASS. Outage symptoms go through the project's
production incident process; a verification task does not authorize restarts or remote fixes.

The first measurement window begins after successful live verification and the declared washout or
full-day boundary. Record propagation uncertainty. Keep partial-day telemetry for diagnosis without
folding it into a comparison that is supposed to be complete. Summaries separate implementation,
delivery, verification and business outcome, and name the remaining work candidly.

## Verification checklist by change type

Build the checklist from the changesets. Universal checks on every changed page: HTTP 200, a present and
correct canonical, no unintended `noindex`, no broken internal links on the page and parseable JSON-LD.

| Change | Also check |
|---|---|
| Meta rewrite | `<title>` and description match the intended values |
| FAQ or schema change | The section exists in the HTML and the JSON-LD has the expected `@type` and required fields |
| Content update | Key phrases and sections are present on the deployed URL |
| New page | 200 (not 404/5xx), real content length, present in the sitemap |
| Redirect or removal | Old URL returns 301/302 with the expected `Location` (inspect headers without following) |
| Sitemap or robots | Expected URLs and rules are present or removed |
| Images | Alt text and lazy-loading attributes present |

Rate-limit checks against your own site to 2 requests per second.

