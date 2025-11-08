# Backend/MCP Setup — Spec (concise)

## 0) Product + demo promise

* **Who:** buyers upload ads; creators link content.
* **What:** system **matches** creator content ↔ ads, **generates** new ad variants, **voices** a 15s script, **proposes** a simple budget plan, and **streams** fake live metrics.
* **Demo flow (one click):** input brief → see ranked matches + 2 copy variants → press “voiceover” → hear audio → see budget split + CTR/CPA counters tick.

## 1) Minimal end-to-end flow (golden path)

1. Frontend sends **content_id** (creator post/transcript), **ad_pool_id**, and optional brief/goals.
2. Backend builds a **Context Object** (brand, audience, tags, constraints) from Snowflake (facts + embeddings).
3. **Match**: hybrid score = cosine(sim(content, ad)) + tag overlap + demographic fit (weights configurable).
4. **Generate**: Gemini creates 2 text variants + a 15s script from the Context Object.
5. **Voice**: ElevenLabs → MP3 URL.
6. **Plan**: deterministic budget plan across 2–3 channels (rule/LP); return rationale.
7. **Metrics**: start fake event stream (impressions, clicks, conv) tied to plan; store events.
8. Persist everything; return links/ids so frontend can render.

## 2) Topology (single Vultr VM to start)

* **API Gateway** (REST + SSE) — stateless.
* **MCP Orchestrator** — runs agents and exposes **tools**.
* **Workers** (optional): TTS + metrics simulator (can be in-process).
* **Object storage** for audio assets (Vultr/S3-compatible).
* Secrets: Gemini, ElevenLabs, Snowflake (read/write), optional Solana.

## 3) Agents (Gemini) + Tools (MCP)

* **Orchestrator Agent**: owns the Context Object; calls tools; writes audit log.
* **BusinessAnalysis Agent**: turns brief + Snowflake lookups into audience/persona, do/don’t list, key claims.
* **ContentGen Agent**: produces copy variants + 15s script (tone per audience).
* **Guardrails/Critique Agent**: checks brand-safety/claims; quick self-edit loop.
* **Strategy Agent**: builds budget/media plan (objective: est. clicks subject to budget + min-spend).

**Tools (MCP):**

* `snowflake.query` (facts/metrics), `snowflake.vector_search(text, k)`
* `score.match(content_id, ad_id|text)` (hybrid score)
* `tts.speak(text, voice)` → MP3 URL
* `opt.plan(goal, variants, channels, budget)` → plan JSON
* `metrics.simulate(campaign_id)` → event stream handle
* `storage.put(object)` / `storage.url(id)`
* `audit.log(event, payload)`

## 4) Public API (v1)

* `POST /match` → {top_k: [ad_id, score, why]}
* `POST /generate` → {variants: […], script}
* `POST /tts` → {audio_url}
* `POST /optimize` → {plan: [{channel, creative_id, budget, reason}]}
* `POST /campaigns` → upsert campaign (ties matches + plan + assets)
* `POST /metrics/simulate` → start; returns stream token
* `GET /metrics/stream?token=…` (SSE) → ticks {impr, clicks, ctr, conv, cpa}
* `GET /health`
  Auth: simple API key header; roles: buyer/creator.

## 5) Data contracts (essentials)

* **Ad**: id, owner_id, primary_text, tags[], product_facts{}, target_demo{}, assets{image?, video?}.
* **ContentItem**: id, creator_id, text/transcript, tags[], audience_estimate{}.
* **MatchResult**: ad_id, score, reasons{overlap[], cosine, demo_fit}.
* **CreativeVariant**: id, channel, headline, body, cta, script15s.
* **AudioAsset**: variant_id, voice, url, duration.
* **Plan**: [{channel, variant_id, budget, est_clicks, note}].
* **Event**: ts, campaign_id, channel, type(impression|click|conv).

## 6) Non-functionals

* **Idempotency** via request keys; **timeouts** + fallbacks (if vector search fails, use LLM-only scoring).
* **Observability**: request logs, tool call traces, prompt+output redaction; counters for LLM latency, TTS latency, match latency.
* **Config**: feature flags for: guardrails on/off, Veo3 (video) off by default, Solana off by default.

## 7) Minimal task set (backend owner)

1. **Repo bootstrap + secrets**: env wiring, roles, API key auth, structured logging.
2. **MCP server** with registered tools (stubs first) + healthcheck.
3. **Snowflake connectors**: fact query + vector search tool (contract agreed with data team).
4. **Matching service**: implement hybrid score; return ranked list with reasons.
5. **Generation pipeline**: Orchestrator → Analysis → ContentGen → Guardrails; persist variants.
6. **TTS wrapper**: text→MP3, cache by text+voice; store via `storage.put`.
7. **Optimizer**: simple rule/LP returning 2–3 line plan with rationale.
8. **Metrics simulator + SSE**: deterministic RNG seeded by campaign_id.
9. **API endpoints** (above) wired to agents/tools; 3 smoke tests: `/match`, `/generate+tts`, `/optimize+metrics`.
10. **Demo script + reset route**: `/admin/reset` seeds ads/content and clears events.

## 8) Context transfer (what we’re building)

* **Goal product:** a creator–buyer marketplace that **surfaces the best ad for a given piece of content**, **auto-generates on-brand variants**, **speaks a ready-to-air audio ad**, and **proposes a budget plan**, all backed by **Snowflake facts + embeddings** and a **deterministic optimizer**.
* **MVP definition for demo:** single click returns (a) top 3 matches with reason, (b) 2 copy variants + 15s script, (c) playable audio, (d) simple plan + live fake KPIs.
* **Out of scope now:** real spend, real attribution, Veo3 video, on-chain payouts. Placeholders allowed.

## 9) Integration checkpoints

* **Frontend**: expects JSON per contracts; supports audio playback URL; reads SSE for metrics.
* **Snowflake**: exposes SQL view(s) for product facts, demographics; vector search proc is callable.
* **ElevenLabs**: one default voice configured; fallback text if TTS fails.
* **Optional Solana**: stub `/payouts/preview` returning a fake tx id.

Ship this skeleton; then we can toggle Veo3 (short B-roll video) and Solana (escrow/receipts) behind flags once the loop is stable.
