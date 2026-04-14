# Orbit Lifecycle — Shared Mechanics

Canonical reference for orbit operations. All skills (/launch, /research, /ultra-research, /autorun) MUST follow these exact commands. Do not reinvent — reference this document.

## 1. Create Per-Orbit Issue

```bash
ORBIT_NAME="<NN>-<name>"   # Orbits are numbered sequentially: 01, 02, 03, ...
STRATEGY="<one-line strategy>"
REPO_URL=$(gh repo view --json url --jq '.url')
ISSUE_URL=$(gh issue create \
  --title "[Orbit] ${ORBIT_NAME}: ${STRATEGY}" \
  --label "orbit,experiment,proposed" \
  --body "Strategy: ${STRATEGY}
Parents: <parent orbit names, or 'none (root)'>
Eval version: eval-v1

**Branch:** [orbit/${ORBIT_NAME}](${REPO_URL}/tree/orbit/${ORBIT_NAME})
**Code:** [solution.py](${REPO_URL}/blob/orbit/${ORBIT_NAME}/orbits/${ORBIT_NAME}/solution.py)
**Log:** [log.md](${REPO_URL}/blob/orbit/${ORBIT_NAME}/orbits/${ORBIT_NAME}/log.md)")
ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -o '[0-9]*$')
echo "Created Issue #${ISSUE_NUMBER} for orbit/${ORBIT_NAME}"
```

**MANDATORY.** Never spawn an orbit without an Issue.

## 2. Create Worktree + Scaffold

```bash
git worktree add .worktrees/${ORBIT_NAME} -b orbit/${ORBIT_NAME}
mkdir -p .worktrees/${ORBIT_NAME}/orbits/${ORBIT_NAME}/figures
```

## 3. Initialize log.md

```bash
cat > .worktrees/${ORBIT_NAME}/orbits/${ORBIT_NAME}/log.md << EOF
---
issue: ${ISSUE_NUMBER}
parents: []
eval_version: eval-v1
metric: null
---

# Research Notes
EOF
```

## 4. Commit + Push Scaffold

```bash
cd .worktrees/${ORBIT_NAME}
git add orbits/${ORBIT_NAME}/
git commit -m "initialize orbit ${ORBIT_NAME}"
git push -u origin orbit/${ORBIT_NAME}
cd -
```

## 5. Update Labels

```bash
gh issue edit ${ISSUE_NUMBER} --add-label "exploring" --remove-label "proposed"
```

## 6. Spawn Agent

```
Agent(prompt="
  Read agents/orbit-agent.md for your full instructions.

  You are working on orbit/${ORBIT_NAME} in worktree .worktrees/${ORBIT_NAME}.
  Your workspace is orbits/${ORBIT_NAME}/ — write ALL files there.

  Hypothesis: ${STRATEGY}
  Issue: #${ISSUE_NUMBER} — post updates and figure embeds here
  Eval: research/eval/evaluator.py --solution <your solution.py> --seed <N>
  Eval prints METRIC=<float> to stdout.
  Style: Read research/style.md BEFORE generating any figures.

  REQUIREMENTS (the hooks enforce these):
  1. Name your solution file solution.py
  2. Generate ≥1 figure in orbits/${ORBIT_NAME}/figures/ following research/style.md
  3. Update log.md metric field with mean across 3+ seeds
  4. Commit and push ALL work before exiting
  5. Post a summary comment to Issue #${ISSUE_NUMBER}
", model="opus", run_in_background=true)
```

## 6b. Parallel Agents / Cross-Validation (if parallel_agents > 1)

Read `parallel_agents` from `research/config.yaml` (under `execution.parallel_agents`).

If `parallel_agents == 1`: skip this section — Steps 1-6 spawn a single agent.

If `parallel_agents > 1`: spawn N agents for the SAME hypothesis, each on its own branch:

