# Manifest

**Pack version:** 2.0.0 — agent-driven architecture revision.  
**Prepared:** 2026-09-26.  
**Contents:** 58 Markdown files. Extract relative paths directly at the repository root.

This is a complete specification, not application code or an implementation report. No upstream skill, font, executable, credential, market dataset or model response is bundled. See [CHANGELOG.md](CHANGELOG.md), [MIGRATION.md](MIGRATION.md) and [docs/PACK_VALIDATION.md](PACK_VALIDATION.md).

## Baseline provenance

The working baseline was extracted from the supplied `adaptive-spot-lab-starter.zip`, containing 47 Markdown files. Its measured archive SHA-256 is:

```text
6d13a3fae1d18dc01d807ad74ac41b1b9e02d0c4132564443217cf2ceafadc00
```

This records the supplied artifact, not a claim about an unseen repository on the user's PC. All original paths are retained. The change log classifies added/modified/unchanged files by actual byte comparison.

## Integrity format

Every file except this manifest is listed below with its UTF-8 byte count and SHA-256. This manifest excludes its own hash to avoid circular self-reference. The aggregate is SHA-256 of the sorted sequence `relative_path`, one tab, hexadecimal SHA-256, one newline for each listed row:

```text
52c5fdf3ce34ab60d1dc4f980ba1f38beaa9a0edbbeea0dafe8b61cfb23d3ddd
```

External ZIP checksum and CRC checks are performed after packaging; no recursive ZIP hash is embedded inside this archive. A checksum verifies bytes, not software correctness or trading performance.

## File inventory

