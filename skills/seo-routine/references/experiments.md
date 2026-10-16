# Planning and outcome review

## Select an experiment

Read config priorities, current goals, prior dated evidence and the experiment ledger. The content budget
is a **maximum, not a quota**: choose zero when measurement is missing, delivery is still pending, or the
expected benefit is weaker than an experiment already running. Verified correctness repairs (broken URLs,
inaccurate claims, measurement defects) are recorded as repairs, not dressed up as growth experiments.

Prefer meaningful acquisition and completed signup or activation outcomes when they are observable.
Query-specific rank, qualified entries and citation accuracy can serve as leading measures. Label them
as such. Inspect query intent before changing a tutorial into a comparison page. Use title, FAQ, schema
or length changes only when they serve the reader or a verified search requirement. There is no universal
CTR-by-rank target, word-count minimum, required FAQ, anchor-text percentage or guaranteed GEO uplift.

Some query clusters are intent-locked: if a full-depth pull shows a cluster returning no clicks and the
SERP rewards a different format, retire it as a target instead of repeating the attempt.

Before editing, record one falsifiable mechanism and its primary outcome, with baseline and target from
the same metric definition, unit, cohort, timezone and window length. Choose a horizon and sufficient
exposure for the decision at hand, and avoid a threshold that one incidental visit can satisfy. Treat
small samples as uncertain even when a predeclared operational threshold is missed. Note pending changes
on the same surface and any concurrent deployment that could confound the result.

A plan names the pages and files, supporting sources, intended reader behavior, expected outcome, checks,
rollback scope and the work deliberately deferred. Work the user already authorized proceeds to
implementation. A plan-only request ends with the reviewable plan. Publishing is governed by
[delivery](delivery.md), not by a second generic approval gate here.

## Experiment ledger

`seo-config.md` names the ledger file (default `experiments.json`). It is an object with `schema_version`
and an `experiments` array; `templates/experiments.json` shows the shape. Check all existing IDs and
semantic duplicates before appending. Allocate IDs as `seo-YYYY-MM-DD-<descriptive-slug>`. Several primary
metrics need distinct prediction IDs inside **one** experiment, not duplicate experiments. A carry-forward
updates the existing record's status and appends to its history. It never creates another counted
prediction.

Each experiment records:

- `id`, `created_at`, `kind` (`growth`, `maintenance` or `repair`), `hypothesis`, `paths`, `evidence`.
- `predictions`: a unique `id`, `metric`, `direction` (`increase` or `decrease`), numeric `baseline` and
  `target`, `baseline_window`, `cohort_definition`, `measurement_version` and a `primary` or `guardrail`
  role. Define the exact comparator, minimum exposure or precision and evaluation horizon before
  deployment. Categorical repairs use an explicit `pass_condition` instead of a forced numeric score.
- `delivery`: `status`, `branch`, `commit_sha`, `pr_url`, `deployed_sha`, `deployed_at`, plus
  `verification` with status, checked URLs, `checked_at` and evidence. Unknown values stay `null`.
- `evaluation`: planned date, actual post-deploy window, source artifacts, actual values and exposure,
  status and reason, `evaluated_at`. `history` preserves every amendment with its reason and timestamp.

Delivery, verification and outcome are separate fields. `pr_open` is not `deployed`, a local check is not
live verification, and a technically successful repair is not evidence of traffic uplift.

### Legacy logs

A pre-v4 `forward-log.md` and scorecard stay as historical evidence. Before scoring a legacy prediction,
map its action, page, metric and deployment to exactly one ledger ID, link the original rows, flag
duplicate and carry rows, and recover the original baseline definition. If provenance or deployment
cannot be recovered, record `unscorable` with the missing evidence. Never silently rewrite past rows,
retarget a prediction after seeing results, or count the same deployment twice in current accuracy. New
records use actual dates even when legacy labels were shifted by one ISO week.

## Score direction, not magnitude

Evaluate only after verified production exposure and the declared horizon both exist. A failed source, an
incomplete window, a changed metric version, an unidentified deployment or inadequate planned exposure
produces `pending`, `insufficient_evidence`, `confounded` or `unscorable`, with a reason. None of those is
a Hit.

For numeric **growth** predictions whose baseline has not already met the target:

```python
sign = 1 if direction == "increase" else -1
required_progress = sign * (target - baseline)
assert required_progress > 0  # otherwise the baseline already met the target, or the direction is wrong
progress = sign * (actual - baseline)
fraction = progress / required_progress
hit = actual >= target if direction == "increase" else actual <= target
status = "Hit" if hit else "Partial" if fraction >= partial_threshold else "Miss"
```

Use the predeclared comparator for strict boundaries. `partial_threshold` comes from config and is fixed
at planning time. Example: for a position target (`decrease`) with baseline 20 and target 10, an actual
of 25 is a regression (fraction −0.5) and so a Miss, while 15 is 50% progress and so Partial at a 0.5
threshold. Never use the absolute size of the change: it rewards movement in the wrong direction.

If the baseline already meets the target, mark a proposed growth prediction invalid *before* work. A
legitimate "stay at #1" objective is maintenance or a guardrail with its own reporting, and it
contributes no growth Hit. Multi-condition outcomes declare their aggregation rule before deployment.
Assess every condition, and never replace a failed primary outcome with a successful guardrail.

Report Hit, Partial and Miss counts separately. `growth_hit_rate = Hit / (Hit + Partial + Miss)` over
unique, evaluable growth predictions. Also report the eligible denominator, the exclusions and the
Partial count. If nothing is evaluable the rate is unavailable. Maintenance and repairs get their own
pass/fail reporting. Even a Hit in an observational experiment does not prove causation.

## Close the loop

Write a dated review with the original prediction, the actual count or rate, the window, the uncertainty
and the strongest alternative explanation. Update the same ledger record. Record durable decisions in
the repo's config and put their evidence in the learnings file. Agent memory may point there but cannot
override it. Do not auto-tune scoring weights from a handful of heterogeneous predictions. Revisit a
paused page when new evidence changes its priority instead of declaring low-volume pages permanently
unable to convert.

**A retraction is not done until it reaches the file the next run reads first.** Learnings accumulate and
a dated analysis is a point-in-time record, but the next run starts from the state or follow-ups block.
Correcting a wrong claim elsewhere and leaving the original wording there is a contradiction the next run
will resolve in favor of the stale copy. Grep every artifact for the original wording and write the
correction as an explicit `RETRACTION:` clause. Do not overwrite silently.

**An unsaved observation is not evidence.** A number that exists only as terminal output cannot be
checked once the turn ends. Any claim that goes into an artifact needs the producing call to have written
a file under the run's `inputs/` first, cited by name. If the measurement is cheap, re-run it to save it
rather than quote an unsaved run.
