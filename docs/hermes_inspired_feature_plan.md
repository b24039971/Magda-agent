# Hermes-Inspired Feature Plan for Magda

Этот план описывает, какие идеи стоит позаимствовать из Hermes Agent и как адаптировать их под Magda, не превращая проект в копию Hermes.

Hermes силен как операционная система агента: skills, session search, gateway, slash commands, cron, subagents, profiles, diagnostics, trajectory compression. Magda должна взять эти механики, но встроить их в свою когнитивную метафору: память, внимание, подсознание, процедурное обучение, риск и личность.

## Что берем из Hermes

### 1. Skill Lifecycle: навыки, которые растут

Hermes делает акцент на closed learning loop: агент создает skills из опыта, улучшает их при использовании, сохраняет знания и ищет прошлые разговоры.

Для Magda это должно стать `Procedural Memory`.

Target architecture:

```text
task success
  -> evaluator score
  -> skill usage trace
  -> procedural memory candidate
  -> curator review
  -> skill draft
  -> sandboxed test
  -> registry activation
```

Magda modules:
- `magda_agent/procedures/`
- `magda_agent/skills/registry.py`
- `magda_agent/metacognition/evaluator.py`
- `magda_agent/subconsciousness/reflection.py`

Правило: skill не активируется только потому, что LLM его придумала. Он должен пройти curator step и test step.

### 2. Session DB and Search

Hermes использует SQLite-backed session store с FTS5 search. Для Magda это полезнее, чем сразу тащить все в ChromaDB.

Magda target:

```text
raw messages -> sqlite session log -> FTS search
important facts -> semantic memory / vector store
successful methods -> procedural memory
```

Почему так:
- SQLite проще дебажить;
- FTS хорошо работает для точного поиска по истории;
- vector memory остается для смыслового recall, а не для всего подряд;
- можно строить `/insights`, `/search`, `/timeline`.

### 3. Gateway and Cross-Platform Continuity

Hermes живет в CLI и messaging gateway: Telegram, Discord, Slack, WhatsApp, Signal and more.

Magda уже имеет Telegram, но ей нужен единый event model:

```text
Telegram message
Voice transcript
API call
Scheduled job
CI event
Jules event
Admin command
  -> UnifiedEvent
  -> Thalamus
  -> Salience
  -> Global Workspace
```

Это позволит не писать отдельную логику сознания для каждого канала.

### 4. Slash Commands and Control Surface

Hermes имеет shared slash command layer across CLI and messaging.

Magda должна получить команды:

- `/state` - internal state summary;
- `/tasks` - active agent/Jules tasks;
- `/memory search <query>` - search session memory;
- `/skills` - list available skills;
- `/skill enable|disable <name>` - tool governance;
- `/reflect` - trigger subconscious reflection;
- `/profile` - show user model;
- `/stop` - interrupt long task;
- `/risk` - explain current risk gates;
- `/doctor` - diagnose environment and dependencies.

Это не UI-фича. Это управляющая поверхность мозга.

### 5. Cron and Scheduled Automations

Hermes ships unattended scheduled automations.

Magda target:

```text
Pineal Gland
  -> circadian schedule
  -> cron jobs
  -> subconscious reflection
  -> memory consolidation
  -> weekly audit
  -> Jules task replenishment
```

Examples:
- nightly memory consolidation;
- weekly architecture audit;
- daily failed CI summary;
- periodic skill curator run;
- user reminders.

### 6. Subagents and Parallel Workstreams

Hermes can delegate and parallelize. Magda should not let the main consciousness do every job.

Target subagents:

- `CriticAgent` - reviews PRs, plans and architecture risks;
- `ResearchAgent` - gathers external references and options;
- `TestAgent` - writes and runs tests;
- `MemoryCuratorAgent` - consolidates memory;
- `SkillCuratorAgent` - proposes/refines skills;
- `JulesSupervisorAgent` - watches autonomous improvement loop.

Basal Ganglia should choose whether to answer directly or spawn a subagent.

### 7. Trajectory Compression

Hermes has research tooling around trajectory compression. Magda needs this for self-improvement.

Target:

```text
full task trajectory
  -> compact narrative
  -> failures
  -> decisions
  -> commands run
  -> tests passed/failed
  -> lessons
  -> reusable procedure candidate
```

This feeds:
- Subconsciousness;
- Procedural Memory;
- Jules task generation;
- evaluator feedback.

### 8. Profiles and User Model

Hermes is profile-aware and has user modeling. Magda should make this more explicit because personality and attachment are core to the project.

Magda user model:

