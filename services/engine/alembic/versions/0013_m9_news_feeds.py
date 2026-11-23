"""M9 update 1: the free feeds the agents read, and every guard's name lookup pinned.

Revision ID: 0013_m9_news_feeds
Revises: 0012_m8_one_run

ExecPlan 0032 sections 5.1 and 6. Additive.

- Four source versions, frozen below and mirrored by ``app.sources.feeds``: the BLS release calendar, the BLS
  latest numbers, the Federal Reserve's monetary policy releases and the ECB's press releases and speeches. They
  are stored like migration 0008's two; the agent worker records each in force as ``SYSTEM`` once it finds the
  stored hash equal to the code's (``app.agents.in_force``), and the fetcher reads it from then on.
- The 27 functions of migrations 0002 to 0009 that were created without a fixed ``search_path`` get
  ``pg_catalog, public, pg_temp``, as every function since 0009 has. Without it the session's temporary schema
  is searched first for tables, so an identity allowed to create a temporary table (``TEMP`` is granted to
  ``PUBLIC`` by default) could shadow a table a guard reads, ``pg_roles`` in ``asl_is_superuser`` among them.
  Nothing else about the functions changes.

Downgrade refuses while anything names the four sources (a request, a fetch, an item, a trigger or an in-force
record), then resets the 27 settings and removes the four rows.
"""

import hashlib
import json

from alembic import op

revision = "0013_m9_news_feeds"
down_revision = "0012_m8_one_run"
branch_labels = None
depends_on = None

