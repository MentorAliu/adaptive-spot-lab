"""The execution worker and the shared pieces of M3's engine that the spot account keeps (ExecPlan 0060).

``worker`` and ``health`` run the ``execution-worker`` service; ``store`` holds the fenced execution lease, ``numbers``
the exact Decimal policy, ``lifecycle`` the deterministic row identities, ``definitions`` the canonical hash of a frozen
definition and ``risk`` the day's reference NAV. The spot engine itself is ``app.spot``. Paper only: nothing here
contacts an exchange, holds credentials or accepts browser-supplied prices, fills or balances.
"""
