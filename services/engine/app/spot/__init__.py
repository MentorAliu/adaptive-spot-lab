"""The main account's spot trading on paper (ExecPlan 0060, M12): BTCUSDT, long or cash, decided by the code rule
``SPOT_RULE_V1`` once a UTC day, with the account's protections and the owner's controls.

``definitions`` holds the code-owned rule, policy and cost; ``rule`` the daily reading; ``money`` every amount;
``ledger`` the only writer of the account's journal; ``store`` the reads and writes; ``engine`` the fenced step and
``worker`` its loop; ``backtest`` the app's own backtest of the rule; ``views``, ``requests`` and ``live`` serve the
API.
"""
