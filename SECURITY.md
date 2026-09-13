# Security

Please report vulnerabilities privately to the repository owner rather than in
a public issue. Do not include API keys, owner tokens, private reports, runtime
DuckDB files, or request logs in a report.

The public static build has no backend or OpenAI connection. The Python service
is a single-owner local demonstration and should bind only to `127.0.0.1`.
Secrets belong in `backend/.env.local` or a local secret manager; that file is
ignored. Live chat requires an owner token, origin and CSRF checks, an explicit
enable switch, a positive cost budget, and a verified sandbox configuration.

If a secret is committed, revoke it first, then remove it from repository
history. Treat runtime telemetry as private because prompts may contain user
data.
