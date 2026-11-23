# Official reference register

The sources the spot app's contracts cite: the official documentation of its libraries, Docker, Binance's public market data, and the trading research behind [TRADING](TRADING.md). The pack's original register (revision of 2026-09-26) and the sources that served only the retired parts (the agents' Codex and Claude runtimes, the news feeds and the event calendar, the futures backtests, the M9 and M10 research) are in the [archived copy](archive/contracts/REFERENCES.md), history only; ExecPlan 0061 removed no source that a current contract cites.

Implementation compares current official guidance with the installed versions and records the evidence in [INTEGRATION_EVIDENCE.md](INTEGRATION_EVIDENCE.md). Moving `/latest` pages are not a dependency lock. Official documentation supports a tool's behaviour, not the profitability of the trading rule; no cited vendor endorses the app or its returns.

## Trading research — 2026-11-01 and 2026-11-02

The sources behind [TRADING](TRADING.md), opened by the project threads "Assess how well the trader agent self-improves" (2026-11-01; review TR-35), "Review trader accuracy with Fable 5.1" (2026-11-01; TR-36, which opened no paper and names its background papers from memory) and "Compare the long/short trader with professionals" (2026-11-02; TR-37), each through the session's fetch tool, which returns a model's reading of a page rather than its raw text. None was re-opened for this register: check a quotation against the page before relying on its wording. They support the principles and the tests in TRADING, not a return expectation, a threshold or a trading rule; none studies this app. Types as in the [builder register](#trading-bot-builder-and-llm-trading-research--2026-10-17); TB-01, TB-12 and TB-13 there are cited beside them. TR-40 to TR-54 were opened on 2026-11-17 by the thread "Design an adaptive multi-strategy trader", through the same fetch tool, for the owner's question how professionals and bots run several strategies ([the note](ideas/strategies-checked-2026-11-17.md)); most are press or practitioner pages, some by managers who sell the strategies they describe.

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
| TR-40 | [Resonanz Capital, Systematic Multi-Strategy vs. Discretionary Pod Platforms, 2026-04-05](https://resonanzcapital.com/insights/systematic-multi-strategy-vs.-discretionary-pod-platforms-different-engines-different-risk) | Practitioner article (an allocator advisory firm, no named author); opened 2026-11-17 | How multi-manager platforms run many strategies at once: capital allocated to semi-autonomous managers, a central risk team that enforces stop-losses (its example a 60 billion dollar platform with 300 pods); systematic multi-strategy funds feed a central signal library (its example 40 signal families) through one risk budget. No limit levels or fees. |
| TR-41 | [Resonanz Capital, When Risk Controls Make Diversification Conditional, 2026-10-26](https://resonanzcapital.com/insights/when-risk-controls-make-diversification-conditional) | Practitioner article; opened 2026-11-17 | Pod limits on exposure, concentration, liquidity and drawdown "differ by firm and strategy; there is no universal stop-out threshold"; diversification weakens when many pods cut risk at once. |
| TR-42 | [Resonanz Capital, The Exclusive Club of Multi-PM Hedge Funds, 2022-12-27](https://resonanzcapital.com/insights/the-exclusive-club-of-multi-pm-hedge-funds) | Practitioner article citing Goldman Sachs and Morgan Stanley (neither opened); opened 2026-11-17 | Gross exposure of 5 to 10 times with high gross and low net exposure, tight stop-losses, market neutrality; an average correlation of about 0.23 between two such funds. |
| TR-43 | [Hedgeweek, BlueCrest and Millennium closed pods amid market turmoil, 2024-09-02](https://www.hedgeweek.com/bluecrest-and-millennium-closed-pods-amid-market-turmoil/) | Press, secondary (it cites a Bloomberg report, which could not be opened); opened 2026-11-17 | Typical practice at multi-strategy funds: capital partially withdrawn after a 5% loss, traders dismissed after a 7% decline; not a named firm's confirmed policy. |
| TR-44 | [Asness, Moskowitz and Pedersen, Value and Momentum Everywhere, JF 2013 (AQR's page)](https://www.aqr.com/Insights/Research/Journal-Article/Value-and-Momentum-Everywhere) | Primary study, its summary page read; opened 2026-11-17 | Value and momentum are negatively correlated within and across asset classes, and their diversified combination has a high Sharpe ratio: strategies are combined, not chosen between. Eight markets and asset classes, not one coin. |
| TR-45 | [Asness, Chandra, Ilmanen and Israel, Contrarian Factor Timing Is Deceptively Difficult, JPM 2017 (AQR's page)](https://www.aqr.com/Insights/Research/Journal-Article/Contrarian-Factor-Timing-is-Deceptively-Difficult-Supplement) | Primary study, its summary page read; opened 2026-11-17 | No robust evidence that value-based timing of factors delivers meaningful outperformance. About stock factors, timed by valuation. |
| TR-46 | [Asness, Ilmanen and Maloney, Market Timing: Sin a Little, JOIM 2017](https://www.Aqr.Com/-/media/AQR/Documents/Insights/White-Papers/Market-Timing-Sin-a-Little.pdf) | Primary study; opened 2026-11-17 | Timing US stocks by valuation: a Sharpe ratio of 0.37 against buy-and-hold's 0.38 over 1900 to 2015; with momentum added 0.43 against 0.38, not statistically significant, before costs. |
| TR-47 | [Mackic (Man Group), The Need for Speed in Trend-Following Strategies](https://www.man.com/insights/need-for-speed-trend-following) | Practitioner article by a trend manager, undated (its backtest ends 2022-08-31); opened 2026-11-17 | Five trend speeds on 50 futures and currency markets, 1995 to 2022: risk-adjusted returns after costs are materially lower for the faster speeds, which protect better in equity falls; funds blend speeds. A hypothetical backtest; its figures are in charts. |
| TR-48 | [Thulin, Harvey, Preston and Cartea, Market Timing: More than a Mirage (Man Group)](https://www.man.com/insights/market-timing) | Practitioner article, a manager's publication, undated (data 2018 to 2024); opened 2026-11-17 | The dissenting view to TR-45 and TR-46: some managers show timing skill; exposure is cut when one-month volatility rises above twelve-month volatility. No out-of-sample test. |
| TR-49 | [DL News, How secretive speed-trading firms like Jump and Jane Street make a killing in crypto, 2023-05-02](https://www.dlnews.com/articles/markets/how-speed-traders-jump-jane-street-make-money-in-crypto) | Press, one interviewed expert; opened 2026-11-17 | Speed traders in crypto run a spectrum of strategies (latency arbitrage, liquidity provision) and need more data than others and a large balance sheet. No profit figures. |
| TR-50 | [Binance Updates Spot Liquidity Provider Program (2024-09-09)](https://www.binance.com/en/support/announcement/6311b67d26804bf48c5d62f5beb91202) | Official exchange announcement; opened 2026-11-17 | Maker fees for the largest market makers: 0% from 0.05% of the weekly maker volume or 25,000,000 USD, then rebates of 0.004%, 0.006% and 0.008% at 0.15%, 0.50% and 1.00%. Terms of 2024; the app's own fee source is `SPOT_COST_V1`'s. |
| TR-51 | [Binance, Binance Trading Bots: Characteristics and Use Cases, 2025-02-20](https://www.binance.com/en/blog/futures/binance-trading-bots-characteristics-and-use-cases-4987930405804222569) | Official exchange article; opened 2026-11-17 | What an exchange's bots are: Spot Grid and Futures Grid (for sideways markets), Spot DCA, Auto-Invest, a Rebalancing Bot, TWAP and VP order splitting; the user picks the bot for the condition; risks listed include limited adaptability and no guaranteed profit. |
| TR-52 | [Chen, Chen and Jang, Dynamic Grid Trading Strategy: From Zero Expectation to Market Outperformance, 2025](https://arxiv.org/abs/2506.11921v1) | Preprint, its abstract read; opened 2026-11-17 | The traditional grid strategy's expected return is "essentially zero" under simple assumptions; the authors' own resetting grid wins in their backtest on 2021 to 2024, which is not evidence here. |
| TR-53 | [Freqtrade README](https://github.com/freqtrade/freqtrade) | Official project docs; opened 2026-11-17 | An open-source bot's tooling: a dry run, backtesting, strategy optimization by machine learning, adaptive prediction modeling; "for educational purposes only". Tooling, not a strategy's edge. |
| TR-54 | [Hummingbot README](https://github.com/hummingbot/hummingbot) and its [V1 strategies](https://hummingbot.org/strategies/v1-strategies/) | Official project docs; both opened 2026-11-17 | An open-source framework for market making and arbitrage bots (pure and Avellaneda market making, cross-exchange market making, spot-perpetual arbitrage). Needs resting orders, which the paper broker does not model. |

## Trading-bot builder and LLM-trading research — 2026-10-17

The owner found these sources through web search on 2026-10-17 and read them mostly through search summaries; Reddit could not be read directly because it blocks Claude's tools. They support the PROPOSED M8 analyses, M9-R25–R28 and M10-R17 recorded under the [owner's instruction](DECISIONS.md#2026-10-17--builder-and-llm-trading-findings-recorded-as-proposed-m8m10-requirements). They motivate tests and limitations, not trading rules, return expectations or thresholds. None studies BTC/SOL spot paper trading by an LLM coordinator under code-held financial authority. This delivery opened each page it could (all but TB-05 and TB-07) through the session's web-fetch tool, which returns a model's extraction of the page, not the raw text: exact wording needs a manual check before it is quoted. Direct `curl` to these hosts was denied by the session's network policy. [Integration evidence](archive/contracts/INTEGRATION_EVIDENCE.md#builder-and-llm-trading-findings--2026-10-17) records what was opened.

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

## AI-03

**OpenAI Codex: AGENTS.md** — [https://developers.openai.com/codex/guides/agents-md](https://developers.openai.com/codex/guides/agents-md)

Use: Repository/scoped instructions and their discovery.

## AI-05

**OpenAI Codex: Skills** — [https://developers.openai.com/codex/skills](https://developers.openai.com/codex/skills)

Use: Skill discovery and authoring-client installation context.

## AI-08

**Anthropic Claude Code: Memory** — [https://code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)

Use: Repository instructions and shared instruction imports; check client-version behavior.

## AI-09

**Anthropic Claude Code: Best practices** — [https://code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices)

Use: Exploration/planning/implementation and executable verification.

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
