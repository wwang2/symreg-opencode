# git-evolve

Simpler parallel, agent-native research plugin. Treats research as evolutionary search: N independent agents → compare → synthesize → iterate.

## Core Concepts

- **Orbit**: A git branch (`orbit/<name>`) where an agent runs one experiment. Each orbit has a GitHub Issue and a `log.md` with 4 frontmatter fields: `issue`, `parents`, `eval_version`, `metric`.
- **Eval harness**: Frozen evaluator (`research/eval/evaluator.py`) tagged as `eval-v1`. Produces a deterministic metric for any solution. Immutable after freeze.
- **Campaign**: A research project tracked by a Campaign Issue on GitHub. Config lives in `research/config.yaml`.
- **Milestone**: Every N completed orbits, `campaign-reviewer` synthesizes findings, triages orbits (EXPLORE/REFINE/EXTEND/CONCLUDE), and generates hypotheses.

## State Model

**Zero local state files.** All state is derived:
- Orbit status: derived from `<!-- RE:EVAL -->` Issue comment existence (no comment = running, comment = complete)
- Verdicts: no verdict gate — `orbit-reviewer` is advisory only
- Labels: derived from status + metric comparison (orchestrator/human decisions)
- Cache (`.re/cache/context.json`): rebuildable, gitignored, deletable. Run `python scripts/campaign_context.py rebuild` to regenerate.

## Agents (5 + 1 mechanical)

| Agent | Role | Model | Mode |
|-------|------|-------|------|
| orbit-agent | Run experiments in orbit worktrees | opus | background |
| orbit-reviewer | Advisory quality notes (non-blocking) | sonnet | background |
| campaign-reviewer | Cross-orbit synthesis at milestones | opus | foreground |
| brainstorm-panel | Cross-debate idea generation | opus | background |
| debate-swarm | Unanimous vote on problem/eval design | sonnet | foreground |
| eval-check (script) | Mechanical metric verification | n/a | hook |

## Hooks (4)

| Hook | Event | Purpose |
|------|-------|---------|
| session-start.mjs | SessionStart | Rebuild cache, audit for breakpoints, cleanup stale branches |
| scope-guard.mjs | PreToolUse | Scope isolation, orbit cap, budget warnings, anti-pattern blocks |
| post-tool.mjs | PostToolUse | Just-in-time prompt injection: validate config/log.md/evaluator writes, remind about solution.py naming, figure verification, Issue tracking |
| agent-complete.mjs | SubagentStop | Auto-commit, eval-check, labels, figure warning, dispatch reviewer |

## Key Patterns

### Parallel Cross-Validation
Configurable `parallel_agents` (default 1). When N > 1, N independent agents solve the same problem → compare results → select best. Applied to orbit execution, eval construction, and brainstorming.

### Evolutionary Design Synthesis
For eval construction and agent specs: N agents independently design → compare strengths → synthesize best patterns from each → iterate `design_iterations` times.

## Skills

| Skill | Purpose |
|-------|---------|
| /launch | Initialize campaign: problem, eval, config, GitHub setup |
| /research | Orchestrator loop: sweep → terminate? → milestone → hypothesize → spawn → harvest → loop |
| /ultra-research | Fully autonomous /research (no human gates) |
| /autorun | Zero-touch: problem in → results out (for benchmarks/validation) |
| /status | Leaderboard from context packet |
| /graduate | Merge winner orbit to main via git tag |
| /checkup | Consistency audit |
| /publish | Generate GitHub Pages visualization |
| /evaluate | Run eval on specific orbit |
| /brainstorm | Assemble cross-debate panel |
| /feedback | File improvement Issue |

## Directory Layout

```
agents/           # Agent specs (markdown)
skills/           # Skill definitions (SKILL.md per skill)
scripts/
  campaign_context.py   # Core state engine (rebuild/refresh/audit)
  hooks/                # 3 Node.js hooks
templates/        # Scaffolding for new campaigns
docs/             # Data contract, benchmarks
tests/            # Unit, hook, integration, LLM, benchmark tests
```

## Scope Guard Rules

- On `orbit/<name>` branch: agent can ONLY write to `orbits/<name>/`
- `research/` directory is read-only on orbit branches
- Max 5 unconcluded orbits at a time
- No label promotion until eval-check passes