```json
{
  "user_id": "telegram:123",
  "communication_style": "direct",
  "detail_preference": "deep",
  "risk_preference": "experimental",
  "trust_level": "friend",
  "topics": ["agents", "biology", "self-improvement"],
  "do_not_do": ["ask what next when task queue has safe work"]
}
```

This is not MBTI cosplay. It is operational personalization.

### 9. Diagnostics: doctor command

Hermes has a strong developer UX around setup and diagnostics. Magda needs `/doctor`.

Checks:
- required env vars;
- missing dependencies;
- platform compatibility;
- ChromaDB availability;
- API health;
- Telegram bot token;
- sandbox support;
- speech optional deps;
- task manifest validity;
- current git remotes and PR status.

### 10. Plugin and Optional Skill Boundary

Hermes separates built-in tools, optional skills and plugins.

Magda target:

```text
core skills: safe, always available
optional skills: require explicit enable
external-effect skills: require policy approval
experimental skills: disabled by default
```

This is the missing safety boundary around `programmer`, `internet_search`, `omnichannel_send`, future image/news/weather/home skills.

## Implementation Phases

### Phase A: Control and Observability

Goal: make the agent inspectable and controllable.

Tasks:
- unified command registry;
- `/doctor`;
- `/skills`;
- `/tasks`;
- `/memory search`;
- task manifest status commands.

Why first:
- autonomous systems need brakes, gauges and logs before deeper autonomy.

### Phase B: Durable Session Memory

Goal: separate raw history from semantic memory.

Tasks:
- SQLite `SessionStore`;
- message table;
- FTS search where available;
- fallback LIKE search if FTS is unavailable;
- `/memory search`;
- session summaries.

Why:
- ChromaDB should not be the only debugging source of truth.

### Phase C: Skill Governance

Goal: skills become explicit capabilities, not arbitrary functions.

Tasks:
- skill metadata;
- enabled/disabled state;
- risk level per skill;
- required env vars;
- policy check before execution;
- optional skill registry.

Why:
- planner-generated tool calls are currently too trusted.

### Phase D: Procedural Memory and Skill Curator

Goal: learn reusable actions from successful work.

Tasks:
- record skill traces;
- evaluator score integration;
- propose procedure candidates;
- curator review;
- archive stale procedures;
- activate stable skills.

Why:
- this is where Magda becomes self-improving rather than just task-running.

### Phase E: Scheduled Internal Life

Goal: the agent has a rhythm.

Tasks:
- scheduler service;
- nightly reflection;
- weekly audit;
- Jules queue replenishment job;
- memory compaction;
- optional user reminders.

Why:
- "subconsciousness" should run even without a user message.

### Phase F: Subagents

Goal: separate roles instead of one god loop.

Tasks:
- subagent interface;
- critic agent;
- researcher agent;
- test agent;
- memory curator agent;
- result aggregation.

Why:
- complex work should not block the main conversation loop.

### Phase G: UI and Gateway Expansion

Goal: make Magda live where the user works.

Tasks:
- unified event model;
- gateway adapters;
- CLI control surface;
- admin API;
- platform-specific command help;
- voice continuity.

Why:
- the agent should have one mind across many channels.

## Feature Map to Biology

| Hermes pattern | Magda brain metaphor | Engineering module |
|---|---|---|
| Session search | Hippocampus | `memory/session_store.py` |
| Skill curator | Cerebellum + Subconsciousness | `procedures/curator.py` |
| Tool governance | Amygdala | `safety/risk_system.py` |
| Slash commands | Motor cortex / executive control | `commands/registry.py` |
| Gateway | Thalamus | `events/unified_event.py` |
| Cron | Pineal gland | `scheduling/scheduler.py` |
| Subagents | Cortical columns / specialist circuits | `agents/subagents.py` |
| Trajectory compression | Sleep consolidation | `subconsciousness/trajectory.py` |
| User profiles | Attachment + social cognition | `user_model/profile.py` |
| Doctor command | Homeostatic health check | `diagnostics/doctor.py` |

## What Not To Copy

- Do not copy Hermes monolithic agent loop patterns into Magda.
- Do not add massive dependencies before the core loop is stable.
- Do not expand platforms before unified events exist.
- Do not let self-generated skills auto-enable.
- Do not put every memory type into one database table.
- Do not hide governance behind prompts. It must be code.

## First 10 Concrete Tasks

1. `command-registry`
2. `doctor-command`
3. `session-store-sqlite`
4. `memory-search-command`
5. `skill-metadata`
6. `skill-policy-gates`
7. `procedure-trace-store`
8. `skill-curator`
9. `scheduler-service`
10. `trajectory-compression`