```bash
# Primary agent (Step 6 above) is on orbit/${ORBIT_NAME}
# Replicas get .rN suffix:
for i in $(seq 1 $((PARALLEL_AGENTS - 1))); do
  REPLICA_NAME="${ORBIT_NAME}.r${i}"
  
  # Create replica worktree
  git worktree add .worktrees/${REPLICA_NAME} -b orbit/${REPLICA_NAME}
  mkdir -p .worktrees/${REPLICA_NAME}/orbits/${ORBIT_NAME}/figures
  
  # Copy log.md scaffold (same Issue number — all replicas share one Issue)
  cp .worktrees/${ORBIT_NAME}/orbits/${ORBIT_NAME}/log.md \
     .worktrees/${REPLICA_NAME}/orbits/${ORBIT_NAME}/log.md
  
  cd .worktrees/${REPLICA_NAME}
  git add orbits/${ORBIT_NAME}/
  git commit -m "initialize replica ${REPLICA_NAME}"
  git push -u origin orbit/${REPLICA_NAME}
  cd -
  
  # Spawn replica agent (same prompt, different branch)
  Agent(prompt="
    Read agents/orbit-agent.md for your full instructions.
    You are working on orbit/${REPLICA_NAME} (replica of ${ORBIT_NAME}).
    Your workspace is orbits/${ORBIT_NAME}/ — write ALL files there.
    Hypothesis: ${STRATEGY}
    Issue: #${ISSUE_NUMBER}
    Eval: research/eval/evaluator.py --solution <your solution.py> --seed <N>
    Style: Read research/style.md BEFORE generating any figures.
    REQUIREMENTS (the hooks enforce these):
    1. Name your solution file solution.py
    2. Generate ≥1 figure in orbits/${ORBIT_NAME}/figures/
    3. Update log.md metric field with mean across 3+ seeds
    4. Commit and push ALL work before exiting
    5. Post a summary comment to Issue #${ISSUE_NUMBER}
  ", model="opus", run_in_background=true)
done
```

**Cross-validation happens automatically** in `agent-complete.mjs` with 3-tier resolution:

```
Tier 1: CONSISTENT (spread < ε, default ε = 0.001)
  → Post RE:CROSSVAL Result: CONSISTENT
  → Pick best metric as primary
  → High confidence — move on

Tier 2: SOFT DIVERGENCE (ε ≤ spread < 10ε)
  → Post RE:CROSSVAL Result: SOFT_DIVERGE
  → Pick best metric, but note the spread
  → "Results differ slightly — best picked, but review at milestone"
  → campaign-reviewer sees this at next milestone

Tier 3: HARD DIVERGENCE (spread ≥ 10ε)
  → Post RE:CROSSVAL Result: DIVERGENT
  → DO NOT pick a winner yet
  → Re-run eval-check on BOTH with fresh seeds (4, 5, 6)
  → If re-run confirms both:
      Keep both, let campaign-reviewer decide at milestone
      Different approaches can produce different metrics legitimately
  → If re-run fails one (metric changes significantly):
      Discard the unstable one, keep the stable one
      Label unstable: +needs-human-review
  → If re-run fails both:
      Label hypothesis: +dead-end
      Both solutions are unreliable
  → Post detailed findings to Issue
```

**Why not just flag everything as "needs-human-review"?**
In autonomous mode (/ultra-research, /autorun) there is no human. The resolution must be mechanical. Tier 1+2 are auto-resolved. Tier 3 uses re-evaluation as a tiebreaker — if the eval harness is deterministic (which we stress-test during /launch), re-running on fresh seeds separates stable solutions from flaky ones.

## 7. Eval-Check (after agent completes)

Run explicitly as backup — hooks may not fire in all modes.

```bash
EVAL_PATH="research/eval/evaluator.py"
SOLUTION_PATH="orbits/${ORBIT_NAME}/solution.py"
REPO_URL=$(gh repo view --json url --jq '.url')

if [ -f "$EVAL_PATH" ] && [ -f "$SOLUTION_PATH" ]; then
  echo "Running eval-check for orbit/${ORBIT_NAME}..."
  METRICS=""
  for SEED in 1 2 3; do
    RESULT=$(python3 "$EVAL_PATH" --solution "$SOLUTION_PATH" --seed $SEED 2>/dev/null | grep "METRIC=")
    METRICS="${METRICS} ${RESULT}"
    echo "  Seed ${SEED}: ${RESULT}"
  done

  MEAN_METRIC=$(echo "$METRICS" | grep -oP 'METRIC=\K[0-9.eE+-]+' | awk '{s+=$1; n++} END {if(n>0) printf "%.6f", s/n}')
  echo "  Mean metric: ${MEAN_METRIC}"

  # Post RE:EVAL comment
  if [ -n "$ISSUE_NUMBER" ] && [ -n "$MEAN_METRIC" ]; then
    gh issue comment ${ISSUE_NUMBER} --body "<!-- RE:EVAL orbit=${ORBIT_NAME} -->
## Eval Check
**Result:** VERIFIED
**Measured:** ${MEAN_METRIC}
**Seeds:** 3/3
**Evaluator:** eval-v1

**Branch:** [orbit/${ORBIT_NAME}](${REPO_URL}/tree/orbit/${ORBIT_NAME})
**Solution:** [solution.py](${REPO_URL}/blob/orbit/${ORBIT_NAME}/orbits/${ORBIT_NAME}/solution.py)"
    echo "Posted RE:EVAL to Issue #${ISSUE_NUMBER}"
  fi
fi
```

