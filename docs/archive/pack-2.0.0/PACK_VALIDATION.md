# Documentation packaging validation

**Pack:** 2.0.0. **Validation date:** 2026-09-26. **Scope:** the generated Markdown replacement pack only.

## Checks performed

| Check | Result |
|---|---|
| Original archive provenance | Original 47-file archive inspected; final manifest records its measured SHA-256. |
| Inventory and migration | 58 Markdown files: 11 added, 38 modified, 9 byte-unchanged; no removed/renamed original paths. Changelog categories matched actual bytes. |
| Text structure | UTF-8, final newlines, balanced fenced blocks and consistent pipe-table column counts checked. No embedded chat citation placeholders or unfinished packaging markers. |
| Local navigation | All local Markdown destinations and referenced heading anchors checked after final assembly. External website availability is not implied. |
| Shared instructions | 6 CLAUDE-to-AGENTS imports resolved; largest repository-only AGENTS chain 7,084 bytes. User/global instructions are outside this measurement. |
| Preset and frontend | Exact bootstrap command and required library/plugin names preserved; upstream shadcn workflow is byte-unchanged. No scaffold/install test was performed. |
| Financial invariants in specification | Ledger and paper-execution documents byte-unchanged; original risk-policy text and full reference-strategy seed preserved. Exact-Decimal funding/NAV identities rechecked in four arithmetic cases. |
| Agent traceability | P01–P20 present in product/test/checklist records; four role templates; 15 named application tools; 38 unchecked acceptance items; M0–M8 headings; 54 unique reference entries. |
| Legacy conflict scan | Known selector-only, blanket no-tool and daily-only active instruction fragments checked; daily selector remains explicitly a baseline, not the agent-driven policy. |
| File integrity | Final manifest hashes every other Markdown file; aggregate inventory hash recomputed. ZIP entries are unique, relative, non-traversing and Markdown-only; CRC and byte-for-byte extraction roundtrip checked. |

The repository-only instruction chain check measures packaged AGENTS files, not all material a client may load, its account context, or future user additions. Passing a size comparison is not proof a model follows instructions.

## Editorial consistency review

Reviewed the permission/role/tool relationship; native-versus-application transport distinction; server-issued child-role grants; exact-hash reviewer semantics; main-domain membership versus new-strategy approval; historical read boundaries; independent financial path; original position protection; transient blocks versus safety latches; resource isolation; migration paths; and honest implementation status.

This is a targeted human-readable specification review supported by structural scans, not a formal proof that no ambiguity remains. Implementers must still report and reconcile material contradictions instead of selecting a more permissive interpretation.

## Not performed

No application code was generated or run. No preset was scaffolded, official skill installed, dependency resolved or lockfile created. No Docker image/Compose stack/browser suite was built or tested. No user's PC or repository was inspected. No runtime login, subscription capacity check, model call, Binance-data request or research experiment was executed. No strategy profitability, fill realism, operational capacity or security assurance has been established.

Current official documentation was reviewed for the subset recorded in [REFERENCES.md](../../REFERENCES.md); the whole inherited reference set was not re-fetched. Some TanStack website pages failed retrieval and their official repository documents were used as disclosed there. URL review is not installed-version compatibility evidence.

The checkboxes in [ACCEPTANCE_CHECKLIST.md](../../ACCEPTANCE_CHECKLIST.md) intentionally remain unchecked. [MANIFEST.md](MANIFEST.md) supplies exact file checksums; [MIGRATION.md](MIGRATION.md) supplies safe replacement instructions.
