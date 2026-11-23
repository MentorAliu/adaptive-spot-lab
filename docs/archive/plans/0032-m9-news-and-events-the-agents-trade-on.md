# ExecPlan 0032 — M9: news and events the agents trade on

**Status: APPROVED on 2026-10-19 at 20:47 UTC ([DECISIONS](../../DECISIONS.md#2026-10-19--m8-accepted-m9-built-under-execplan-0032)); update 1 installed on the PC on 2026-10-20 (`COMPLETE` at `89b9de2`); update 2 installed on the PC on 2026-10-20 (`COMPLETE` at `a5743df`, [§14](#14-progress)); acceptance is the owner's.** Proposed earlier the same day. It re-scopes M9 ([ExecPlan 0027](0027-m9-market-intelligence-and-event-driven-trading.md)) under M8's rules ([ExecPlan 0031](0031-m8-simple-app-that-runs-itself.md)), as 0031 §3 planned. The owner's go-ahead in the project thread "Get M9 ready to build" starts the build. That go-ahead also accepts M8 as installed (§6). Where this plan and 0027 differ, this plan governs; 0027 stays as the design record and the source of the requirement IDs cited here. Written from `main` at `f6b0a56`.

Labels: `OBSERVED` (seen in code, records or official pages), `INFERRED`, `PROPOSED`, `NOT RUN`.

## 1. Goal and observable outcome

The owner asked for M9 on 2026-10-15 ([DECISIONS](../../DECISIONS.md#2026-10-15--m9-roadmap-and-future-implementation-handoff)). The ask was news, an economic calendar, macro news, explanations of price moves, original announcements and selected SEC filings, with the agents able to buy, hold or sell without waiting for the hourly check. On 2026-10-19 at 19:36 UTC, right after M8's last update, the owner asked "whats next now".

The goal: the agents read free news and official releases, and they can act on them between the hourly checks. They trade BTC and SOL only, under the same limits. Nothing new is asked of the owner except one double-click per update.

Observable after M9:
1. The app collects a set of free feeds by itself (§5.1). The Evidence page shows each feed's health and its newest items.
2. A relevant item, or a sharp price move, starts the analyst's investigation. Its reviewed assessment starts a decision at once, so the coordinator can enter or exit between hourly checks.
3. The analyst and the coordinator see the scheduled US releases of the last and next 24 hours.
4. A compact table shows what came of each kind of trigger and each feed: decisions, trades, abstentions, refusals and after-cost results.
5. M9 arrives as two updates, each one double-click.

## 2. What the app already has (OBSERVED at `f6b0a56` unless marked)

- **A source fetcher with strict rules.** It accepts an exact HTTPS host, a constant GET path and typed integer filters. It follows no redirect, caps the response size and needs a registered parser (`app/sources/registry.py`, `app/sources/transport.py`). Two sources exist, both release lists on GitHub: Bitcoin Core and Agave (`app/research/definitions.py`). The only parser is `GITHUB_RELEASES_V1`.
- **News already reaches decisions, in code.** A new source item records a `SOURCE_REVISION` trigger. That starts `EVENT_INVESTIGATION_V1` (ANALYST, generation 2), then its review `ASSESSMENT_REVIEW_V2`. An `ACCEPTABLE` review records `ASSESSMENT_READY` (`app/agents/decisions.py:489`). Under `AGENT_POLICY_V1` and `V2`, that starts a decision at once (`REVIEWED_ASSESSMENT` in `cadence.decision_after`). An investigation's reviewed assessment can be an entry's basis (`BASIS_PURPOSES`, `app/agents/tools/decisions.py:48`). So entries between hourly bars are already possible; what is missing is news.
- **Market data.** The app streams the hourly candles and the 24-hour ticker of BTC and SOL (`app/market_data/provider.py:22`). The ticker carries the best bid and ask, which is enough for a price-move check in code.
- **Limits in force.** The policy allows 2 entries in any 24 hours and 1 per coin. Each UTC day allows 36 decisions, 4 briefs and 8 outcome reviews. Investigations share 24 workflows a day with research (generation 2). Decision starts are at least 10 minutes apart, except after a fill or a position's end. A waiting trigger goes stale after 20 to 30 minutes. Nothing new starts between HH:58 and HH:07 UTC.
- **No web search.** The runner turns off Codex's web search (`web_search = "disabled"`, `services/agent-runner/runner/invocation.py:47`) along with every native tool. The agents read only registered sources.
- **Authority since M8.** New sources and policy versions reach the app only as code in an update the owner installs. The agent worker records them in force as `SYSTEM`. The app moves the main run to a newer policy by itself once the account holds no position ([AUTONOMY_MATRIX](../contracts/AUTONOMY_MATRIX.md#m8-the-app-runs-itself-execplan-0031)).
- **Not known:** whether the main run has moved to `AGENT_POLICY_V2` ([STATUS](../../STATUS.md)).
- **The cloud cannot reach the feeds.** On 2026-10-19 this session's network refused the Federal Reserve, ECB, BLS, Solana status, CoinDesk and SEC hosts, and GitHub answered 403. The first real fetch of any new feed happens on the PC.

## 3. What changes from ExecPlan 0027

| 0027 asked for | M9 now |
|---|---|
| Owner source grants and approvals (0027 §5, §7, B9) | Sources ship as code in an update; `SYSTEM` records them in force (M8) |
| Capability probes before activation (0027 §5, R24) | M8's short check, which runs by itself after the definitions change |
| PC harness and load runs, a frozen latency matrix (0027 §3, §7, B8, Q06) | Cloud tests and the update's own checks. Timings come from the app's records, which already store each step's time |
| Ten batches, B0 to B9 | Two updates (§9) |
| Web search and bounded page reads (0027 §5, R04) | Deferred (D3) |
| SEC filings | Deferred (D5) |
| Consensus forecasts | None (D6) |
| Matched comparisons, semantic and reviewer trials, repeatability, remembered-outcome audit, news base rates (0027 §8, R11, R22 to R28) | Deferred; replaced by the trigger and feed table (§5.3) and the version segments M8 already keeps |
| Asset research records, relative strength, advisory feasibility (R16, R17, R21) | Deferred |
| Execution invalidation independent of the agent worker (R20) | Not extended: M9 adds no new kind of entry basis (§6) |
| More roles, a coordinator that directs the others ([the idea note](../ideas/agent-roles-and-coordinator.md)) | The four roles stay as they are (D4) |

Kept from 0027: five of the six categories; free sources; BTC and SOL only; publication, receipt and availability times kept apart; corrections kept as new revisions; feed text treated as untrusted data; no invented forecasts or probabilities; no catch-up trades after downtime; every protection of 0031 §4.1.

## 4. Decisions Claude made under the owner's delegation

The owner delegated these calls ("you have my authorization for everything", 2026-10-19 11:08 UTC; "decide for me" on the model choice, 08:30 UTC). They are recorded here, not in DECISIONS, which holds the owner's own choices.

- **D1. Free sources only.** No accounts, keys or spending.
- **D2. BTC and SOL only.** News about other coins is stored and searchable as context. It never makes another coin tradable (A01).
- **D3. Web search is deferred.** The runner turns it off on purpose, so no way the agents already have permits it. Codex's built-in search would give the model a tool whose requests and results the code cannot check, which rule 10 rules out. The same holds for reading the article behind a feed item. The analyst works from the feed's own text. Adding either later is its own update with its own design.
- **D4. Agent roles: the simplest option.** The four roles stay: analyst, researcher, evaluator, coordinator. M9 adds no role, no follow-up menu the coordinator picks from, no specialist role and no digest. From the idea note, E2, S5 and S6 are already today's rules, and E4 (fresher inputs before more agents) is what M9 builds. E1, E3 and S1 to S4 stay ideas.
- **D5. SEC filings are deferred.** EDGAR asks each automated caller to name a contact email in every request ([SEC, Accessing EDGAR data](https://www.sec.gov/os/accessing-edgar-data), read 2026-10-19). Claude does not put the owner's address into outside requests without the owner's word. With that word, the filings feed is a small later update.
- **D6. No consensus forecasts.** No free official source publishes them. The analyst sees the actual and previous values; the consensus stays unknown, and no surprise score is computed.
- **D7. Two updates, sources first.** The feeds can only be tried from the PC (§2). Update 1 lets them run, and update 2 fixes what the PC shows.
- **D8. No money rule changes.** Entry limits, the decision cap, sizes, stops and exits are the same as under `AGENT_POLICY_V2`.

## 5. Design (PROPOSED)

### 5.1 Free feeds (update 1)

Each feed below is checked when it is built: its address, format, media type, terms and rate. A feed whose terms forbid this use, or that answers only to a browser, is dropped and the plan says so. The addresses marked OBSERVED were listed on the publisher's own page on 2026-10-19.

| Category | Feed | Coins | Status |
|---|---|---|---|
| Economic calendar | BLS release calendar, iCalendar: `https://www.bls.gov/schedule/news_release/bls.ics` | both | OBSERVED on [bls.gov](https://www.bls.gov/schedule/news_release/) |
| Macro releases | BLS latest numbers `https://www.bls.gov/feed/bls_latest.rss`, CPI `cpi_latest.rss`, employment `empsit.rss` | both | OBSERVED on [bls.gov/feed](https://www.bls.gov/feed) |
| Central banks | Federal Reserve monetary policy releases `https://www.federalreserve.gov/feeds/press_monetary.xml` | both | OBSERVED on [federalreserve.gov/feeds](https://federalreserve.gov/feeds) |
| Central banks | ECB press releases, speeches and interviews `https://www.ecb.europa.eu/rss/press.html` | both | OBSERVED on [ecb.europa.eu/rss](https://www.ecb.europa.eu/rss) |
| Crypto news | CoinDesk's RSS feed, and other outlets found at build time under the same checks | by name | Dropped: CoinDesk's [terms](https://coindesk.com/terms/) forbid "any robot, spider, scraper, or other automated means" without written permission. No other outlet confirmed in update 1 |
| Network status | Solana's status page incident history, if it offers a feed | SOL | Not added: no feed confirmed on the publisher's own page (only third-party monitors were found) |
| Announcements | Bitcoin Core and Agave releases | BTC, SOL | Running today |

**As built in update 1** (source documents in `app/sources/feeds.py`, stored by migration `0013_m9_news_feeds`; formats and terms in [INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#m9-update-1-the-free-feeds--2026-10-19)):

| Source version | Address | Reader | Polls | Starts work |
|---|---|---|---|---|
| `CALENDAR_BLS_V1` | `www.bls.gov/schedule/news_release/bls.ics` | `ICALENDAR_V1`: events from 1 day back to 45 days ahead, 100 at most, start times through the file's own time zone | every 6 h | never; its events are stored for the agents to read |
| `NUMBERS_BLS_V1` | `www.bls.gov/feed/bls_latest.rss` | `RSS_V1` | every 15 min | each new item, for both coins, at most once in 4 h per coin |
| `PRESS_FED_MONETARY_V1` | `www.federalreserve.gov/feeds/press_monetary.xml` | `RSS_V1` | every 15 min | as above, once in 4 h |
| `PRESS_ECB_V1` | `www.ecb.europa.eu/rss/press.html` | `RSS_V1` | every 15 min | as above, once in 12 h (the feed also carries every speech) |

None of the publishers states a rate limit, so each document caps itself at twice its budget, and the fetcher waits only on a stated limit (`HTTP_RETRY_AFTER_V1`: a 429, or a 503 with `Retry-After`). The first fetch that stores items is each feed's baseline and starts nothing. BLS's CPI and employment feeds are left out because the latest-numbers feed carries both.

- **Parsers.** New registered parsers for RSS 2.0, Atom and iCalendar. XML that declares a DTD or an entity is refused. The existing size cap, plain-text cleaning and "a link is only text" rule apply. Publication, receipt and availability times stay separate, and an unknown time stays unknown. *As built:* `RSS_V1` and `ICALENDAR_V1`; no feed of update 1 is Atom, so the Atom reader waits for one that is.
- **Which items start work.** A code filter decides. An item starts an investigation only if it names BTC or SOL by a fixed alias list (for example bitcoin, btc, solana, sol), or if it comes from a feed marked as macro, which concerns both coins. Every other item is stored and searchable, and starts nothing. Each feed keeps its own cooldown and request budget in its source document, as the GitHub sources do. *As built:* every feed of update 1 is macro, so its trigger rule is `EVERY_ITEM` (both coins) or `NONE` (the calendar); the name list waits for a feed that needs it.
- **The calendar** is read like any feed. Its entries become scheduled releases that the snapshots show (§5.2). A release itself arrives as an item of the BLS or Federal Reserve feed. FOMC meeting dates come from the Fed's calendar page only if it parses under the fetcher's rules. Otherwise the statement still arrives through the monetary-policy feed.
- **The update file** also prints, read-only, each new feed's first fetch result and the main run's policy and state. That answers STATUS's open question about `AGENT_POLICY_V2` without asking the owner.

After update 1, the existing chain of §2 already carries a relevant item to a decision: generation 2's investigation, its review, then `ASSESSMENT_READY`.

### 5.2 The agents and `AGENT_POLICY_V3` (update 2)

- **Generation 4 of the agent definitions.** It is generation 3 plus the investigation and its review, changed as follows:
  - **Investigations** start from a relevant feed item or from a price move (below). They get their own daily count of 16, so news and research cannot starve each other; today both share 24. The count changes only with a recorded reason.
  - **Prompts.** A new analyst prompt covers news, central-bank and statistics releases, and price-move explanations. It carries 0027's evidence rules: a publisher's claim is not a verified fact; an authentic announcement is not evidence of a benefit to the coin; "no reliable explanation found" is a valid result; no invented consensus or probability. The evaluator's assessment review checks the same rules. The coordinator's prompt names the kind of trigger behind each decision.
  - **Snapshots** show the scheduled releases of the last and next 24 hours, in UTC.
  - **Tool text made true.** Generation 3 still says "only the owner resumes entries". Generation 4 says what M8 built: the agent's entry pause ends after 24 hours, or earlier by the owner. No tool is added or removed.
- **The price-move check** runs in code, with no model. A move of the ticker's mid price over 15 minutes of at least one hourly ATR(14) records a `PRICE_MOVE` trigger. It keeps a one-hour cooldown per coin and fires at most 4 times a coin a day. It starts an investigation that looks for an explanation in the items already collected. These numbers are Claude's engineering choices, not measurements. The trigger table (§5.3) shows how often the check fires, and a change to the numbers is a later version.
- **`AGENT_POLICY_V3`** is `AGENT_POLICY_V2` bound to generation 4, with every limit and cadence value unchanged (D8). The update installs it, the agent worker records it in force, and the app moves the main run to it once the account holds no position, as update 3 of M8 built. Positions opened under V2 keep their terms (R08).

**As built in update 2** (`app/agents/definitions_v4.py` and `app/agents/price_moves.py`, frozen in migration `0014_m9_agents`; [RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m9-runtime-news-and-price-moves-start-investigations-execplan-0032)):
- **Generation 4** is one investigation, `EVENT_INVESTIGATION_V2` (ANALYST), and its fixed review `ASSESSMENT_REVIEW_V3` (EVALUATOR), with prompts `ANALYST_PROMPT_M9_V1` and `EVALUATOR_PROMPT_M9_V1`. Its catalog is the analyst's and the evaluator's part of catalog v3, so no tool, grant or effect is added; step schema v3 is used as it is. A new item of a source in force and a price move both start it; the owner's start keeps M6's `EVENT_INVESTIGATION_V1`. One investigation is open at a time per source and coin (a feed item) or per coin (a price move).
- **Its own count:** 16 a UTC day (`BUDGETS_V4`), in the runtime profile beside the other generations' budgets. Every `INVESTIGATION` parent counts there, the owner's M6 ones included, and none counts any longer against the 24 that research and promotions share.
- **To a decision:** an `ACCEPTABLE` review records `ASSESSMENT_READY`, as M6's does, and names the assessment in its target column, as a brief's review does, so that assessment can be an entry's basis.
- **Scheduled releases:** the analyst's and the evaluator's market view lists up to 12 events of the calendar sources in force that start within 24 hours of the cutoff, nearest first. Each is an evidence item the model can open and cite. Each event's newest revision available by the cutoff decides its time, so a moved release shows at its new time, and a cancelled one shows its status. The coordinator's portfolio snapshot (schema 2) shows the nearest 6, each with its time, title and status as the publisher wrote them and never a result, labeled `SCHEDULED_RELEASES_ARE_TIMES_NOT_RESULTS` and `RELEASE_TITLES_AND_STATUS_ARE_THE_PUBLISHERS_TEXT`. To fit its size it drops the farthest releases first, before any of the run's history. When the calendar cannot be read, the decision goes on without it, labeled `RELEASES_UNAVAILABLE`.
- **The price-move check** as planned: the mids of the newest valid recorded quotes (each no older than 5 seconds) now and 15 minutes earlier, against `ATR14_1H_V1` on at least 16 contiguous finalized hourly bars; 60 minutes apart and at most 4 a coin per UTC day. The trigger keeps both quotes, the ATR and the move in ATRs and as a fraction, labeled as the app's calculation and not an explanation. A missing or invalid quote, or too short a history, records nothing, and nothing is caught up after downtime.
- **No `AGENT_POLICY_V3`, and no run move.** The policy binds generation 3's six hashes, the decision templates, which update 2 leaves unchanged; the investigation and its review are bound by the runtime profile, not by a policy. So `AGENT_POLICY_V2` stays in force and the main run keeps going, with nothing to wait for. The coordinator's prompt and the pause tool's text are generation 3's hashed texts and stay as they are; changing them would need a new policy and a run move, which the owner's simplest path does not need. Each decision's job already names the trigger it consumed, by family and event.

### 5.3 What came of it (update 2)

A compact table on the Decisions page shows, per version segment and per kind of trigger (hourly bar, position event, feed item, price move):
- decisions, entries, exits and abstentions;
- refusals, by cause: the daily cap, the review or the engine;
- the after-cost result of the positions opened;
- per feed, the items stored, the investigations started and the decisions that cited it and acted.

It adds the model token counts where the runner reports them, which is 0030's token summary, an M8 follow-up. The table makes no profitability claim. Segments differ in market conditions, so a difference between them is not proof that news helped. The UI work follows the shadcn rules (rule 6).

**As built in update 2** (`GET /v1/trigger-results`, [API_CONTRACTS](../contracts/API_CONTRACTS.md#m9-update-2-what-came-of-each-trigger-execplan-0032); the card "What came of each trigger" below the drafts on the Decisions page, [FRONTEND](../contracts/FRONTEND.md#m9-update-2-what-came-of-each-trigger-execplan-0032)):
- A version segment is one run of an operating policy in the main mode that the engine started (its `ACTIVATED` event), newest first, the newest 6. The page shows the newest, or the one the URL names, with a toggle between them.
- Per kind of trigger (hourly bar, position event, feed item and price move always; market brief, the owner's start and other when used): the triggers recorded, waiting and canceled; the decisions started, and of those the ones that submitted, ended without a submission or are still open; the entries, exits and stop or cancel requests submitted; refusals by cause (the daily cap, too old, a newer trigger, the intent's review, the engine); the positions opened and closed and the closed ones' realized result after fees; and the model tokens of the decisions with their reviews. A decision counts once, under the trigger it consumed; a reviewed assessment counts under the kind of work behind it.
- Per feed (every code-owned source, listed before its first item) and for the price-move check: items stored; triggers, waiting and canceled; the ones refused before an investigation, by cause (the investigations' daily cap, too old, one already open, other); investigations, the ones found acceptable, the decisions they started and the ones that submitted something to the engine; and the investigations' tokens. Feeds are counted from their start, across runs. A feed item or price move counts in a segment's table once its reviewed assessment is ready for a decision.

### 5.4 What stays

- The five protections of [0031 §4.1](0031-m8-simple-app-that-runs-itself.md#41-what-stays-and-why), and positions' original terms.
- Exits never wait for a model, and stale data blocks new exposure.
- A model that is down or at its usage limit stops no protective exit.
- After downtime there are no catch-up trades.
- Feed text is data, never an instruction, and links are never followed.
- The quiet window stays. A release at the full hour, such as an FOMC statement at 18:00 or 19:00 UTC, is fetched from HH:07.

## 6. M8's open items, and M8's acceptance

M8's acceptance under its own rules is its three updates, installed and checked ([0031 §15](0031-m8-simple-app-that-runs-itself.md#15-progress)). The roadmap's older M8 evidence items and 0027 §3's prerequisites are handled as follows:

| Item | In M9 |
|---|---|
| Has the main run moved to `AGENT_POLICY_V2`? | Update 1's file prints it (§5.1). *Read on 2026-10-20 at 07:11 UTC:* run `2580d8ea` is `RUNNING` on `AGENT_POLICY_V2`; `a8b3ae07` on V1 is `COMPLETED` |
| Guard functions without a fixed search path (0027 §3) | Update 1 checks whether any app identity can create objects on those functions' search path. If one can, an additive migration pins the path; if none can, this plan records why no change is needed. *Found:* every identity may create temporary tables (`TEMP` is granted to `PUBLIC` and no migration revokes it), and a session's temporary schema is searched first. On the scratch cluster, a temporary `pg_roles` made the unpinned `asl_is_superuser()` answer true for `asl_api`. Migration `0013` pins `pg_catalog, public, pg_temp` on the 27 such functions, defined in `0002` to `0009`; the same table then leaves the answer false ([SECURITY](../contracts/SECURITY.md#guards-look-names-up-on-a-fixed-path-m9-update-1)) |
| Real-model behavior of the new definitions | M8's short check runs after update 2 and gains one investigation case; a failure shows on the Agents page. *As built:* no case is added. The check already runs the analyst and the evaluator on the same tools, and an investigation case would spend more of the shared usage allowance at every check. A failing investigation fails alone: it starts no decision, and it shows in the trigger table and on the Agents page |
| The first live decision and M6's and M7's walk-throughs | They happen as the app runs. The thread reads the records read-only after update 1 |
| Forward evidence and the value of each role | The table of §5.3. Role ablations and shadow accounts stay deferred (M7-OD5) |
| Invalidation independent of the agent worker | M9 adds no new kind of entry basis; the existing checks at submission and in the engine stay. Promoted candidates remain no basis under V2 or V3, an M8 follow-up |
| CI | None; the cloud tests of 0031 §4.8 |

## 7. Requirements and tests (PROPOSED)

| ID | Requirement | Test |
|---|---|---|
| N1 | Each new parser keeps the publisher's times, text and revisions, refuses a DTD or entity, and never invents a missing field | Parser tests on recorded fixtures, including malformed, empty, oversized and revised feeds |
| N2 | Only items naming BTC or SOL, or from a macro feed, start an investigation; other coins never become tradable | Filter tests with ambiguous names (for example "Solana" in a company name) and other coins' news |
| N3 | A feed that fails, times out, changes its media type or rate-limits stays visible and backs off; the other feeds go on | Fetcher tests with a stand-in transport |
| N4 | Feed text cannot add a tool, change a limit or reach the engine | Injection fixtures through investigation, review and decision; the existing grant tests |
| N5 | A relevant item leads to a reviewed assessment and a decision between hourly bars, inside the cooldown, staleness and daily caps | Workflow test from a fixture item to a recorded decision |
| N6 | The price-move check fires at its threshold, keeps its cooldown and daily cap, and runs no model | Detector tests on recorded ticker sequences |
| N7 | Generation 4 and `AGENT_POLICY_V3` validate; the app records them in force and moves the main run only when flat; V2's positions keep their terms | Definition, policy and run-keeper tests |
| N8 | The investigation count and the research count are kept apart | Budget tests |
| N9 | The trigger and feed table counts each decision once, and labels refusals by cause | API and browser tests at 390 px |
| N10 | The update file prints each feed's first fetch and the main run's policy, and reports failure honestly | The update file's model test (`tools/m8/update-model.ps1`) |
| N11 | The five protections hold | The existing money-path, stop and off-switch tests, unchanged and passing |

## 8. Not in M9

Each of these needs its own later update, if wanted:
- web search, and reading article pages;
- SEC filings (D5);
- consensus forecasts;
- asset research memory, relative-strength figures and advisory feasibility;
- matched comparisons, semantic trials and the rest of 0027's evaluation (R11, R22 to R28);
- conditional orders;
- more roles (the idea note);
- promoted candidates as an entry basis under V3;
- the coordinator's early lift of its pause;
- a no-entry window before scheduled releases. It was considered and left out: the coordinator sees the schedule and can abstain.

M10 ([ExecPlan 0028](0028-m10-coin-discovery-and-controlled-expansion.md)) is re-scoped the same way after M9.

## 9. Implementation sequence

Each part is its own pull request, merged by its thread once ready. Each update is one double-click on `update-app.cmd`, after which the thread checks the result read-only. Update 2 is merged only after update 1 ran on the PC, because the update file installs whatever `main` holds.

1. **This plan** (documents only).
2. **Update 1, the feeds:** the parsers, the source versions, the item filter, the guard check of §6 and the update file's two read-outs.
   - Documents: DATA_CONTRACTS, MARKET_DATA, SECURITY, CONFIGURATION, OPERATIONS, TESTING, COMMANDS, INTEGRATION_EVIDENCE and REFERENCES.
3. **Update 2, the agents:** generation 4, the price-move check, the calendar in snapshots, `AGENT_POLICY_V3`, the short check's new case, and the table of §5.3.
   - Documents: RUNTIME_AGENTS, AGENT_TOOL_CONTRACTS, STRATEGIES, API_CONTRACTS, FRONTEND, TESTING, COMMANDS, and an AUTONOMY_MATRIX line naming V3. No permission changes.

M9 is complete when both updates are installed with `COMPLETE` records, and the thread has read, read-only, that the feeds collect and that an investigation from a new feed or a price move ran. If none ran, the completion records why. Results then accumulate in the table; M9 sets no profit target.

## 10. Verification commands (PROPOSED)

As [0031 §10](0031-m8-simple-app-that-runs-itself.md#10-verification-commands-proposed), in the cloud for each update:
- `pnpm --dir apps/web lint`, `typecheck`, `test` and `build`;
- `uv run ruff check` and the OpenAPI drift check in `services/engine`;
- `uv run pytest` without a database, then on a scratch PostgreSQL;
- the browser suites.

On the PC: the update file's own checks. The exact commands go into [COMMANDS](../COMMANDS.md) as each update is built; none is VERIFIED for M9 yet.

## 11. Failure and rollback

- A feed that fails shows as failed on the Evidence page, and nothing fills its gap.
- More model work shares the owner's ChatGPT usage allowance with the owner's own Codex use; it ran out twice on 2026-10-19. The caps bound it (16 investigations, 36 decisions a day). At the usage limit the agents pause and resume by themselves, and the code's stops keep protecting positions.
- A version that misbehaves trades on paper until a later update fixes it, and its segment stays in the history, labeled. The owner's off switch stops the agents at any time.
- Each update takes a backup and rollback tags, and its migrations are additive.

## 12. Q01–Q10 (affected gates)

| Gate | Applies | Condition |
|---|---|---|
| Q01, Q02 | Update 2 | The table and the feed health read well at 390 px, with loading, empty and error states (N9) |
| Q03 | Yes | N1, N2, N5 to N8 |
| Q04 | Yes | N4 and N11: no new authority, and the money path unchanged |
| Q05 | Yes | N3: failures stay visible and back off |
| Q06 | Yes | Timings from the app's records; no PC load run (0031 §4.8) |
| Q07 to Q10 | Yes | The cloud tests and the update's checks, unrun checks recorded, documents changed with each update |

## 13. Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-10-19 | M9 is re-scoped under M8's rules in this plan; 0027 stays as the record | 0031 §3 planned it; 0027 still assumed approvals, probes and PC runs that M8 removed |
| 2026-10-19 | D1 to D8 (§4), by Claude under the owner's delegation | The owner delegates such calls; each is the simplest option that keeps the five protections |
| 2026-10-19 | M9 builds on the chain the app already has (§2) instead of a new event store | A feed item already reaches a decision through an investigation and its review; the missing part is feeds |
| 2026-10-19 | The owner's "Go" (20:47 UTC): this plan approved, M8 accepted | [DECISIONS](../../DECISIONS.md#2026-10-19--m8-accepted-m9-built-under-execplan-0032) |
| 2026-10-19 | Update 1: CoinDesk dropped; no Solana status or other crypto feed; no name filter or Atom reader yet; first fetch as baseline; the ECB feed's 12-hour cooldown; the guards pinned | Each by Claude under the delegation; reasons in §5.1, §6 and DECISIONS |
| 2026-10-20 | Update 2: no `AGENT_POLICY_V3` and no run move; the coordinator's prompt and the pause tool's text unchanged; no short-check case | Generation 4 adds only what no policy binds, so V2 stays in force (§5.2); the check's case would cost usage at every check (§6) |
| 2026-10-20 | Update 2: the investigations' own count of 16 also takes the owner's M6 investigations, which leave the shared 24 | One count per purpose is simpler, and the owner's starts are rare |
| 2026-10-20 | Update 2: the coordinator's snapshot shows 6 releases, each its time, title and status as published and never a result, dropped before any history to fit; the analyst's view 12, each citable | The snapshot is bounded in size, the run's own history matters more to a decision, and the coordinator cites the review, not the calendar (the independent review found the first build said "times only" while it sent titles) |
| 2026-10-20 | Update 2: the trigger table is its own route, `/v1/trigger-results`; a segment is a run the engine started; feeds are counted since they started, across runs | Segments are M8's runs; a draft never started has no trigger; a feed's items do not belong to a run |
| 2026-10-20 | Update 2: the agent worker's healthcheck no longer imports the worker, and the image compiles its bytecode once | Update 1's read-out found the container `UNHEALTHY` on every probe while the worker ran: the probe's imports outlasted its 3-second timeout |

## 14. Progress

- 2026-10-20 09:43 UTC: **update 2 installed on the PC** (`COMPLETE` at `a5743df`, from 09:36 UTC; schema `0014_m9_agents` in 1 attempt; 11 services recreated; reconciliation `OK`; the pages answering). OBSERVED read-only through the owner's device session at about 10:03 UTC: every feed's latest fetch HTTP 200; `agent-worker` `healthy`, its last 5 probes passing in about 0.1 s each; the app composed profile `a8de17535d40` with `budgets_v4`, and its check waits for the owner's Codex usage allowance, used up since about 09:00 UTC (`PROBE_ONLY`, `CHECK_PENDING`, quota `BLOCKED`; the 09:00 decision and the checks at 09:16 and 09:36 were refused on it); the main run `2580d8ea` `RUNNING` on `AGENT_POLICY_V2`. No `PRICE_MOVE` trigger or generation-4 investigation yet: both wait for the agents to work again (NOT OBSERVED).
- 2026-10-20: **update 2 built and tested in the cloud** on branch `claude/plan-m9-ob2ejk` ([COMMANDS](../COMMANDS.md#m9-update-2-the-agents-act-on-news-and-price-moves--2026-10-20)): generation 4 and its prompts, the price-move check, scheduled releases in the views, the investigations' own count, `/v1/trigger-results` with its card on the Decisions page, and the agent worker's healthcheck, with migration `0014_m9_agents`. Not yet installed: the owner's double-click on `update-app.cmd` installs it, and the thread then reads the result.
- 2026-10-20 07:11 UTC: **update 1 installed on the PC** (`COMPLETE` at `89b9de2`, from 06:48 UTC; schema `0013_m9_news_feeds`; reconciliation `OK`; the pages answering; the agents `ENABLED`). OBSERVED read-only through the owner's device session: each of the four new sources fetched on its first try (HTTP 200: the calendar 18 items, the BLS numbers 1, the ECB 15, the Federal Reserve 15), and none started work, as the baseline rule says; the main run `2580d8ea` is `RUNNING` on `AGENT_POLICY_V2`. The agent worker's container read `UNHEALTHY` on every probe while the worker ran normally (§13).
- 2026-10-19 22:20 UTC: **update 1 built and tested in the cloud** on branch `claude/plan-m9-ob2ejk` ([COMMANDS](../COMMANDS.md#m9-update-1-the-free-feeds--2026-10-19)): the `RSS_V1` and `ICALENDAR_V1` readers, the four source versions of §5.1, the `HTTP_RETRY_AFTER_V1` rate policy, the trigger rule (`match`, `first_fetch`), migration `0013_m9_news_feeds` (the feeds and the guards' fixed path), and the update file's read-out of each source's newest fetch and the main run's policy. Not yet installed: the owner's double-click on `update-app.cmd` installs it, and the thread then reads the read-out.
- 2026-10-19 20:47 UTC: the owner's "Go"; APPROVED.
- 2026-10-19: PROPOSED (documents only). [ExecPlan 0027](0027-m9-market-intelligence-and-event-driven-trading.md), the [roadmap](../../ROADMAP.md#m9--market-intelligence-and-event-driven-adaptive-paper-trading), [STATUS](../../STATUS.md), the [documents index](../../README.md) and [the idea note](../ideas/agent-roles-and-coordinator.md) point here. Nothing implemented or run.
