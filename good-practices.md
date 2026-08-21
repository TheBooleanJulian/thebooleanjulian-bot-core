# Good Practices — TheBooleanJulian Ecosystem

Living checklist for session hygiene, knowledge management, and agent architecture across all repos (bot-core fleet, Accurova apps, cyborg-juliana, tutoring tools). Source: notes from Hypergrowth Summit / SuperSeed Live Events talks, Aug 2026.

---

## 1. Session Hygiene & Quality Control

- [x] **Handover docs** — every active repo gets a `handover.md` updated at end of each work session: current state, what changed, open questions. Enables instant restart next session (for you or for a fresh Claude Code session). *(Adopted in `thebooleanjulian-bot-core` 2026-08-21 — see its `handover.md`. Not yet propagated to other repos.)*
- [ ] **Rewind & fork, don't argue** — if a Claude Code session goes down a wrong path, branch to a new session or subagent instead of correcting in-thread. Cheaper and cleaner.
- [ ] **Keep the main thread clean** — push exploratory "noise" (debugging tangents, side experiments) to a separate session/subagent.
- [ ] **Periodic audits** — monthly pass where a model re-verifies `.md` docs against actual code. Models (including past sessions) hallucinate about their own prior work — trust but verify.
- [ ] **Cross-checking on high-stakes work** — for anything client-facing (Accurova pricing logic, invoice/payment code), let a second model or a fresh session challenge the first pass.
- [x] **Ask the AI what's worth automating** — periodically prompt for recurring-pattern detection across the bot fleet; it's good at spotting what should become a shared skill in `bot-core`. *(Done 2026-08-21: surveyed 9 real Python Telegram bots, drove the bot-core v2 rewrite from what was actually repeated. Repeat periodically as the fleet grows — this isn't a one-time task.)*

## 2. Knowledge Management & Security

- [ ] **PDFs/images → text** — any business doc, BNI material, or tutoring curriculum gets converted to markdown so it's referenceable by agents, not locked in a binary/image.
- [ ] **No secrets in code** — audit all Zeabur deployments; API keys (Claude, Google, WhatsApp, Telegram) live in env vars/secrets store, never hardcoded. High priority given 15+ bots share `bot-core`. *(Not run 2026-08-21 — the bot-core v2 rewrite touched logging specifically because httpx/httpcore can leak `BOT_TOKEN` into logs, but a full fleet-wide secrets audit is separate, unscoped work — needs its own explicit pass.)*
- [ ] **Key rotation schedule** — build a reminder system (could be a MiguQuest task or a cron in bot-core) to rotate API keys on a schedule instead of relying on memory.
- [ ] **Least privilege** — check whether bots (MonitoringMiku, MiguQuest, etc.) share one god-mode credential. Isolate access per bot where feasible to limit blast radius if one is compromised.
- [ ] **Version control discipline** — deliberate, well-scoped commits across all GitHub repos; nothing live only on local disk.

## 3. The Zeroth Principle

- [ ] **Ask the AI first when stuck** — before manual debugging (failed Zeabur deploy, silent bot death), ask the model: *"Why not, and what would fix it?"* Let it propose or attempt the fix directly.
- [ ] **Escalate via handover, not workaround** — if a session hits a wall, write a `handover.md` for a fresh model/session rather than trying to bypass safeguards or credential controls. A new chat with a different "persona" can unstick things.

## 4. Agent Architecture Pattern (persona + knowledge base + backend)

Reusable pattern for any client-facing bot (loyalty program, live-event bot, future Accurova/tutoring assistant):

- **Persona = front door only.** The LLM prompt routes and converses; it does not freehand facts.
- **Structured knowledge base = source of truth.** Versioned fact-sheet files (e.g. `accurova-pricing-v1.txt`, `tutoring-faq-v1.txt`) that the agent retrieves from — never guessed pricing/specs.
- **Backend script = real actions.** Order lookups, quote calculations, status sync handled by actual code (Apps Script / FastAPI endpoint), not the model.
- **Human fallback** built in for anything the agent can't resolve.

## 5. Meeting → Dashboard Pipeline

`Meeting → Transcription (Fireflies or equivalent) → Agent extract → Follow-up dashboard`

Candidate use cases:
- BNI 1-2-1s → auto-populate the BNI dashboard / Notion MTL kit with Pain/Challenge/Solution fields.
- Accurova client consults → auto-drafted follow-up summary + next steps.

## 6. Experience Prompting Framework

Before firing a build request at Claude Code, structure the prompt as:

1. **Current state** — what exists now.
2. **Problem** — what's actually wrong/missing.
3. **Desired outcome** — what success looks like.
4. **Opinions labeled as opinions** — if pushing a preference, say so explicitly.

State → Problem → Outcome, in that order, before asking for a solution. Reduces back-and-forth on multi-stage builds.

---

*Last updated: Aug 2026. Review and prune quarterly — delete anything that hasn't been used.*
