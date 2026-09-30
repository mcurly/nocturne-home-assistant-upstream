# Nocturne installeren zonder technische voorkennis

De HA-app helpt je Nocturne te starten. Een vaste naam, een vertrouwd certificaat en
een werkende route vanaf jouw apparaat moeten daarbij bij elkaar passen. De hulp blijft
in Home Assistant bereikbaar wanneer een certificaat ontbreekt of onjuist is.

## 1. Kies je situatie

Heb je al een domein met een werkend certificaat in Home Assistant? Gebruik die bestaande
certificaatbeheerder en bestanden. DuckDNS is dan niet verplicht. Verander de domeinnaam
van een bestaande Nocturne-account niet zomaar: passkeys horen bij de oorspronkelijke naam.

Begin je opnieuw? Kies een eigen DuckDNS-naam en volg hieronder. Je hoeft Nocturne niet
vanaf internet bereikbaar te maken. Certificaatuitgifte en toegang vanaf internet zijn
twee afzonderlijke keuzes.

## 2. DuckDNS en je certificaat

Open [DuckDNS](https://www.duckdns.org), meld je aan en registreer je gewenste naam.
Installeer vervolgens **DuckDNS** via **Instellingen → Apps** in Home Assistant.
Vul in die app je volledige domeinnaam en token in. Het token hoort uitsluitend bij
DuckDNS; voer het niet in bij Nocturne en deel het niet in een ticket.

Lees de Let's Encrypt-voorwaarden. Als je ermee akkoord gaat, schakel je in DuckDNS
de certificaatoptie in. Gebruik `fullchain.pem` en `privkey.pem` als bestandsnamen.
Start DuckDNS. Controleer in het logboek of het certificaat succesvol is uitgegeven.
Nocturne gebruikt deze bestanden uit `/ssl`, zonder ze te wijzigen.

De actuele velden staan in de [officiële DuckDNS-handleiding](https://github.com/home-assistant/addons/blob/master/duckdns/DOCS.md).
Een eventuele instructie daar om HA Core HTTPS te wijzigen is niet nodig om alleen
Nocturne HTTPS te geven. Behoud de huidige HA-configuratie.

## 2a. Tenantadressen: het basisdomein én een wildcard

Voor `https://user1.mynocturne.duckdns.org:8448` moet het certificaat beide DNS-namen
bevatten: `mynocturne.duckdns.org` én `*.mynocturne.duckdns.org`. Alleen de eerste
dekt geen tenants; alleen de wildcard dekt het basisdomein niet. De poort staat niet
in het certificaat. Dit stel je bij de certificaatbeheerder in, niet door `public_url`
naar een tenant te veranderen.

**Als DuckDNS jouw certificaat beheert:**

1. Open **Instellingen → Apps → DuckDNS → Configuratie → Bewerken als YAML**.
2. Behoud je token en overige instellingen. Gebruik voor jouw geregistreerde naam:

   ```yaml
   domains:
     - mynocturne.duckdns.org
     - "*.mynocturne.duckdns.org > mynocturne.duckdns.org"
   ```

   Vervang de voorbeeldnaam overal. De `>`-notatie hoort specifiek bij DuckDNS en
   bepaalt de uitvoernaam. Voeg het basisdomein dus ook als eerste regel toe.
3. Behoud `fullchain.pem` en `privkey.pem` (of jouw bestaande bestandsnamen).
   Accepteer de voorwaarden zelf voordat je `lets_encrypt.accept_terms` aanzet.
   Sla op, herstart DuckDNS en wacht op succesvolle uitgifte in het logboek.
4. Controleer bij het certificaat de DNS-namen onder **Subject Alternative Name**:
   beide namen moeten aanwezig zijn. Herstart daarna Nocturne of wacht op herladen.
   Een oud certificaat krijgt niet vanzelf een wildcard doordat Nocturne herstart.
   Verwijder geen certificaten of appdata om dit te proberen af te dwingen.

[DuckDNS wildcardnotatie](https://github.com/home-assistant/addons/blob/master/duckdns/DOCS.md).
De actuele app combineert deze regels in één certificaataanvraag. Uitgifte en
vernieuwing op een echte HA-installatie blijven onderdeel van de pilot.

**Als de aparte Let's Encrypt-app jouw certificaat beheert:** gebruik DNS-validatie,
`provider: dns-duckdns` en je token onder `duckdns_token`. Zet onder `domains` de
twee losse namen `mynocturne.duckdns.org` en `"*.mynocturne.duckdns.org"`, zonder `>`.
HTTP-validatie kan geen wildcard uitgeven. De [Engelse handleiding](SETUP.en.md#when-the-separate-lets-encrypt-app-manages-your-certificate)
bevat het volledige YAML-voorbeeld en uitleg voor de visuele editor. Start de app
voor uitgifte en plan regelmatig starten voor vernieuwing. Zet certificaatbeheer
in DuckDNS dan uit; laat DNS-updates aan. Kies één schrijver voor dit bestandspaar.

Dit fragment kun je in de **YAML-configuratie van de aparte Let's Encrypt-app**
plakken. Vervang domein en token en behoud je overige instellingen, waaronder
e-mailadres, `certfile` en `keyfile`:

```yaml
domains:
  - mynocturne.duckdns.org
  - "*.mynocturne.duckdns.org"
challenge: dns
dns:
  provider: dns-duckdns
  duckdns_token: YOUR_DUCKDNS_TOKEN
```

Gebruik je de visuele editor, plak dan in **DNS Provider configuration** alleen
`provider: dns-duckdns` en `duckdns_token: ...`, zonder de regel `dns:`. Zet de
twee domeinnamen in het aparte domeinenveld. De hulppagina toont beide YAML-fragmenten
ook direct, zodat je niet eerst deze handleiding hoeft op te zoeken.

**DNS is een aparte voorwaarde:** basisdomein én tenantnamen moeten naar de HA-server
leiden. Een lokale DNS-regel voor alleen het basisdomein is soms onvoldoende. Gebruik
een wildcard/suffixregel of losse tenantregels en test ook op een telefoon met wifi.
Laat `public_url` op `https://mynocturne.duckdns.org:8448` staan (Main: `:8449`),
zonder `user1` of `*`. Maak de tenant in Nocturne en test beide URLs zonder waarschuwing.

De wildcard dekt één extra niveau, zoals `user1`, niet `a.b` of `token.share`.
Functies met diepere hostnamen vragen aparte certificaat- en DNS-dekking. Native mode
zonder gatewaycode laat na de wrappercorrectie het basisdomein en één tenantniveau
door; vreemde domeinen blijven geblokkeerd. Nocturne controleert de toegang zelf.
Verander bestaande account-/passkeynamen niet zomaar.

## 3. Vul de Nocturne-app in

Open **Configuratie** van de gekozen Nocturne-app. Voor een nieuw voorbeeld:

| Veld | Wat vul je in? |
| --- | --- |
| Publiek adres (`public_url`) | `https://jouw-naam.duckdns.org:8448` voor Stable; `:8449` voor Main |
| Certificaat (`certificate`) | `fullchain.pem` |
| Privésleutel (`private_key`) | `privkey.pem` |
| Extra gatewaycode (`gateway_auth`) | Aan laten tijdens de eerste installatie |
| Taal (`language`) | `en` is standaard; kies `nl` of expliciet `auto` voor de browsertaal |

Vervang de voorbeeldnaam door jouw naam. Heb je een andere hostpoort ingesteld, gebruik
die poort in het adres. Vul alleen de bestandsnamen in: de app koppelt `/ssl` zelf.
Bij een bestaand certificaat behoud je de bestaande namen. Sla op en herstart deze app.

## 4. Laat je vaste naam thuis werken

Je telefoon en computer moeten de gekozen naam kunnen bereiken. DuckDNS houdt een
publieke DNS-verwijzing bij; dat garandeert nog geen werkende route binnen je thuisnetwerk.
Gebruik lokale DNS, zodat de naam naar het lokale HA-adres verwijst, of NAT-loopback als
je router dat ondersteunt. De exacte instelling verschilt per router/DNS-app.

Bij split DNS blijft de naam hetzelfde, maar is het adres thuis lokaal. Verander niet
het domein in Nocturne naar een IP-adres om dit op te lossen. Laat de app jouw hostname,
de certificaatnaam en je browseradres bij elkaar controleren. Test ook op een telefoon
met wifi; een hosts-regel op een computer helpt die telefoon niet.

Voor DNS-01-certificaatvalidatie is geen open Nocturne-poort nodig. HTTP-01 gebruikt
wel publiek bereikbare poort 80. Kies voor de beginnersroute de DNS-methode van je
certificaatbeheerder; maak geen routerwijziging zonder dat die route dat nodig heeft.
[Uitleg van de validatiemethoden](https://letsencrypt.org/docs/challenge-types/).

## 5. Open Nocturne

Open de **Webinterface** in Home Assistant. Zolang iets ontbreekt, lees je hier de
volgende stappen. Als de diensten gereed zijn, verschijnt **Nocturne openen**.
Die knop opent het vaste HTTPS-adres in een apart tabblad.

Je browser mag geen certificaatwaarschuwing tonen. Een servercontrole bewijst niet dat
jouw browser de keten vertrouwt. Controleer datum/tijd en gebruik de volledige keten.
Omzeil de waarschuwing niet als installatieoplossing.

Wanneer de gateway om gebruikersnaam en wachtwoord vraagt, vul je als gebruikersnaam
**`nocturne`** in. Het wachtwoord is de extra toegangscode uit de HA-hulppagina.
Die pagina toont gebruikersnaam en code bij elkaar zodra de app gereed is. Voltooi
daarna de account- en passkeyaanmaak van Nocturne zelf. Test ook een tweede apparaat en
een herstart. De gatewaycode en Nocturne-aanmelding zijn twee verschillende stappen.

## 6. Vernieuwing en herstel

Laat je gekozen certificaatbeheerder de vernieuwing verzorgen. De DuckDNS-app controleert
dit tijdens het draaien. De aparte **Let's Encrypt**-app werkt anders: die controleert
bij een start en stopt daarna. Plan bij die route regelmatig starten in HA; alleen
installeren is onvoldoende. Laat geen twee beheerders dezelfde bestanden overschrijven.
[Officiële handleiding voor de aparte app](https://github.com/home-assistant/addons/blob/master/letsencrypt/DOCS.md).

Bij een fout staat direct onder de statusmelding **Dit kun je nu doen**, met de
foutcode en de bijbehorende handelingen. Je hoeft hiervoor Technische details niet te
openen. De stappen begeleiden je naar Configuratie of het Logboek van de app die
het probleem moet oplossen. De tabel hieronder is ook een naslaglijst.

De Nocturne-wrapper controleert nieuwe certificaatbestanden en herlaadt geldige updates.
Bij een afgewezen nieuw paar blijft de laatste geldige kopie actief zolang die nog geldig
is. Bij een herstart moeten de bronbestanden kloppen. Herstel het paar bij de beheerder,
sla de Nocturne-config op en herstart wanneer de hulp dat vraagt.

| Probleem | Volgende stap |
| --- | --- |
| `CERT_FILES` | Controleer beide bestandsnamen en succesvolle uitgifte in `/ssl` |
| `CERT_HOSTNAME` / `CERT_SAN` | Het certificaat moet exact bij jouw vaste domein passen |
| `CERT_KEY_MISMATCH` | Certificaat en sleutel moeten uit dezelfde uitgifte komen |
| `CERT_EXPIRED` | Controleer vernieuwing bij de certificaatbeheerder |
| `CERT_NOT_YET_VALID` | Controleer de klok en ingangsdatum |
| `SETUP_REQUIRED` | Controleer HA-config en de app-log; data niet wissen |
| Adres opent niet | Controleer domein, lokale DNS, hostpoort en wifi-route |
| Adres opent maar geeft waarschuwing | Controleer naam, keten en vertrouwen op dat apparaat |

Maak een cold backup voor een upgrade. Main kan nieuwe databasemigraties bevatten;
alleen een oud image terugzetten is geen databaseherstel. Stable en Main hebben ieder
eigen data. Lees [de migratiechecklist](ACCEPTANCE.md) voordat je een bestaande account
naar deze nieuwe repository verplaatst.

## 7. Wat krijg je in Home Assistant en waar vind je het?

| Beschikbaar | Waar vind je het? |
| --- | --- |
| Installatiehulp, foutgerichte herstelstappen, gatewaygebruikersnaam/-code en wildcard-YAML | Nocturne-app → **Webinterface** |
| Domein, poort, certificaatbestanden, gatewaykeuze en taal | Nocturne-app → **Configuratie** |
| Starten, stoppen, herstarten en huidig CPU-/RAM-gebruik | Nocturne-app → **Informatie**; bij een draaiende app |
| Startfouten en dienstmeldingen | Nocturne-app → **Logboek** |
| CPU- en geheugensensoren, geïnstalleerde en nieuwste versie | **Home Assistant Supervisor**-integratie → apparaat **Nocturne Stable** of **Nocturne Main** |

Deze sensoren worden door Home Assistant aangeboden voor de geïnstalleerde app;
je hoeft geen losse Nocturne-integratie, extra token of statistiek-app te installeren.
De diagnostische entiteiten zijn standaard uitgeschakeld. Zo maak je ze beschikbaar:

1. Open **Instellingen → Apparaten & diensten → Home Assistant Supervisor**.
2. Open het apparaat van de gewenste Nocturne-app. Stable en Main hebben elk hun
   eigen apparaat en eigen gebruik.
3. Toon ook uitgeschakelde entiteiten. Vind je ze niet op het apparaat, open dan
   **Instellingen → Apparaten & diensten → Entiteiten** en filter op de integratie
   **Home Assistant Supervisor** en status **Uitgeschakeld**.
4. Open **CPU Percent** / **CPU-percentage** en ga naar de entiteitsinstellingen
   (tandwiel). Schakel de entiteit in. Herhaal dit voor **Memory Percent** /
   **Geheugenpercentage**. Desgewenst kun je **Versie** en **Nieuwste versie** ook
   inschakelen. De precieze labels volgen jouw HA-taal en versie.
5. Wacht tot Home Assistant de waarden ophaalt. Voeg de ingeschakelde sensoren via
   **Dashboard bewerken → Kaart toevoegen** aan je dashboard toe. Kies de entiteiten
   uit de lijst; hun IDs kunnen per installatie verschillen.

CPU en geheugen gaan over de **hele Nocturne-container**: API, webapp, PostgreSQL
en nginx samen. Er zijn geen afzonderlijke sensoren voor elk van die diensten.
De hulppagina legt uit waar de waarden staan, maar haalt zelf geen live meetwaarden op.
Een gestopte app kan geen actuele statistieken leveren. Het zijn systeemmetingen;
deze opzet publiceert geen glucosewaarden of andere medische gegevens als HA-entiteiten.

[Officiële Supervisor-sensoren](https://www.home-assistant.io/integrations/hassio/).