| Relative file | Bytes | SHA-256 |
|---|---:|---|
| [AGENTS.md](../../../AGENTS.md) | 4959 | `0f3fdd16f0a22041a7c8990fce1311c4a255aaa7df64770449f818403387a857` |
| [CHANGELOG.md](CHANGELOG.md) | 10645 | `cd5cd58729155cdc5677d1f9eeb1f3a3f75f67ced886b7363f9410eb92b50e5b` |
| [CLAUDE.md](../../../CLAUDE.md) | 264 | `07710c3e866feaef7d19f57f7a684995ceec8b4f7aef65f0120e698ac4840570` |
| [MIGRATION.md](MIGRATION.md) | 5735 | `1112f74f8b83c34856f412b505b2e80e3ec59dc2be368c1eefa1423c1e3f167f` |
| [README.md](../../../README.md) | 3597 | `0dccfbf6ea63e23e684cc9f14dc21604798d175816890f72794c5f2eef487c9b` |
| [START_HERE.md](START_HERE.md) | 6733 | `c5fee86e55f7ea4636f49745f77658133b8d62a4f61600505af34d22ce2adb49` |
| [apps/web/AGENTS.md](../../../apps/web/AGENTS.md) | 2125 | `1279a2220666e258c9d283ce13ea9f8ed08108b71a3c87555f21af90d65fb257` |
| [apps/web/CLAUDE.md](../../../apps/web/CLAUDE.md) | 11 | `336cc4fbf19beaada7ccf9986414fa91851a8d7a07dfb3ccbe800a69eed0ab49` |
| [docs/ACCEPTANCE_CHECKLIST.md](../../ACCEPTANCE_CHECKLIST.md) | 8213 | `8cd4a7a604327a6603ec935e3eb27964d6b74e0fcc35fd94e6410079f757fa85` |
| [docs/ADAPTATION.md](../ADAPTATION.md) | 7373 | `d61e81b5cc18bb1d2e65a90a198f98879c14a43363553a160cb046604ac112b2` |
| [docs/AGENTS.md](../../AGENTS.md) | 1159 | `ed79a0f80dfeceb446a1000677f5e1bd8079bb114a8a62d3a0d57cfa1b4e00e2` |
| [docs/AGENT_TOOL_CONTRACTS.md](../AGENT_TOOL_CONTRACTS.md) | 13413 | `62003dd638644c0f920bdff15de66d9826c30f639d57c99f82e6e885e66b9dd9` |
| [docs/API_CONTRACTS.md](../../API_CONTRACTS.md) | 9252 | `d4d8adabcf1ccd627d224edded54c9e5569f6d92298d085a76fa43573b83772c` |
| [docs/ARCHITECTURE.md](../../ARCHITECTURE.md) | 6762 | `4efd2c1ecda004a36a3cef75e473151f73db07897037062e9e03536119299178` |
| [docs/AUTONOMY_MATRIX.md](../../AUTONOMY_MATRIX.md) | 8309 | `227da636c93cd396ddff63bd8374bd97aacb8b8524935a96a67379e481051746` |
| [docs/CLAUDE.md](../../CLAUDE.md) | 11 | `336cc4fbf19beaada7ccf9986414fa91851a8d7a07dfb3ccbe800a69eed0ab49` |
| [docs/COMMANDS.md](../COMMANDS.md) | 4358 | `cf38ed5c8587f12dfff62aefed6d3a624449cb93e00d0fd83fdba16d1d6979e7` |
| [docs/CONFIGURATION.md](../../CONFIGURATION.md) | 6067 | `58f3980d9cf0338d472358b31d8b30576571a16f919799fca9893858f83ad7a5` |
| [docs/DATA_CONTRACTS.md](../../DATA_CONTRACTS.md) | 9423 | `20414cd84ca448d68278eebe213e4f18af441999272918268a698bcb77a3a251` |
| [docs/DECISIONS.md](../../DECISIONS.md) | 4747 | `d61dfefdcf8952bf7bcd3e8645f0fd5f759e97274a04f28d3085ab68c0c291be` |
| [docs/DOCKER.md](../../DOCKER.md) | 6846 | `b81d851da289f1fb2f97d6d78720c84f2366e8dc998f65d8388f9d9bed325a77` |
| [docs/EVALUATION.md](../EVALUATION.md) | 9369 | `cf02e036a73e436b59c5841aa9b92bf253b8c96ea5a943d3129694e0bca0856d` |
| [docs/FRONTEND.md](../../FRONTEND.md) | 10697 | `9abba2bc6db1547c89373141869e4871079ca686c4cea0a00d9b21ea2e3b7e04` |
| [docs/INTEGRATION_EVIDENCE.md](../../INTEGRATION_EVIDENCE.md) | 2362 | `8fa0e782d65cead2906d042eed1d3ed926d4319ce507a06d18a8f68782061b98` |
| [docs/LEDGER.md](../../LEDGER.md) | 6172 | `a0be8c0cf92f42af5b649d49e06f899a4db6ff51b953315579a680d6619e8ea4` |
| [docs/LIBRARIES.md](../../LIBRARIES.md) | 6933 | `5b83c50b4adce536a819da64da30cd39b700cdf5db36e18c81f9d06dc2feeae2` |
| [docs/MARKET_DATA.md](../../MARKET_DATA.md) | 5123 | `803b3ddf2f01df6bd79ed0cf489f5032dfd5fa41f3691efd06b10103c0a3ff8b` |
| [docs/OPERATIONS.md](../../OPERATIONS.md) | 6917 | `80f9f9446c5e14cd7f48f704f0090348a78ec6853c2e43d903431f61c533022a` |
| [docs/PACK_VALIDATION.md](PACK_VALIDATION.md) | 4023 | `770e69f091859f104d3cc6862087a92944289ac5776da3146aa22e281b2f85ec` |
| [docs/PAPER_EXECUTION.md](../../PAPER_EXECUTION.md) | 5506 | `b9fb5e5c94b039e5624a9d5ea24474b7438ee0fe09ebd0f465172b6dc3c3b719` |
| [docs/PLANS.md](../../PLANS.md) | 2001 | `1ce34e4d98db8c63b1be406da66ffdfe4073acd26386ceb006a10efae7a259d2` |
| [docs/PROJECT.md](../../PROJECT.md) | 5413 | `673f5ec71539c715be2db8cb0c15974f847d96bfbe62e8a8595ac55f88381f0f` |
| [docs/README.md](../../README.md) | 5113 | `bcbcb7bc43a7a5bf23190de60c1bca06330431801e8c2d5fb8c51502fb1fb61d` |
| [docs/REFERENCES.md](../../REFERENCES.md) | 16544 | `2daa3e002b83144f46051105ff6160a302b7718b408fe1084b0599593c42e9f6` |
| [docs/RESEARCH_WORKFLOWS.md](../RESEARCH_WORKFLOWS.md) | 9754 | `b5adce8045874092a6b02e92d2d1c5c99b1d7e2ef327b27447bab0c5c0c4577d` |
| [docs/RISK_POLICY.md](../../RISK_POLICY.md) | 8340 | `3ddfbe60856b2dd5b9ef7013e66037fc08ec43f9e4d7f4a06018f866ca66ccd9` |
| [docs/ROADMAP.md](../../ROADMAP.md) | 8651 | `329d27d51d9f61efef5b5c446a96ad4a81754a426bdb8d47c15f3c80ab834a77` |
| [docs/RUNTIME_AGENTS.md](../RUNTIME_AGENTS.md) | 12118 | `caf6f26a73a5467afb54394377cb2eb1f0c66074cb471efb7fa4e76412fb30b9` |
| [docs/SECURITY.md](../../SECURITY.md) | 6751 | `3ed64d98bda1736fc8b1e0a1a329c8c1dc3c867350aac12dde0346f74f077a3c` |
| [docs/SHADCN_WORKFLOW.md](../../SHADCN_WORKFLOW.md) | 6902 | `926cb99964eefbb110e1808e2bc325543d9651d2af44d6cb165f434768af185d` |
| [docs/STATUS.md](../../STATUS.md) | 2568 | `207247c6f7cf81978f9919e79d366d5584e59d93d41c4a179bd2d4a97049cdcb` |
| [docs/STRATEGIES.md](../../STRATEGIES.md) | 7100 | `b70a0f93e54b0a5df68e5ff1029d999f09bf8623d3f2b34c7af0f6b75d6fb13c` |
| [docs/TESTING.md](../TESTING.md) | 10198 | `05ec1f9b5d6a5e1fe1510fd74d8f680d37b5f3fa05213bb2ee94270717aa5a0b` |
| [docs/plans/0001-foundation.md](../plans/0001-foundation.md) | 6290 | `664b0885bf752adebeb45846c60263f3db80f1528cc68c064f7b194e6ac81a62` |
| [docs/templates/EXPERIMENT_REPORT.md](../templates/EXPERIMENT_REPORT.md) | 2812 | `f47eddc5c3b11ce47072c88e87e8059dce5032dde0112ed010732c1810b9b179` |
| [docs/templates/FEATURE_TASK.md](../../templates/FEATURE_TASK.md) | 2169 | `a9ff02febd3da05178de2d0bb48d1db693b6a923c1b910f339e47d58d0aca431` |
| [docs/templates/STRATEGY_PROPOSAL.md](../templates/STRATEGY_PROPOSAL.md) | 2640 | `380859f2dacbb7569960607f01de503d8f86fd784b193e87c12207cde4ef02e2` |
| [services/agent-runner/AGENTS.md](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/agent-runner/AGENTS.md) | 1994 | `fd213b598440f9c3bc0db4cdfae1b442f97597695713d527ed585152060b3794` |
| [services/agent-runner/CLAUDE.md](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/agent-runner/CLAUDE.md) | 11 | `336cc4fbf19beaada7ccf9986414fa91851a8d7a07dfb3ccbe800a69eed0ab49` |
| [services/agent-runner/prompts/evaluator.md](https://github.com/MentorAliu/adaptive_spot_lab/blob/cf6360d/services/agent-runner/prompts/evaluator.md) | 3071 | `e7c5b58cf365ade7613331289fdfdf82c49222b17dd99767d17e06158abb1a45` |
| [services/agent-runner/prompts/market-analyst.md](https://github.com/MentorAliu/adaptive_spot_lab/blob/cf6360d/services/agent-runner/prompts/market-analyst.md) | 2674 | `03d88bde7734f8bd0b7e8d038fc5abf62b2b2655912c58340e0d13629d29cd1a` |
| [services/agent-runner/prompts/portfolio-coordinator.md](https://github.com/MentorAliu/adaptive_spot_lab/blob/cf6360d/services/agent-runner/prompts/portfolio-coordinator.md) | 3569 | `42f04feaa63c4db5dacae0e9824e4a7605dbd06f7370990d87d9807faf2ffa60` |
| [services/agent-runner/prompts/strategy-researcher.md](https://github.com/MentorAliu/adaptive_spot_lab/blob/cf6360d/services/agent-runner/prompts/strategy-researcher.md) | 3035 | `850083c18aae2f9cbca995172a4ffdd71b345daa4a26d10835911ed2764f1e29` |
| [services/engine/AGENTS.md](../../../services/engine/AGENTS.md) | 1706 | `e6500909e3bccc4f3cdf1473072d3fe77e49746c624b6e99339b7cd60ef277c8` |
| [services/engine/CLAUDE.md](../../../services/engine/CLAUDE.md) | 11 | `336cc4fbf19beaada7ccf9986414fa91851a8d7a07dfb3ccbe800a69eed0ab49` |
| [tests/AGENTS.md](../../../tests/AGENTS.md) | 1405 | `15d262eec215d20e90b0bc4228596538d7af7787dc1dd754e7320ac6e5de60d4` |
| [tests/CLAUDE.md](../../../tests/CLAUDE.md) | 11 | `336cc4fbf19beaada7ccf9986414fa91851a8d7a07dfb3ccbe800a69eed0ab49` |

The manifest itself is the remaining file in the stated total. Preserve the relative paths when copying. Global/client instructions are not bundled or measured here.
