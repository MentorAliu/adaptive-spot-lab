# ExecPlan 0022 — Reference checks and REST budget without losing the collection

**Status: APPROVED by the owner on 2026-10-02 with clock option (a). IMPLEMENTED and VERIFIED in isolation (run `ref-1002b`, commit `0eb208a`). DEPLOYED to the normal app's market worker on 2026-10-03 at 05:22 UTC with the owner's approval; the two-hour soak passed ([§13.1](#131-executed-2026-10-03-05200522-utc-owner-approved)). Merged as `ed9fae3`.** Owner request of 2026-10-02, after [ExecPlan 0021](0021-publication-cost-at-density.md) was deployed and merged: "merge PR #13 and draft the follow-up plan". This is the follow-up that 0021 recommends in [its §12](0021-publication-cost-at-density.md#12-findings-outside-this-change-and-proposed-follow-ups), items 2 and 10, and that [ExecPlan 0012](0012-market-stream-continuity.md) left open: a routine clock check that closes a healthy collection, and REST weight-budget waits that let the reference checks expire.

Labels: `OBSERVED` (seen in code or data), `INFERRED` (reasoned from observations), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`.

**How this draft was made.** From the repository at `d075a78` and from what the approved 0021 deployment and soak had already read from the normal app: the worker log, the incident table and the once-per-second usability probe. For this plan no command was run against the normal app, the provider was not contacted, and nothing was reproduced in isolation. The first draft was then checked against the code by an independent read-only review. After the approval the defects were reproduced in isolation, the change was implemented, a second independent review read the code, and the acceptance run passed. §18 lists each step and what the reviews changed.

**The owner's constraints stay in force.** No Docker or Compose command against the normal `adaptive-spot-lab` project without approval in chat, not even a read-only one; no build, recreate, restart or stop of its services; no read of `.env` or `secrets/`; isolated stacks only; delivery by pull request without merging. A redeploy of the market worker needs the owner's explicit approval and leaves the execution worker's image alone.

## 1. Goal and observable outcome

Three terms used throughout:
- A **reference check** is the worker's verification of the provider clock or of one instrument. A quote is usable only while both are less than 120 seconds old.
- A **refresh** is one round of those checks: three `/time` requests, then one `exchangeInfo` request per symbol. A refresh starts 45 seconds after the previous one started.
- **Fail closed** means quotes read as unusable. It does not require closing the stream.

Goals:
1. **Clock.** A routine clock check that cannot measure the clock precisely, or whose request fails, keeps quotes unusable until the clock is verified again, as it does now. It no longer closes the stream collection: the socket, the generation and the captured frames stay, and usability returns in seconds instead of most of a minute. A clock that is measured out of bounds still closes the collection, as now.
2. **Measurement.** The check measures the request and its answer only, not the waiting before the request and not the set-up of a connection.
3. **REST budget.** Request weight that other clients on the same public IP use no longer makes this worker wait a minute per request. The worker's own ceiling of 120 weight a minute stays.
4. **Provider back-off.** After a 429 or 418 no request leaves before the provider's `Retry-After` has passed, whichever part of the worker asks.
5. **Evidence.** Every interval with an unverified clock and every long REST wait leaves a record.
6. **Same boundaries.** The quote-usability rule, the clock rule, the schema, the API and the web app do not change. Only the market worker executes changed code, so it deploys by recreating `market-worker` alone and the pilot's code identity is untouched.

**Observable on the normal app after an approved deployment** (targets for the read-only soak in §13):
- No `COLLECTION_GAP` caused by a routine clock check, in maintenance or in a rotation's revalidation, unless the recorded offset was over 1,000 ms.
- After a routine clock check that fails and that the next two checks clear, quotes are usable again within 20 seconds. The two events of the 0021 soak cost 58 and 35 seconds.
- While the IP-wide weight is below the guard, no reference check older than 120 seconds. Any longer REST wait has a record.

## 2. What was observed

Source: the read-only checks of the approved 0021 deployment and soak on 2026-10-02 ([0021 §11.1](0021-publication-cost-at-density.md#111-executed-2026-10-02-15151518-utc-owner-approved)). Times are UTC. The worker's request log records each REST answer when it arrives.

### 2.1 Two routine clock checks closed a healthy collection (OBSERVED)

A normal check shows three `/time` answers 0.25–0.31 s apart, for example at 15:36:27.41, .65 and .91, or at 16:00:48.46, .78 and 49.09.

| | Event 1 | Event 2 |
|---|---|---|
| The three `/time` answers | 15:37:12.57, 13.64, 14.70: 1.06 s apart | 16:01:33.92, 34.96, 37.53: 1.04 s and 2.57 s apart |
| Collection closed | 15:37:14.74, phase `maintenance_refresh`, `clock_uncertain`; the socket close took 2.0 s | 16:01:37.56, the same |
| First restart | 15:37:19.03, a new generation; its clock check was good and ended in `clock_recovery_pending` | 16:01:42.44, the same |
| Second restart | 15:37:28.18; clock and both instruments checked by 15:37:35.71 | 16:01:49.18; checked by 16:01:51.76 |
| 720-row history for both symbols | 15:37:37.44 to 15:38:01.77; the BTC request was answered twice, 18 s apart | 16:01:52.77 to 16:01:59.20 |
| Stream connected | 15:38:12.49 | 16:02:12.16 |
| Unusable quotes (probe) | 58 s, 15:37:15–15:38:12 | 35 s, 16:01:38–16:02:12 |

- In both events the next clock check, about seven seconds later, was normal again. Nothing suggests the clock itself was wrong (INFERRED: the offsets stored by the failed checks were not read).
- Each event started two new generations, read 720 hourly candles per symbol again and opened a new socket. In event 1 that was the response to a best sample at most 0.06 s over the one-second limit.

### 2.2 Three requests in a row each waited a minute (OBSERVED)

| Time | Worker log |
|---|---|
| 16:55:58–59 and 16:56:42–43 | two normal refreshes, five answers within 1.3 s each |
| 16:57:28.69–29.30 | the three `/time` answers of the next refresh |
| 16:58:31.45 | its BTC `exchangeInfo` answer, 62 s later |
| 16:59:32.76 | its SOL `exchangeInfo` answer, 61 s later |
| 17:00:34.12 | the first `/time` answer of the following refresh, 61 s later; that refresh finished at 17:00:37.49 |

- The probe found a feed `FEED_OR_REFERENCE_UNAVAILABLE` in every sample from 16:58:43 to 17:00:37, 115 in all, with quotes at most 3 s old: SOL in 111 of them, BTC in 69, and both together for 65 s from 16:59:29.
- The order follows the checks. SOL's instrument check of 16:56:43 turned 120 s old first. The clock check of 16:57:29 turned 120 s old at 16:59:29 and closed both feeds until the next one at 17:00:34. BTC's instrument check of 16:58:31 expired last, for a few seconds.
- No incident was recorded. Both evaluation marks of 17:00:00 fell inside the 65 s and are `UNAVAILABLE`.
- **These three requests also show what a new connection costs.** A wait on the header ends 60 s after the answer that set it (§3), so their send times are known. Each went to a different address than the request before it, which means a new connection. They took 2.15 s and 1.31 s (`exchangeInfo`) and 1.36 s (`/time`). On an open connection `/time` takes 0.25–0.31 s.

### 2.3 Incident history (OBSERVED, read at 16:29 UTC on 2026-10-02)

| Day | `CLOCK_UNCERTAIN` | `provider_dns_unavailable` | `stream_silent` | `provider_rest_unavailable` |
|---|---|---|---|---|
| 09-28 | 1 | 0 | 2 | 1 |
| 09-29 | 9 | 0 | 2 | 0 |
| 09-30 | 16 | 996 | 7 | 0 |
| 10-01 | 18 | 9 | 7 | 1 |
| 10-02, to 16:29 | 16 | 100 | 2 | 0 |

- `CLOCK_UNCERTAIN` is recorded for every failed measurement, at start-up too. On 2026-10-02 five collection gaps had `clock_uncertain` as their cause, three before the 0021 swap and two after it. The other eleven failed checks therefore happened while the worker was already restarting (INFERRED from the counts).
- One collection gap of 2026-10-02 had `provider_dns_unavailable` as its cause.
- A REST wait leaves no incident, so its history is not known.

### 2.4 Already on record

[ExecPlan 0012](0012-market-stream-continuity.md) saw both behaviours on 2026-09-28 and left them as follow-ups:
- A 107 s gap at 13:47: `CLOCK_UNCERTAIN`, a 60 s back-off, then `clock_recovery_pending`.
- Quotes unavailable with fresh data for 2–3 s at 20:37, 20:48 and 22:02. Each followed an `exchangeInfo` request that had waited a minute on the REST budget while a second worker shared the public IP. 0012 then started refreshes 45 s apart, which covers one such wait, and recorded back-to-back waits as a residual.

## 3. Current facts (OBSERVED in code at `d075a78`)

**The clock check**
- `PublicBinance.clock()` times the whole `get()` call and reports half of it as the uncertainty (`provider.py:154-163`). That call includes the wait for the weight budget, a DNS lookup, connection set-up and any transport retries with their back-off sleeps (`provider.py:115-151`).
- `best_clock()` takes three samples one after another and keeps the one with the smallest uncertainty. A sample whose request fails makes the whole check fail (`provider.py:165-170`).
- The worker accepts the clock when the offset is at most 1,000 ms and the uncertainty at most 500 ms. That means a round trip of at most one second. After a failed measurement it requires two good checks. A failed request does not touch that count (`worker.py:311-321`).
- The check time it writes is taken after the last sample, not at the sample that was chosen (`worker.py:314`).
- A failed measurement is written to the feed state and sets both feeds `UNAVAILABLE` with `CLOCK_UNCERTAIN` or `CLOCK_RECOVERY_PENDING` (`store.py:180-195`), which makes every quote unusable at once (`app/execution/eligibility.py:36`). Then the check raises (`worker.py:324-328`).
- A failed `/time` request raises before anything is written: a DNS failure, a rate limit, an HTTP error or five failed attempts (`worker.py:311`).

**What an exception in a routine refresh does**
- The refresh runs in the maintenance task (`worker.py:541-560`). An exception ends that task, and the collection loop raises it again (`worker.py:765-767`). The teardown marks the feeds interrupted, records `COLLECTION_GAP` and closes the socket (`worker.py:789-842`). An exception type the run loop does not list ends the process instead (`worker.py:864`, `883-886`).
- The run loop then waits 2–3 s, starts a new generation and checks again. A good check after a failed measurement still raises `clock_recovery_pending`, so there is a second wait of 4–5 s and a second new generation (`worker.py:864-882`). Each new generation runs 0021's recovery scan; the second one also runs both instrument checks, the 720-row history for both symbols and a new socket.
- Instrument checks behave differently. A failed one is caught, makes that feed unavailable and keeps the subscription (`worker.py:360-367`). That is 0012's rule.

**Rotation**
- The maintenance task is cancelled before every rotation attempt and created again after it (`worker.py:774-781`). It decides when to check only from the start time of the last completed refresh (`worker.py:371`, `543`).
- Each attempt first advances the epoch (`worker.py:650`), then revalidates. The two measurement failures are raised on purpose and end the collection (`worker.py:659-662`).
- A failed `/time` request there counts as a failed replacement (`worker.py:663`). The current generation stays and, because nothing was written, its quotes stay usable on the previous check.
- Five failed replacements end the collection (`worker.py:732-733`), with 60 s between attempts.

**Conflict confirmation**
- The `/klines` request for a candle conflict has no guard (`worker.py:408-425`). A failed request or an invalid payload ends the collection.
- An empty answer (`worker.py:253`) or one that does not match the conflict (`store.py:593-594`) raises an error the run loop does not list. That ends the process.

**The feed state**
- Publication never re-enables an `UNAVAILABLE` feed (`store.py:356-359`). A later good check moves the feed to `CHECKING`, and its next published quote of the current generation makes it `CONNECTED` (`store.py:174-177`, `464-469`).
- After a failed clock request, or while recovery is pending, the stored offset, uncertainty and check time are still good values. The feed's `status` is then the only thing that keeps quotes unusable (`app/execution/eligibility.py:36-48`).
- Two writes re-open a closed feed although the check that closed it has not passed:
  - a failed history request sets `DEGRADED` (`worker.py:399-403`), and publication may connect a `DEGRADED` feed (`store.py:357`);
  - every good clock check moves every feed that is not `CONNECTED` to `CHECKING`, including one that a failed instrument check closed (`store.py:174-177`, `193-195`).
- A frame whose event time is more than two seconds ahead of its receipt time is rejected and stored as an invalid payload with an incident, one of each per frame (`worker.py:494-501`).

**The REST weight budget**
- The budget allows a request when `max(own, observed) + weight <= 120`. `own` is the weight of the worker's own requests in the last 60 s. `observed` is the last `X-MBX-USED-WEIGHT-1M` header value, used for 60 s after it was read (`provider.py:57-79`).
- When the request does not fit, the reservation sleeps until the oldest own request leaves the minute or the observation turns 60 s old (`provider.py:69-72`). It holds the budget's lock while it sleeps, and reading a header needs the same lock (`provider.py:58`, `74-79`). Requests are never concurrent today, so that has not mattered.
- One refresh costs 3 × 1 + 2 × 20 = 43 weight. At one refresh every 45 s the worker uses about 57 a minute on average and at most 86 in any 60 s.
- A 429 or 418 raises `provider_rate_limited` with the provider's `Retry-After` (`provider.py:130-132`). The run loop waits that long when the failure reaches it (`worker.py:873`). The instrument loop, the history loop and the rotation's revalidation catch the failure instead (`worker.py:360`, `399`, `663`), so `Retry-After` is not kept there. The answer's weight header is stored first (`provider.py:129`), which holds the next request for up to 60 s when the value is high.

**The transport**
- Requests go one at a time from the maintenance task. The client keeps at most two connections and leaves the keep-alive expiry at the library default (`provider.py:99-105`).
- Every request resolves the provider host again and connects to the first address it checked (`provider.py:46`, `119-125`).

**The contract**
- [ExecPlan 0003](0003-market-data-charts.md#failure-and-recovery-rules), the M2 plan, lists the failure behaviours. For a clock anomaly: "Invalidate time-dependent eligibility, retain observations diagnostically, resample the clock and require successful recovery checks." For a queue overload it says to disconnect. For the clock it does not.
- Its [operating bounds](0003-market-data-charts.md#proposed-operating-bounds): "application ceiling 120 weight/minute or a lower discovered provider allowance", and for the clock "maximum absolute offset 1 second and uncertainty 500 ms; require two successful samples after a detected anomaly". Its recovery rules add: "account for IP-wide weight headers".
- [MARKET_DATA](../contracts/MARKET_DATA.md#implemented-m2-observation-boundary) says a refresh that waits up to a minute for the REST budget cannot age a check past 120 seconds, and that five failed replacements hand over to normal failure recovery.

## 4. Root causes

### 4.1 A failed routine clock check is an exception, and an exception ends the collection (OBSERVED)

- The worker fails closed correctly: the failed check makes every quote unusable at once.
- It then also throws the collection away, because the check reports its result by raising and nothing in the maintenance path catches it. The M2 contract asks for the first and not for the second (§3).
- The cost is the restart, not the check: two new generations, because the rule's second good check happens in a start-up of its own; 720 hourly candles per symbol; a new socket. That took 35 and 58 seconds. With the 60-second back-off of a fifth attempt it took 107 seconds on 2026-09-28.
- The restart also depends on more of the network than the check did. In event 1 a history request had to be answered twice, which cost 18 of the 58 seconds.

### 4.2 Why the check fails on this host (OBSERVED and INFERRED)

- **On an open connection there is room (OBSERVED).** A `/time` round trip takes 0.25–0.31 s, and the rule allows one second.
- **A new connection is already over the limit (OBSERVED).** The one `/time` request on a new connection whose send time is known took 1.36 s (§2.2). Connection set-up alone costs about a second here.
- **The measured interval contains that set-up (OBSERVED in code).** It also contains the wait for the weight budget, the DNS lookup and any retry. None of them says anything about the clock.
- **The first sample of every check uses a new connection (INFERRED).** HTTPX closes a connection that has been idle for five seconds by default (§9), and refreshes are 45 s apart. So the first sample fails by itself, and the check passes on samples two and three, which reuse the connection.
- **In the two failing checks the samples took 1.04–1.06 s, the cost of a new connection.** Whether each of those samples opened its own connection, or the network path was slow, is not known. The log has only answer times. The same soak saw the stream itself stall for seconds four times, so slow paths do occur on this host.

### 4.3 The budget counts other clients' weight against the worker's own ceiling (OBSERVED in code; the values are INFERRED)

- The provider's header reports the weight used by the whole IP (§9). The budget adds the next request to that value and compares the sum with the worker's own ceiling of 120.
- In §2.2 the worker's own requests of the preceding minute weighed 46, 20 and 20 when the three waits began. For the budget to wait, the header must have read more than 100, more than 100 and at least 120. So at least 55, 81 and 100 weight came from elsewhere (INFERRED from the budget's arithmetic; the header is not logged).
- The provider's documented allowance is 6,000 weight a minute for the IP (§9). The worker stopped at 2% of it.
- The M2 plan describes a ceiling for the application, "or a lower discovered provider allowance". The implementation is stricter than that wording whenever another client shares the IP.
- **Who the other client was is not known.** It is something behind the same public IP: another container on this host, another device on the same network, or another customer if the internet provider shares one address among several. No isolated worker of this project was running.

### 4.4 Why refreshes 45 seconds apart did not protect the checks (OBSERVED)

- A wait on the worker's own usage ends when its earlier requests leave the minute. When no request is retried, all such waits of one refresh together stay under a minute, and 45 + 60 < 120.
- A wait on the header starts again with every answer that reports a high value. In §2.2 both instrument requests of one refresh waited a minute each, and so did the first clock request of the next. The clock went 185 s without a renewed check, SOL's instrument 169 s and BTC's 125 s.

### 4.5 A provider back-off is not kept by every caller (INFERRED from code; never observed)

`Retry-After` is honoured only when the failure reaches the run loop. In the instrument loop, the history loop and the rotation's revalidation the next request is held only by the weight header of the 429 answer, for at most 60 s, which can be shorter than what the provider asked for (§3). The provider's rule is to back off, and it bans addresses that do not (§9). Whether the normal app has ever received a 429 was not queried.

### 4.6 Conflict confirmation can end the collection or the process (INFERRED from code; REPRODUCED in isolation, §8; never observed on the normal app)

The confirmation request is routine work on a healthy collection, like the clock check. A failed request or an invalid payload closes the collection. An empty answer, or one that is not exactly the one finalized candle asked for, stops the worker process (§3).

### 4.7 A closed feed can be re-opened by a check that is not the one that closed it (INFERRED from code; the first case REPRODUCED in isolation, §8; never observed on the normal app)

- A failed history request re-opens a feed that a failed instrument check had closed, as soon as its next quote is published (§3). The two failures are likely to come together, because both are REST requests.
- A good clock check does the same for about a second in every refresh, until the instrument is checked again.
- In both cases the instrument's last good check is still under 120 s old, so the age rule would allow the quote. What is broken is 0012's stricter rule: unavailable until a later instrument check succeeds.
- For this plan it matters because the design keeps the feed closed by `status` alone while the clock is unverified (§3). The design must not reach either write in that state.

### 4.8 Not known

- Which part of a slow clock sample was slow (§4.2).
- Who used the other weight (§4.3), and how often such waits happened before.
- Whether the provider's minute is a fixed or a rolling window. Its document does not say (§9). The design assumes neither.
- Whether the answers to `exchangeInfo?symbol=…` carry the `rateLimits` array. The provider documents the array for `exchangeInfo`; the worker's stored answers were not read (§7, decision 3).

## 5. Scope and exclusions

**In scope:** the market worker's REST transport and budget (`provider.py`), its routine reference checks, rotation revalidation and conflict confirmation (`worker.py`), a reader for the declared allowance (`parse.py`), one guarded status write (`store.py`), their tests, the harness's test list and a fault option in the density workload, the contract text, and a deployment proposal for the running pilot.

**Excluded:**
- The clock rule, its two-good-checks recovery, the 120 s reference bound and the 5 s quote age. Decision 2 in §7 is the only place where the owner may choose to change how the first is applied.
- Everything under `app/execution/`, and `read.py`: the usability rule the pilot's execution worker runs.
- What happens when the clock is measured out of bounds: the collection closes and start-up waits for a verified clock, as now.
- The start-up path after a real failure, including its back-off and the full history it reads. Narrowing that history is its own follow-up from 0012.
- The overload policy (0021 §12, item 1), `stream_silent` and stream delivery stalls.
- Raising the worker's own ceiling.
- Any schema migration, grant, API or web change.
- Normal deployment. It is proposed in §13 and needs the owner's approval. *(Approved and run on 2026-10-03, §13.1.)*

## 6. Design (IMPLEMENTED)

The principle is 0012's rule for instruments, applied to the clock: **a routine check that cannot be made, or cannot be made precisely, makes quotes unusable; it does not close a healthy socket.** A clock that is measured wrong is a different case and keeps today's behaviour.

**D1 — An unmeasurable clock keeps the collection; a wrong clock still closes it.**

A routine clock check ends in one of five verdicts:

| Verdict | Meaning | Feed state written | Collection |
|---|---|---|---|
| *verified* | offset at most 1,000 ms, uncertainty at most 500 ms, no recovery pending | as now: `CHECKING` unless already `CONNECTED` | kept |
| *recovery pending* | a good measurement, but the two-good-checks count is not complete | as now: `UNAVAILABLE`, `CLOCK_RECOVERY_PENDING` | **kept** (today: closed) |
| *imprecise* | uncertainty over 500 ms, and the measurement does not show the clock out of bounds | as now: `UNAVAILABLE`, `CLOCK_UNCERTAIN`; two good checks required | **kept** (today: closed) |
| *no measurement* | every sample's request failed | **new write:** `UNAVAILABLE`, `CLOCK_CHECK_FAILED`; the last measured values stay | **kept** (today: closed) |
| *out of bounds* | offset over 1,000 ms on a precise measurement, or beyond 1,000 ms by more than the uncertainty of an imprecise one | as now: `UNAVAILABLE`, `CLOCK_UNCERTAIN`; two good checks required | closed, as now |

- **Kept means:** the socket stays open, the generation and its epoch stay, frames keep being captured and published, and no `COLLECTION_GAP` is recorded, because no collection ended.
- **A slow sample is imprecise, not wrong.** With a three-second sample deadline an exchange of two or three seconds can put the estimate beyond a second although the clock is right. Such a measurement is *imprecise* unless it is out of bounds by more than its own uncertainty.
- **The state is set before anything is written.** The worker marks the clock unverified before it writes the feed state, so a rotation that becomes due in that moment already waits.
- **The state belongs to the worker, not to the maintenance task.** That task is cancelled and created again around every rotation attempt (§3), so the verdict, the unverified interval and the time of the next check are kept on the worker and handled in one place for both callers.
- **The two-good-checks count works as now.** A good measurement advances it; an imprecise or out-of-bounds one sets it back to two; a failed request neither advances nor resets it. So a failed measurement, then a failed request, then one good check is still *recovery pending*.
- **While the clock is unverified the refresh stops after the clock check.** No instrument check, no history, no conflict confirmation, no retention, and no rotation (D4). None of the writes that can re-open a feed (§4.7) is reached before a verified check.
- **Evidence of a wrong clock ends the grace.** While the clock is unverified, a frame whose event time is more than two seconds ahead of its receipt closes the collection, as an out-of-bounds measurement does.
- **Why a wrong clock still closes the collection.** With the local clock behind, every frame would be rejected as coming from the future and stored as an invalid payload with an incident, about three a second for as long as it lasts. With the clock ahead, wrong receipt times would be stored. Only the unmeasurable case was observed; the wrong-clock case keeps the behaviour that protects against both.

**D2 — Recheck every five seconds; the rule and the way back do not change.**
- While unverified, the worker checks the clock again five seconds after the previous attempt ended, instead of 45 s after the last refresh started. That is at most 3 weight every five seconds, 36 a minute. While the request itself keeps failing, the wait doubles up to a minute, so a provider that is unreachable or rate limiting is not asked every five seconds. The time of the next check is its own value on the worker; the schedule of full refreshes is not touched by a failed check.
- The acceptance rule is unchanged: offset at most 1,000 ms, uncertainty at most 500 ms, and two good checks after a failed measurement.
- Usability returns by the existing path only. The verifying check moves the feeds to `CHECKING` and continues as a full refresh. Each feed becomes `CONNECTED` with its next published quote, and its instrument check must be under 120 s old for that quote to be usable, as always.
- A clock that stays unverified stays closed for as long as it takes. No timer closes the collection: closing it does not help to verify a clock.
- Expected cost of an event like the two in §2.1, if D3 does not already prevent it: two rechecks five seconds apart, then the next quote. About 15 s (INFERRED), against 35–58 s.

**D3 — Measure the request and its answer, nothing else.**
- The measured interval starts when the request is written to an open connection and ends when the answer's body is complete. HTTPX reports both moments through its `trace` extension (§9). The budget wait, the DNS lookup and the TCP and TLS set-up all happen before the interval starts.
- The bound stays sound: the provider read its clock between those two moments, so the true offset lies within half the interval on either side of the estimate. This removes local waiting and connection set-up from the error bar. It does not loosen the rule.
- On this host that should give every sample, including the first, the 0.25–0.31 s of an open connection (INFERRED from §2.2). If the two observed failures were connection set-up, they would not have happened; if they were a slow path, D1 and D2 apply.
- A clock sample is one request attempt with a three-second deadline. A sample that fails is dropped. A check needs at least one sample, and a provider back-off ends the check. This applies at start-up too.
- A sample for which the transport did not report both moments is measured over the whole transport call instead. That is wider and still sound, and it is logged.
- The check time written is the time of the sample that was used, not the time the last sample ended.
- Each sample's parts are logged: budget wait, DNS lookup, connection set-up, exchange. That answers §4.2's open question from the first day of running.

**D4 — Rotation.**
- **No rotation starts while the clock is unverified.** A rotation that is due waits; its reason stays. So an unverified clock cannot advance the epoch once a minute or use up the five replacement attempts.
- **A clock check that fails inside a rotation's revalidation** gets the same handling as in maintenance. The feeds are closed, which for a failed request is a new write. The replacement is abandoned once, with `STREAM_REPLACEMENT_FAILED` and phase `revalidate`, and the current generation stays. D2 then verifies the clock, and the rotation follows.
- **This makes one existing path stricter.** Today a failed `/time` request during revalidation leaves quotes usable on the previous check. Under decision 2(a) it closes them until the clock is verified; under 2(b) it stays as it is.
- An out-of-bounds offset ends the collection, as now.

**D5 — Conflict confirmation.**
- A failed request, an invalid payload, an empty answer and an answer that does not match the conflict are handled alike: logged, recorded as `CONFIRMATION_FAILED`, and tried again at the next refresh. None ends the collection or the process.
- The interval stays out of the usable projection until it is confirmed, as now.

**D6 — The worker's own ceiling counts its own requests; the IP-wide value is compared with the provider's allowance.**
- *Own ceiling:* 120 weight in any 60 s, counted from the worker's own requests, every attempt charged. Unchanged.
- *Declared allowance:* the `REQUEST_WEIGHT` limit per one minute in the `rateLimits` array of an `exchangeInfo` answer, read from the answers the worker already requests. Only that exact shape is accepted. If the declared allowance is below 120, it becomes the own ceiling.
- *IP guard:* half the declared allowance. A request waits when the observed IP-wide value plus its weight exceeds the guard. With the documented 6,000 the guard is 3,000, against 120 today. Above the guard requests wait as they do now; nothing is sent against the header.
- *Before an allowance has been read,* or when the array is missing or malformed, the guard is the own ceiling. That is today's behaviour, and it applies to the first requests of every process.
- Reading a header never waits behind a sleeping reservation.
- Only an observed IP-wide value holds a request back, and it stops counting a minute after it was read.
- A request heavier than the ceiling itself still goes, alone in an empty minute. A declared allowance below the weight of one instrument request therefore slows the worker down instead of locking it out.
- A waiting reservation looks again at least once a second.

**D7 — A provider back-off is held in the budget.**
- A 429 or 418 sets a block until the provider's `Retry-After` has passed, at least one second as now. Every reservation waits for the block, so no caller can send early.
- The request that received the 429 still fails to its caller, as now.
- A reservation that is waiting, for any reason, ends at once when the worker is asked to stop. Today the run loop's wait can be interrupted and a reservation's sleep cannot.

**D8 — Evidence.**
- *Clock, kept collection.* One incident when an unverified interval begins: `CLOCK_UNCERTAIN` for an imprecise measurement, `CLOCK_CHECK_FAILED` with the failure code for a failed request. One incident when it ends: `CLOCK_UNVERIFIED` with start, end, number of checks, collection and how it ended (verified, collection closed, worker stopped). The closing record is also written when a teardown or a stop ends the interval, as far as the worker can still write.
- *Clock, everywhere.* `CLOCK_UNCERTAIN` gains the measured offset and uncertainty in its detail, so that an out-of-bounds offset can be told from an imprecise measurement. Start-up records it per failed check, as now. Every check that is not *verified*, and the one that verifies, is a log event with its verdict, values and sample parts.
- *REST waits.* A log event for every reservation that waited a second or more: path, weight, wait, reason (`own_ceiling`, `ip_guard` or `provider_backoff`), own usage, observed IP-wide value and guard. The budget reports waits of 30 s or more to the worker, which records a `REST_WAIT` incident, at most one every ten minutes.
- *Provider back-off.* A `REST_BACKOFF` incident for every 429 or 418, with the HTTP status and the `Retry-After` value. A 418 is a ban and is distinguishable from a 429.
- *Allowance.* A log event when the declared allowance is first read or changes. The highest IP-wide value seen is logged once per refresh.
- A record that cannot be written is logged and does not fail the request it describes; only a lost lease does.
- No new table or column. Incident codes are free text in the schema, the API and the web app.

**D9 — A failed history request does not re-open a closed feed.**
- The `DEGRADED` write of a failed history request applies only to a feed that is `CHECKING` or `CONNECTED`. An `UNAVAILABLE` feed stays `UNAVAILABLE`.
- The other write of §4.7 is not changed. A good clock check still moves a feed that a failed instrument check closed to `CHECKING` for about a second per refresh. Changing it means changing the status rules of 0012's store functions, for a quote the age rule allows anyway. It is recorded as a known limit (§18).

**What does not change.**
- The clock rule and its recovery, the 120 s reference bound and the 5 s quote age; `app/execution/**` and `read.py`.
- What an out-of-bounds clock does.
- The own ceiling of 120, two concurrent requests, five attempts per instrument and history request, the fixed hosts and paths, the redirect and size limits.
- Capture identity, publication, fencing, retention and the overload rule.
- Start-up and its back-off, apart from D3's single-attempt samples, and the make-before-break rotation order.

**Expected effect (INFERRED; the soak measures it).** Of the 215 unusable seconds in the 0021 soak, 93 came from the two clock events and 115 from the REST waits. With this plan the REST waits would not have happened. The clock events would either not have happened (if they were connection set-up) or have cost about 30 s together. The 7 s of stream stalls are outside this plan.

**Considered and not chosen.**
- *Keeping the collection when the clock is measured out of bounds.* See D1: it stores wrong times or floods the invalid-payload record.
- *Loosening the one-second bound or the 120 s age.* Both are part of the usability rule in `app/execution/eligibility.py`, which the pilot's execution worker runs. Out of scope while the pilot runs.
- *More samples, or a longer sampling time, before a check counts as failed.* It hides a transient delay by trusting the previous check a little longer. That is decision 2(b) in a weaker form, so it is put to the owner there instead.
- *Sending one refresh a minute while the IP-wide value is above the guard.* It would keep the checks fresh under pressure, but it sends requests while the header says the IP is close to the provider's limit. With the guard at half the allowance that state is rare, and failing closed is the right answer in it.
- *Resampling in place at start-up.* It would save a few seconds in a rare case and is not needed for the observed defect.
- *Keeping the REST connection open between refreshes; caching the checked DNS answer.* D3 makes the clock check independent of both. The second also touches the checked-address rule.
- *One `exchangeInfo` request for both symbols.* It would halve the worker's own weight, but it changes the shape of the stored evidence.
- *Ignoring the IP-wide header.* The provider bans addresses that keep sending at its limit; the header is how the worker sees that coming.
- *A switch to turn the new behaviour off.* The rollback is the previous image (§14).
- *A new quality value for quotes captured while the clock is unverified.* It needs a schema migration beside the running pilot (§10 describes what is recorded instead).

## 7. Decisions for the owner

**Decided on 2026-10-02** ([DECISIONS](../../DECISIONS.md#2026-10-02--execplan-0022-approved-for-implementation-clock-option-a-one-read-only-query)). The owner approved the plan for implementation, chose option (a) in decision 2 and approved the read-only query of decision 3, which found the array (§18). Decision 4, the deployment, is open. The text below is what was asked.

1. **Approve this plan for implementation.** Until then nothing is built. Implementation and its tests run on isolated stacks only.
2. **What happens to quotes when a routine clock check could not measure precisely or could not be made.** Both options keep the socket, and both close the collection when the offset is measured over 1,000 ms.
   - **(a) As now. Recommended, and the plan's default.** Any check that is not good makes quotes unusable at once, and they return when the clock is verified. Cost per transient event: about 15 s without usable quotes (INFERRED), which is also that long without protection for an open position. It makes the rotation path of D4 stricter than it is today.
   - **(b) Grace inside the existing 120 seconds.** Such a check leaves the last good check standing. Quotes stay usable while that check is under 120 s old, which the read rule already allows, and the worker rechecks every five seconds. Cost per transient event: none. The price: a clock that jumps at a moment when it cannot be measured could go unnoticed for up to 120 s instead of about 45 s.
   - (a) is recommended because it changes no safety rule, and D3's sample timings will show within days how often a check still fails with a good clock. (b) can then be decided on evidence.
3. **Confirm the declared allowance on a real answer before the budget is written.** D6 needs the `rateLimits` array in the answers the worker already gets. Either way needs a go-ahead:
   - **Read one stored `exchangeInfo` answer from the normal database, read-only. Recommended:** it sends nothing to the provider.
   - Or run the existing `PublicSmoke` phase from an isolated container: 47 weight, once, on the shared IP. The normal worker's budget would count it for a minute and could delay one of its requests.
   - If the array is not there, D6 comes back to the owner as a revised proposal before any code.
4. **Deployment.** Recreating `market-worker` beside the running pilot needs explicit approval once the change is verified (§13). *(Approved on 2026-10-03.)*

Not asked of the owner: the guard at half the declared allowance, the five-second recheck and the other values in §6 are ordinary, reversible engineering choices. They are recorded in §17.

**Optional, read-only, with the same go-ahead as decision 3.** Two more reads would size the benefit before any code is written: whether a `provider_rate_limited` incident exists (§4.5); and, since the 0021 swap, the clock tear-downs with their durations and the hourly evaluation marks by quality.

## 8. Requirements and tests (IMPLEMENTED; results in §12)

| # | Requirement | Evidence |
|---|---|---|
| R1 | A routine clock check that ends *imprecise*, *recovery pending* or *no measurement* keeps the socket, the generation, the epoch and the capture. No `COLLECTION_GAP`. | W1, W3, W4, W15 |
| R2 | From such a check until the clock is verified no quote is usable. Publication, a pending adoption, a due history request and a failed history request do not re-open a feed. | W1, W3–W6, W18, sampled every 50 ms |
| R3 | The rule and its recovery are unchanged, including a failed request between two measurements. Usability returns within 12 s of the failed check when the next two checks are good (isolated bound, instant REST). | W1, W4; the existing `test_clock_anomaly_requires_two_good_rechecks` |
| R4 | A measurement that shows the clock out of bounds closes the collection as now, also inside an unverified interval. So does a frame from the future while the clock is unverified. | W2, W12, W16 |
| R5 | Rechecks are at least 5 s apart, and further apart while the request keeps failing. A clock unverified for minutes stays closed on one collection and one epoch, with no instrument or history request and no rotation attempt. | W8, W10, W17 |
| R6 | A clock failure met inside a rotation's revalidation closes the feeds for both kinds of failure, abandons the replacement once and keeps the current generation; the rotation completes after verification. | W9 |
| R7 | No answer to a conflict-confirmation request ends the collection or the process. | W11 |
| R8 | The uncertainty covers only the time from writing the request to completing the answer, for a single attempt. Budget wait, DNS, connection set-up and retries are outside it. A failed or slow sample is dropped, and the check time is that of the sample used. | U8, U9, U10, U14, W14 |
| R9 | The own ceiling counts own requests only, every attempt charged. A lower declared allowance lowers it without locking a request out. | U3, U11; the existing `test_every_actual_rest_retry_is_charged` |
| R10 | The IP-wide value is compared with half the declared allowance. Before one is read, or with a malformed array, the guard is the own ceiling. The header values of §2.2 cause no wait once the allowance is known. | U1, U4, U6 |
| R11 | After a 429 or 418 no request is sent before `Retry-After`, whichever caller asks, and the event is recorded with its status. | U2, U5, W19 |
| R12 | A waiting reservation ends at once when the worker stops. Reading a header never waits behind a reservation. | U5, W21 |
| R13 | Each unverified interval has one opening and one closing record, also when a teardown or a stop ends it. A wait of 30 s or more is recorded, at most once in ten minutes, with the reason it waited longest for. A record that cannot be written does not fail the request. | W1, W13, W20, U12, U13 |
| R14 | A failed history request leaves an `UNAVAILABLE` feed `UNAVAILABLE`. | W6, W7 |
| R15 | Start-up, the 45 s cadence without faults, adoption, rotation, overload and publication behave as before. | The unchanged `WorkerFaults` and `Regression` suites, `RecoveryMemory`, `PerformanceBurst`, `PerformanceDensity` |
| R16 | With stored history and stream load, injected clock faults close and reopen usability within the bound, without a gap, and publication stays within its budgets. | `PerformanceDensity -ReferenceFaults` |
| R17 | No file under `app/execution/`, no `read.py` and no migration changes. The execution worker's image is not rebuilt. | The diff of `0eb208a`; the image list at deployment |

**Worker tests on the real loopback path** (`tests/test_m2_reference_checks.py`, in `WorkerFaults`; 21 tests, 26 cases):
- W1 `test_imprecise_routine_clock_check_keeps_the_collection_and_fails_closed` (real elapsed time)
- W2 `test_clock_offset_out_of_bounds_still_closes_the_collection`
- W3 `test_failed_clock_request_keeps_the_collection_and_fails_closed` (DNS failure, REST unavailable, rate limit, invalid payload)
- W4 `test_failed_request_between_measurements_does_not_shorten_the_recovery`
- W5 `test_nothing_re_opens_a_feed_while_the_clock_is_unverified`
- W6 `test_failed_history_request_does_not_re_open_a_closed_feed`
- W7 `test_degrade_leaves_an_unavailable_feed_unavailable`
- W8 `test_clock_unverified_for_minutes_stays_closed_on_one_collection`
- W9 `test_rotation_waits_for_a_verified_clock` (imprecise, failed request)
- W10 `test_rotation_due_while_the_clock_is_unverified_does_not_start`
- W11 `test_no_confirmation_answer_ends_the_collection_or_the_process` (failed request, invalid payload, empty answer, answer that does not match)
- W12 `test_future_frame_while_the_clock_is_unverified_closes_the_collection`
- W13 `test_an_unverified_interval_that_a_stop_or_a_teardown_ends_is_recorded` (stop, socket closed)
- W14 `test_the_check_time_is_the_time_of_the_sample_that_was_used`
- W15 `test_slow_sample_with_a_straying_estimate_is_imprecise_not_wrong`
- W16 `test_clock_measured_wrong_during_an_unverified_interval_closes_the_collection`
- W17 `test_rechecks_back_off_while_the_clock_request_keeps_failing`
- W18 `test_pending_adoption_does_not_re_open_a_feed_while_the_clock_is_unverified`

**The real transport class and budget over an HTTPX mock transport, with the loopback stream and a database** (the same file):
- W19 `test_provider_back_off_holds_every_request_of_a_running_worker`
- W20 `test_long_rest_waits_are_recorded_and_a_stop_ends_them`
- W21 `test_a_stop_ends_a_rest_wait_at_start_up`

**Transport tests without a database** (14 new tests in `tests/test_m2_unit.py`):
- U1 `test_other_clients_weight_on_the_ip_does_not_stop_the_worker` (the header values of §2.2)
- U2 `test_no_request_leaves_before_a_provider_back_off_ends`
- U3 `test_own_ceiling_counts_only_own_requests`
- U4 `test_ip_wide_weight_is_compared_with_the_declared_allowance`
- U5 `test_a_provider_back_off_blocks_every_reservation_until_it_ends_or_the_worker_stops`
- U6 `test_declared_allowance_reader_accepts_only_the_documented_shape`
- U7 `test_worker_clock_bounds_are_the_read_rule_bounds`
- U8 `test_the_transport_reports_the_moments_the_clock_measure_uses` (the locked transport against a loopback HTTP server)
- U9 `test_clock_uncertainty_covers_only_the_request_and_its_answer`
- U10 `test_a_failed_clock_sample_is_dropped_and_a_back_off_ends_the_check`
- U11 `test_a_request_heavier_than_a_tiny_allowance_still_goes_in_an_empty_minute`
- U12 `test_a_wait_is_reported_with_the_reason_it_waited_longest_for`
- U13 `test_a_budget_record_that_cannot_be_written_does_not_fail_the_request`
- U14 `test_the_check_time_is_the_used_sample_and_a_slow_sample_is_cut`

**Reproduced on the unchanged code first (B0, isolated, synthetic).** Evidence under `.cache/m2/ref-1002a/unchanged-code/`.
- W1, U1 and U2 failed on `dafc18d`: the collection closed; the request waited behind the other client's weight; a request left 0.2 ms after a 429.
- All 19 cases of the worker tests that exist without the new transport failed on `dafc18d`. Three of them confirm what the plan had only derived from code: a failed clock request during a rotation's revalidation left quotes usable (W9); a failed history request re-opened a feed that a failed instrument check had closed (W6); and the confirmation path ended the collection.
- Two direct checks on `dafc18d` passed, which confirms §4.6: a failed confirmation request raised out of the collection, and an empty answer raised an `IndexError` the run loop does not list.

## 9. Official sources and versions

Read on 2026-10-02 through the authoring client's web fetch, which returns extracts of a page. The implementation reads the pages again and checks the header, the `rateLimits` array and the trace events on real answers and in the built image before relying on them (§11).

| Source | What it says | Used for |
|---|---|---|
| Binance Spot REST API, official repository [`rest-api.md`](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md) | Each answer carries `X-MBX-USED-WEIGHT-(intervalNum)(intervalLetter)`, the used weight "for the IP". Limits are "based on the IPs, not the API keys". 429 means the limit was exceeded and the client must back off; 418 is an automatic ban for not doing so; `Retry-After` gives the seconds to wait. Weights: `/api/v3/time` 1, `/api/v3/exchangeInfo` 20, `/api/v3/klines` 2. Public market data is served at `data-api.binance.vision`. It does not say whether the minute is fixed or rolling. | D6, D7, §4.3, §4.5 |
| The same repository, [`CHANGELOG.md`](https://github.com/binance/binance-spot-api-docs/blob/master/CHANGELOG.md), newest entry 2026-09-18 | Entry of 2023-08-25: the `REQUEST_WEIGHT` limit "adjusted to 6,000 every minute"; `exchangeInfo` weight raised from 10 to 20. | §4.3, D6 |
| The same repository, [`enums.md`](https://github.com/binance/binance-spot-api-docs/blob/master/enums.md) | The `rateLimits` entry shape: `rateLimitType` `REQUEST_WEIGHT`, `interval` `MINUTE`, `intervalNum` 1, `limit` 6000. | D6 |
| HTTPX 0.28.1 (locked), [resource limits](https://www.python-httpx.org/advanced/resource-limits/) | `keepalive_expiry`: the time limit on idle keep-alive connections, default 5 seconds. | §4.2 |
| HTTPX 0.28.1, [extensions](https://www.python-httpx.org/advanced/extensions/) | The `trace` extension installs a callback for the events of the underlying `httpcore` transport, among them `connection.connect_tcp.*`, `connection.start_tls.*`, `http11.send_request_headers.started` and `http11.receive_response_body.complete`. In async code the callback must be an `async def`. The set of events "may be subject to change across different versions of `httpcore`"; pinning is recommended. | D3. `httpcore` is locked at 1.0.9 (`uv.lock`); U1 fails if an event is missing. |
| HTTPX 0.28.1, [transports](https://www.python-httpx.org/advanced/transports/) | `httpx.MockTransport` takes a handler that maps requests onto pre-determined responses. | H1, H2 |

No new dependency. No version changes.

## 10. Data and trust-boundary changes

- **No new destination, path, parameter, credential, grant, table or column.** The worker reads one more field, `rateLimits`, of an answer it already requests and stores.
- **New evidence rows.** Incident codes `CLOCK_CHECK_FAILED`, `CLOCK_UNVERIFIED`, `REST_WAIT`, `REST_BACKOFF` and `CONFIRMATION_FAILED`, written through the existing fenced insert. `CLOCK_UNCERTAIN` gains its measured values. In the kept-collection path it is recorded once per unverified interval instead of once per failed check.
- **A new feed-state value.** `last_error` can read `CLOCK_CHECK_FAILED`. The column is free text.
- **Quotes captured while the clock is unverified are kept.** Today that interval holds no quotes, because the collection is closed. After this change it holds quotes that were captured and published while every live reader treated them as unusable.
  - Live decisions are unaffected. The execution engine uses the live rule and records its eligibility snapshot.
  - Replay uses a reduced rule that does not see feed state ([ExecPlan 0011 §5.11](0011-paper-broker-reference.md#511-replay)). It would treat those quotes as usable, as it already does for quotes captured while a reference check was stale or an instrument check had failed. The `CLOCK_UNVERIFIED` incident gives the exact interval, so a replay or an analysis can exclude it. The replay rule itself is not changed here.
  - Their receipt times come from a local clock that could not be verified at that moment. That is why they are unusable live, and why the interval is recorded. A clock that is measured wrong closes the collection instead (D1).
- **Logs.** The new events carry timings, weights and failure codes. They carry no secret; the worker has none.
- **Fixtures.** The new tests use the loopback provider, a mock transport and synthetic instruments only.

## 11. Implementation sequence (DONE; deployed 2026-10-03)

- **B0 — Gate and reproduction. DONE.** The owner-approved read-only query found the `rateLimits` array in the stored answers (§18). W1, U1 and U2 failed on the unchanged code, and the code-derived defects reproduced (§8).
- **B1 — Transport timing. IMPLEMENTED.** The trace-based interval, single-attempt clock samples with a three-second deadline, the time of the sample used and the logged parts (D3). U8 runs the locked transport in the built image and finds both trace events.
- **B2 — Budget. IMPLEMENTED.** Own ceiling and IP guard, the declared-allowance reader, the back-off block, waits that end on a stop, and the wait reports (D6–D8).
- **B3 — Worker. IMPLEMENTED.** Clock verdicts and worker-level state, the recheck schedule, rotation deferral and revalidation handling, the future-frame guard, conflict confirmation, the guarded `DEGRADED` write, incidents and events (D1, D2, D4, D5, D8, D9).
- **B4 — Tests and harness. IMPLEMENTED.** W1–W21 and U1–U14; the new file in `WorkerFaults`; `-ReferenceFaults` for the density workload.
- **B5 — Contracts. DONE.** MARKET_DATA, OPERATIONS, TESTING, INTEGRATION_EVIDENCE, COMMANDS and STATUS.
- **B6 — Isolated acceptance on the final source. VERIFIED** (§12). The diff of `0eb208a` touches `app/market_data/` (`parse.py`, `provider.py`, `store.py`, `worker.py`, `performance_density.py`), two test files and the harness script; nothing under `app/execution/`, no `read.py`, no migration.
- **B7 — Pull request MentorAliu/adaptive_spot_lab#15. DONE.** Deployed on 2026-10-03 with the owner's approval (§13.1).

## 12. Verification (isolated)

Isolated Compose projects of one run only, on Windows PowerShell 5.1, as for 0021. `-ReferenceFaults` is the density fault option this plan adds.

```powershell
./tools/m2-acceptance.ps1 -RunId <run> -Phase Prepare
./tools/m2-acceptance.ps1 -RunId <run> -Phase Snapshot
./tools/m2-acceptance.ps1 -RunId <run> -Phase Build
./tools/m2-acceptance.ps1 -RunId <run> -Phase Checks
./tools/m2-acceptance.ps1 -RunId <run> -Phase WorkerFaults
./tools/m2-acceptance.ps1 -RunId <run> -Phase Regression
./tools/m2-acceptance.ps1 -RunId <run> -Phase RecoveryMemory
./tools/m2-acceptance.ps1 -RunId <run> -Phase PerformanceDensity -DensityLevels '1000000,1800000' -DensitySeconds 600 -ReferenceFaults
./tools/m2-acceptance.ps1 -RunId <run> -Phase PerformanceBurst
./tools/m2-acceptance.ps1 -RunId <run> -Phase Snapshot
./tools/m2-acceptance.ps1 -RunId <run> -Phase Stop
```

- **Budgets.** The existing ones of every phase. The density workload fails today on any unusable sample, so the fault option changes its acceptance: unusable samples are allowed only between an injected fault and its reopening. Each fault must close usability within 2.5 s and reopen it within 15 s, as the workload's one-second sampling sees it. REST answers take 150 ms in that workload, so the bound is wider than the worker tests' 12 s with instant answers. Outside the windows the existing budgets hold: no `COLLECTION_GAP`, one collection per level, receipt-to-publication p95 ≤ 250 ms and p99 ≤ 1 s, every frame published.
- **Two density levels instead of six.** The store's publication path is not changed, so the run checks the changed maintenance loop under stream load at about the normal app's size and at the seven-day size. One density run at a time: it loads about 3 GB into a database limited to 2 GiB, on the Docker VM the pilot also uses.
- **No isolated public worker before deployment.** It shares the public IP with the normal worker, and until the normal worker runs D6 it would lengthen that worker's REST waits, which is the defect of §2.2. The real-provider evidence is the soak in §13. The one-off `PublicSmoke` of decision 3 is the only exception, and only with the owner's go-ahead.
- **The read-only reads of §7** are run only with approval, inside a read-only transaction, in the form recorded in 0021 §11.1. The one for decision 3 ran on 2026-10-02 (§18); the two optional ones were not approved and not run.

### 12.1 Run `ref-1002b` on commit `0eb208a` (VERIFIED, 2026-10-02 21:17–22:17 UTC)

The eleven commands above, with the run's own Compose projects `asl-m2-ref-1002b-*`. All exited 0. Synthetic data only; the provider was not contacted.

| Phase | Result |
|---|---|
| Snapshot (before and after) | Both record commit `0eb208aba5488cbf6cd15cf792f030243f76b524` and the same 375 source hashes. |
| Checks | Web lint, typecheck, 49 unit tests, API-contract check, Ruff, OpenAPI check, format check and the production build. No web source changed. |
| WorkerFaults | 69 passed, none skipped: the 43 existing tests and the 26 new cases. |
| Regression | 421 passed, with the one pre-existing Starlette test-client warning. |
| RecoveryMemory | 30 measured recoveries, 464 KiB settled growth, 0 retained market tasks. |
| PerformanceDensity with reference faults | No budget failure at either level; table below. |
| PerformanceBurst | 30,000 of 30,000 published; p50 139.6 ms, p95 162.7 ms, p99 172.6 ms; schedule lag p99 2.0 ms; maximum RSS 72,552 KiB. |

| Stored observations | Receipt to publication p95 / p99 | Published | Faults | Closed after | Reopened after | Unusable outside the faults | Collections |
|---|---|---|---|---|---|---|---|
| 1,000,002 | 115.8 / 118.1 ms | 1,783 of 1,783 | 4 | 0.1–0.9 s | 11.7–12.3 s | 0 | 1 |
| 1,803,225 | 116.0 / 117.9 ms | 1,790 of 1,790 | 4 | 0.3–0.9 s | 11.9–12.7 s | 0 | 1 |

- **Each fault** was one imprecise routine clock check under the stream. It produced one `CLOCK_UNCERTAIN` and one `CLOCK_UNVERIFIED` record with two checks, ended by verification, on the unchanged collection. No `COLLECTION_GAP` at either level.
- **At the second level** the retention ran under the stream as in 0021: 32 calls deleted 16,000 observations and 16,000 payloads.
- **The statements of 0021 are unchanged:** identity publication p95 16.4 ms and 7.9 ms; the recovery scan at most 1,800 ms and 790 ms.
- **Before this run,** the development run `ref-1002a` had exercised the fault schedule once at 3,000 stored rows: four faults, closed after 0.1–0.8 s and reopened after 12.1–12.8 s. That run's only failed budget was the retention minimum, which a 3,000-row level cannot meet.

### 12.2 Not run, and limits of this evidence

- **The provider was not contacted.** The trace events are verified against a loopback HTTP server, not against TLS and the provider. The declared allowance was read from stored answers, not by the new code. Both show on the first refreshes after a deployment (§13, step 7). They did on 2026-10-03 (§13.1).
- **The 60-minute M2 normal workload and the browser phases:** NOT RUN. No web source changed; the density and burst phases cover the worker under load.
- **GitHub CI:** did not start on 2026-10-02 for this repository. The local harness is the only automated evidence.
- **Not exercised by a test** (from the second review): lease loss while unverified; a stop inside rotation, history or confirmation; a 418; an HTTP-date `Retry-After`; an allowance that changes while running; the TLS path of the trace.

## 13. Normal deployment (RUN 2026-10-03)

### 13.1 Executed 2026-10-03, 05:20–05:22 UTC (owner-approved)

**Approval.** After the report on this plan's isolated verification the owner wrote in chat at 05:20 UTC: "I approve the deployment in the next HH:15–HH:45 window". That approves the steps of §13.2 for the market worker, including the read-only commands that verify them and the soak. It does not approve merging the pull request, removing any volume or image, or touching postgres, the pilot workers, the API, the web or the agent services ([DECISIONS](../../DECISIONS.md#2026-10-03--market-worker-deployment-approved-execplan-0022)).

**Source.** This worktree at `60997d8`, whose `services/`, `tools/` and `compose.yaml` equal the tested commit `0eb208a`; clean tree. Its `compose.yaml` is identical to the primary checkout's, which stayed on `main` at `cd5a5e9`, untouched.

**Read-only starting state (05:20:44 UTC; OBSERVED).**
- Schema `0007_m5_agent_runtime`. Experiment `d779fbf4…` FORWARD_PAPER RUNNING, version 3; execution lease epoch 4, held; checkpoint 899,172, 1.3 s old. No open position (two `CLOSED_WITH_DUST`). The last `experiment_events` row is 71 and the last `execution_incidents` row is 89, both of 2026-10-01 06:57.
- Agent runtime `PROBE_ONLY`; 13 workflows, all terminal.
- Market: both feeds `CONNECTED`; market lease epoch 2157; `publication_lag_ms` 117. In the preceding hour one `CLOCK_UNCERTAIN` (04:36:31, phase `maintenance_refresh`, followed by `clock_recovery_pending`), one `stream_silent` (05:05:50) and the two `COLLECTION_GAP` records they caused, and three generations: the old worker's clock tear-down of §2.1 happened once more in that hour.
- Stored rows (planner estimates): 881,805 observations, 881,483 publications; 1.53 GB of market relations.
- The market worker: container `1becbec082dc`, image `sha256:0d6ac003d933…` (ExecPlan 0021), started 2026-10-02 15:17:09, restart count 0.

**Steps (all exit 0).**

| Step | Time (UTC) | Result |
|---|---|---|
| Protected backup | 05:21:03–05:21:44 | `pg_dump -Fc` in the postgres container, copied to the primary checkout's `.cache/deployments/reference-checks-20261003T052055Z/asl.dump`: 282,957,442 bytes, SHA-256 `a491f820efba0892601d5ec5b39d8a76dd848930e3b81fe2ce5a20e14111b9cb`, identical inside the container and on the host, and written beside it as `asl.dump.sha256`. The directory's ACL grants only the owner's Windows account. The temporary copy in the container was removed. No isolated restore: there is no schema change. |
| Rollback tag | 05:21:53 | `adaptive-spot-lab-market-worker:pre-0022` = `sha256:0d6ac003d933…`, the running image. |
| Build one image | 05:21:53–05:22:01 | `docker compose -f compose.yaml -p adaptive-spot-lab --profile market build market-worker` → `sha256:0d4d29bb4765ab288e893ce506c29c79ea5ff627b17bd79300a020bf110e6df3`. |
| Tested source in the image | 05:22:08 | The image's `/app/app` tree (103 files) hashes to `ba9dc949…9c65`, equal to the tree of the tested image `asl-m2-ref-1002b-density-engine-tests`; `worker.py` `922f4842…` and `provider.py` `e81cde5e…` are equal too. |
| Recreate one service | 05:22:17–05:22:22 | `docker compose -f <primary>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env --profile market up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker`. New container `117df6d29bda`, started 05:22:21. |

As for 0021, the image was built from this worktree, and the service was recreated with the primary checkout's `compose.yaml`, `.env` and secrets directory, neither of which was read.

**Verified after the swap (read-only; OBSERVED).**
- **Only the market worker changed.** `postgres`, `api`, `web`, `execution-worker`, `evaluation-worker`, `agent-egress`, `agent-runner` and `agent-worker` have the same container, image, start time and restart count as before.
- **The running code is the tested code.** Inside the running container the `/app/app` tree hashes to `ba9dc949…9c65`, and `worker.py`, `provider.py`, `parse.py` and `store.py` equal the commit's files. Its settings: collection enabled, `ASL_TEST_ISOLATED=0`, database `asl`, no rotation override.
- **Start-up.** Lease epoch 2158 at 05:22:23.0, generation 2159 at once. The first `exchangeInfo` answer declared the allowance: `market_rest_allowance` with allowance 6,000, own ceiling 120 and guard 3,000 at 05:22:25.4. Stream connected at 05:22:31.7. No incident was written by the swap.
- **The first real-provider clock samples.** Every sample of the start-up check and of the first refresh is `traced: true`. The request and its answer took 241–244 ms. Opening the connection, which the old measure included, took 737–800 ms on its own. Every refresh opens a new connection: refreshes are 45 s apart and the keep-alive expiry is 5 s. This is §4.2's cause, now outside the measured interval.
- **The gap.** The old worker's last quotes were received at 05:22:17.3 (SOL) and 05:22:18.2 (BTC); the new worker's first at 05:22:31.9 (SOL) and 05:22:32.1 (BTC): 14–15 s without new quotes, against about 37 s for the 0021 swap. Both feeds were `CONNECTED` on the new collection at the first read after the swap (05:24:43). The probe started later (05:26:52), so the moment usability returned is not measured.
- **Publication.** `publication_lag_ms` 124; over the first 322 stream observations receipt-to-publication p50 112 ms, p95 118 ms, p99 120 ms; none unpublished.
- **The pilot.** At 05:24:43 the experiment was RUNNING at version 3, the lease at epoch 4 and held, the checkpoint 0.1 s old at 899,759, with no new `experiment_events` or `execution_incidents` row.

**Soak (read-only): PASSED.** Two consecutive hours of the continuity probe at 1 Hz, 05:26:55–07:27:02 UTC, across the 06:00 and 07:00 boundaries, and read-only SQL up to 07:27:30. The probe files are in this worktree's `.cache/deployments/reference-checks-20261003T052055Z/`.

- **Usability.** 7,169 of 7,200 samples were usable (99.6%); the 0021 soak had 6,985. The 31 unusable ones have two causes:

| Interval (UTC) | Samples | What the probe read | Cause |
|---|---|---|---|
| 06:00:03–06:00:17 | 15 | `FEED_OR_REFERENCE_UNAVAILABLE` on both feeds | The one routine clock check that failed. Three `/time` answers took 1,088, 1,105 and 1,097 ms, so the best uncertainty was 544 ms against the bound of 500. The worker recorded `CLOCK_UNCERTAIN`, closed both feeds and **kept the collection**. The recheck at 06:00:10 measured 122 ms (recovery pending) and the one at 06:00:16 verified the clock. The hourly instrument change was then adopted, and both feeds were active at 06:00:18. |
| Nine intervals of 1–3 s between 05:31 and 07:14 | 16 | `QUOTE_STALE` on SOL only | The provider published no SOL ticker for more than five seconds, nine times, for at most 7.0 s. Every SOL frame since the swap was received within 128 ms of its event time, so nothing was delayed. The 5 s quote-age rule failed closed. Not caused by this change and not changed by it. |

- **The targets of §1.**
  - No `COLLECTION_GAP` since the swap. One collection, `0350fb9d…`, from start-up to the end of the soak; market lease epoch 2159 throughout; restart count 0.
  - After the failed check, quotes were usable again 15 s later, against the target of 20 s and against 58 s and 35 s for the same event in the 0021 soak.
  - No reference check aged past 120 s. No REST wait or back-off occurred, so none was recorded.
- **Every unverified interval matches the probe.** The one `CLOCK_UNVERIFIED` record runs from 06:00:03.73 to 06:00:16.75 with two rechecks. The probe's unusable samples run from 06:00:03.94 to 06:00:17.94. The last two seconds are the instrument adoption and each feed's next published quote.
- **Publication.** No `QUEUE_OVERLOAD`. Over the 19,595 stream observations received since the swap, receipt-to-publication was p50 113.6 ms, p95 122.3 ms, p99 125.2 ms and at most 142.5 ms, and none was left unpublished. `publication_lag_ms` read 123–131 at every check.
- **The clock measure against the provider.** 169 checks with 507 samples between the swap and the end of the soak:
  - Every sample that completed was timed from the trace events. The request and its answer took 246 ms at the median.
  - 170 samples opened a new connection, which took 723–2,694 ms and is no longer counted.
  - 27 completed samples took more than a second, and 22 samples failed (`provider_rest_unavailable`), 18 of them the first of their check. The check drops a failed sample and uses the best of the others.
  - Only the check at 06:00:03 had no sample under a second.
  - **INFERRED from the logged timings:** in three more checks (05:39:06, 06:03:23 and 06:27:29) the only fast sample was the one that had also opened the connection. Timed over the whole call, as before this change, those checks would have been imprecise too, and each would have closed the collection. Three further checks are ambiguous because a sample failed.
- **Before the swap, for comparison (OBSERVED).** Between 17:30 UTC on 2026-10-02 and the swap the previous worker recorded 6 `CLOCK_UNCERTAIN` tear-downs, the last at 04:36 UTC, and 8 `COLLECTION_GAP` incidents. Of its 28 hourly marks from 16:00 UTC to 05:00 UTC, 4 were `UNAVAILABLE`.
- **Hour boundaries.** The changed instrument snapshots were adopted in place at 06:00:17.3 and 07:00:30.4 and activated within a second. The second caused no unusable sample.
- **The pilot.** Unchanged through the soak: RUNNING at version 3, lease epoch 4 and held, checkpoint advancing (899,172 → 919,037), no `experiment_events` or `execution_incidents` row. The SNAPSHOT reports for 06:00 and 07:00 were created at 06:05:21 and 07:05:22.
- **Hourly evaluation marks.** All four marks at 06:00 and 07:00 were `VALID`.
- **Every other container** was identical to the starting state at 07:27.
- **Not exercised by the soak.**
  - The REST budget against another client: the highest IP-wide weight the provider reported was 90, against a guard of 3,000, and the worker's own use peaked at 106 of 120.
  - A provider back-off, a clock measured out of bounds, a conflict confirmation, and a rotation while unverified.

**Rollback (not needed).** `docker tag adaptive-spot-lab-market-worker:pre-0022 adaptive-spot-lab-market-worker:latest`, then the recreate command above. The `:pre-0021` tag remains for the image before that.

### 13.2 The steps as proposed

This is the proposal as it stood before the approval. It is kept unchanged as the record of what was approved; §13.1 says what was done.

The procedure is the one that ran for 0021 ([its §11.1](0021-publication-cost-at-density.md#111-executed-2026-10-02-15151518-utc-owner-approved)), with the rollback tag `:pre-0022`:

1. **Window.** HH:15–HH:45 UTC, never 23:50–00:20. If the owner prefers, at a moment with no open position.
2. **Starting state, read-only.** Containers, images, schema revision, pilot state, incident counts.
3. **Protected backup** with its SHA-256. No schema change, so no isolated restore.
4. **Rollback tag** on the running market-worker image.
5. **Build one image** from a clean tree at the pull request's head and compare its `app/` tree with the tested image.
6. **Recreate one service:** `market-worker`, with `--no-deps`. Expect about 40 s without usable quotes, as on 2026-10-02.
7. **Verify, read-only.** Every other container unchanged; the pilot's lease epoch and experiment version unchanged; the declared allowance read and logged; quotes usable.
8. **Soak across two hour boundaries,** with the once-per-second probe and read-only SQL. Pass conditions:
   - the three outcomes of §1;
   - publication as in the 0021 soak: no `QUEUE_OVERLOAD`, receipt-to-publication p99 under one second;
   - every `CLOCK_UNVERIFIED` interval matches the probe's unusable seconds for it;
   - the pilot unchanged.
9. **Next-day check, read-only.** About one routine clock failure an hour was seen before (two in the two-hour 0021 soak). The sample timings and incidents since the swap show whether D3 removed them and what the remaining ones cost.
10. **Record** the commands, backup, image identities and results in this plan, STATUS and COMMANDS.

## 14. Failure and rollback

- **Rollback** is the previous image: tag `:pre-0022` back to `:latest` and recreate `market-worker` with the same command. No schema or data change has to be undone. Incident rows with the new codes stay as history; the old worker ignores them.
- **If a routine clock failure still closes the collection, or usability does not return after two good checks:** roll back and keep the logs.
- **If the trace events are missing in the running image:** the samples fall back to the wider measure and the log says so. The clock check then behaves as it does today on a new connection, and D1 and D2 still apply. U1 is there to catch this before deployment.
- **If the provider answers 429 after the change:** D7 holds every request for the stated time and records it. A `REST_BACKOFF` with status 418 is reported to the owner at once.
- **The pilot** is not touched by the deployment or by a rollback. A longer loss of quotes than the swap itself is visible to it as `PROTECTION_UNAVAILABLE`, as on any other gap.

## 15. Q01–Q10 (affected gates)

[Gate definitions](../../ACCEPTANCE_CHECKLIST.md#quality-gates-for-every-milestone).

| Gate | Applies | Acceptance condition | Planned evidence |
|---|---|---|---|
| Q01 UX, Q02 Accessibility | No | No UI change. New incident codes appear as text in the existing incident list. | — |
| Q03 Data correctness | Yes | Fail-closed state transitions exact (R2–R4, R14); fencing and publication unchanged; the unverified interval recorded (R13). | T1–T10, `WorkerFaults`, `Regression` |
| Q04 Security | Yes, limited | No new destination or parameter; provider back-off enforced (R11); logs without secrets. | U4, H1; diff review; the existing transport negative tests |
| Q05 Reliability | Yes, core | R1–R7, R12; no collection lost to an unmeasurable clock; persistent failures stay closed and bounded; a stop is not delayed by a wait. | T1–T9, H1, H2, density with faults, the soak |
| Q06 Performance | Yes | The existing budgets; reopening within 12 s in isolation and 20 s on the normal app; at most 36 weight a minute while rechecking. | `PerformanceDensity`, `PerformanceBurst`, T6, the soak |
| Q07 Automated verification | Yes | Every phase of §12 in Docker with no skipped test. GitHub CI did not start on 2026-10-02; if it still does not, the local harness is the only automated evidence. | §12 |
| Q08 Visibility | Yes | The clock and REST records of D8; the silent interval of §2.2 would be explained by a record. | T10, H1, H2, the soak |
| Q09 Deployment | Yes | §13: approval, backup, one image, one service, tested source, soak, image rollback. | §13 |
| Q10 Maintainability | Yes | Contracts updated with the code (B5); official sources re-read (§9); no new dependency. | Diff review |

**Result on `0eb208a`.** Q03, Q04, Q05, Q06, Q07, Q08 and Q10 are VERIFIED in isolation by §12.1, with the limits in §12.2. Q09 was NOT RUN at that point.

**Result on the normal app (2026-10-03, §13.1).** Q09 is VERIFIED: approval, backup, one image, one service, the tested source, a soak that met every pass condition, and a rollback tag. Q05, Q06 and Q08 hold against the provider for what the soak exercised: the unmeasurable-clock path, publication and the new records. The REST budget against another client, a provider back-off and a clock measured out of bounds were not exercised there.

## 16. Files (IMPLEMENTED in `0eb208a`)

- `services/engine/app/market_data/provider.py` — trace-based timing, single-attempt clock samples, the budget.
- `services/engine/app/market_data/worker.py` — clock verdicts and state, recheck schedule, rotation deferral, future-frame guard, conflict confirmation, incidents and events.
- `services/engine/app/market_data/parse.py` — the declared-allowance reader.
- `services/engine/app/market_data/store.py` — the guarded `DEGRADED` write only.
- `services/engine/app/market_data/performance_density.py` — the density fault schedule. The loopback provider in `acceptance.py` needed no change.
- `services/engine/tests/test_m2_reference_checks.py` (new), `tests/test_m2_unit.py`.
- `tools/m2-acceptance.ps1` — the new test file in `WorkerFaults`; `-ReferenceFaults`.
- `docs/MARKET_DATA.md`, `docs/OPERATIONS.md`, `docs/TESTING.md`, `docs/INTEGRATION_EVIDENCE.md`, `docs/COMMANDS.md`, `docs/STATUS.md`, this plan.

Not touched: `services/engine/app/execution/**`, `services/engine/app/market_data/read.py`, the status rules of `clock_checked` and `reference_checked`, every migration, `apps/web/**`, `compose.yaml`.

## 17. Decision log

- **One principle for routine checks.** 0012 chose "fail the feed closed, keep the subscription" for instruments. This plan applies it to a clock that cannot be measured, to rotation revalidation and to conflict confirmation, because the M2 contract asks for invalidation and resampling, not for a disconnect (§3).
- **A clock measured out of bounds keeps today's behaviour.** The first draft kept the collection for every failed check. The review showed what that costs when the clock really is wrong (D1), and only the unmeasurable case was observed.
- **The clock rule is not changed.** It is the owner's approved rule and part of the code the pilot runs. The only relaxation that seems worth weighing is put to the owner as decision 2(b).
- **The measurement is tightened, not loosened.** Excluding the waiting and the connection set-up makes the error bar describe the request and its answer alone (D3). The first draft excluded only the budget wait and the DNS lookup; §2.2's send times showed that connection set-up is the larger part.
- **Five seconds between rechecks.** Long enough for a transient delay to pass and for two checks to be independent; short enough to cost about ten seconds; 36 weight a minute at most.
- **No rotation while the clock is unverified.** Otherwise a clock that stays unverified would close the collection through the five-attempt limit after four minutes (§3).
- **The guard is half the declared allowance.** The worker's own use is about 1% of the documented allowance. Half leaves the other half to whatever else uses the IP, and the provider's own 429 remains the last line (D7).
- **The declared allowance is read, not written into the code.** The M2 plan says "discovered". A constant would go stale without notice. Its presence in the answers is confirmed before the budget is written (decision 3).
- **No sending against the header.** The first draft let a refresh pass once a minute while the IP-wide value was above the guard. The review's objection holds: that ignores the header exactly when it matters.
- **One of the two re-opening writes is fixed, the other recorded** (D9).
- **One release for both parts.** Each swap of the market worker costs about 40 s of quotes beside the pilot and needs its own approval.
- **A slow sample is imprecise unless it proves the clock wrong** (second review). The first implementation closed the collection whenever the estimate was beyond a second, which a two-second exchange can cause by itself.
- **Rechecks back off while the request itself fails** (second review). Five seconds is right for a measurement that was only slow; a provider that answers 429 or cannot be reached is asked less often, up to once a minute.
- **A request heavier than the ceiling goes alone in an empty minute** (second review), so a very small declared allowance cannot lock the instrument checks out for good.
- **A budget record never fails its request** (second review). The record is evidence; the request is the worker's function.
- **The density fault bound is 15 s, not the 12 s of the worker tests.** REST answers take 150 ms in that workload, and the reopening is seen at one-second sampling. The measured values were 11.7–12.7 s.
- **Storage-limit handling in the history path is left as it was.** It is caught there as before; the next stream batch stops the collection.
- **Decided by the owner:** the merge of pull request #13 and the request for this plan ([DECISIONS](../../DECISIONS.md#2026-10-02--pull-request-13-merged-follow-up-plan-requested-execplan-0022)); the approval to implement it with option (a) and the one read-only query ([DECISIONS](../../DECISIONS.md#2026-10-02--execplan-0022-approved-for-implementation-clock-option-a-one-read-only-query)). The deployment, and the merge once the soak had passed ([DECISIONS](../../DECISIONS.md#2026-10-03--market-worker-deployment-approved-execplan-0022)).

## 18. Progress and completion evidence

**2026-10-02 (UTC).**
- 18:32: pull request MentorAliu/adaptive_spot_lab#13 merged as `d075a78` on the owner's instruction. `services/engine` on `main` has the same git tree as at `4003e75`, the commit the running market-worker image was built from.
- 18:35–19:40: first draft, from the code at `d075a78`, the evidence of the 0021 deployment and the official pages in §9. Pull request MentorAliu/adaptive_spot_lab#15 opened with it.
- 19:05–19:40: an independent read-only review checked the draft against the code. It confirmed the code facts, the budget arithmetic and the fail-closed property of the kept-collection design. It also found the following, each checked in the code afterwards and taken into this revision:
  - a failed `/time` request during a rotation's revalidation does not fail closed today, so the planned test would have passed without the property (now D4, R6, T7);
  - the recovery-pending verdict and the mixed sequence of failures were missing (D1, T4);
  - a clock that stays unverified would have run into the replacement limit (D4);
  - the unverified state cannot live in the maintenance task (D1, D2);
  - a new connection is over the one-second limit by itself, and the first draft's measurement still contained it (§2.2, §4.2, D3);
  - keeping the collection with a clock measured wrong stores wrong times or floods the invalid-payload record (D1);
  - the once-a-minute refresh above the guard ignored the header (removed);
  - what follows a 429 was described too simply (§3, §4.5), and a waiting reservation would have delayed a stop (D7);
  - conflict confirmation can also stop the process (§4.6, D5);
  - the check time is stamped after the last sample (D3);
  - two writes re-open a closed feed (§4.7, D9).
- The same day a recheck against the probe file corrected the description of the REST-wait interval, here and in ExecPlan 0021: a feed was unusable for 115 s, SOL for 111 s, BTC for 69 s and both for 65 s.

- 19:53: the owner approved the plan, option (a) and the read-only query ([DECISIONS](../../DECISIONS.md#2026-10-02--execplan-0022-approved-for-implementation-clock-option-a-one-read-only-query)).
- 19:57: the query, one statement in a read-only transaction: the two stored `exchangeInfo` answers of 19:00:42 UTC carry `rateLimits` with `REQUEST_WEIGHT`, `MINUTE`, `intervalNum` 1, `limit` 6000, beside two `ORDERS` entries and one `RAW_REQUESTS` entry. D6's gate is met.
- 20:03: B0. W1, U1 and U2 fail on the unchanged code (run `ref-1002a`).
- 20:05–20:27: B1–B4. The first full pass: 43 existing worker-fault tests, 22 new worker cases and 31 unit tests.
- 20:27–20:33: the worker tests against the unchanged code in a scratch checkout of `dafc18d` (run `ref-1002u`): all 19 applicable cases fail, and two direct checks confirm §4.6. That run's stack, images and checkout were removed afterwards.
- 20:33–20:43: density smoke with reference faults at 3,000 rows.
- 20:33–20:52: a second independent read-only review, of the code. It found no path that opens a feed while the clock is unverified, and these, each fixed and tested:
  - a rotation could cancel a failed check before the unverified state was set (the state is now set before anything is written; W1 checks it);
  - a slow sample whose estimate strays could be taken for a wrong clock and close the collection (D1's *imprecise* and *out of bounds*, W15);
  - the future-frame evidence could stay latched across a verification (cleared when verified);
  - a declared allowance below one request's weight would have locked the instrument checks out (D6, U11);
  - a 429 without `Retry-After` on the clock path would have been asked again every five seconds (the recheck now backs off, W17);
  - a record written inside a request could have ended the process (D8, U13);
  - a wait was reported with its last reason instead of its longest (U12);
  - four tests did not prove what they claimed (W5 gained W18 for a pending adoption; W1 samples from before the failure; U14 pins the check time; W20's stop is covered by W21).
- 21:16: commit `0eb208a`.
- 21:17–22:17: acceptance run `ref-1002b` (§12.1). All phases passed.

**2026-10-03 (UTC).**
- 05:20: the owner approved the deployment ([DECISIONS](../../DECISIONS.md#2026-10-03--market-worker-deployment-approved-execplan-0022)).
- 05:20–05:22: deployed to `market-worker` only (§13.1).
- 05:36: the owner: "merge PR #15 once the soak passes".
- 05:47: `main`, with the M5 closure record, was merged into this branch. `services/`, `tools/` and `compose.yaml` are unchanged from `0eb208a`.
- 05:26–07:27: the two-hour soak. It met every pass condition of §13.2, step 8.
- 07:32: pull request MentorAliu/adaptive_spot_lab#15 merged as `ed9fae3`. `services/`, `tools/` and `compose.yaml` on `main` equal the deployed source.

**Completion evidence.** R1–R17 are VERIFIED in isolation on commit `0eb208a` (§12.1), with the limits in §12.2. The change has run on the normal app's market worker since 05:22 UTC on 2026-10-03, and its soak passed (§13.1). Pull request MentorAliu/adaptive_spot_lab#15 was merged as `ed9fae3` on the owner's instruction to merge once the soak had passed.

**Disposable resources.**
- Removed: the stack, the two images and the scratch checkout of run `ref-1002u`.
- Left in place, stopped: the volumes and images of runs `ref-1002a` and `ref-1002b`, among them the density volume of `ref-1002b` with 1.8 million synthetic rows. Removing them is the owner's decision, as for the 0021 runs. The evidence is under `.cache/m2/ref-1002a` and `.cache/m2/ref-1002b`. *(The volumes and images were removed on 2026-10-03 on the owner's instruction; the evidence stays. See [COMMANDS](../COMMANDS.md#test-run-cleanup--2026-10-03).)*

**Residual limitations.**
- Stream delivery stalls, `stream_silent` gaps and the cost of a real restart are not changed. After this plan a real restart still reads 720 candles per symbol.
- A clock measured out of bounds still closes the collection and restarts it, as now.
- Each transient clock failure that D3 does not prevent still costs about 12 s of usable quotes in isolation. Against the provider the one such failure of the soak cost 15 s. It happens when no sample of a check is under a second, which was one check in 169.
- Until the first `exchangeInfo` answer of a process the guard is the own ceiling, so a start-up request can still wait up to a minute while another client is active. On the worker's own ceiling a start-up shortly after two refreshes can also wait some seconds (0012's "REST weight budget during recovery").
- Above the guard, and during a provider back-off, the reference checks can still expire. That fails closed and is now recorded.
- A check whose first sample is the best and whose later samples wait for the budget is written with the first sample's time, so it can be old when written. That is the conservative side; the next refresh is due at once.
- A good clock check still re-opens a feed that a failed instrument check closed, for about a second per refresh (§4.7).
- Quotes captured while the clock is unverified look usable to replay's reduced rule (§10).
- The deployed worker's samples show where the time goes, not why. Opening a connection takes 0.7–2.7 s. About one completed sample in twenty takes more than a second, and about one sample in twenty fails. No other client used the IP during the soak, so the one seen on 2026-10-02 stays unidentified.
- In a quiet market the provider can publish no ticker for a symbol for more than five seconds. The quote-age rule then fails closed for a second or more: nine times for SOL in the two-hour soak. This plan does not change it.
- The REST budget against another client, a provider back-off and a clock measured out of bounds have isolated evidence only.
- Before the deployment the evidence was isolated and synthetic (§12.2). The soak adds two hours against the provider (§13.1).

**Next.** The next-day check of §13.2, step 9, read-only: the clock incidents and sample timings since the swap. The first deleting retention is expected about 05:19 UTC on 2026-10-05 ([ExecPlan 0021](0021-publication-cost-at-density.md)).
