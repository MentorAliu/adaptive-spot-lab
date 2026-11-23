# M3 Windows Narrator review

**RETIRED — NOT RUN.** On 2026-09-29 the owner turned off manual screen-reader review for M3 and the rest of the application ([decision](../DECISIONS.md#2026-09-29--manual-screen-reader-review-retired)). No row below was performed, and the checklist is kept for reference only. Its build instructions refer to the since-removed M3 worktree.

This manual check covered the new read-only M3 pages. Automated accessibility-tree, keyboard, zoom and 390-pixel layout assertions are separate evidence (see [ExecPlan 0011](plans/0011-paper-broker-reference.md)). Record **PASS**, **FAIL** with the exact unexpected speech or control behavior, or **NOT RUN** for every row. Speech findings are owner-reported; the coding tools do not observe them.

## Build under review

Use an isolated review project built from the accepted source (the accepted run `m3-0929e` has been stopped). From the M3 worktree:

```powershell
./tools/m3-acceptance.ps1 -RunId m3-review -Phase Prepare
./tools/m3-acceptance.ps1 -RunId m3-review -Phase Build
./tools/m3-acceptance.ps1 -RunId m3-review -Phase BrowserInactive
./tools/m3-acceptance.ps1 -RunId m3-review -Phase BrowserPopulated   # leaves api/web running
# review at http://127.0.0.1:<browser web_port from .cache/m3/m3-review/manifest.json>
./tools/m3-acceptance.ps1 -RunId m3-review -Phase Stop
```

The data are labeled `SYNTHETIC TEST`. The disposable test passphrase is `browser fixture passphrase 123`; it is not the owner's password. Do not use the normal owner installation: its main account is intentionally empty and inactive in M3.

Start Narrator with Windows+Ctrl+Enter; Narrator's key is normally Caps Lock or Insert ([official command reference](https://support.microsoft.com/en-us/accessibility/windows/narrator/appendix-b-narrator-keyboard-commands-and-touch-gestures)).

| ID | Action | Required result | Finding |
|---|---|---|---|
| R01 | Sign in with the keyboard; move through Account → Markets → Orders → Positions → Risk → System with Tab/Shift+Tab and Enter. | Each link has an understandable name; focus is visible and never trapped; the page heading identifies the page. | NOT RUN |
| R02 | On Orders, change Status and Symbol with the keyboard; reload; use browser Back. | Group labels and the selected state are spoken; the chosen filter survives reload and Back. | NOT RUN |
| R03 | Read the Orders and Modeled fills tables with Narrator table navigation (Ctrl+Alt+arrow keys). | Column headers and values are understandable; `SYNTHETIC TEST` and `MODELED FILL` are spoken as text, not only color. | NOT RUN |
| R04 | Open an order; read the event timeline, risk decision, reservation and provenance cards. | Statuses, reasons and times are understandable; the planned stop sentence is read as "not a guaranteed exit price". | NOT RUN |
| R05 | Open the gapped-stop position. | "Realized loss exceeded the planned loss" and the dust notice are announced as alerts and read in full. | NOT RUN |
| R06 | On Risk, switch the ledger mode to Synthetic test, then back to Main paper account. | The inactive-activation alert and its milestone blockers are read; latches and unavailable values state their reasons; nothing implies trading can be started. | NOT RUN |
| R07 | Set browser zoom to 200% and repeat R02–R06; also inspect a window near 390 pixels wide. | Controls and text remain reachable; tables scroll within their own region; no page-wide horizontal overflow or obscured focus. | NOT RUN |
