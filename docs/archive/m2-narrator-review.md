# M2 Windows Narrator review

**PASS — N01–N09 passed by owner report.** The owner reported “all narrator has passed” after receiving the complete checklist; recorded 2026-09-28 04:00 UTC. This closes the scoped manual Q02 condition alongside the automated accessibility evidence. Speech was reviewed by the owner, not directly observed by the coding tools. No failures were reported.

## Build under review

- Isolated normal browser project: `asl-m2-m2-completion-0927e-browser`.
- Review URL: <http://127.0.0.1:54053> (**now offline after completed review**). Automated checks passed; review build frozen at 2026-09-27 22:04:36 UTC (2026-09-28 00:04:36 Budapest). The final backend images include the corrected failure-log metadata; the verified UI, database and owner session were preserved for review. Earlier bindings remain in the run directory. The task review stack was stopped at 2026-09-28 04:07:16 UTC; its logs and database volume remain retained.
- Source manifest: `.cache/m2/m2-completion-0927e/source-images-20260927T220435377.json`, SHA-256 `3bfdba75a258103cd8842c7e3e523521425199a5d1108a3e73d197d4ebf59b31`.
- Running web image: `sha256:8c96dac8575ddb8b2e73f9ce37957ce3326afa7ec1b0c72106d465794863d44e`.
- Running API image: `sha256:01650cd55233b89f102045508f284e3f75581b2e7a70e912637bdd19f4ac15eb`.
- Running synthetic feed image: `sha256:a23aeb65b2d231d249922e21bdbb0e4f918ec6eb9858ececd2188a722cf06f27`.
- Data: visibly labeled `SYNTHETIC_FIXTURE`; no public quotes or financial performance claim.
- Test passphrase: `browser fixture passphrase 123`. This is a disposable test credential, not the owner's password.
- Read-only host metadata: Windows display version `25H2`, build `26200.9457`; Narrator file version `10.0.26100.8972`. This is installed-file evidence. The owner confirmed Narrator was running, reported N01 PASS (recorded 03:53 UTC), then all remaining checks PASS (recorded 04:00 UTC on 2026-09-28). Browser: **Chrome, owner-reported**. Browser version, Narrator voice and exact execution times were not supplied; do not infer them from installed-file metadata.
- N01 evidence: `.cache/m2/m2-completion-0927e/narrator-N01.json`. All three running image IDs were rechecked against the binding above at 03:53:41 UTC. Speech findings are owner-reported, not directly observed by the coding tools.
- Final evidence: `.cache/m2/m2-completion-0927e/narrator-final.json`. All three running image IDs were rechecked against the same binding at 04:00:28 UTC. The report applies to N01–N09 and preserves the distinction between owner findings and automated assertions.

The source and web/API images stayed fixed during review. Automated sign-in tests were kept separate because this single-owner application rotates sessions on login. The instructions below are retained to reproduce the review.

## Guided checks

The guide originally proposed Edge; the owner used Chrome. Start Narrator with Windows+Ctrl+Enter. Narrator's key is normally Caps Lock or Insert; its [official command reference](https://support.microsoft.com/en-us/accessibility/windows/narrator/appendix-b-narrator-keyboard-commands-and-touch-gestures) covers scan mode, headings and table cells. Record **PASS**, **FAIL** with the exact unexpected speech/control behavior, or **NOT RUN** for every row. Remaining row results below come from the owner's all-pass report at 04:00 UTC, not independently captured speech transcripts.

| ID | Action | Required result | Finding |
|---|---|---|---|
| N01 | Sign in with keyboard only. Navigate Account → System → Markets using Tab/Shift+Tab and Enter. | Passphrase field, sign-in/out and navigation have understandable names; focus is visible, logical and never trapped. Headings identify the page. | **PASS — owner reported**, recorded 2026-09-28 03:53 UTC; bound images reverified. |
| N02 | Select SOL, then BTC; change 30/90 days using keyboard controls. Use browser Back/Forward. | Symbol/history group and selected state are spoken; page, quote and chart/table remain tied to the requested symbol. Focus remains usable. | **PASS — owner reported** |
| N03 | In browser DevTools Network choose a slow throttling preset, then change uncached history/symbol. Return to no throttling afterward. | Loading announces the requested symbol, has visible skeletons and never reads old-symbol values as current. Completion is understandable without repetitive price announcements. | **PASS — owner reported** |
| N04 | Read the chart description and exact-values table. In Narrator scan mode use table navigation and Ctrl+Alt+arrow keys between cells. | Table headers and values are understandable; final/provisional status and exact prices are available without interpreting the canvas. Missing ranges have a text alternative. | **PASS — owner reported** |
| N05 | Leave a healthy quote updating for 15 seconds while reading another paragraph. | Price refreshes do not repeatedly interrupt speech or move focus. | **PASS — owner reported** |
| N06 | Run the isolated `ReviewUnavailable` command below. After at least seven seconds inspect the quote and queue cards. | A stale/unavailable quote is not announced as usable; telemetry becomes unknown with its retained timestamp. Text explains the state without color alone. | **PASS — owner reported** |
| N07 | Run `ReviewRecover`, then wait for fresh data. | Recovery has a meaningful announcement; current usability returns only with a fresh quote. Navigation/focus still work. | **PASS — owner reported** |
| N08 | In DevTools Network choose Offline for this tab and wait for a refresh; restore No throttling. | Read failure is announced, retained values are explicitly unverified, and a successful retry recovers visibly. | **PASS — owner reported** |
| N09 | Set browser zoom to 200%, repeat symbol/history/table navigation, then restore 100%. Also inspect a narrow window near 390 pixels. | Essential controls/content remain reachable; no clipped status text, obscured focus or page-wide horizontal overflow. The exact-values table can scroll within its own region. | **PASS — owner reported** |

Edge's [official Network reference](https://learn.microsoft.com/en-us/microsoft-edge/devtools/network/reference) describes throttling and Offline. Those settings affect this browser tab; do not disconnect the host or normal owner stack.

From the repository's PowerShell directory, these commands affect only the manifest-owned synthetic browser feed:

```powershell
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase ReviewUnavailable
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase ReviewRecover
```

All nine results are now recorded. Missing browser-version/voice details limit environment reproducibility and remain explicitly unknown; they are not invented test failures or a whole-WCAG conformance claim. Future failures need the row ID, expected versus spoken behavior, and reproduction steps. After any behavior fix, rebuild and retest affected automated and manual rows against a new source/image binding.
