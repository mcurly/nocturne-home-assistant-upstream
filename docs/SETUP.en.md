# Guided Home Assistant setup

Open the app's HA web interface for the same installation guidance in all eleven
Nocturne languages. English (`en`) is the default. Choose `auto` explicitly to use
your browser language, or select another language in app Configuration. Upgrades
preserve your existing setting, including `auto`; change it to `en` if desired.
The helper remains available when certificates or startup fail.

For Nocturne tenants, complete the wildcard section below before creating accounts.

1. Choose one permanent domain you control. Existing Nocturne accounts/passkeys depend
   on that hostname. If you already have a trusted matching certificate, reuse your
   existing certificate manager; DuckDNS is optional.
2. For a fresh DuckDNS setup, register a name on duckdns.org, install the HA DuckDNS
   app, and enter the complete domain and token there. Read/accept Let's Encrypt terms
   yourself and enable its certificate option. Use `fullchain.pem` and `privkey.pem`.
   Start DuckDNS and verify successful issuance in its log. Do not copy the token into
   the Nocturne app or issue discussion.
3. In Nocturne Configuration, enter the HTTPS domain plus host port (Stable 8448,
   Main 8449 by default), certificate filename and private key filename. Keep the
   gateway code enabled initially. Save and restart. `/ssl` is read-only to this app.
   You do not need to change Home Assistant Core HTTPS to configure Nocturne.
4. Make the same domain resolve/reach HA from your local devices. Use local split DNS
   or a router with NAT loopback. DuckDNS alone may point at the public address. Test
   a phone on Wi-Fi as well as a computer. DNS-01 validation does not require public
   Nocturne access; HTTP-01 requires public port 80. Do not treat certificate issuance
   as a reason to expose the app.
5. When startup checks succeed, choose Open Nocturne. Check the HTTPS tab has no browser
   certificate warning. For the gateway, use username **`nocturne`** and the access
   code shown through authenticated HA ingress as the password. Both are displayed together,
   then complete Nocturne's own account/passkey setup. Test a second device and restart.

Your certificate manager owns renewal. DuckDNS checks while running. The separate
Let's Encrypt app checks on start and stops; schedule recurring starts if using it.
Use one writer for the certificate pair. The wrapper watches/reloads valid replacement
files, retaining the previous active pair when a new pair is invalid; that does not
extend the previous certificate's expiry.

For `CERT_FILES`, check issuance and both filenames. For `CERT_HOSTNAME`/`CERT_SAN`,
check the exact permanent domain. `CERT_KEY_MISMATCH` requires a matching pair.
`CERT_EXPIRED` means renewal needs attention; `CERT_NOT_YET_VALID` also requires clock
checks. For `SETUP_REQUIRED`, inspect configuration and app logs; do not reset data.
The helper shows the error code and its specific next actions immediately below the
status in **What to do now**. No technical-details expansion is required. Selectable
wildcard YAML snippets are also available directly in the helper.

The server cannot prove your browser's DNS route, certificate trust or passkey ceremony.
Keep these as user checks. Use cold backups before upgrades; an old image does not
reverse a database migration. Stable and Main have independent data. Moving from the
old repository is a separate identity/backup migration, not an in-place package rename.

## Tenant addresses: base domain AND wildcard certificate

For `https://user1.mynocturne.duckdns.org:8448`, the certificate must contain both
`mynocturne.duckdns.org` and `*.mynocturne.duckdns.org` as DNS Subject Alternative
Names (SANs). A certificate for the base name alone does not cover tenants. A wildcard
alone does not cover the base name. The port is not part of a certificate name.

### When DuckDNS manages your certificate

1. Open **Settings → Apps → DuckDNS → Configuration**, then edit as YAML.
2. Keep your existing token and other settings. For a registered DuckDNS name
   `mynocturne.duckdns.org`, replace only the `domains` list with:

   ```yaml
   domains:
     - mynocturne.duckdns.org
     - "*.mynocturne.duckdns.org > mynocturne.duckdns.org"
   ```

   Replace the example name everywhere. The `>` syntax belongs specifically to
   the DuckDNS app, not the separate Let's Encrypt app. It identifies the certificate
   output name; it does not itself add the base name, which is why the first entry matters.
3. Set `lets_encrypt.accept_terms` only after accepting the terms. Keep the existing
   `certfile` and `keyfile` names (normally `fullchain.pem` and `privkey.pem`). Save
   and restart DuckDNS. Wait for its log to confirm successful certificate issuance.
4. Confirm the certificate's SAN list contains **both** names above, then restart
   Nocturne or wait for its certificate reload. Do not delete existing certificate
   files or Nocturne data to force this change. If issuance fails, read the DuckDNS
   log first; restarting Nocturne cannot add names to an old certificate.

