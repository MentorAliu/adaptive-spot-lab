# Official reference register

**Revision date: 2026-09-26.** The original 50 primary references are retained from pack 1.0.0; the v2 refresh scope is listed below. Retention is not a claim that every URL was fetched again in this revision. Redirects to new official documentation locations are expected. No package, preset, client, API or account integration has been executed in the user's environment by this pack.

Implementation must compare current official guidance with actual installed versions and record evidence in [INTEGRATION_EVIDENCE.md](INTEGRATION_EVIDENCE.md). Moving `/latest` pages are not a dependency lock. Official documentation supports API/tool behavior, not the profitability of the proposed trading policy.

The architecture, risk numbers, strategy seed and workflow are **project design proposals** unless explicitly identified as owner-confirmed or observed. No cited vendor endorses the proposed trading system or its returns. No external skill text, licensed font, credential or library code is bundled in this Markdown pack.

## Backtest data — 2026-11-03

Opened by the thread "Backtest the rule twins on history" for [ExecPlan 0051](../plans/0051-backtest-the-rule-twins-on-history.md). BT-01 was read through the session's fetch tool, which returns a model's reading of a page rather than its raw text; BT-02 and BT-03 were used by a device session on the owner's PC, since the cloud refuses Binance's hosts. Public market data only: no key, no account, no private endpoint.