SOURCE_LINES = r"""
["CALENDAR_BLS_V1", "SOURCE_VERSION", 1, "PROPOSED", "{\"authentication\":\"NONE\",\"budget\":{\"failure_backoff_seconds\":1800,\"poll_interval_seconds\":21600,\"refresh_interval_seconds\":3600,\"requests_per_hour\":1,\"unstated_limit_backoff_seconds\":3600},\"extract_max_bytes\":1024,\"host\":\"www.bls.gov\",\"id\":\"CALENDAR_BLS_V1\",\"kind\":\"SOURCE_VERSION\",\"method\":\"GET\",\"name\":\"BLS release calendar\",\"owner_approval\":\"EXACT_HASH_REQUIRED\",\"parser\":\"ICALENDAR_V1\",\"path_template\":\"/schedule/news_release/bls.ics\",\"poll_filters\":{},\"port\":443,\"rate_limit_per_ip_per_hour\":2,\"rate_limit_policy\":\"HTTP_RETRY_AFTER_V1\",\"redirects\":\"REFUSED\",\"response\":{\"content_type\":\"text/calendar\",\"deadline_seconds\":20,\"max_bytes\":1048576},\"retention\":{\"attribution\":\"CITE_THE_BUREAU_OF_LABOR_STATISTICS\",\"basis\":\"US_GOVERNMENT_PUBLIC_DOMAIN_CITE_BLS\",\"excluded\":[\"LINKED_DESTINATIONS\",\"BLS_EMBLEM\",\"PREVIOUSLY_COPYRIGHTED_PHOTOGRAPHS_AND_ILLUSTRATIONS\"],\"expiry\":null,\"license\":\"Public domain (U.S. Bureau of Labor Statistics)\",\"license_url\":\"https://www.bls.gov/opub/copyright-information.htm\",\"review\":\"docs/INTEGRATION_EVIDENCE.md M9 update 1\",\"review_date\":\"2026-10-19\",\"scope\":\"SCHEDULED_RELEASE_EVENTS_ONLY\",\"terms\":\"https://www.bls.gov/opub/copyright-information.htm\"},\"scheme\":\"https\",\"source\":\"ExecPlan 0032 section 5.1; feed and terms read 2026-10-19; the publisher states no rate limit, so the per-address figure is this app's own cap\",\"status\":\"PROPOSED\",\"symbols\":[\"BTCUSDT\",\"SOLUSDT\"],\"timestamps\":{\"availability\":\"LOCAL_VALIDATED_AVAILABILITY\",\"publication\":\"NONE\",\"receipt\":\"LOCAL_RECEIPT\",\"scheduled\":\"DTSTART_RESOLVED_BY_THE_FILES_OWN_VTIMEZONE\",\"update\":\"LAST-MODIFIED_IF_THE_EVENT_SUPPLIES_IT\"},\"trigger\":{\"cooldown_seconds\":3600,\"family\":\"SOURCE_REVISION\",\"first_fetch\":\"BASELINE\",\"match\":\"NONE\"},\"typed_filters\":{},\"version\":1}", "72171a8c0515522c9818ba740b63f6ba1e37f2722920d3c2ac351d0481458c2d"]
["NUMBERS_BLS_V1", "SOURCE_VERSION", 1, "PROPOSED", "{\"authentication\":\"NONE\",\"budget\":{\"failure_backoff_seconds\":900,\"poll_interval_seconds\":900,\"refresh_interval_seconds\":600,\"requests_per_hour\":4,\"unstated_limit_backoff_seconds\":3600},\"extract_max_bytes\":8192,\"host\":\"www.bls.gov\",\"id\":\"NUMBERS_BLS_V1\",\"kind\":\"SOURCE_VERSION\",\"method\":\"GET\",\"name\":\"BLS latest numbers\",\"owner_approval\":\"EXACT_HASH_REQUIRED\",\"parser\":\"RSS_V1\",\"path_template\":\"/feed/bls_latest.rss\",\"poll_filters\":{},\"port\":443,\"rate_limit_per_ip_per_hour\":8,\"rate_limit_policy\":\"HTTP_RETRY_AFTER_V1\",\"redirects\":\"REFUSED\",\"response\":{\"content_type\":\"application/rss+xml\",\"deadline_seconds\":20,\"max_bytes\":1048576},\"retention\":{\"attribution\":\"CITE_THE_BUREAU_OF_LABOR_STATISTICS\",\"basis\":\"US_GOVERNMENT_PUBLIC_DOMAIN_CITE_BLS\",\"excluded\":[\"LINKED_DESTINATIONS\",\"BLS_EMBLEM\",\"PREVIOUSLY_COPYRIGHTED_PHOTOGRAPHS_AND_ILLUSTRATIONS\"],\"expiry\":null,\"license\":\"Public domain (U.S. Bureau of Labor Statistics)\",\"license_url\":\"https://www.bls.gov/opub/copyright-information.htm\",\"review\":\"docs/INTEGRATION_EVIDENCE.md M9 update 1\",\"review_date\":\"2026-10-19\",\"scope\":\"FEED_TEXT_ONLY\",\"terms\":\"https://www.bls.gov/opub/copyright-information.htm\"},\"scheme\":\"https\",\"source\":\"ExecPlan 0032 section 5.1; feed and terms read 2026-10-19; the publisher states no rate limit, so the per-address figure is this app's own cap\",\"status\":\"PROPOSED\",\"symbols\":[\"BTCUSDT\",\"SOLUSDT\"],\"timestamps\":{\"availability\":\"LOCAL_VALIDATED_AVAILABILITY\",\"publication\":\"pubDate\",\"receipt\":\"LOCAL_RECEIPT\",\"update\":\"NONE\"},\"trigger\":{\"cooldown_seconds\":14400,\"family\":\"SOURCE_REVISION\",\"first_fetch\":\"BASELINE\",\"match\":\"EVERY_ITEM\"},\"typed_filters\":{},\"version\":1}", "9adc4cb283cdde387668d5ba3c72067ccbc3852309798a65c0a9fe9214850499"]
["PRESS_FED_MONETARY_V1", "SOURCE_VERSION", 1, "PROPOSED", "{\"authentication\":\"NONE\",\"budget\":{\"failure_backoff_seconds\":900,\"poll_interval_seconds\":900,\"refresh_interval_seconds\":600,\"requests_per_hour\":4,\"unstated_limit_backoff_seconds\":3600},\"extract_max_bytes\":4096,\"host\":\"www.federalreserve.gov\",\"id\":\"PRESS_FED_MONETARY_V1\",\"kind\":\"SOURCE_VERSION\",\"method\":\"GET\",\"name\":\"Federal Reserve monetary policy\",\"owner_approval\":\"EXACT_HASH_REQUIRED\",\"parser\":\"RSS_V1\",\"path_template\":\"/feeds/press_monetary.xml\",\"poll_filters\":{},\"port\":443,\"rate_limit_per_ip_per_hour\":8,\"rate_limit_policy\":\"HTTP_RETRY_AFTER_V1\",\"redirects\":\"REFUSED\",\"response\":{\"content_type\":\"application/rss+xml\",\"deadline_seconds\":20,\"max_bytes\":1048576},\"retention\":{\"attribution\":\"CITE_THE_BOARD_AS_THE_SOURCE\",\"basis\":\"FEDERAL_RESERVE_BOARD_PUBLIC_DOMAIN_CITE_THE_BOARD\",\"excluded\":[\"LINKED_DESTINATIONS\",\"MATERIAL_FROM_NON_BOARD_SOURCES\",\"COPYRIGHTED_MATERIAL\"],\"expiry\":null,\"license\":\"Public domain unless otherwise indicated (Federal Reserve Board)\",\"license_url\":\"https://federalreserve.gov/disclaimer.htm\",\"review\":\"docs/INTEGRATION_EVIDENCE.md M9 update 1\",\"review_date\":\"2026-10-19\",\"scope\":\"FEED_TEXT_ONLY\",\"terms\":\"https://federalreserve.gov/disclaimer.htm\"},\"scheme\":\"https\",\"source\":\"ExecPlan 0032 section 5.1; feed and terms read 2026-10-19; the publisher states no rate limit, so the per-address figure is this app's own cap\",\"status\":\"PROPOSED\",\"symbols\":[\"BTCUSDT\",\"SOLUSDT\"],\"timestamps\":{\"availability\":\"LOCAL_VALIDATED_AVAILABILITY\",\"publication\":\"pubDate\",\"receipt\":\"LOCAL_RECEIPT\",\"update\":\"NONE\"},\"trigger\":{\"cooldown_seconds\":14400,\"family\":\"SOURCE_REVISION\",\"first_fetch\":\"BASELINE\",\"match\":\"EVERY_ITEM\"},\"typed_filters\":{},\"version\":1}", "aada9b3782573c51578e581d83147a5d72940a66e4bc3932354f3cbca9f7b670"]
["PRESS_ECB_V1", "SOURCE_VERSION", 1, "PROPOSED", "{\"authentication\":\"NONE\",\"budget\":{\"failure_backoff_seconds\":900,\"poll_interval_seconds\":900,\"refresh_interval_seconds\":600,\"requests_per_hour\":4,\"unstated_limit_backoff_seconds\":3600},\"extract_max_bytes\":4096,\"host\":\"www.ecb.europa.eu\",\"id\":\"PRESS_ECB_V1\",\"kind\":\"SOURCE_VERSION\",\"method\":\"GET\",\"name\":\"ECB press releases and speeches\",\"owner_approval\":\"EXACT_HASH_REQUIRED\",\"parser\":\"RSS_V1\",\"path_template\":\"/rss/press.html\",\"poll_filters\":{},\"port\":443,\"rate_limit_per_ip_per_hour\":8,\"rate_limit_policy\":\"HTTP_RETRY_AFTER_V1\",\"redirects\":\"REFUSED\",\"response\":{\"content_type\":\"application/rss+xml\",\"deadline_seconds\":20,\"max_bytes\":1048576},\"retention\":{\"attribution\":\"CITE_THE_ECB_AS_THE_SOURCE_ACCURATELY\",\"basis\":\"ECB_FREE_USE_WITH_THE_ECB_CITED\",\"excluded\":[\"LINKED_DESTINATIONS\",\"AUTHORED_DOCUMENTS_BEYOND_THE_FEED_ITEM\"],\"expiry\":null,\"license\":\"ECB website copyright: free use of information with the ECB cited as the source\",\"license_url\":\"https://www.ecb.europa.eu/home/disclaimer/html/index.en.html\",\"review\":\"docs/INTEGRATION_EVIDENCE.md M9 update 1\",\"review_date\":\"2026-10-19\",\"scope\":\"FEED_TITLE_AND_SUMMARY_KEPT_LOCALLY_NEVER_REPUBLISHED\",\"terms\":\"https://www.ecb.europa.eu/home/disclaimer/html/index.en.html\"},\"scheme\":\"https\",\"source\":\"ExecPlan 0032 section 5.1; feed and terms read 2026-10-19; the publisher states no rate limit, so the per-address figure is this app's own cap\",\"status\":\"PROPOSED\",\"symbols\":[\"BTCUSDT\",\"SOLUSDT\"],\"timestamps\":{\"availability\":\"LOCAL_VALIDATED_AVAILABILITY\",\"publication\":\"pubDate\",\"receipt\":\"LOCAL_RECEIPT\",\"update\":\"NONE\"},\"trigger\":{\"cooldown_seconds\":43200,\"family\":\"SOURCE_REVISION\",\"first_fetch\":\"BASELINE\",\"match\":\"EVERY_ITEM\"},\"typed_filters\":{},\"version\":1}", "19535afdb1507bde396c24e68e0501c9eeee765c67f7bb6707a48dc899c39e7a"]
"""
# Created without SET search_path in 0002 to 0009 and never re-created with one (0009 re-created the workflow guard
# without it). Every one takes no argument.
UNPINNED = ("asl_account_state_guard", "asl_agent_actor_guard", "asl_agent_detail_retention", "asl_agent_epoch_guard",
            "asl_agent_probe_run_guard", "asl_agent_runtime_state_guard", "asl_agent_step_guard", "asl_agent_workflow_guard",
            "asl_check_journal_balance", "asl_definition_guard", "asl_execution_mode_guard", "asl_experiment_event_actor",
            "asl_experiment_guard", "asl_experiment_insert_guard", "asl_immutable", "asl_is_superuser",
            "asl_journal_source_guard", "asl_m6_approval_guard", "asl_m6_candidate_guard", "asl_m6_content_guard",
            "asl_m6_fixture_guard", "asl_m6_transition_guard", "asl_market_retention_delete_guard", "asl_obligation_guard",
            "asl_order_transition_guard", "asl_position_guard", "asl_posting_source_guard")
