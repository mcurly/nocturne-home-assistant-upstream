# Nocturne for Home Assistant — upstream proposal

[![Toevoegen aan Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fsmokkelaar%2Fnocturne-home-assistant-upstream%23home-assistant)

[![Wrapper checks](https://github.com/smokkelaar/nocturne-home-assistant-upstream/actions/workflows/ha-validate.yml/badge.svg)](https://github.com/smokkelaar/nocturne-home-assistant-upstream/actions/workflows/ha-validate.yml)
[![Publish Stable and Main](https://github.com/smokkelaar/nocturne-home-assistant-upstream/actions/workflows/ha-publish.yml/badge.svg)](https://github.com/smokkelaar/nocturne-home-assistant-upstream/actions/workflows/ha-publish.yml)

Stable and Main, prebuilt in GitHub Actions, with a multilingual setup assistant.
This clean repository contains the complete existing HA runtime, redesigned help,
and a publication pipeline. Personal extensions and legacy test channels are excluded.
The runtime derives from smokkelaar/nocturne-home-assistant at
`8ad3595da10fd109411e3e1cb58a5d8fc8816ea8`, under AGPL-3.0-only.

**Pilot, not yet an accepted Nightscout distribution.** Images become installable only
after container tests and anonymous registry verification pass. A build failure keeps
the previously published store version. Real HAOS upgrades and passkey/browser checks
remain part of the user test plan.

## Install

Use **Toevoegen aan Home Assistant** above to add the tested pilot repository, or add:

```
https://github.com/smokkelaar/nocturne-home-assistant-upstream#home-assistant
```

The `home-assistant` branch contains only generated store metadata. `main` contains
the maintained source. This separation is deliberate: Supervisor discovers configs
recursively, including unrelated `config.json` files in a large application repository.

Choose **Nocturne Stable** or **Nocturne Main**, start the app, then open its HA web
interface. It guides you through the domain, DuckDNS / Let's Encrypt, certificate files,
local DNS and Nocturne sign-in. Certificate/setup errors keep the help interface running.
Configure the app in Home Assistant and restart after saving. Certificates in `/ssl`
are read-only; the assistant does not change your router or Home Assistant Core HTTPS.

- [Uitgebreide Nederlandse installatiehulp](docs/SETUP.nl.md)
- [English setup guide](docs/SETUP.en.md)
- [Exact upstream integration plan](docs/UPSTREAM-INTEGRATION.md)
- [Architecture and automatic publication](docs/ARCHITECTURE.md)
- [Acceptance and migration checklist](docs/ACCEPTANCE.md)
- [Issue discussion and rationale](https://github.com/smokkelaar/nocturne-home-assistant/issues/41)

## Development

Python 3.12+, Node 24, OpenSSL; Docker Linux for runtime tests.

```sh
python -m unittest discover -s deploy/home-assistant/tests -v
python deploy/home-assistant/tools/check_locales.py --upstream
python deploy/home-assistant/tools/preview.py
```

Open `http://127.0.0.1:8765/?lang=nl` for a synthetic setup preview. It has no access
to HA, credentials or medical data. Stop the preview with Ctrl+C.

Edit messages in `deploy/home-assistant/shared/rootfs/opt/nocturne-ha/locales/*.json`.
All eleven Nocturne languages have the same message keys. Browser language, explicit
language selection and HA's `language` setting are supported. Translations are initial
drafts and should receive native-speaker review before upstream acceptance.

AMD64 is the first published target. Change `deploy/home-assistant/platforms.json`
to `["amd64", "arm64"]` to run the complete native build/test pipeline for both.
No ARM64 app is advertised until all requested platform jobs pass. HA calls ARM64
`aarch64`; the generator maps that to Docker's `linux/arm64`.

The first GHCR packages may default to private. Make the two package visibilities public;
the promote job refuses to advertise images that cannot be pulled anonymously. A rerun
gets a fresh package version. Subsequent successful publications are automatic.

Original wrapper copyright and license notices are preserved in [LICENSE](LICENSE).
Upstream Nocturne and dependencies retain their own licenses. See
[distribution provenance](docs/ARCHITECTURE.md#source-and-licenses).