## 8. Label Updates (after eval-check)

```bash
gh issue edit ${ISSUE_NUMBER} --add-label "evaluated"

TARGET=$(python3 -c "import yaml; c=yaml.safe_load(open('research/config.yaml')); print(c.get('metric',{}).get('target',''))" 2>/dev/null)
DIRECTION=$(python3 -c "import yaml; c=yaml.safe_load(open('research/config.yaml')); print(c.get('metric',{}).get('direction','minimize'))" 2>/dev/null)

if [ "$DIRECTION" = "minimize" ] && [ -n "$TARGET" ]; then
  python3 -c "exit(0 if float('${MEAN_METRIC}') <= float('${TARGET}') else 1)" 2>/dev/null && \
    gh issue edit ${ISSUE_NUMBER} --add-label "winner"
elif [ "$DIRECTION" = "maximize" ] && [ -n "$TARGET" ]; then
  python3 -c "exit(0 if float('${MEAN_METRIC}') >= float('${TARGET}') else 1)" 2>/dev/null && \
    gh issue edit ${ISSUE_NUMBER} --add-label "winner"
fi
```

## 9. Cache Refresh

```bash
python3 $PLUGIN_ROOT/scripts/campaign_context.py refresh ${ORBIT_NAME} --repo-root .
```

---

## Campaign Setup (shared across /launch and /autorun)

### GitHub Labels (exact 11 commands)

```bash
gh label create "orbit" --color "0075ca" --force 2>/dev/null
gh label create "campaign" --color "d73a4a" --force 2>/dev/null
gh label create "experiment" --color "a2eeef" --force 2>/dev/null
gh label create "proposed" --color "e4e669" --force 2>/dev/null
gh label create "exploring" --color "f9d0c4" --force 2>/dev/null
gh label create "evaluated" --color "bfdadc" --force 2>/dev/null
gh label create "promising" --color "0e8a16" --force 2>/dev/null
gh label create "dead-end" --color "b60205" --force 2>/dev/null
gh label create "winner" --color "fbca04" --force 2>/dev/null
gh label create "concluded" --color "5319e7" --force 2>/dev/null
gh label create "needs-human-review" --color "d93f0b" --force 2>/dev/null
```

### Campaign Issue Template

```bash
REPO_URL=$(gh repo view --json url --jq '.url')
CAMPAIGN_URL=$(gh issue create \
  --title "[Campaign] <research question>" \
  --label "campaign" \
  --body "## Research Question
<from problem.md>

## Teaser
![teaser](${REPO_URL}/raw/main/research/figures/teaser.png)

## Config
- Metric: <name> (<direction>)
- Target: <target>
- Eval version: eval-v1
- Budget: <max_orbits> orbits")
CAMPAIGN_NUMBER=$(echo "$CAMPAIGN_URL" | grep -o '[0-9]*$')
```

### Config v2 Schema

```yaml
metric:
  name: "<metric_name>"
  direction: <minimize or maximize>
  target: <target_value or null>
  min_relative_improvement: 0.1

baselines:
  baseline: <value>

eval:
  timeout: 60
  seeds: 3

execution:
  parallel_agents: 1
  budget: null
  max_orbits: 10
  milestone_interval: 3
  design_iterations: 1
  brainstorm_debate_rounds: 2

agents:
  orbit-agent: { model: opus }
  campaign-reviewer: { model: opus }
  orbit-reviewer: { model: sonnet }
  brainstorm-panel: { model: opus }
  debate-swarm: { model: sonnet }
```

---

## Mode Differences

| Step | /launch | /research | /ultra-research | /autorun |
|------|---------|-----------|-----------------|----------|
| Problem definition | Interactive | — | — | From prompt |
| Eval construction | Interactive + debate-swarm | — | — | Auto (N agents) |
| Config | Interactive | — | — | Auto (template) |
| Teaser figure | Interactive | — | — | Auto |
| Hypothesis generation | — | Campaign-reviewer | Campaign-reviewer | Auto |
| **Human gate: approve hypothesis** | — | **YES** | No | No |
| Orbit spawn | — | Steps 1-9 above | Steps 1-9 above | Steps 1-9 above |
| **Human gate: milestone steering** | — | **YES** | No | No |
| Eval-check | — | Step 7 | Step 7 | Step 7 |
| Label updates | — | Step 8 | Step 8 | Step 8 |
| Graduation | /graduate (manual) | /graduate (manual) | Suggested | Suggested |