SEARCH_PATH = "pg_catalog, public, pg_temp"


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def source_rows():
    """The frozen source versions, each checked against its own hash."""
    rows = []
    for line in SOURCE_LINES.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind != "SOURCE_VERSION":
            raise RuntimeError("frozen M9 source version is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


def upgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    for row in source_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id,kind,version,status,definition,canonical,sha256) "
            "VALUES (%(id)s,%(kind)s,%(version)s,%(status)s,CAST(%(document)s AS jsonb),%(canonical)s,%(sha256)s)",
            {**row, "document": row["canonical"]})
    for name in UNPINNED:
        op.execute(f"ALTER FUNCTION {name}() SET search_path = {SEARCH_PATH}")


def downgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    ids = _quoted([row["id"] for row in source_rows()])
    if bind.exec_driver_sql(f"""
        SELECT (SELECT count(*) FROM source_refresh_requests WHERE source_id IN {ids})
             + (SELECT count(*) FROM source_fetches WHERE source_id IN {ids})
             + (SELECT count(*) FROM evidence_items WHERE source_id IN {ids})
             + (SELECT count(*) FROM agent_triggers WHERE detail->>'source_id' IN {ids})
             + (SELECT count(*) FROM agent_approvals WHERE target_kind = 'SOURCE_VERSION' AND target_id IN {ids})
    """).scalar_one():
        raise RuntimeError("M9 feed records exist; downgrade refused; fix forward")
    for name in UNPINNED:
        op.execute(f"ALTER FUNCTION {name}() RESET search_path")
    # The definition store is immutable even for the migration role: relax only this trigger, inside this
    # transaction, and delete only the four frozen rows, which nothing names (checked above).
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in source_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("M9 source version mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
