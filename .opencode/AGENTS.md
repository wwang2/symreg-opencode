# git-evolve Agents

Agent discovery index. Each agent is defined in `agents/<name>.md` with YAML frontmatter.

## Agent Roster

| Agent | Model | Mode | Role | Spawned by |
|-------|-------|------|------|------------|
| [orbit-agent](agents/orbit-agent.md) | opus | background | Run experiments in isolated orbit worktrees | /research Step 5 |
| [orbit-reviewer](agents/orbit-reviewer.md) | sonnet | background | Advisory quality notes on completed orbits | agent-complete hook |
| [campaign-reviewer](agents/campaign-reviewer.md) | opus | foreground | Cross-orbit synthesis at milestones, triage, hypothesis generation | /research Step 3 |
| [brainstorm-panel](agents/brainstorm-panel.md) | opus | background | Cross-debate idea generation with confidence ratings | /research Step 3 |
| [debate-swarm](agents/debate-swarm.md) | sonnet | foreground | Unanimous vote on problem statement and eval design | /launch Phase 2 |

## Mechanical (Not Agents)

| Check | Location | Trigger | Purpose |
|-------|----------|---------|---------|
| eval-check | `agent-complete.mjs` hook | Orbit agent completes | Re-run evaluator.py, verify claimed metric |
| cross-validation | `agent-complete.mjs` hook | All replicas complete | Compare metrics across N parallel agents |

## Dispatch

All agents are spawned via Claude Code's native `Task()` / `Agent()` tools:

```
Agent(prompt="Read agents/<name>.md for your instructions. ...",
      model="<from research/config.yaml agents.<name>.model>",
      run_in_background=<true for background, false for foreground>)
```

Model resolution order:
1. `research/config.yaml → agents.<name>.model` (campaign-level override)
2. `RE_*` env vars (session-level override)
3. Agent spec frontmatter `model:` field (default)

## Parallel Cross-Validation

When `execution.parallel_agents > 1` in config:
- N agents work independently on the same hypothesis
- Each on its own branch: `orbit/<NN>-<name>`, `orbit/<NN>-<name>.r1`, ...
- Same GitHub Issue tracks all replicas
- agent-complete hook compares metrics when all N finish
- Consistent → pick best as primary. Divergent → flag `needs-human-review`

## Evolutionary Design Synthesis

For eval construction and agent spec design (`execution.design_iterations > 1`):
1. DIVERGE: N agents independently design/implement
2. COMPARE: Analyze strengths of each
3. SYNTHESIZE: Combine best patterns into one
4. VALIDATE: Test synthesized version against all originals
5. ITERATE: Repeat if `design_iterations > 1`
