# ExecPlan 0033 — M10: the agents look beyond BTC and SOL

**Status: APPROVED on 2026-10-20 at 11:03:32 UTC with "Research and trade" ([DECISIONS](../../DECISIONS.md#2026-10-20--m10-approved-research-and-trade)); update 1 built and tested in the cloud, not yet installed ([§14](#14-progress)); update 2 waits for update 1 to run on the PC.** Proposed earlier the same day. It re-scopes M10 ([ExecPlan 0028](0028-m10-coin-discovery-and-controlled-expansion.md)) under M8's rules ([ExecPlan 0031](0031-m8-simple-app-that-runs-itself.md)), as [ExecPlan 0032](0032-m9-news-and-events-the-agents-trade-on.md) re-scoped M9. The owner's pick on the go-ahead card in the project thread "Get M9 ready to build" approved it and settled the scope question of §12: both updates. Where this plan and 0028 differ, this plan governs; 0028 stays as the design record and the source of the requirement IDs cited here. Written from `main` at `ed041b8`.

Labels: `OBSERVED` (seen in code, records or official pages), `INFERRED`, `PROPOSED`, `NOT RUN`.

## 1. Goal and observable outcome

The owner asked on 2026-10-16 for broader coin coverage and fuller use of the app's agents, with discovery first and more tradable coins gated separately ([DECISIONS](../../DECISIONS.md#2026-10-16--m9-refinements-and-separate-m10-discovery-specification)). On 2026-10-20 at 10:34:53 UTC the owner picked "Go" on the card "Accept M9 and plan M10, where the agents research coins beyond BTC and SOL?" ([DECISIONS](../../DECISIONS.md#2026-10-20--m9-accepted-m10-planned-under-execplan-0033)).

The goal: the app finds the coins on Binance's spot market that are worth a look, and the analyst researches them while the evaluator checks the research. If the owner says yes (§12), the agents may then trade three of them on paper as well as BTC and SOL. The total limits stay where they are, so the agents get more choice and no more total risk.

Observable after M10:
1. Every day the app scans Binance's USDT spot pairs and keeps a watchlist of the 8 most liquid coins that pass fixed rules. A new Coins page shows the watchlist, the coins left out and why.
2. The analyst writes a short note on each watchlist coin, and the evaluator reviews it. The notes are on the Coins page.
3. With the owner's yes, update 2 lets the agents trade three watchlist coins on paper under the same limits. Their positions and results show on the existing pages.
4. Each part is one update and one double-click.

## 2. What the app already has (OBSERVED at `ed041b8` unless marked)

- **Market data for two coins, fixed in code and in the database.** The market worker reads Binance's market-data-only hosts without credentials, with fixed streams for `btcusdt` and `solusdt` (`app/market_data/provider.py:20-22`). Database checks name the coins in many tables: ledger assets `USDT`, `BTC`, `SOL` (`0002_m1_account.py:103`), market symbols (`0003_market_data.py:95`), holdings (`0005_m3_paper_broker.py:108`), and the agents' decision tables (`0009_m7_agent_decisions.py:402`). The API types name them too (`app/main.py:304`), and so do the agents' step schemas.
- **The operating policy names its coins.** `AGENT_POLICY_V2` has `universe` `["BTCUSDT", "SOLUSDT"]` with the limits it enforces: 2 accepted entries in any 24 hours and 1 per coin, 0.75 of equity in committed notional, and exposure fractions of 0.05 to 0.25, the smallest of these and every risk limit applying (`0012_m8_one_run.py:45`).
- **Binance's free endpoints cover a scan.** The market-data-only host `data-api.binance.vision` serves `exchangeInfo`, `ticker/24hr`, `ticker/bookTicker`, `klines` and `uiKlines` among its 13 REST endpoints ([Binance, market-data-only services](https://developers.binance.com/docs/binance-spot-api-docs/faqs/market_data_only), read 2026-10-20). The weights are: all 24-hour tickers 80, all book tickers 4, klines 2 per request ([market data endpoints](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints), read 2026-10-20), and `exchangeInfo` 20 as the app charges it (`app/market_data/provider.py:368`), against an allowance of 6,000 a minute per IP that the PC read on 2026-10-02 ([INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#market-rest-budget-and-clock-measure--2026-10-02-execplan-0022)). The PC already reaches this host.
- **Four agent roles and their counts.** The analyst investigates, the evaluator reviews, and the coordinator decides. The researcher is not used in M10 (§8). Investigations have their own 16 a day, decisions 36.
- **The agents share the owner's ChatGPT usage allowance** with the owner's own Codex use. It ran out on 2026-10-19 twice and on 2026-10-20 at about 09:00 UTC. At the limit the agents pause and resume by themselves, and the stops keep protecting positions ([STATUS](../../STATUS.md)).
- **No free per-coin news or token data.** M9's update 1 dropped CoinDesk's feed, whose terms forbid automated reading, and confirmed no other crypto news outlet (0032 §5.1). Token supply, unlocks and project news for other coins have no source the app can use without keys or spending (INFERRED from 0028 §4; not searched again).

## 3. What changes from ExecPlan 0028

| 0028 asked for | M10 now |
|---|---|
| Several providers, a cross-provider asset registry and identity resolution (§4) | One provider: Binance's own spot listing. A coin is its Binance base asset and USDT pair, and no other provider is joined, so no ticker has to be matched across providers |
| Screening thresholds frozen from measurements at B0 (§4) | Fixed rules by rank, with no volume or market-cap minimum (§5.1, D3) |
| A discovery workflow with follow-ups, experiments and handoffs (§5) | One research note per coin, reviewed once. No researcher experiments on new coins |
| Owner approval per coin and a dynamic eligible universe (§7) | The owner's yes on this plan's scope; then three coins named in update 2, which the owner installs. Changing them is a later update |
| B0 to B8, PC load runs, matched comparisons (§8, §10) | Two updates, the cloud tests and each update's own checks (0031 §4.8). The Decisions page's version segments show V2 beside V3, with no claim that more coins help |
| Multi-asset accounting, valuation and policy work (§7) | Kept for update 2, for exactly five coins |

Kept from 0028: discovery and trading stay separate; a rank or a note is never an order to buy; unknowns stay unknown; positions keep their original terms; protections stay in code; no new role, provider, credential, spending, DEX or on-chain trading.

## 4. Decisions Claude made under the owner's delegation

The owner delegates such calls ("you have my authorization for everything", 2026-10-19 11:08 UTC). They are recorded here.

- **D1. Binance only.** The scan and every number about a coin come from the host the app already uses. No CoinGecko or other screener: their free use is either keyed or not meant for scheduled use (0028 §4).
- **D2. A watchlist of 8.** It is enough to show alternatives and small enough to research weekly within a small daily count.
- **D3. Rules by rank, no minimums.** Candidates are ranked by liquidity, and the 8 best that pass fixed exclusions make the list. A fixed volume minimum would be an invented number.
- **D4. Research notes, not investigations.** A coin note is a new kind of work for the analyst with its own count of 3 a day. It never takes from the 16 investigations that news and price moves use for BTC and SOL.
- **D5. Three more coins, picked from the PC's data.** Update 2 names three coins from the watchlist as the PC reads it after update 1 (§5.2). Three keeps the coordinator's view, the market data and the money-path change small. More later is its own update.
- **D6. Same totals.** Every total limit of `AGENT_POLICY_V2` stays as it is, along with 1 entry per coin in 24 hours.
- **D7. Fixed coins, no rotation.** A traded coin stays tradable until a later update changes the list, so the ledger never has to drop a coin. A coin Binance stops trading blocks new entries through the checks the app already has.
- **D8. Two updates, research first.** Update 2 is built only from what update 1 shows on the PC, and only with the owner's yes (§12).

## 5. Design (PROPOSED)

### 5.1 Update 1: the watchlist and the coin notes

As proposed; what the build changed is in [§14](#14-progress) (2026-10-20, update 1 built), and the records in [DATA_CONTRACTS](../contracts/DATA_CONTRACTS.md#m10-records-execplan-0033).

- **The daily scan** runs once a day at 00:20 UTC, outside the quiet window, in code with no model. It runs outside the market worker, so the BTC and SOL collection keeps its own request budget. A scan costs about 170 weight: `exchangeInfo`, all 24-hour tickers, all book tickers and 30 daily-kline requests of 90 bars. It spreads that over several minutes and keeps the IP-wide weight far below the market worker's guard of 3,000.
- **Candidates:** USDT spot pairs that Binance lists as `TRADING` with spot trading allowed. Excluded, each with its reason recorded:
  - BTC and SOL;
  - stablecoins, fiat and commodity tokens, from a list in code (for example USDC, FDUSD, EUR, PAXG);
  - wrapped or staked versions of another coin, from a list in code (for example WBTC, WBETH);
  - leveraged tokens.
- **Rules:** take the 30 with the highest 24-hour quote volume. Of those, keep the ones with at least 90 finalized daily bars and a spread no wider than 20 bps in the book ticker at the scan. Rank them by the median daily quote volume of the last 30 days. The best 8 are the watchlist. Each number is Claude's engineering default, not a measurement. Binance's answers are stored as received with their times, and a missing field leaves the coin out with that reason.
- **Watchlist candles.** Every hour the app reads the finalized hourly bars of the watchlist coins (8 requests of weight 2) and keeps 120 days of them. They are research data, labeled so. They never become a quote, a fill or a mark.
- **Coin notes.** For each watchlist coin, the analyst writes a note when the coin joins the list, and again when its note is 7 days old. The note covers:
  - how the coin moved against BTC over 7, 30 and 90 days, its volatility, its correlation with BTC and SOL, and its liquidity (each figure calculated in code);
  - what the app cannot know: project news, token supply and unlocks;
  - what would make it worth trading, and what would rule it out;
  - one of `WORTH_WATCHING`, `NOT_NOW` or `RULE_OUT`.

  The evaluator reviews each note as it reviews an assessment. At most 3 notes a UTC day, apart from the investigations' 16. The notes use the existing macro feeds as context, and no new source.
- **Generation 5** of the agent definitions holds the note's template, with a new analyst prompt and its review child. Its tools are the analyst's and the evaluator's read tools, plus one read of the watchlist view. No tool with an effect is added. As with generation 4 in M9, generation 5 adds only what no policy binds, so `AGENT_POLICY_V2` stays in force through update 1 ([0032 §5.2](0032-m9-news-and-events-the-agents-trade-on.md#52-the-agents-and-agent_policy_v3-update-2)).
- **The Coins page** shows:
  - the watchlist, with each coin's rank, median volume, spread, return against BTC, and the date, label and review of its note;
  - the candidates that were left out, each with its reason;
  - the time of the last scan.

  Each note opens below its row. The page follows the shadcn rules (rule 6) and reads well at 390 px.
- **The update file** prints the first scan's watchlist and whether the first note was written.

### 5.2 Update 2: three more coins on paper (only with the owner's yes)

- **The coins.** About two days after update 1 is installed, the thread reads the watchlist on the PC, read-only. It picks the three best-ranked coins whose latest note has an acceptable review and is not `RULE_OUT`, and records them and the data behind them in §13. If fewer than three qualify, update 2 adds fewer and says so.
- **Money path.** Migration `0016` (update 1 took `0015`) adds the three coins to every coin list in the database (ledger assets, holdings, market tables and agent tables). BTC's and SOL's rows and history are untouched. Accounting, valuation, fees, reservations and reconciliation read one coin list in code instead of two literals, with exact decimals as now.
- **Market data.** The market worker streams the new coins' ticker and hourly candles under the same rules: freshness, gap handling and instrument filters from `exchangeInfo`. Its own weight ceiling is unchanged.
- **The policy.** `AGENT_POLICY_V3` is `AGENT_POLICY_V2` with the five coins in `universe` and `symbol_priority`, bound to generation 6 of the agent definitions, whose decision templates and step schema name the five coins. (M9 built no V3, so the name is free.) Every limit and cadence value is V2's (D6). The app records V3 in force and moves the main run to it once the account holds no position, as M8's update 3 built. Positions opened under V2 keep their terms.
- **The coordinator** sees each coin's latest reviewed note beside the existing evidence. An entry still needs the evidence V2 asks for: a reviewed assessment of that coin, inside its expiry.
- **Sources.** If a new coin's project publishes its releases on GitHub, its release list is added as a source the way Bitcoin Core and Agave are.
- **Pages.** The trigger card and the positions show results by coin.
- **Documents.** Rule 1 of [AGENTS.md](../../../AGENTS.md), [PROJECT](../../PROJECT.md) P02 and [ACCEPTANCE_CHECKLIST](../../ACCEPTANCE_CHECKLIST.md) A01 change from "BTC/SOL" to "BTC, SOL and the coins the installed operating policy names", with the earlier texts kept in DECISIONS. The same update changes RISK_POLICY, MARKET_DATA, LEDGER and AUTONOMY_MATRIX.

### 5.3 What stays

- The five protections of [0031 §4.1](0031-m8-simple-app-that-runs-itself.md#41-what-stays-and-why), and positions' original terms.
- Paper only, spot only, long only. No exchange credentials, no leverage.
- Exits never wait for a model, and stale data blocks new exposure.
- A rank, a label or a note is data. None of them adds a coin, raises a limit or places an order.
- The app reads no project websites, social media or paid data.

## 6. M9's open items, and M9's acceptance

M9 is accepted as installed: both updates are `COMPLETE` on the PC (0032 §14), by the owner's pick of 10:34:53 UTC. Its open item is the first investigation of a feed item or a price move on the PC, which waits for the agents to work again after the usage limit. The thread reads it read-only when M10's update 1 is installed, and records it in 0032 §14.

## 7. Requirements and tests (PROPOSED)

| ID | Requirement | Test |
|---|---|---|
| C1 | The scan stores Binance's answers as received, applies the fixed rules and exclusions, records why each coin is out, and never invents a missing field | Scan tests on recorded fixtures: missing fields, halted pairs, a stablecoin, a leveraged token, ties, fewer than 8 qualifying |
| C2 | The scan and the watchlist candles never become BTC or SOL market data, a quote, a fill or a mark, and stay inside their own request budget | Tests on the stores and on the weight budget with a stand-in transport |
| C3 | A coin note runs within 3 a day and once a week per coin; it cannot add a coin to trading, a tool, a source or a limit | Budget and grant tests; the existing injection fixtures through note and review |
| C4 | A note keeps unknowns unknown, and its review refuses an unsupported claim | Fixtures with invented supply figures and causal claims |
| C5 | The Coins page reads well at 390 px with its loading, empty and error states | Component and browser tests |
| C6 | With three more coins, accounting, valuation, fees, reservations and reconciliation are exact, and BTC's and SOL's records keep their meaning | Money-path tests on five coins, partial fills and restarts; independent review (rule 13) |
| C7 | V3 accepts only its five coins at every effect; intents for different coins share one capacity, and the totals stay V2's | Policy, risk and dispatcher tests |
| C8 | The new coins' market data meets the same freshness and gap rules; a missing quote blocks entries and shows the stop as unavailable | Market worker tests with the new streams |
| C9 | The main run moves to V3 only when flat; V2's positions keep their terms | Run-keeper tests |
| C10 | The update file prints the first scan and note (update 1) and the three coins' first quotes (update 2), and reports failure honestly | The update file's model test |
| C11 | The five protections hold | The existing money-path, stop and off-switch tests, unchanged and passing |

## 8. Not in M10

Each of these needs its own later update, if wanted:
- per-coin news, token supply and unlocks, project websites and social media (no source the app may use);
- other providers, DEX data and on-chain data;
- more than three extra coins, or changing them automatically;
- researcher experiments on new coins;
- the matched comparisons of 0028 R10, R11, R16 and R17;
- a fifth role or one agent per coin.

## 9. Implementation sequence

Each part is its own pull request, merged by its thread once ready. Each update is one double-click on `update-app.cmd`, after which the thread checks the result read-only.

1. **This plan** (documents only).
2. **Update 1:** the scan, the watchlist candles, the coin notes and generation 5, and the Coins page. No money path changes.
   - Documents: DATA_CONTRACTS, MARKET_DATA, RUNTIME_AGENTS, AGENT_TOOL_CONTRACTS, AUTONOMY_MATRIX (one line: SYSTEM keeps the watchlist), API_CONTRACTS, FRONTEND, TESTING, COMMANDS and INTEGRATION_EVIDENCE.
3. **Update 2,** only with the owner's yes (§12): the three coins, migration `0016`, the market worker's streams, generation 6 and `AGENT_POLICY_V3` and the scope documents of §5.2, with an independent review of the money path. It is merged only after update 1 ran on the PC and its coins are recorded in §13.

M10 is complete when its updates are installed with `COMPLETE` records and the thread has read, read-only, the first watchlist and a reviewed note. With update 2, the thread also reads the new coins' first quotes and the main run on V3. M10 sets no profit target.

## 10. Verification commands (PROPOSED)

As [0032 §10](0032-m9-news-and-events-the-agents-trade-on.md#10-verification-commands-proposed): in the cloud, the web lint, types, unit tests and build, the engine's ruff, OpenAPI check and tests without and with a scratch PostgreSQL, and the browser suites. On the PC, the update file's own checks. The exact commands go into [COMMANDS](../../COMMANDS.md) as each update is built; none is VERIFIED for M10 yet. The cloud cannot reach Binance (0028's measurement was refused there on 2026-10-17), so the scan's real answers are first seen on the PC.

## 11. Failure and rollback

- A scan that fails leaves the previous watchlist in place, marked with its age. Nothing fills the gap.
- The notes add up to 3 model runs a day to the shared usage allowance. At the limit they wait, and the decisions and stops are unaffected.
- A coin Binance halts or delists stops being quoted. New entries in it are blocked. A position in it keeps its stop, shown as unavailable while no valid quote exists; nothing is filled at an invented price.
- Each update takes a backup and rollback tags. Migrations `0015` and `0016` are additive. Once a position in a new coin exists, rolling back to two-coin code is refused and the fix goes forward (0028 §13).

## 12. The owner's question

Trading coins beyond BTC and SOL changes rule 1 of AGENTS.md, so it is the owner's call, asked on the go-ahead card:
- **Research and trade:** both updates. Update 2 lets the agents trade three more coins on paper, under the same total limits.
- **Research only:** update 1 only. Trading stays BTC and SOL until the owner says otherwise.

## 13. Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-10-20 | M10 is re-scoped under M8's rules in this plan; 0028 stays as the record | 0028 still assumed approvals, multiple providers, PC runs and comparisons that M8 removed |
| 2026-10-20 | D1 to D8 (§4), by Claude under the owner's delegation | Each is the simplest option that keeps the five protections and the total limits |
| 2026-10-20 | The owner's "Go" (10:34:53 UTC): M9 accepted, this plan written | [DECISIONS](../../DECISIONS.md#2026-10-20--m9-accepted-m10-planned-under-execplan-0033) |
| 2026-10-20 | The owner's "Research and trade" (11:03:32 UTC): this plan approved with both updates | [DECISIONS](../../DECISIONS.md#2026-10-20--m10-approved-research-and-trade) |
| 2026-10-20 | Update 1: no hourly watchlist candles; the scan keeps the daily bars it reads | The notes use daily figures only, and nothing reads hourly bars of a coin that is not traded; update 2 streams the traded coins' candles as BTC's and SOL's |
| 2026-10-20 | Update 1: no watchlist read tool; the note's job carries its coin's entry as the scan recorded it | The analyst needs one coin's figures, and a value in the job cannot be misread or fetched for another coin; generation 5 adds no tool |
| 2026-10-20 | Update 1: `exchangeInfo` and the book tickers are asked for the 30 candidates only | The PC's read (11:07 UTC) found the unfiltered `exchangeInfo` 5.9 MB, over the 2 MiB answer cap every client keeps |
| 2026-10-20 | Update 1: two more reasons to leave a pair out, `STABLE_PRICE` (every close within 0.97 to 1.03) and `TRACKS_BTC_OR_SOL` (daily returns correlated 0.98 or more) | A pegged coin or a version of BTC or SOL that the name lists miss would otherwise take a watchlist place |
| 2026-10-20 | Update 1: a failed scan is tried again an hour later, at most 4 times a UTC day | One failure would otherwise leave a day without a watchlist |
| 2026-10-20 | Update 1: each note sits in its own card under the table, with a link to its workflow, rather than opening below its row | The table already scrolls sideways at 390 px; a note opened inside it would not read |
| 2026-10-20 | Update 1, after the independent review: a lost request for any coin's daily bars fails the whole scan; a scan that cannot be written is recorded as a failed attempt; the update file checks the Coins page and prints the newest scan in each case; the day's note count is the cap's; the API and the agents may not read the daily bars; only the coin note searches the sources unnarrowed | A network fault would otherwise have shown a partial or empty watchlist as a success for the whole day (§11), and the rest closes gaps the review found; reasons in [COMMANDS](../COMMANDS.md#m10-update-1-the-coin-watchlist-and-the-notes--2026-10-20) |
| 2026-10-21 | The owner's "go" (06:24 UTC) to build update 2 | [DECISIONS](../../DECISIONS.md#2026-10-21--m10-update-2-zec-near-and-xrp-traded-on-paper-execplan-0033) |
| 2026-10-21 | Update 2's coins: **ZEC, NEAR and XRP**, by §5.2's rule, from a read-only read of the PC at about 06:30 UTC | The 00:20 UTC scan ranked ETH, ZEC, NEAR, XRP, SUI, BNB, DOGE, UNI (median 30-day quote volume 696.2M, 215.6M, 180.7M and 170.1M USDT for the first four; spreads 0.04 to 2.02 bp). ETH has no note (its note of 2026-10-20 13:30 UTC ended `QUOTA_BLOCKED`). ZEC (`NOT_NOW`, 18:06 UTC), NEAR (`WORTH_WATCHING`, 18:11 UTC) and XRP (`NOT_NOW`, 2026-10-21 00:00 UTC) each have a note reviewed `ACCEPTABLE`; none is `RULE_OUT`. Their 14-day ATR is 9.5 %, 10.9 % and 4.7 % of price, and their 90-day correlation with BTC 0.55, 0.43 and 0.89 |
| 2026-10-21 | Update 2 adds generation 6 (five templates, step schema v5, tool catalog v6) and `AGENT_POLICY_V3` instead of editing generation 3 and V2 | Installed definitions are bound by their hashes; a new generation and a new policy keep every earlier record readable as it was. V3 is V2 with the five coins: only its identity, universe, symbol order and agent definitions differ |
| 2026-10-21 | Generation 6 gives the model the length limits the app checks (schema and prompts), and a retry is told which field failed and why, in the schema's own words only | 13 answers were refused `SCHEMA_INVALID` from 2026-10-19 to 2026-10-21, each with a valid shape and a string over its limit (notes and deficiencies of 310 to 378 characters against 300); the retry was not told why. The detail names only fields the schema has, so no text the model wrote reaches the next prompt |
| 2026-10-21 | The coordinator sees the latest reviewed note of each traded coin; an entry still needs a reviewed brief that covers its coin | The notes are research about the coins it may now trade; a note alone stays no entry basis, by the tool and the database guard |
| 2026-10-21 | No release sources or price-move rule for the new coins in this update | Generation 4's investigation and its `PRICE_MOVE_V1` rule name BTC and SOL only, so adding them needs a later generation; the hourly decisions with the five-coin brief cover ZEC, NEAR and XRP ([STATUS](../../STATUS.md#open-follow-ups)) |
| 2026-10-21 | The market worker asks one combined `exchangeInfo` for the five coins and falls back to one request per coin, BTC and SOL first; its retention runs up to 80 calls an hour and its storage stop is 12 GiB | One request keeps the hourly check's weight as for one coin, and a coin Binance stops listing fails only itself. Five coins bring about 27,000 observations an hour (two brought 10,800), so retention and the stop keep the same margins as before. The PC's free disk was not checked for this |
| 2026-10-21 | Update 2, after the independent review: (a) the retry detail names no field the schema lacks; (b) V1, V2 and V3 count together for the 24-hour notional window and the wait after a protective stop, so the move to V3 resets neither; (c) the engine reads and values every coin it holds, has a position or an order in, not only its policy's coins; (d) migration `0016` takes its locks up front in the workers' order and adds the widened checks `NOT VALID`; (e) its downgrade also refuses while a runtime profile binds generation 6; the update file names the move to V3 only for a main run on an earlier policy | (a) a key the model invented reached the next prompt; (b) a flat V2 run moved to V3 would otherwise skip V2's six-bar wait and restart the window; (c) a dust balance in a new coin would leave an older policy's valuation invalid for good; (d) the old checks were re-validated across a week of quotes under exclusive locks while the app runs; (e) the downgrade would delete definitions a profile binds |
| 2026-10-21 | Update 2: the agent-runtime view carries `budgets_v6`; found by the Decisions browser suite, which failed before the fix | Without it the API refused its own view (`extra_forbidden`), and the Agents page would not have loaded after the install |
| 2026-10-21 | Update 2, from the whole engine suite: a coin with no feed row reads as unavailable in the risk and experiment views; tests that expected two coins (the stream faults, a clock reference check's pending feeds, the account and agent holdings) now expect the five, and the test profiles that cap a decision-family purpose bind the cap in generation 6 too | A database before `0016` has feed rows for BTC and SOL only, and the risk view read on a database at `0008` (R29) failed on ZEC. A day's cap is read from the newest generation that names its purpose (`generations.daily_cap`), now generation 6, whose values equal generation 3's; no check was loosened |
| 2026-10-21 | Update 2's web changes stay small: the coin lists come from one place, the Markets page's coin buttons wrap, and the Coins page marks a watchlist coin the app trades on paper | The project thread "Simpler app for trading" (its ExecPlan 0035, not yet merged) is reshaping the pages and builds on this update after it is installed |
| 2026-10-21 | Fills in the new coins are modeled with the same cost scenario as BTC and SOL | No coin's own fee or slippage measurement exists in the app; the fills stay labeled modeled, and the paper results in these coins are as uncertain as that assumption |
| 2026-10-21 | The agent runner accepts a prompt up to 98,304 bytes, generation 6's `prompt_max_bytes`, instead of 65,536; a test ties the two bounds together | Found on the PC after the install: generation 6 composes prompts up to 96 KiB for five coins, but the runner still refused any prompt over 64 KiB with `400 INVALID_JOB`. The worker treats a refused submission as an unknown outcome and resubmits until the call's deadline, so the review's fifth step (69,280 and 69,383 bytes) ended `NEVER_CONFIRMED` and the first V3 check failed. Raising the runner's bound changes neither its identity (binary, configuration) nor any agent definition; a refused submission that fails at once instead of at its deadline is left for later |
| 2026-10-21 | The agents' check counts what the tools returned as the brief's own finish counts it: each result's and completion's reference and the IDs its envelope made citable, such as the releases a `search_evidence` call found; probe CP-01 uses the same rule | Found on the PC: the second V3 check (probe run 32, 10:39 to 10:44 UTC) reached the model at every step and its review finished, but its brief case failed because the assessment cited two releases its search returned. The brief's finish accepted them; the check, counting only result references, did not. The check was stricter than the app; a reference no tool returned still fails it |

## 14. Progress

- 2026-10-21 (12:16 to 13:25 UTC, OBSERVED read-only on the PC): **the first decisions under V3** held all five coins: the 12:00 bar's decision (12:06 UTC, before the brief), the one the 12:00 brief's `ACCEPTABLE` review started (12:16 UTC; its notes: trend alone not enough for BTC and SOL, NEAR's latest hour negative, XRP's relative weakness, ZEC's continuation uncertain) and the 13:00 bar's (13:06 UTC). No intent, order or fill. The 12:00 brief's review reached 71,081 bytes, which only the runner fix admits; the brief's finish was refused once `SCHEMA_INVALID` and its retry passed. **The check's citation fix installed** by the owner's third double-click (record `COMPLETE`, 12:41:48 to 13:09:45 UTC, `2bf5b1e`, no migration, reconciliation OK, seven pages 200); no check has run since run 33, so the new rule is not yet seen on the PC. The first `PRICE_MOVE` investigations ran (BTC 13:06 UTC, SOL 13:09 UTC; both reviews `NEEDS_EVIDENCE`, the reviewers writing that they could not inspect the search results the investigation cited; not investigated). One review step straddled the runner's recreation (`RUNNER_FORGOT_CALL_KEY`, 13:08 UTC) and its retry passed.
- 2026-10-21 (11:14 to 11:20 UTC, OBSERVED read-only on the PC): **the agents' check passed under `AGENT_POLICY_V3`** on the new runner (probe run 33, 11:14:02 to 11:18:47 UTC, 16 of 18 calls, generation 6's templates): the decision case held, and the brief's eight steps and its review's six reached the model at the first try, the largest prompt 55,012 bytes; the review's own verdict was `REJECT`, which the check does not judge. Decision verification `VERIFIED` for V3; runtime `ENABLED` (`CHECK_PASSED`). That brief cited only result references (its search returned no release), so the citation fix below was not exercised. The 11:00 UTC hourly decision had been refused (`CHECK_PENDING`); the first under V3 is due at 12:00 UTC.
- 2026-10-21 (10:39 to 11:13 UTC, OBSERVED read-only on the PC): the second V3 check (probe run 32, 10:39:27 to 10:44:01 UTC, still on the old runner) failed only in its brief case: the review's six steps reached the model (prompts 42,446 to 54,775 bytes) and it finished `NEEDS_EVIDENCE`, but the assessment cited 8 references, 6 tool results and 2 release IDs that `search_evidence` returned in its citable list, and the check did not count the 2 (§13). The owner's second double-click installed the runner fix with ExecPlan 0035's pages (record `COMPLETE`, 10:50:44 to 11:11:02 UTC, `7440a89`, no migration). The check's fix was installed at 13:09 UTC (above).
- 2026-10-21 (10:11 to 10:31 UTC, OBSERVED read-only on the PC): **update 2 installed** by the owner's double-click (record `COMPLETE`, 09:43:13 to 10:10:54 UTC, `3dd5011`; schema `0016_m10_three_coins`; reconciliation OK; the six pages answering). BTC, SOL, ZEC, NEAR and XRP feeds `CONNECTED` with quotes at 10:11 UTC; the new coins' holding rows at zero; main run `8fb7a74e` `RUNNING` on `AGENT_POLICY_V3` from 10:09 UTC (the V2 run `2580d8ea` stopped). The agents' check at 10:09 UTC passed, but for V2: it started 3 seconds before the V3 run. The first check for V3 (10:16 to 10:24 UTC, generation 6) failed: the decision case passed, while the brief's review never reached the model because the runner refused its fifth step's prompt (69,280 and 69,383 bytes) as longer than 64 KiB (`submit 400` in the agent worker's log, 108 times for each attempt). No `SCHEMA_INVALID` refusal since 09:00 UTC. Fixed in the cloud the same day (§13); not yet installed.
- 2026-10-21: **update 2 built and tested in the cloud** on branch `claude/plan-m9-ob2ejk` ([COMMANDS](../COMMANDS.md#m10-update-2-zec-near-and-xrp-on-paper--2026-10-21)): one coin list in code (`app/markets.py`) for the market worker's streams, accounting, valuation, risk, the API and the web; migration `0016_m10_three_coins` (the widened checks, the new coins' holding rows, generation 6 and `AGENT_POLICY_V3`, installed `PROPOSED` as V2 was); generation 6; the run keeper's move of a flat main run to V3; and the update file's read-out of each coin's newest quote. An independent review found no ledger defect; its findings are fixed (§13). Not yet installed: the owner's double-click on `update-app.cmd` installs it, and the thread then reads the new coins' first quotes and the main run on V3.
- 2026-10-21 (about 06:30 UTC, OBSERVED read-only on the PC): the 00:20 UTC scan and its notes (§13); XRP's note (00:00 UTC, `NOT_NOW`), SUI's (00:08 UTC, `WORTH_WATCHING`) and BNB's (00:10 UTC, `NOT_NOW`) were each reviewed `ACCEPTABLE`; the main account held no position.

- 2026-10-20 13:11 UTC: **update 1 installed on the PC** by the owner's double-click on `update-app.cmd` (`3ec85ec`; schema `0015_m10_coins`; the Coins page answering; its record read `COMPLETE` by the building thread at about 13:25 UTC). OBSERVED read-only through the owner's device session at about 21:50 UTC:
  - the first scan ran by itself at 13:11 to 13:12 UTC (`SUCCEEDED`, weight 166, 34 requests); the watchlist, best first: ETH, ZEC, NEAR, XRP, SUI, BNB, DOGE, UNI;
  - ETH's note (13:30 UTC) ended `QUOTA_BLOCKED`: the owner's Codex allowance was used up. ZEC's note (18:06 UTC, `NOT_NOW`) and NEAR's (18:11 UTC, `WORTH_WATCHING`) were each reviewed `ACCEPTABLE`;
  - a coin whose note was started is not tried again for 24 hours (`NOTE_RULE`), so ETH's note waits for a later pass (NOT OBSERVED).

  With these, update 1's part of §9, the first watchlist and a reviewed note, is read. Update 2 follows from 2026-10-22 13:30 UTC.
- 2026-10-20: **update 1 built and tested in the cloud** on branch `claude/plan-m9-ob2ejk` ([COMMANDS](../COMMANDS.md#m10-update-1-the-coin-watchlist-and-the-notes--2026-10-20)): the daily scan (`app/coins`, rules `COIN_SCAN_V1`) in its own thread of the source fetcher, with its own client and weight count; migration `0015_m10_coins` (the scan's three tables and generation 5); the analyst's coin note and the evaluator's review (`COIN_NOTE_V1`, `COIN_NOTE_REVIEW_V1`, at most 3 a UTC day, one at a time, best rank first); `GET /v1/coins` and the Coins page; and the update file's read-out of the newest scan and the notes written. As built, against §5.1:
  - no hourly candles of the watchlist coins, and no watchlist read tool (§13);
  - a scan sends up to about 168 weight: the 24-hour tickers (80), `exchangeInfo` (20) and the book tickers (4) for the 30 candidates, and 32 daily-kline requests of 92 bars (2 each), the candidates' and BTC's and SOL's, which the figures against BTC and SOL need; a scan keeps 91 finalized days;
  - two more reasons to leave a pair out, and a failed scan retried hourly, at most 4 times a day (§13);
  - each note in its own card with its review and a link to its workflow (§13);
  - the cut to 30 candidates comes before the instrument check, so a pair Binance no longer trades but still lists with recent volume can take one of the 30 places; it is then left out as `NOT_TRADING`, and the watchlist takes the next coins.

  Not yet installed: the owner's double-click on `update-app.cmd` installs it, and the thread then reads the first scan and the first note on the PC.
- 2026-10-20: PROPOSED (documents only). [ExecPlan 0028](0028-m10-coin-discovery-and-controlled-expansion.md), the [roadmap](../../ROADMAP.md#m10--coin-discovery-and-controlled-expansion), [STATUS](../../STATUS.md) and the [documents index](../../README.md) point here. Nothing implemented or run.
