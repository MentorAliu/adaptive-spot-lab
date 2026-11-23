# Security

## Reporting a problem

Please report security problems privately, not in a public issue: on GitHub, open the repository's **Security** tab and press **Report a vulnerability**. Say what you found, how to reproduce it, and what it lets someone do.

Only the latest `main` is supported. There are no separate releases to patch.

## What the app protects

Adaptive Spot Lab trades on paper only. It holds no exchange account, no API key of any outside service and no real money, so the worst a flaw can do is damage the copy's own records or the computer it runs on. The design keeps both safe:

- **No way to trade for real.** The app has no exchange credentials, signs no exchange request and has no live switch. The market worker talks only to Binance's public market-data hosts (`data-api.binance.vision` and `data-stream.binance.vision`), on fixed unauthenticated paths, and refuses redirects and private addresses.
- **This computer only.** The web app listens on `127.0.0.1:3000`, refuses a `Host` header outside its allowlist (against DNS rebinding) and refuses cross-site requests. The API and PostgreSQL are on a private Docker network with no published port. There is no sign-in, so whoever can use the computer acts as the owner: don't publish the app to your network or the internet.
- **The money stays in code.** Only the engine posts to the ledger, with exact decimals, in one database transaction per step, under a fenced lease so that two workers can never trade at once. Each service connects as its own PostgreSQL role with only the grants it needs; the browser and the API can't set a balance.
- **Secrets stay out of Git and images.** Database passwords and the internal service key are files under `secrets/`, created with random bytes on first setup, given to each container as Docker secrets, and ignored by Git and Docker builds.
- **Locked-down containers.** No Docker socket, no privileged mode and no host folder mounts in the running services; the workers run as non-root with a read-only root filesystem and CPU, memory and process limits.

[docs/SECURITY.md](docs/SECURITY.md) has the full threat model and controls.

## Keeping your copy safe

- Keep the `secrets/` folder private and back it up with the database: the app's roles log in with those passwords.
- Don't change `WEB_PORT`'s binding to listen beyond `127.0.0.1`.
- Keep the copy up to date with `update-app.cmd` (see the README).
