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

## 3. Vul de Nocturne-app in

Open **Configuratie** van de gekozen Nocturne-app. Voor een nieuw voorbeeld:

| Veld | Wat vul je in? |
| --- | --- |
| Publiek adres (`public_url`) | `https://jouw-naam.duckdns.org:8448` voor Stable; `:8449` voor Main |
| Certificaat (`certificate`) | `fullchain.pem` |
| Privésleutel (`private_key`) | `privkey.pem` |
| Extra gatewaycode (`gateway_auth`) | Aan laten tijdens de eerste installatie |
| Taal (`language`) | `auto` voor de browsertaal, of bijvoorbeeld `nl` |

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

Wanneer de gateway om de extra code vraagt, vind je die in de HA-hulppagina. Voltooi
daarna de account- en passkeyaanmaak van Nocturne zelf. Test ook een tweede apparaat en
een herstart. De gatewaycode en Nocturne-aanmelding zijn twee verschillende stappen.

## 6. Vernieuwing en herstel

Laat je gekozen certificaatbeheerder de vernieuwing verzorgen. De DuckDNS-app controleert
dit tijdens het draaien. De aparte **Let's Encrypt**-app werkt anders: die controleert
bij een start en stopt daarna. Plan bij die route regelmatig starten in HA; alleen
installeren is onvoldoende. Laat geen twee beheerders dezelfde bestanden overschrijven.
[Officiële handleiding voor de aparte app](https://github.com/home-assistant/addons/blob/master/letsencrypt/DOCS.md).

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