This combines the [DuckDNS wildcard syntax](https://github.com/home-assistant/addons/blob/master/duckdns/DOCS.md)
with a base-domain entry. The current app sends those entries to one
[Dehydrated certificate request](https://github.com/home-assistant/addons/blob/master/duckdns/rootfs/etc/s6-overlay/s6-rc.d/duckdns/run).
Actual issuance/renewal on your HA installation remains a pilot acceptance check.

### When the separate Let's Encrypt app manages your certificate

Use DNS validation and request both names. In YAML configuration, the relevant fields
are below; retain your other configuration and replace the example email/token locally:

```yaml
email: your-email@example.com
domains:
  - mynocturne.duckdns.org
  - "*.mynocturne.duckdns.org"
certfile: fullchain.pem
keyfile: privkey.pem
challenge: dns
dns:
  provider: dns-duckdns
  duckdns_token: YOUR_DUCKDNS_TOKEN
```

In the visual editor's **DNS Provider configuration** field, paste only the two
provider/token fields, without the enclosing `dns:` key. HTTP validation cannot issue
wildcards. Start the app, verify issuance, and schedule recurring starts for renewal.
If choosing this manager, disable certificate management in DuckDNS while retaining
its DNS updates. Never let both apps write the same certificate pair.
[Official Let's Encrypt configuration](https://github.com/home-assistant/addons/blob/master/letsencrypt/DOCS.md).

### DNS, Nocturne and verification

Keep Nocturne `public_url` at `https://mynocturne.duckdns.org:8448` (Main: `:8449`),
without `user1` or `*`. Tenant creation is managed in Nocturne, not by HA's certificate
configuration. The wrapper forwards the requested tenant host unchanged. Native mode
(gateway code disabled) accepts the base host and one tenant label; unrelated domains
and deeper labels remain blocked. Nocturne still checks accounts and tenant permissions.

Ensure the base name **and** tenant names resolve to the HA server from every device.
For local split DNS, use a wildcard/suffix rule or explicit entries for each tenant;
an override for the base name alone may not cover `user1`. Test the tenant URL on your
phone as well. A valid wildcard certificate cannot repair a missing DNS/network route.

Open both the base URL and a real tenant URL and inspect their browser certificates:
both must be trusted, without warnings. `*.mynocturne.duckdns.org` covers `user1` but
not `a.b.mynocturne.duckdns.org` or `token.share.mynocturne.duckdns.org`. Features using
those deeper hosts need separate DNS/certificate coverage; they are not included in
this one-level tenant setup. Keep existing account/passkey hostnames unchanged.

## Available Home Assistant diagnostics

| Available | Where to find it |
| --- | --- |
| Guided setup, error-specific next actions, gateway username/code, wildcard YAML | Nocturne app → Web interface |
| Domain, port, certificate files, gateway choice and language | Nocturne app → Configuration |
| Start/stop/restart and current CPU/RAM usage | Nocturne app → Information, while running |
| Startup errors and service messages | Nocturne app → Log |
| CPU/memory sensors, installed and latest version | Home Assistant Supervisor integration → Nocturne Stable or Main device |

Home Assistant provides these diagnostic entities for installed apps; no separate
Nocturne integration, token or statistics app is needed. They are disabled by default:

1. Open **Settings → Devices & services → Home Assistant Supervisor** and choose
   the device for Nocturne Stable or Main. They have separate devices and metrics.
2. Show disabled entities. Alternatively, open the **Entities** tab and filter for
   the Supervisor integration and **Disabled** status.
3. Open **CPU Percent**, then entity settings (gear), and enable it. Repeat for
   **Memory Percent**. Optionally enable **Version** and **Latest version**.
   Labels may differ with your HA language/version.
4. Allow Home Assistant to fetch values, then add the enabled entities to your
   dashboard using **Edit dashboard → Add card**. Select them from the list;
   entity IDs are installation-specific.

CPU and RAM measure the whole container, combining API, web, PostgreSQL and nginx.
There are no separate per-service sensors. This helper explains where to obtain
values; it does not fetch/display live usage. Stopped apps may have unavailable
statistics. These are system diagnostics; this package does not expose glucose or
other medical data as HA entities.
[Official Supervisor sensors](https://www.home-assistant.io/integrations/hassio/).

[Dutch walkthrough](SETUP.nl.md) ·
[DuckDNS app](https://github.com/home-assistant/addons/blob/master/duckdns/DOCS.md) ·
[Separate Let's Encrypt app](https://github.com/home-assistant/addons/blob/master/letsencrypt/DOCS.md) ·
[Certificate challenge methods](https://letsencrypt.org/docs/challenge-types/).
