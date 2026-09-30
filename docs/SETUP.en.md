# Guided Home Assistant setup

Open the app's HA web interface for the same installation guidance in all eleven
Nocturne languages. English (`en`) is the default. Choose `auto` explicitly to use
your browser language, or select another language in app Configuration. Upgrades
preserve your existing setting, including `auto`; change it to `en` if desired.
The helper remains available when certificates or startup fail.

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
   certificate warning. Use the gateway code shown through authenticated HA ingress,
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

The server cannot prove your browser's DNS route, certificate trust or passkey ceremony.
Keep these as user checks. Use cold backups before upgrades; an old image does not
reverse a database migration. Stable and Main have independent data. Moving from the
old repository is a separate identity/backup migration, not an in-place package rename.

[Detailed Dutch walkthrough](SETUP.nl.md) ·
[DuckDNS app](https://github.com/home-assistant/addons/blob/master/duckdns/DOCS.md) ·
[Separate Let's Encrypt app](https://github.com/home-assistant/addons/blob/master/letsencrypt/DOCS.md) ·
[Certificate challenge methods](https://letsencrypt.org/docs/challenge-types/).