| ID | Source | Read | Narrow use |
|---|---|---|---|
| BT-01 | [Binance — binance-public-data](https://github.com/binance/binance-public-data) | 2026-11-03, cloud | The kline columns (open time, open, high, low, close, volume, close time, quote volume, trades, taker buy base and quote volume, ignore), the `.CHECKSUM` beside every zip and its `sha256sum -c` check, the spot archive's microsecond timestamps from 2025 (the futures examples are milliseconds). The repository's licence is MIT; the page states no separate licence for the data. It does not give the futures paths. |
| BT-02 | [Binance public data archive, USDⓈ-M futures](https://data.binance.vision/?prefix=data/futures/um/) | 2026-11-03 08:26 to 08:52 UTC, owner's PC | The monthly and daily 1-minute `klines`, `markPriceKlines` and the monthly `fundingRate` of BTCUSDT, 2020-01 to 2026-10, each zip equal to its SHA-256 `.CHECKSUM` (the device session's `manifest.txt`); 2019-09 to 2019-12 and three daily files answer 404 ([0051 §14](../plans/0051-backtest-the-rule-twins-on-history.md#14-progress)). |
| BT-03 | Binance USDⓈ-M futures, public `GET /fapi/v1/exchangeInfo` ([MARKET_DATA](MARKET_DATA.md)) | 2026-11-03 08:27:00 UTC, owner's PC | BTCUSDT's tick 0.10, step 0.001, minimum quantity 0.001, market maximum 120 and minimum notional 50 for the simulator's fills; read once, today's values applied to the whole history. |

## Event calendar — 2026-11-04 and 2026-11-09

Opened for [ExecPlan 0058](../plans/0058-the-event-calendar.md) by the project threads "Research an event calendar for the trader" (2026-11-04) and "Add the event calendar to the trader" (2026-11-09), the Fed's pages through the session's fetch tool, which returns a model's reading of a page rather than its raw text: check a date against the page before relying on it. The Fed's dates are in `definitions_v19.FED_STATEMENTS`, each converted to UTC by a test with the IANA zone.

| ID | Source | Type; opened | Supported use and limits |
|---|---|---|---|
| EC-01 | An event calendar for the trader (2026-11-04), with its files in the project's `event-calendar/` (the study's script, its 153 events, its results and the PC's read of the stored BLS calendar) | The project's own review and event study; 11-04 | Bitcoin's moves, ranges and modeled stop-outs around 57 CPI, 57 jobs-report and 39 Fed releases, 2022-01 to 2026-10, against matched non-event days, on Binance's archive ([BT-02](#backtest-data--2026-11-03)); CALCULATED, modeled fills. The window's ends (0058 §2). Not a return expectation. |
| EC-02 | [Federal Reserve — Meeting calendars and information](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | Official page; 11-09 15:26 UTC | The 2026 meeting of December 8-9, 2027's eight (January 26-27, March 16-17, April 27-28, June 8-9, July 27-28, September 14-15, October 26-27, December 7-8), the note of a meeting on January 25-26, 2028, and that each date is tentative until confirmed at the meeting before. |
| EC-03 | [Federal Reserve — FOMC statement of 2026-10-28](https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm) | Official press release; 11-09 15:26 UTC | "For release at 2:00 p.m. EDT": the statement's time of day, applied to every date of EC-02. |

## Trading research — 2026-11-01 and 2026-11-02

The sources behind [TRADING](../../TRADING.md), opened by the project threads "Assess how well the trader agent self-improves" (2026-11-01; review TR-35), "Review trader accuracy with Fable 5.1" (2026-11-01; TR-36, which opened no paper and names its background papers from memory) and "Compare the long/short trader with professionals" (2026-11-02; TR-37), each through the session's fetch tool, which returns a model's reading of a page rather than its raw text. None was re-opened for this register: check a quotation against the page before relying on its wording. They support the principles and the tests in TRADING, not a return expectation, a threshold or a trading rule; none studies this app. Types as in the [builder register](#trading-bot-builder-and-llm-trading-research--2026-10-17); TB-01, TB-12 and TB-13 there are cited beside them.

| ID | Source | Type; opened | Supported use and limits |
|---|---|---|---|
| TR-01 | [Moskowitz, Ooi and Pedersen, Time Series Momentum, JFE 2012](https://papers.ssrn.com/abstract=2089463) | Primary study; 11-02 | Past returns predict the next 1 to 12 months and then partly reverse, in 58 futures markets. Not crypto. |
| TR-02 | [Liu and Tsyvinski, Risks and Returns of Cryptocurrency, NBER 2018](https://www.nber.org/system/files/working_papers/w24877/w24877.pdf); [RFS 2021 version](https://papers.ssrn.com/abstract=3226806) | Primary study; 11-02 and 11-01 | Bitcoin's weekly return predicts the next 1 to 4 weeks; the one-day effect is not robust; attention predicts returns. |
| TR-03 | [Hurst, Ooi and Pedersen, A Century of Evidence on Trend-Following Investing, JPM 2017](https://www.TrendFollowing.com/whitepaper/Century_Evidence_Trend_Following.pdf) | Primary study (practitioner authors); 11-02 | How trend funds trade: 1-, 3- and 12-month signals, volatility sizing, 67 markets, net Sharpe 0.77 over 1880 to 2013, always long or short. |
| TR-04 | [Rozario, Holt, West and Ng, A Decade of Evidence of Trend Following in Cryptocurrencies, 2020](https://arxiv.org/pdf/2009.12155) | Preprint; 11-02 | Bitcoin moving-average rules: best windows 141 and 781 hours, in-sample Sharpe 0.5 to 1.5, walk-forward inconsistent, zero costs assumed. |
| TR-05 | [Kim and Hansen, The Quarter-Hour Effect, 2026](https://arxiv.org/pdf/2607.09426) | Preprint; 11-02 | Binance perpetuals 2021 to 2024: 15-minute boundary predictability of about 57% accuracy and 0.5 bp gross, a tenth of a taker fee, framed as an input to execution, not a signal. |
| TR-06 | [Stylized Facts of High-Frequency Bitcoin Time Series, 2024](https://arxiv.org/abs/2402.11930v2) | Preprint; 11-02 | Bitcoin's return autocorrelation decays rapidly at high frequency. |
| TR-07 | [Jaquart, Dann and Weinhardt, J. Finance and Data Science 2021](https://publikationen.bibliothek.kit.edu/1000150665) | Primary study; 11-01 | Machine learning on Bitcoin 1 to 60 minutes ahead: 50.9 to 56.0% accuracy; trading turned negative at 0.30% round-trip costs. 2019 data; the app's modeled round trip is 0.12%. |
| TR-08 | [Jaquart, Köpke and Weinhardt, J. Finance and Data Science 2022](https://doaj.org/article/cfc09801314441198e3e1c92a3914e54) | Primary study; 11-01 | 100 coins, next day: 52.9 to 54.1% accuracy, 57.5 to 59.5% on the most confident tenth. Daily, many coins. |
| TR-09 | [Shen, Urquhart and Wang, Bitcoin Intraday Time Series Momentum, Financial Review 2022](https://research.birmingham.ac.uk/en/publications/bitcoin-intraday-time-series-momentum/) | Primary study; 11-01 | The first half-hour's return predicts the last half-hour's. One specific effect. |
| TR-10 | [Harvey, Hoyle, Korgaonkar, Rattray, Sargaison and Van Hemert, The Impact of Volatility Targeting, JPM 2018](https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf) | Primary study; 11-02 | Volatility scaling across 60+ assets since 1927: fewer extreme returns, lower drawdowns, a higher Sharpe for risk assets (US equities 0.40 to 0.48 to 0.51). |
| TR-11 | [Harvey, Rattray, Sinclair and Van Hemert, Man vs. Machine, JPM 2017](https://people.duke.edu/~charvey/Research/Published_Papers/P130_Man_vs_machine.pdf) | Primary study; 11-02 | Systematic macro funds 5.01% a year against discretionary 2.86% over 1996 to 2014, at least as good after risk and factor adjustment. |
| TR-12 | [Kaminski and Lo, When Do Stop-Loss Rules Stop Losses?, JFM 2014](https://dspace.mit.edu/bitstream/handle/1721.1/114876/Lo_When%20Do%20Stop-Loss.pdf) | Primary study; 11-02 | Stops add value under momentum and subtract it under mean reversion; short-horizon stop rules had negative stopping premiums; the condition is the autocorrelation at the trading frequency against the Sharpe ratio at that frequency. |
| TR-13 | [He, Manela, Ross and von Wachter, Fundamentals of Perpetual Futures, 2023](https://arxiv.org/pdf/2212.06888v3) | Preprint; 11-02 | Funding mechanics; positive about 85% of the time; 7.39 of 17.89 percentage points of a BTC basis strategy's return. |
| TR-14 | [Guéant, Lehalle and Fernandez-Tapia, Dealing with the Inventory Risk, 2011](https://www.arxiv.org/pdf/1105.3115v1) | Preprint; 11-02 | How market makers earn the spread and skew inventory back to flat, with no directional view. |
| TR-15 | [Chague, De-Losso and Giovannetti, Day Trading for a Living?, 2020 (Quantpedia summary)](https://quantpedia.com/retail-day-trading-is-an-uphill-battle/) | Secondary (a summary of the study); 11-02 | 19,646 Brazilians who started day trading index futures: 97% of those who persisted 300 days lost money, 1.1% earned more than minimum wage, no evidence of learning. The study itself was not opened. |
| TR-16 | [Barber, Lee, Liu, Odean and Zhang, Do Day Traders Rationally Learn About Their Ability?](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/Day%20Trading%20Skill%20110523.pdf) | Working paper; 11-02 | About 360,000 Taiwanese day traders a year; fewer than 1% predictably profitable after costs. |
| TR-17 | [ESMA, 27 March 2018 (Next Finance copy)](https://www.next-finance.net/ESMA-agrees-to-prohibit-binary) | Secondary (a copy of the regulator's statement); 11-02 | 74 to 89% of retail CFD accounts lose; a 2:1 leverage cap on crypto CFDs. |
| TR-18 | [ForkLog on Alpha Arena season 1](https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/) | Practitioner report (press); 11-01 and 11-02 | Six language models trading crypto perpetuals with 10,000 USD each for 16 days in October 2025: four of six lost, from +22% to −59%. One short run, not peer-reviewed. |
| TR-19 | [Tan et al., Are Language Models Actually Useful for Time Series Forecasting?, NeurIPS 2024](https://arxiv.org/abs/2406.16964v2) ([proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6ed5bf446f59e2c6646d23058c86424b-Abstract.html)) | Primary study; 11-02 and 11-01 | Removing the language model from LLM-based time-series forecasters does not degrade them and in most cases improves them. Numbers, not decisions. |
| TR-20 | [Lopez-Lira and Tang, Can ChatGPT Forecast Stock Price Movements?, 2023](https://arxiv.org/abs/2304.07619v1) | Preprint; 11-02 | Headline classification correlated with next-day stock returns: where language models show signal. Stocks, daily. |
| TR-21 | [Lopez-Lira, Tang and Zhu, 2025](https://arxiv.org/html/2504.14765v2) | Preprint; 11-01 | Models recall data from before their cutoff; only later data is a fair test. Supports the app's forward paper test. |
| TR-22 | [LiveTradeBench, Yu et al., 2025](https://www.arxiv.org/abs/2511.03628) | Preprint; 11-01 | 21 language models trading live for 50 days: high benchmark scores did not imply better trading. |
| TR-23 | [CryptoTrade, Li et al., EMNLP 2024](https://arxiv.org/html/2407.09546v1) | Primary study; 11-01 | A GPT-4-class crypto trader with a reflection step, daily trades: mostly trailed buy-and-hold in bull markets; one run, no variance reported. |
| TR-24 | [Kamoi et al., survey of LLM self-correction, TACL 2024](https://arxiv.org/abs/2406.01297v3) | Primary study (survey); 11-01 | Self-correction works in tasks with reliable external feedback; no work shows it with feedback from prompted models alone. |
| TR-25 | [Huang et al., Large Language Models Cannot Self-Correct Reasoning Yet, ICLR 2024](https://arxiv.org/abs/2310.01798v2) | Primary study; 11-01 | Without outside feedback models struggle to self-correct and sometimes get worse after revising. |
| TR-26 | [Xiong et al., Can LLMs Express Their Uncertainty?, ICLR 2024](https://arxiv.org/abs/2306.13063) | Primary study; 11-01 | Models stating their confidence tend to be overconfident. |
| TR-27 | [Zhao et al., Calibrate Before Use, ICML 2021](https://arxiv.org/abs/2102.09690v2) | Primary study; 11-01 | Example order alone can swing few-shot accuracy from near chance to near state of the art: why the position of the newest scores in a prompt matters. |
| TR-28 | [FLAG-Trader, 2025](https://arxiv.org/html/2502.11433v3) | Preprint; 11-01 | A fine-tuned language-model trader; backtests on a handful of stocks. Why fine-tuning on the app's own trades is not proposed. |
| TR-29 | [Harvey, Liu and Zhu, ... and the Cross-Section of Expected Returns, RFS 2016](https://nber.org/papers/w20592) | Primary study; 11-01 | Multiple testing among return predictors: the bar rises with the number of trials. |
| TR-30 | [Sullivan, Timmermann and White, Data-Snooping, Technical Trading Rule Performance, and the Bootstrap, JF 1999](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf) | Primary study; 11-01 | Technical rules chosen after the fact look good by chance; the reality check bootstrap. |
| TR-31 | [Bailey, Borwein, López de Prado and Zhu, The Probability of Backtest Overfitting, 2017](https://papers.ssrn.com/abstract=2326253) | Primary study; 11-01 | How to estimate the chance a chosen backtest is overfit; a trial ledger. |
| TR-32 | [Bailey and López de Prado, The Deflated Sharpe Ratio, JPM 2014](https://papers.ssrn.com/abstract=2460551) | Primary study; 11-01 | A Sharpe ratio corrected for the number of trials and non-normal returns. |
| TR-33 | [Howard, Ramdas, McAuliffe and Sekhon, Time-uniform confidence sequences, Annals of Statistics 2021](https://arxiv.org/pdf/1810.08240) | Primary study; 11-01 | Intervals that can be read daily without a false stop. |
| TR-34 | [Pesaran and Timmermann, A Simple Nonparametric Test of Predictive Performance, 1992 (statsmodels reference)](https://www.statsmodels.org/stable/generated/statsmodels.stats.diagnostic.pesaran_timmermann.html) | Official library docs for a primary test; 11-01 | A direction-call test against the market's own up and down rates. |
| TR-35 | Does the trader improve itself? An honest assessment (2026-11-01) | The project's own review; read 11-02 | The feedback channels (VERIFIED in the code), the PC read of 2026-11-01 08:18 and 08:24 UTC, the sample-size table and the champion-challenger pipeline. Its files are in the project's `self-improvement/` folder. |
| TR-36 | Trader accuracy: a second opinion (2026-11-01) | The project's own review, on another model; read 11-02 | The paired test against the last-hour rule, the PC read of 10:15 UTC (Q1 to Q5), the 4-hour verdicts, the confidence findings and the ranked steps. Its files are in `second-opinion/`. |
| TR-37 | The long/short trader versus the professionals (2026-11-02) | The project's own review; read 11-02 | What the trader does today (VERIFIED on main at `50f24c5`), the pros and cons with their sources, the three camps that profit, the match table and the ideas with whether each restarts the test. |
| TR-38 | [Rzym and Abou Zeid (Man Group), In Crypto We Trend, 2024-12](https://www.man.com/insights/in-crypto-we-trend) | Practitioner article; opened 2026-11-10 | Trend-following across coins at equal risk, costs and shorting included: the best ratio of return to risk at about 10 to 15 coins, an average pairwise correlation of about 0.6, liquidity thin beyond the top 15. Its figures are in charts only; a simplified model, not a fund's record. |
| TR-39 | [Liu, Tsyvinski and Wu, Common Risk Factors in Cryptocurrency, NBER w25882](https://www.nber.org/papers/w25882.pdf) | Primary study; opened 2026-11-10 | The crypto momentum factor from three-week returns, rebalanced weekly; momentum stronger among the larger coins (4.2% a week above the median size, 0.6% below). Thousands of coins, 2014 to 2018, before costs. |

## M9 update 1: feeds and terms — 2026-10-19

Official pages read on 2026-10-19 for the feeds of [ExecPlan 0032 §5.1](../plans/0032-m9-news-and-events-the-agents-trade-on.md#51-free-feeds-update-1). What each said is in [INTEGRATION_EVIDENCE](INTEGRATION_EVIDENCE.md#m9-update-1-the-free-feeds--2026-10-19). A page's terms can change; the source documents record the review date.

| ID | Source | Use |
|---|---|---|
| M9U1-01 | [BLS — RSS feeds](https://www.bls.gov/feed) | The list of BLS feeds, `bls_latest.rss` among them |
| M9U1-02 | [BLS — Latest numbers feed](https://www.bls.gov/feed/bls_latest.rss), [release calendar](https://www.bls.gov/schedule/news_release/bls.ics) | Their formats, read once |
| M9U1-03 | [Federal Reserve — monetary policy feed](https://www.federalreserve.gov/feeds/press_monetary.xml) | Its format |
| M9U1-04 | [ECB — RSS feeds](https://www.ecb.europa.eu/rss), [press feed](https://www.ecb.europa.eu/rss/press.html) | The list and the press feed's format |
| M9U1-05 | [BLS — Copyright information](https://www.bls.gov/opub/copyright-information.htm), [Linking and copyright](https://www.bls.gov/bls/linksite.htm) | Public domain; cite BLS; the emblem excluded |
| M9U1-06 | [Federal Reserve — Website linking policies](https://www.federalreserve.gov/website-linking-policies.htm) | Nothing on reuse or automated access |
| M9U1-07 | [Federal Reserve — Disclaimer](https://federalreserve.gov/disclaimer.htm) | Public domain unless otherwise indicated; cite the Board |
| M9U1-08 | [ECB — Disclaimer and copyright](https://www.ecb.europa.eu/home/disclaimer/html/index.en.html) | Free use with the ECB cited accurately; authored documents excluded |
| M9U1-09 | [CoinDesk — Terms of use](https://coindesk.com/terms/) | Automated access forbidden without written permission: not used |
| M9U1-10 | [Python — XML processing modules, XML security](https://docs.python.org/3/library/xml.html) | Expat's entity-expansion and large-token risks by version; why the reader refuses every declaration |

## Model and effort guidance — 2026-10-19

Official pages read on 2026-10-19 for the owner's question whether the agents use the best model per role ([ExecPlan 0030](../plans/0030-agent-models-and-effort-per-role.md), [DECISIONS](../../DECISIONS.md#2026-10-19--the-owner-delegates-the-agents-model-choice-no-profile-change-during-m7s-switch-on)). Each was read through a summarizing fetch, so wording is paraphrased unless quoted, and none shows a page date unless noted. They describe tasks and prices; none benchmarks this application's work, and none promises capacity on a ChatGPT plan.

| ID | Official source | Supported use and limitation |
|---|---|---|
| MG-01 | [OpenAI — Using GPT-6](https://developers.openai.com/api/docs/guides/latest-model) | Model positioning (Astra "highest intelligence"; 6.1 Sol "balanced speed, cost, and intelligence"; Luna "fastest and most cost-effective"); 6.1 Sol efforts low to max, default medium, `minimal` unsupported; keep request-level effort stable for caching. API page; Codex exposes effort through `model_reasoning_effort`. |
| MG-02 | [OpenAI — Reasoning models](https://developers.openai.com/api/docs/guides/reasoning) | Effort levels and their uses: medium "default configuration for most workloads", high where "quality matters more than latency" with "evaluate both medium and high", xhigh "only use when your evals show a clear benefit". No latency figure per level. |
| MG-03 | [OpenAI — A model guide for the GPT-6 family](https://openai.com/index/practical-guide-building-gpt-6/) (2026-10-02) | Effort by use case (low: extracting facts; medium: comparing options; high: careful review); Luna for "focused, repeated tasks with a clear goal"; list prices per model. Marketing page with customer quotes; no benchmark. |
| MG-04 | [ChatGPT — Model selection](https://learn.chatgpt.com/docs/model-selection) | Pairings of model and effort by task; "if cost and latency don't matter, default to Astra". Written for ChatGPT and Codex users, not for a brokered runtime. |
| MG-05 | [ChatGPT — Models](https://learn.chatgpt.com/docs/models) | Which models the Codex CLI offers with a ChatGPT sign-in and on which plans; GPT-5.5 retired 2026-10-14 with GPT-6.1 Sol as its replacement on paid plans. "Availability depends on the rollout, your sign-in method, and your client." |
| MG-06 | [OpenAI Help — Codex rate card](https://help.openai.com/en/articles/20001106-codex-rate-ca) | Credits per million tokens by model on credit-based plans (Astra 250/25/1,250; 6.1 Sol 50/2.5/250; Luna 2.5/0.25/12.5 for input, cached input, output) and the Fast and Ultrafast multipliers. The Plus and Pro figures are on another page the fetch did not reach; a credit figure is not computed in the app. |
| MG-07 | [OpenAI — Prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering) | Developer-message structure (identity, instructions, examples, context), high-level guidance for reasoning models, reusable content first for caching. The role prompts follow it; this is not evidence of their accuracy. |
| MG-08 | [ChatGPT — Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode.md) and [Config basics](https://learn.chatgpt.com/docs/config-file/config-basic) | `codex exec --output-schema`, `--json`, `--ignore-user-config`, `--ignore-rules`; `model_reasoning_effort` "tunes reasoning effort when supported". Both already in the pinned invocation; the pages do not state a minimum client version. |

## Trading-bot builder and LLM-trading research — 2026-10-17

The owner found these sources through web search on 2026-10-17 and read them mostly through search summaries; Reddit could not be read directly because it blocks Claude's tools. They support the PROPOSED M8 analyses, M9-R25–R28 and M10-R17 recorded under the [owner's instruction](../../DECISIONS.md#2026-10-17--builder-and-llm-trading-findings-recorded-as-proposed-m8m10-requirements). They motivate tests and limitations, not trading rules, return expectations or thresholds. None studies BTC/SOL spot paper trading by an LLM coordinator under code-held financial authority. This delivery opened each page it could (all but TB-05 and TB-07) through the session's web-fetch tool, which returns a model's extraction of the page, not the raw text: exact wording needs a manual check before it is quoted. Direct `curl` to these hosts was denied by the session's network policy. [Integration evidence](INTEGRATION_EVIDENCE.md#builder-and-llm-trading-findings--2026-10-17) records what was opened.

Types: **primary study** (peer-reviewed or proceedings), **preprint** (not peer-reviewed), **official project docs**, **practitioner report** (self-reported, sometimes promotional), **commentary** (an unreviewed critique of another source) and **secondary** (a synthesis of other sources).

| ID | Source | Type; opened | Supported use and limits |
|---|---|---|---|
| TB-01 | [HindsightBench, arXiv:2607.18867](https://arxiv.org/abs/2607.18867) (Jia; v2, 2026-08-10) | Preprint; opened | Black-box audit of outcome recall with date-revealed, date-only, masked and transplanted prompts across 15 models. Its abstract says effective cutoffs span 22 months across vendors and precede vendor-reported dates by up to eight months, and results depend on quantization and reasoning mode. Supports M9-R25's date-removed/shifted reruns; it does not measure this app's runtime model. |
| TB-02 | [A Test of Lookahead Bias in LLM Forecasts, arXiv:2512.23847v1](https://arxiv.org/html/2512.23847v1) (Gao, Jiang, Yan) | Preprint; opened | Uses a membership-inference score on prompts to show that memorization inflates predictive results on US equity headlines and earnings calls with Llama models. Needs open weights and log-probabilities, which a hosted runtime model may not expose; a later v2 changes the method, so cite by version. |
| TB-03 | [What survives honest evaluation?, arXiv:2608.27734](https://arxiv.org/abs/2608.27734) (Gençay, v1) | Preprint; opened | Leakage-safe, search-aware assessment of LLM-discovered strategies on US stocks and ETFs: a trial ledger, Deflated Sharpe Ratio with the trial count, probability of backtest overfitting and bootstrap intervals. Reports that no discovered strategy survived and that a planted leaky strategy still passed the deflation test, so deflation alone does not catch leakage. Supports M9-R28; equities only, two models, one period. |
| TB-04 | [Dispute of TB-03, research-issues #1316](https://github.com/jjakimoto/research-issues/issues/1316) | Commentary (agent-generated); opened | An issue generated by a coding agent (its footer says so), closed with no visible response, disputing TB-03's claim that honest evaluation certifies passive benchmarks for the 2022–2025 equity experiment. It concedes TB-03's main rejection result; its proposed check was not run. It limits TB-03's benchmark claim, not its search-intensity method. |
| TB-05 | [Multifaceted variability in LLM-driven stock recommendations](https://www.sciencedirect.com/science/article/abs/pii/S1544612325021762) (Chon, Kim, Kim; *Finance Research Letters* 86, 108923, 2025) | Primary study; **not opened** (the site refuses automated fetching) | Identity confirmed through its DOI record; content known only from an abstract in a repository record: identical, reworded and re-instructed queries change recommendations significantly, and keeping only recurring picks improves consistency. Supports measuring M9-R26 repeatability; stock selection, abstract-level only, no figures recorded here. |
| TB-06 | [Non-Determinism of "Deterministic" LLM System Settings in Hosted Environments](https://aclanthology.org/2025.eval4nlp-1.12.pdf) (Atil et al.; Eval4NLP 2025) | Primary study (workshop); opened | Ten runs at temperature 0 with fixed seeds on hosted APIs varied in accuracy by up to about 15% on multiple-choice tasks; a locally run model was deterministic. Supports M9-R26's assumption that a hosted model's repeated decisions can differ; not a finance study. |
| TB-07 | [Reproducibility in the TradingAgents Framework](https://dl.acm.org/doi/10.1145/3800973.3801029) (ACM, 2026 conference proceedings) | Primary study; **not opened** (client error; DOI resolver also failed) | Title and venue known from search results only; its method and findings are unverified here and nothing in this repository relies on them. |
| TB-08 | [TradingAgents repository](https://github.com/tauricresearch/tradingagents) (TauricResearch; Apache-2.0) | Official project docs; opened | Multi-agent LLM trading framework with analyst, researcher-debate, trader, risk and portfolio-manager roles. Its README says performance varies with model, temperature, period and other non-deterministic factors and that backtests are not guaranteed to match published figures. Its LLM roles make trade decisions, unlike this app, where code holds financial authority. |
| TB-09 | [Dissecting AI Trading: Behavioral Finance and Market Bubbles, arXiv:2604.18373](https://arxiv.org/abs/2604.18373) (Ouyang, Sui) | Preprint; opened | Simulated laboratory-style asset market with 14 LLMs; reports a pronounced disposition effect and extrapolative beliefs. AI-only simulated market with constant fundamental value; motivates M8's exit what-if, proves nothing about this app. |
| TB-10 | [A Comprehensive Evaluation of Cognitive Biases in LLMs, arXiv:2410.15413](https://arxiv.org/pdf/2410.15413) (Malberg et al.) | Preprint; opened | Thirty biases in generated managerial scenarios across 20 models. The disposition effect measured in the opposite direction on average (a preference for change). Not trading data; shows the direction is not settled. |
| TB-11 | [LLM Agents Do Not Replicate Human Market Traders, arXiv:2502.15800](https://arxiv.org/pdf/2502.15800) (Henning et al.) | Preprint; opened | Experimental asset markets: LLM agents traded near fundamental value with muted bubbles compared with human markets. Counterpoint to TB-09; simulated, model-dependent. |
| TB-12 | [StockBench, arXiv:2510.02209](https://arxiv.org/abs/2510.02209) (Chen et al.; v2) | Preprint; opened | Thirteen models trading 20 Dow Jones stocks daily for four months in 2025, after their knowledge cutoffs, without costs or slippage. The abstract says most models struggle to beat buy-and-hold, while its results table shows small margins above the equal-weight baseline for several; three seeds. Its section 4.1 runs portfolios of 5, 10, 20 and 30 stocks and says all models degrade as the portfolio grows, though its own table is not monotonic (two models, three repeats). Motivates M10-R17's declared universe factor, not a scale result. |
| TB-13 | [FINSABER: Can LLM-based Financial Investing Strategies Outperform the Market in Long Run?, arXiv:2505.07078](https://arxiv.org/pdf/2505.07078) (Li et al.; KDD '26) | Primary study (accepted conference paper); opened | Backtests 2004–2024 over 100+ US symbols with delisted names and point-in-time data; reported LLM timing advantages fade and buy-and-hold beats two LLM agents. US equities and two frameworks; supports the existing baselines and all-trial rules. |
| TB-14 | [LiveTradeBench, arXiv:2511.03628](https://www.arxiv.org/pdf/2511.03628) (Yu, Li, You) | Preprint; opened | Twenty-one models allocating live over 50 trading days (stocks/ETFs and prediction markets); general reasoning rank did not predict returns. No fees or spreads; one short window. Supports judging a model on the app's own probes and forward segments. |
| TB-15 | [Freqtrade lookahead analysis](https://www.freqtrade.io/en/stable/lookahead-analysis/) and its linked [recursive analysis](https://www.freqtrade.io/en/stable/recursive-analysis/) | Official project docs; both opened | Lookahead analysis compares a full backtest with sliced re-runs per signal. Recursive analysis compares indicator values computed with different startup-candle counts against a full-range benchmark and reports the variance; it says recursive indicators such as EMA should reach "low enough" variance and that it checks the last row only, not entries and exits. Closest documented method for M8's warm-up measurement; Freqtrade's own interface, unversioned stable docs. |
| TB-16 | [How I Built an AI Crypto Trading Bot with Claude AI](https://dev.to/dineshstack/how-i-built-an-ai-crypto-trading-bot-with-claude-ai-426e) (Wijethunga) | Practitioner report; opened | Advises a placebo test, which here feeds the model a fake time-shifted signal and reports that the edge collapses; no counts or method details. It is not the random-acceptance control M8 proposes. Self-reported; runs on Binance Testnet, which this project forbids. |
| TB-17 | [AI crypto trading bot on a Mac mini](https://www.indiehackers.com/post/i-built-an-ai-crypto-trading-bot-that-runs-24-7-on-my-mac-mini-heres-what-i-learned-4a8476add5) (PassiveBot AI, 2026-04-07) | Practitioner report, selling code; opened | Three LLMs must agree before a trade, described by the author as "a noise reduction layer, not alpha generation"; no figures on the gate's effect. It names three models, not repeated samples of one; M9-R26 tests agreement within the one approved runtime model in isolation. |
| TB-18 | [Six bots on a Mac mini](https://www.indiehackers.com/post/started-building-bots-because-i-was-scared-of-falling-behind-on-ai-ended-up-with-six-of-them-running-24-7-on-a-mac-mini-1c26e805cf) (AI_Finder, 2026-04-05) | Practitioner report; opened | Reports 1,056 news entries with an average price change after news of −0.012%, with no categories, window, assets or test. Motivates M9-R27's computed base rates; it is not a base rate for BTC/SOL. |
| TB-19 | [What I Learned When Building an AI News Trading Bot](https://profitview.net/blog/what-i-learned-when-building-an-ai-news-trading-bot) (ProfitView) | Practitioner report (vendor blog); opened | GPT headline sentiment was "too slow to pick up the change in mood" in major news; no P&L figures, no backtest and no discussion of base rates. Supports latency caution only. |
| TB-20 | Trading-bot builders: lessons for Adaptive Spot Lab (the owner's background report, 2026-10-17) | Secondary; read | Claude-written synthesis of TB-01–TB-19 and further community pages, made from search summaries. A map of the findings, not evidence. One reading differs from the source as opened here: it describes TB-01's effective cutoffs as later than vendor dates, while TB-01's abstract says they precede them. |

No package, provider subscription, data source or credential is added by this register. Historical registers below remain unchanged.

## Agent readiness research — 2026-10-16

Official pages below were searched/opened for the owner-requested readiness refinement of [M9](../plans/0027-m9-market-intelligence-and-event-driven-trading.md) and [M10](../plans/0028-m10-coin-discovery-and-controlled-expansion.md). They support engineering requirements, not an official rating, profitable strategy, account entitlement or verified runtime integration. [Integration evidence](INTEGRATION_EVIDENCE.md#agent-readiness-refinement--2026-10-16) separates source inspection from unrun tests. Recheck moving vendor guidance against the installed release before adoption.

| ID | Official source | Supported use and limitation |
|---|---|---|
| AR-01 | [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) | Use task-specific cases, continuous evaluation and human calibration; justify multi-agent complexity through evaluations. Revisited MI-02. Apply methodology in the local harness; no hosted Evals service or paid API dependency is introduced. |
| AR-02 | [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | Distinguish tasks, repeated trials and actual outcomes; use suitable deterministic/model/human grading, balanced behavior cases and isolated trial state. Adapt to this app's evidence and authority rules, not a prescribed tool sequence or another judge agent. |
| AR-03 | [OpenAI — Latency optimization](https://developers.openai.com/api/docs/guides/latency-optimization) | Reduce unnecessary sequential calls, use ordinary code for suitable work and parallelize independent tasks where justified. Generic examples do not establish this app's latency, justify bypassing review or prove a smaller model preserves quality. |
| AR-04 | [OpenAI — Codex as a platform](https://developers.openai.com/blog/codex-as-a-platform) | Documents bounded `codex exec` jobs, SDK programmatic interfaces and app-server lifecycle control for embedded agents. A runtime comparison is conditional on need; this page does not demonstrate compatibility with pinned `rust-v0.159.2`, search entitlements, speed gains or permission to migrate. |
| AR-05 | [PostgreSQL 17 — Function security](https://www.postgresql.org/docs/17/perm-functions.html) and [CREATE FUNCTION security guidance](https://www.postgresql.org/docs/17/sql-createfunction.html) | Audit object ownership, writable search-path schemas, temporary-object shadowing and function privileges. Apply guidance according to each function's actual invocation/ownership model; the repository finding is not proof of an exploit or a reason to change all identities without review. |
| AR-06 | [AWS Builders' Library — Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | Bind retry identity to request meaning, account for late requests and reject changed parameters under the same key. Applies to local job/tool semantics; no AWS dependency or blanket exactly-once claim follows. |
| AR-07 | [GitHub — Status checks](https://docs.github.com/en/pull-requests/reference/status-checks) | Distinguishes startup failure and check conclusions; skipped jobs can report success. Release evidence must show required jobs actually executed. It does not diagnose this repository's historical startup failure or establish today's remote state. |

No new package, provider subscription or credential is needed for this documentation research. Any later integration must record purpose, installed compatibility and license obligations; historical source registers below remain unchanged.

## UI-01

**shadcn: Skills** — [https://ui.shadcn.com/docs/skills](https://ui.shadcn.com/docs/skills)

Use: Official skill installation and project-aware component discovery.

## UI-02

**shadcn: CLI** — [https://ui.shadcn.com/docs/cli](https://ui.shadcn.com/docs/cli)

Use: Preset/template/pointer bootstrap and component CLI workflows.

## UI-03

**shadcn: official skill source** — [https://github.com/shadcn-ui/ui/blob/main/skills/shadcn/SKILL.md](https://github.com/shadcn-ui/ui/blob/main/skills/shadcn/SKILL.md)

Use: Upstream skill instructions; install and verify rather than invent a substitute.

## UI-04

**shadcn: MCP** — [https://ui.shadcn.com/docs/mcp](https://ui.shadcn.com/docs/mcp)

Use: Optional development-time component registry tooling.

## UI-05

**shadcn: React Hook Form** — [https://ui.shadcn.com/docs/forms/react-hook-form](https://ui.shadcn.com/docs/forms/react-hook-form)

Use: Official form composition guidance; match the actual component base and versions.

## UI-06

**shadcn: Data Table** — [https://ui.shadcn.com/docs/components/data-table](https://ui.shadcn.com/docs/components/data-table)

Use: Headless table integration and application-specific composition; follow the selected base variant.

## TS-01

**TanStack Start: TanStack Query** — [https://tanstack.com/start/latest/docs/framework/react/guide/tanstack-query](https://tanstack.com/start/latest/docs/framework/react/guide/tanstack-query)

Use: Request-scoped Query SSR integration, mutation/cache ownership and isolation.

## TS-02

**TanStack Start: Hosting** — [https://tanstack.com/start/latest/docs/framework/react/guide/hosting](https://tanstack.com/start/latest/docs/framework/react/guide/hosting)

Use: Production host/runtime integration; verify actual generated build output.

## TS-03

**TanStack Start: Server Functions** — [https://tanstack.com/start/latest/docs/framework/react/guide/server-functions](https://tanstack.com/start/latest/docs/framework/react/guide/server-functions)

Use: Server-only boundaries and request handling.

## TS-04

**TanStack Query: ESLint plugin** — [https://tanstack.com/query/latest/docs/eslint/eslint-plugin-query](https://tanstack.com/query/latest/docs/eslint/eslint-plugin-query)

Use: Official Query lint package and compatible recommended configuration.

## TS-05

**TanStack Router: ESLint plugin** — [https://tanstack.com/router/latest/docs/eslint/eslint-plugin-router](https://tanstack.com/router/latest/docs/eslint/eslint-plugin-router)

Use: Official Router lint package and framework-specific rule considerations.

## TS-06

**Zod documentation** — [https://zod.dev/](https://zod.dev/)

Use: Schema validation; use the installed major version and resolver compatibility.

## TS-07

**TanStack Table: Data Guide** — [https://tanstack.com/table/latest/docs/guide/data](https://tanstack.com/table/latest/docs/guide/data)

Use: Typed table data/column ownership and stable references; inspect current major-version APIs.

## FE-01

**React Hook Form: resolvers** — [https://github.com/react-hook-form/resolvers](https://github.com/react-hook-form/resolvers)

Use: Official Zod resolver integration and input/output typing.

## FE-02

**Lightweight Charts: getting started** — [https://tradingview.github.io/lightweight-charts/docs](https://tradingview.github.io/lightweight-charts/docs)

Use: Chart API, client execution and attribution/NOTICE requirements.

## FE-03

**Lightweight Charts: Build with AI** — [https://tradingview.github.io/lightweight-charts/docs/ai](https://tradingview.github.io/lightweight-charts/docs/ai)

Use: Official chart skills and AI-readable documentation.

## FE-04

**Lightweight Charts: React lifecycle tutorial** — [https://tradingview.github.io/lightweight-charts/tutorials/react/advanced](https://tradingview.github.io/lightweight-charts/tutorials/react/advanced)

Use: React lifecycle integration; verify installed-version APIs.

## FE-05

**React: eslint-plugin-react-hooks** — [https://react.dev/reference/eslint-plugin-react-hooks](https://react.dev/reference/eslint-plugin-react-hooks)

Use: Official React lint guidance.

## FE-06

**typescript-eslint: typed linting** — [https://typescript-eslint.io/getting-started/typed-linting/](https://typescript-eslint.io/getting-started/typed-linting/)

Use: Type-aware ESLint setup and project configuration.

## FE-07

**Vitest: guide** — [https://vitest.dev/guide/](https://vitest.dev/guide/)

Use: Frontend test setup and supported integration.

## FE-08

**Playwright: Docker** — [https://playwright.dev/docs/docker](https://playwright.dev/docs/docker)

Use: Real-browser container testing and version matching.

## FE-09

**openapi-typescript: introduction** — [https://openapi-ts.dev/introduction](https://openapi-ts.dev/introduction)

Use: Type generation from OpenAPI; not a substitute for runtime validation.

## FE-10

**React Testing Library: introduction** — [https://testing-library.com/docs/react-testing-library/intro/](https://testing-library.com/docs/react-testing-library/intro/)

Use: Behavior-focused React component tests.

## AI-01

**OpenAI Codex: Authentication** — [https://developers.openai.com/codex/auth](https://developers.openai.com/codex/auth)

Use: ChatGPT login, headless/device authentication and protected auth storage. May redirect to ChatGPT Learn.

## AI-02

**OpenAI Codex: Non-interactive mode** — [https://developers.openai.com/codex/noninteractive](https://developers.openai.com/codex/noninteractive)

Use: Structured exec output and advanced private ChatGPT-managed automation; API auth remains the documented automation default.

## AI-03

**OpenAI Codex: AGENTS.md** — [https://developers.openai.com/codex/guides/agents-md](https://developers.openai.com/codex/guides/agents-md)

Use: Repository/scoped instructions and their discovery.

## AI-04

**OpenAI Codex: Best practices** — [https://developers.openai.com/codex/learn/best-practices](https://developers.openai.com/codex/learn/best-practices)

Use: Scoped tasks, planning context and concrete verification.

## AI-05

**OpenAI Codex: Skills** — [https://developers.openai.com/codex/skills](https://developers.openai.com/codex/skills)

Use: Skill discovery and authoring-client installation context.

## AI-06

**OpenAI Codex: CLI reference** — [https://developers.openai.com/codex/cli/reference](https://developers.openai.com/codex/cli/reference)

Use: Installed-client command/feature verification; do not infer unsupported flags.

## AI-07

**OpenAI Codex: Configuration reference** — [https://developers.openai.com/codex/config-reference](https://developers.openai.com/codex/config-reference)

Use: Effective configuration, shell/exec/web-search/auth/log controls; verify complete tool isolation.

## AI-08

**Anthropic Claude Code: Memory** — [https://code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)

Use: Repository instructions and shared instruction imports; check client-version behavior.

## AI-09

**Anthropic Claude Code: Best practices** — [https://code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices)

Use: Exploration/planning/implementation and executable verification.

## AI-10

**Anthropic Claude Code: Headless** — [https://code.claude.com/docs/en/headless](https://code.claude.com/docs/en/headless)

Use: Alternative automation documentation; not authorization to substitute credentials or billing.

## BE-01

**FastAPI: Docker deployment** — [https://fastapi.tiangolo.com/deployment/docker/](https://fastapi.tiangolo.com/deployment/docker/)

Use: Containerized API build/process guidance.

## BE-02

**Pydantic: documentation** — [https://docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/)

Use: Runtime model validation and current installed-version behavior.

## BE-03

**SQLAlchemy: session transactions** — [https://docs.sqlalchemy.org/en/20/orm/session_transaction.html](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)

Use: Explicit ORM transaction scope and concurrency-related semantics.

## BE-04

**PostgreSQL: numeric types** — [https://www.postgresql.org/docs/current/datatype-numeric.html](https://www.postgresql.org/docs/current/datatype-numeric.html)

Use: Exact NUMERIC versus inexact types; define domain precision and rounding.

## BE-05

**uv: Docker integration** — [https://docs.astral.sh/uv/guides/integration/docker/](https://docs.astral.sh/uv/guides/integration/docker/)

Use: Containerized Python environments, lock/install and build integration.

## BE-06

**Alembic: tutorial** — [https://alembic.sqlalchemy.org/en/latest/tutorial.html](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

Use: Migration environment and explicit migration workflow.

## BE-07

**pytest: documentation** — [https://docs.pytest.org/en/stable/](https://docs.pytest.org/en/stable/)

Use: Engine test setup and execution.

## BE-08

**Hypothesis: documentation** — [https://hypothesis.readthedocs.io/en/latest/](https://hypothesis.readthedocs.io/en/latest/)

Use: Property-based invariant tests with explicitly synthetic inputs.

## OPS-01

**Docker Compose: startup order** — [https://docs.docker.com/compose/how-tos/startup-order/](https://docs.docker.com/compose/how-tos/startup-order/)

Use: Readiness and dependency conditions; not continuous-availability guarantees.

## OPS-02

**Docker Compose: secrets** — [https://docs.docker.com/compose/how-tos/use-secrets/](https://docs.docker.com/compose/how-tos/use-secrets/)

Use: Service-scoped static secrets; distinguish refreshable auth state.

## OPS-03

**Docker Engine: port publishing** — [https://docs.docker.com/engine/network/port-publishing/](https://docs.docker.com/engine/network/port-publishing/)

Use: Explicit host bindings and exposure checks.

## EX-01

**Binance Spot: market-data-only services** — [https://developers.binance.com/docs/binance-spot-api-docs/faqs/market_data_only](https://developers.binance.com/docs/binance-spot-api-docs/faqs/market_data_only)

Use: Unauthenticated public market observations; no private account integration.

## EX-02

**Binance Spot: WebSocket streams** — [https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams](https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams)

Use: Stream schemas, lifecycle, limits and order-book synchronization.

## EX-03

**Binance Spot: filters** — [https://developers.binance.com/docs/binance-spot-api-docs/filters](https://developers.binance.com/docs/binance-spot-api-docs/filters)

Use: Price/quantity/notional constraints and applicability.

## EX-04

**Binance Spot: commission FAQ** — [https://developers.binance.com/docs/binance-spot-api-docs/faqs/commission_faq](https://developers.binance.com/docs/binance-spot-api-docs/faqs/commission_faq)

Use: Fee conditions and explicitly fictional examples; no actual owner fee established.

## EV-01

**Alpaca: paper trading** — [https://docs.alpaca.markets/docs/paper-trading](https://docs.alpaca.markets/docs/paper-trading)

Use: Provider-documented paper/live execution differences; not a selected broker integration.

## EV-02

**scikit-learn: TimeSeriesSplit** — [https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)

Use: Chronological validation motivation; not a complete financial backtest methodology.

## AI-11

**OpenAI Codex: MCP** — [https://developers.openai.com/codex/mcp](https://developers.openai.com/codex/mcp)

Use: Official extension/allowlist controls for an optional future native transport. The default application-brokered JSON action loop in this pack is a project design, not a claim that the CLI's output schema automatically dispatches tools.

## AI-12

**OpenAI: Safety in building agents** — [https://developers.openai.com/api/docs/guides/agent-builder-safety](https://developers.openai.com/api/docs/guides/agent-builder-safety)

Use: Untrusted-input, structured-data and isolation considerations. Mitigations reduce rather than eliminate risk. The project's preauthorized paper-only action policy is its own design decision; this source is not vendor approval to remove tool safeguards or run an unrestricted trading agent.

## OPS-04

**Docker Engine: resource constraints** — [https://docs.docker.com/engine/containers/resource_constraints/](https://docs.docker.com/engine/containers/resource_constraints/)

Use: Implement and verify resource-limited research processes on the actual local environment; no universal hardware/capacity limits are inferred.

## SEC-01

**OWASP: Server-Side Request Forgery Prevention Cheat Sheet** — [https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)

Use: Defensive design for registered-source fetching, destination validation, redirects and private-network access. Actual controls must be tested in the chosen network/client implementation.

## V2 documentation refresh record

The revision reviewed official pages for Codex non-interactive execution, authentication, configuration, MCP and best practices; OpenAI agent safety; shadcn skills/CLI/RHF integration; TanStack Start–Query integration; Lightweight Charts AI skills; Claude Code memory and best practices; Docker resource constraints; OWASP SSRF; and Binance public market-data/filter documentation. Review supports the cited tool/engineering interfaces, not profitable trading or working local integration.

Some OpenAI Codex URLs redirected to `learn.chatgpt.com`; original official entry URLs remain usable references. Do not infer model names or account entitlement from a documentation sidebar. Verify installed client behavior before adding CLI flags or changing tool settings. The current Claude guidance supports `AGENTS.md` in compatible releases and retains `@AGENTS.md` imports; the pack keeps its explicit shared imports rather than claiming native support never exists.

The TanStack Query and Router ESLint website pages returned retrieval errors in this revision. Their **official repository documentation** was readable and confirmed the scoped plugins and flat-configuration guidance:

- Query source: [https://raw.githubusercontent.com/TanStack/query/main/docs/eslint/eslint-plugin-query.md](https://raw.githubusercontent.com/TanStack/query/main/docs/eslint/eslint-plugin-query.md)
- Router source: [https://raw.githubusercontent.com/TanStack/router/main/docs/router/eslint/eslint-plugin-router.md](https://raw.githubusercontent.com/TanStack/router/main/docs/router/eslint/eslint-plugin-router.md)

These are source fallbacks for [TS-04](#ts-04) and [TS-05](#ts-05), not installation results. In implementation, prefer documentation and package source matching the locked version; `main` and `/latest` can move. If relevant online guidance cannot be retrieved, report the exact unresolved integration instead of guessing.

No preset was scaffolded, upstream skill installed, dependency resolved, Docker service built, model authenticated, exchange request executed or strategy evaluated during this documentation revision. The original reference set remains available for later installed-version checks; do not mark its unrefreshed entries newly verified.

## M5 Codex documentation refresh — 2026-09-30

[ExecPlan 0020 §6](../plans/0020-m5-agent-runtime.md#6-official-source-and-version-evidence) read these official pages on 2026-09-30. Every `developers.openai.com/codex/…` URL above (AI-01, AI-02, AI-06, AI-07, AI-11) now permanently redirects (308) to `learn.chatgpt.com/docs/…`. The final URLs are:
- AI-01 → https://learn.chatgpt.com/docs/auth
- AI-02 → https://learn.chatgpt.com/docs/non-interactive-mode
- AI-06 → https://learn.chatgpt.com/docs/developer-commands?surface=cli
- AI-07 → https://learn.chatgpt.com/docs/config-file/config-reference
- AI-11 → https://learn.chatgpt.com/docs/extend/mcp

Documentation tracks the newest release. Every fact used by the runner is re-verified against the pinned binary and its source tag, and recorded in [INTEGRATION_EVIDENCE](INTEGRATION_EVIDENCE.md#m5-agent-runtime-execplan-0020).

## AI-13

**OpenAI Codex: CI/CD authentication (advanced)** — [https://learn.chatgpt.com/docs/auth/ci-cd-auth](https://learn.chatgpt.com/docs/auth/ci-cd-auth)

Use: ChatGPT-managed auth for trusted private automation, the refresh behavior, and the rule of one `auth.json` per runner or serialized job stream. The vendor still recommends API keys for most automation, and this project has no API key.

## AI-14

**OpenAI Codex: Environment variables** — [https://learn.chatgpt.com/docs/config-file/environment-variables](https://learn.chatgpt.com/docs/config-file/environment-variables)

Use: `CODEX_HOME` contents and custom CA variables. Proxy variables are not documented there, which is why proxy support is verified at the pinned version (M5-OD2).

## AI-15

**OpenAI Codex: Sandboxing and approvals** — [https://learn.chatgpt.com/docs/sandboxing](https://learn.chatgpt.com/docs/sandboxing), [https://learn.chatgpt.com/docs/agent-approvals-security](https://learn.chatgpt.com/docs/agent-approvals-security)

Use: Linux sandbox mechanisms and their container limitations. The container remains the isolation boundary.

## AI-16

**OpenAI Codex: Models, pricing and limits** — [https://learn.chatgpt.com/docs/models](https://learn.chatgpt.com/docs/models), [https://learn.chatgpt.com/docs/pricing](https://learn.chatgpt.com/docs/pricing)

Use: Model selection, and plan limits shared with ChatGPT usage. No entitlement or reset time is inferred.

## AI-17

**OpenAI Codex: App server** — [https://learn.chatgpt.com/docs/app-server](https://learn.chatgpt.com/docs/app-server)

Use: A candidate quota source (`account/rateLimits/read`). It is used only if verified at the pinned version.

## AI-18

**OpenAI Codex: releases and license** — [https://github.com/openai/codex/releases](https://github.com/openai/codex/releases), [https://github.com/openai/codex/blob/main/LICENSE](https://github.com/openai/codex/blob/main/LICENSE)

Use: The pinned release asset, its SHA-256 digest and sigstore bundle, and the Apache-2.0 license.

## M9 documentation research — 2026-10-15

The following official pages were read for the future [M9 handoff](../plans/0027-m9-market-intelligence-and-event-driven-trading.md). This is a dated documentation review, not runtime integration evidence. Reverify moving documentation, source terms and actual installed versions at M9 B0. Source examples are candidates, not approved subscriptions or a claim of worldwide coverage. The design choices in the plan belong to this project; vendors do not certify their trading effectiveness.

| ID | Official source | Narrow use in M9 |
|---|---|---|
| M9-01 | [OpenAI — Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) | Durable plans, bounded milestones, verification checkpoints and progress records for an implementation that spans sessions. |
| M9-02 | [OpenAI — Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | Repository/scoped instruction discovery; retain shared authoring instructions rather than embedding the whole milestone in root instructions. |
| M9-03 | [Anthropic — Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) | Explore/plan before editing; give concrete verification criteria and checks. |
| M9-04 | [Anthropic — How Claude remembers your project](https://code.claude.com/docs/en/memory) | Existing CLAUDE.md `@AGENTS.md` imports share instructions; imported paths resolve relative to their containing file. |
| M9-05 | [OpenAI — Config basics](https://learn.chatgpt.com/docs/config-file/config-basic) | Cached and live web-search modes differ. Documentation does not prove compatibility with this repository's pinned runner or authorize a capability change. |
| M9-06 | [SEC — EDGAR Application Programming Interfaces](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [SEC — Developer Resources](https://www.sec.gov/about/developer-resources) | Public submissions/XBRL interfaces at data.sec.gov do not require API keys. Fair-access rules still apply; verify exact limits and identification requirements before integration. This is distinct from submission/authentication APIs. |
| M9-07 | [Federal Reserve — RSS feeds](https://www.federalreserve.gov/feeds/feeds.htm) | Candidate primary announcements, monetary-policy releases, speeches and statistical-release notifications. |
| M9-08 | [ECB — RSS news feeds](https://www.ecb.europa.eu/home/html/rss.en.html) | Candidate euro-area announcements and statistical releases. RSS readers periodically request updates; the feed is not inherently a pushed connection. |
| M9-09 | [BLS — Release schedule](https://www.bls.gov/schedule/), [BLS — Public Data API](https://www.bls.gov/developers/) | Candidate schedules, official releases and data. The schedule uses Eastern time; normalize DST correctly. Do not infer consensus forecasts, release-time latency or historical vintages from a current data API. |
| M9-10 | [IETF — RFC 9110, conditional requests](https://www.rfc-editor.org/rfc/rfc9110.html#name-conditional-requests) | ETag/Last-Modified validation and 304 handling where supported; HTTP caching does not establish a provider's quota policy. |
| M9-11 | [IETF — RFC 6585, section 4](https://www.rfc-editor.org/rfc/rfc6585.html#section-4) | 429 rate-limit responses may include Retry-After; implement bounded provider-aware retries. |
| M9-12 | [OWASP — SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) | Application/network defenses, destination validation and redirect/DNS protections for the bounded fetch broker. |
| M9-13 | [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) | Task-specific, reproducible evaluation with representative/adversarial cases, retained results and ongoing regression checks. Methodology only; no dependency on a hosted Evals platform or paid API. |

No exact poll interval, latency target, search entitlement, API price, model accuracy or trading return is established by these references. Record new dependencies' purpose, locked compatibility and license evidence when they are actually selected.

## M9/M10 agent and discovery research — 2026-10-16

This register records the official documentation and primary research read during the 2026-10-15 design research, incorporated into the [M9 refinement](../plans/0027-m9-market-intelligence-and-event-driven-trading.md) and [M10 specification](../plans/0028-m10-coin-discovery-and-controlled-expansion.md) on 2026-10-16. The findings support engineering hypotheses and verification requirements, not trading recommendations or a claim that more agents improve returns. Reverify moving guidance, terms and installed versions at implementation.

| ID | Source | Supported use and limitation |
|---|---|---|
| MI-01 | [OpenAI — Agent orchestration](https://developers.openai.com/api/docs/guides/agents/orchestration) | Distinct workflows/tools, controlled specialist invocation and explicit handoffs. Apply through the existing application broker; SDK examples do not establish subscription runtime capabilities or require an SDK dependency. |
| MI-02 | [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) | Task-specific evaluation, representative cases and evaluation-driven decisions about multi-agent complexity. Methodology only; no hosted evaluation product or paid API is required by these plans. |
| MI-03 | [OpenAI — Agent evaluations](https://developers.openai.com/api/docs/guides/agent-evals) | Inspect end-to-end traces and individual workflow failures as well as final outputs. Use the app's retained records and local evaluation harness; tool traces are not hidden chain-of-thought. |
| MI-04 | [OpenAI — Safety in building agents](https://developers.openai.com/api/docs/guides/agent-builder-safety) | Treat external text as untrusted input; use structured boundaries and constrained tools. These reduce risk without proving injection immunity. The app's existing preapproved tool grants still determine routine action authority. |
| MI-05 | [OpenAI — Config basics](https://learn.chatgpt.com/docs/config-file/config-basic) | Cached and live web-search modes differ and returned content is untrusted. Repeats M9-05 for this handoff; current docs do not prove a transport works with pinned `rust-v0.159.2` or approve enabling it. |
| MI-06 | [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Start with simple composable workflows; use tool feedback and clear stopping conditions. Additional complexity/latency needs demonstrated value. This is engineering guidance, not evidence of financial returns. |
| MI-07 | [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Selective retrieval, concise working context and structured durable notes. Implement memory as permission/time-aware app records, not a new native filesystem capability. |
| MI-08 | [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | Specialized research can help broad independent investigations but incurs coordination and resource costs. The reported research results do not establish trading performance or require a fifth app role. |
| MI-09 | [CoinGecko — Coins list](https://docs.coingecko.com/reference/coins-list) | Provider IDs, names/symbols and optional platform/contract information support identity resolution. Active is the default; the documented inactive-list option requires Analyst plan or higher. Neither option by itself reconstructs a historical point-in-time universe. |
| MI-10 | [CoinGecko — Coins markets](https://docs.coingecko.com/reference/coins-markets) | Aggregate price, capitalization, volume and supply fields are possible screening inputs. Availability/semantics must be validated; aggregate metrics are not local venue depth or paper-fill evidence. |
| MI-11 | [CoinGecko — Keyless public API](https://docs.coingecko.com/docs/keyless-public-api) | Shared, variable IP-based limits; the documentation discourages production and scheduled/high-frequency dependence. Do not assume keyless access or a free Demo key provides sufficient app capacity. No plan price or numeric limit is frozen here. |
| MI-12 | [Binance — Market-data-only services](https://developers.binance.com/en/docs/products/spot/faqs/market_data_only) | Public market-data REST/stream services without private exchange credentials; verify endpoint availability, restrictions and applicable rate limits. Public access does not grant trading authority. |
| MI-13 | [Binance — Spot general endpoints](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general) | Exchange information exposes instrument/base/quote/status/permission/filter and rate-limit metadata. Runtime observations and implemented semantics are required; documentation examples are not actual current limits. |
| MI-14 | [Primary study — LLM financial forecasting memorization, arXiv:2504.14765](https://arxiv.org/abs/2504.14765) | Evidence that historical financial prediction tests can be contaminated by outcome recall. Preprint findings motivate explicit limitations and forward evaluation; they do not prove every model/dataset is contaminated or that masking removes it. |
| MI-15 | [Bailey and colleagues — The Probability of Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf) | Repeated strategy selection can produce misleading backtest winners. Retain trial/selection history and declare validation methodology; do not import a statistical threshold or estimator without checking its assumptions. |
| MI-16 | [Gneiting and Raftery — Strictly Proper Scoring Rules, Prediction, and Estimation](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf) | Evaluate defined probabilistic forecasts with appropriate scoring rules and calibration checks. It does not turn qualitative confidence into probability or require agents to emit numeric forecasts. |

The six information categories and their primary-source candidates remain in [M9-01–M9-13](#m9-documentation-research--2026-10-15). No new package, source subscription, external-data permission or model capability was installed or enabled by this research. [Integration evidence](INTEGRATION_EVIDENCE.md#m9m10-design-refinement--2026-10-16) separates source reads from observed repository facts and unrun checks.
