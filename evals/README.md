# Evals

Empty by design, and the most valuable gap in this repo.

Each skill should have a slice of question/answer pairs that would fail without
the skill and pass with it. Until those exist, every claim this pack makes about
improving accuracy is an assertion rather than a measurement.

## Layout

```
evals/
├── causal-claim-guardrail/evals.json
├── uncertainty-reporting/evals.json
└── warehouse-navigation/evals.json
```

## Rules

- **Pin ground truth.** Anchor to a snapshot date, write against a stable fact
  table, or grade the agent's query rather than its number. An eval written
  against live data goes stale the moment the number moves.
- **Verify the eval discriminates.** An eval that passes with and without the
  skill is testing nothing. Run the baseline.
- **Store results like telemetry, not test logs.** Skill version, git SHA, model
  ID, per-assertion pass/fail. "Did that change help?" should be a query.

See `CONTRIBUTING.md` for the JSON schema.
