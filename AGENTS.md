# Repository maintenance rules

- Published HA package versions MUST be plain `MAJOR.MINOR.PATCH`, without
  prerelease, build metadata, leading zeroes or a hyphenated build counter.
- Generate versions through `deploy/home-assistant/tools/versions.py`. Never
  hand-edit the generated store branch or reuse/overwrite a published image tag.
- Before building AND before promoting, require the candidate to be strictly
  newer than each affected channel's published config using Home Assistant's
  AwesomeVersion comparator. Fail closed on unreadable or unrecognized metadata.
- Retain regression tests for upgrades from `0.2.0-201` and `0.2.0-401`, equal
  versions, downgrades, workflow retries and counter resets. Run the complete
  tests with `requirements-ci.txt` installed before publishing changes.
- Upstream Nocturne version, source SHA and HA package version are separate.
- English (`en`) is the default setup language. Browser detection is opt-in
  through `auto`; preserve explicit user language settings during upgrades.
- Keep all eleven locale catalogs complete. Default documentation links use
  the English guide; other languages remain selectable.
- Tenant names are created dynamically. Never maintain a per-user host allowlist:
  accept the base domain and any valid single tenant label under that fixed domain.
  Keep unrelated/lookalike domains and deeper labels blocked. Preserve Nocturne's
  authentication, tenant checks and untrusted forwarded-header protections.
- Document base plus wildcard SANs and wildcard DNS together. Certificate coverage
  and DNS must work for future tenants, not just the first test account.

- Keep `skip_gateway_check` default false. Honor explicit opt-in only with gateway
  disabled, display the bypass, and preserve Nocturne permissions and TLS/host checks.
- Never interpolate installation domains or secrets into copyable examples. Use
  `mynocturne.duckdns.org`; retain regression coverage for generic examples.
