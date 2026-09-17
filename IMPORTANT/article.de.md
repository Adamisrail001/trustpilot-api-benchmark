> **lobstr.io ist die beste Trustpilot-Reviews-API, um im großen Stil Bewertungen zu sammeln.** Ich habe sie nach 1.000 Bewertungen für jedes von 5 Unternehmen gefragt, und sie hat alle **5.000 geliefert, mit 0 Duplikaten und 0 Fehlern**. Apifys `memo23`-Actor war die einzige andere API, die in meinen Tests die 200-Bewertungen-Mauer überwunden hat.

## ⚡ 15-Sekunden-Zusammenfassung

1. **Das Problem:** Trustpilot sperrt anonyme Besucher nach Seite 10 der Bewertungen aus, bei 20 Bewertungen pro Seite. Die meisten APIs bleiben deshalb bei genau **200 Bewertungen pro Unternehmen** hängen.
2. **Wie ich getestet habe:** **5 APIs, 5 Unternehmen, 200 Bewertungen als Basiswert** (1.000 insgesamt), dann **1.000 pro Unternehmen (5.000 insgesamt)** für die APIs, die die Mauer überwunden haben. Jeder rohe Testlauf steckt in einem [öffentlichen Repo](https://github.com/Adamisrail001/trustpilot-api-benchmark).
3. **lobstr.io:** **5.000/5.000**, 0 Duplikate, 100 % Feldabdeckung, 35 Felder pro Bewertung. **2,00 $ pro 1K Bewertungen** im 20-$-Plan, **0,50 $ pro 1K** bei Volumen. Asynchroner Workflow, also rechne mit fünf API-Aufrufen, bevor du eine Bewertung siehst.
4. **Apify über `memo23`:** **5.000/5.000**, 0 Duplikate, **0,63 bis 0,66 $ pro 1K** gemessen. Schneller als lobstr.io bei einem einzelnen Lauf, aber keine Felder auf Unternehmensebene und keine Filter.
5. **DataForSEO:** **0,038 $ pro 1K**, mit Abstand am günstigsten, aber hart gedeckelt bei **200 Bewertungen pro Unternehmen**, ohne Möglichkeit, das zu umgehen.

![Vergleich der Trustpilot-APIs](https://d37gzvgyugjozl.cloudfront.net/main_trustpilot_apis_compariosn_d4baeaefa8.png "width=888;height=544")

Jedes Trustpilot-Scraping-Projekt, das ich gesehen habe, läuft gegen dieselbe Mauer. Du fragst nach allen Bewertungen und bekommst genau 200. Keine Fehlermeldung, keine Warnung, einfach 200 und ein `SUCCEEDED`-Status.

Die offizielle API ist auf andere Weise noch schlimmer: Du kannst nicht mal starten, ohne auf einer Warteliste freigeschaltet zu werden. Und die Drittanbieter-APIs, die "alle Bewertungen" versprechen, liefern das meistens nicht.

![⚡ 15-Sekunden-Zusammenfassung](https://d37gzvgyugjozl.cloudfront.net/newarticle_15_second_summary_72358e86bf.png "width=1876;height=450")

Also habe ich die wichtigsten Trustpilot-Reviews-APIs nebeneinander getestet, gleiche Unternehmen, gleiches Anfrageformat, wo möglich am gleichen Tag.

Damit das nachvollziehbar bleibt, steckt alles in einem öffentlichen Repo, bis hin zu den rohen Antworten und den Credit-Ständen.

[Benchmark der Trustpilot-Review-Scraping-APIs](https://github.com/Adamisrail001/trustpilot-api-benchmark#cta-link)

Aber zuerst die Frage, die alle stellen ... **warum nicht einfach die offizielle Trustpilot-API nutzen?**

## Hat Trustpilot eine offizielle Reviews-API?

Ja. Trustpilot bietet mehrere APIs an (**Business Units, Product Reviews, Service Reviews, Data Solutions**), aber bei den meisten kannst du nur **deine eigenen** Bewertungen lesen und beantworten.

👉 [Trustpilot-API-Dokumentation ansehen](https://developers.trustpilot.com/)

Um Bewertungen **anderer Unternehmen** zu sammeln, ist nur die [Data Solutions API](https://developers.trustpilot.com/data-solutions-get-started) relevant. Sie legt Unternehmensprofile und Kundenbewertungen offen, mit **Get Latest Reviews** und **Get Service Reviews** als wichtigsten Endpunkten, wobei Letzterer über `nextToken` paginiert.

```bash
curl -X GET "https://datasolutions.trustpilot.com/v1/business-units/{businessUnitId}/reviews" \
  -H "apikey: YOUR-API-KEY"
```

Eine Beispielantwort aus der offiziellen Dokumentation:

```json
{
  "reviews": [
    {
      "id": "507f191e810c19729de860ea",
      "stars": 4,
      "title": "Great Service!",
      "text": "I had a wonderful experience.",
      "language": "en",
      "isVerified": true,
      "createdAt": "2023-12-31T12:00:00Z",
      "updatedAt": "2023-12-31T12:00:00Z",
      "experiencedAt": "2023-12-31T12:00:00Z",
      "source": "organic",
      "reviewedLocationName": "Pilestraede 58"
    }
  ],
  "nextToken": "..."
}
```

![Trustpilot Data Solutions API](https://d37gzvgyugjozl.cloudfront.net/data_solution_api_gif_0ac60a40a7.gif)

Der Haken ist der Zugang. Keine Selbstregistrierung, kein API-Key auf Zuruf.

Du **trägst dich auf einer Warteliste ein**, Trustpilot entscheidet, ob dein Use Case eine Freigabe verdient, und dafür gibt es keinen festen Zeitrahmen.

![Zugang zur Trustpilot Data Solutions API](https://d37gzvgyugjozl.cloudfront.net/how_to_access_trutpilot_data_solution_api_2843090cbe.png "width=965;height=665")

Wenn du kein Enterprise-Unternehmen oder eine Non-Profit-Organisation bist, stehen deine Chancen schlecht. Deshalb habe ich sie aus dem Vergleich rausgenommen, wegen der **Zugänglichkeit**, nicht wegen der Fähigkeiten.

Wenn du die komplette Aufschlüsselung willst, was die offizielle API kann und nicht kann, das habe ich im [Trustpilot-API-Guide](https://www.lobstr.io/blog/trustpilot-reviews-api) behandelt.

## Was ist mit Trustpilots interner API?

Trustpilots eigene Bewertungsseiten holen ihre Daten von einem internen Next.js-Endpunkt.

Öffne die DevTools, wechsle zum **Network**-Tab, klick auf Seite 2 einer beliebigen Liste, und du siehst eine Anfrage wie diese hier für The Pearl Source:

```text
/_next/data/businessunitprofile-consumersite-2.7799.0/review/www.thepearlsource.com.json?page=2&businessUnit=www.thepearlsource.com
```

![Trustpilot interne API](https://d37gzvgyugjozl.cloudfront.net/internal_api_image_b367ed18df.png "width=1341;height=598")

Die Antwort ist sauberes JSON mit allem, was die Seite anzeigt.

![Antwort der internen Trustpilot-API](https://d37gzvgyugjozl.cloudfront.net/internal_api_reponse_fd48f63881.png "width=1071;height=465")

Verlockend, aber zwei Probleme.

Es ist ein **undokumentierter interner Endpunkt**, die Build-Nummer im Pfad und die Struktur der Antwort können sich also ohne Vorwarnung ändern.

Und sie stößt auf dieselbe Mauer wie dein Browser: **Trustpilot erzwingt nach Seite 10 einen Login**, die interne API liefert dir also nur eine schönere JSON-Form für dieselben 200 Bewertungen.

![Trustpilot-Pagination leitet zur Anmeldung um](https://d37gzvgyugjozl.cloudfront.net/trutpilot_pagination_hell_fedec6c83e.png "width=1357;height=572")

Gut, um zu verstehen, wie Trustpilot seine Bewertungen lädt. Nichts, worauf ich eine Produktions-Pipeline aufbauen würde.

Bleiben zwei Wege: einen eigenen Scraper bauen oder eine Drittanbieter-API für Trustpilot-Bewertungen nutzen.

Einen eigenen Scraper zu bauen funktioniert für den ersten Durchlauf. Ihn gegen Trustpilots Seitenänderungen, Anti-Bot-Maßnahmen und diese Login-Mauer am Laufen zu halten, wird dann zum Dauerjob.
Für diesen Artikel habe ich mich für Drittanbieter-APIs entschieden.

## Wie ich die APIs ausgewählt und getestet habe

Ich habe mich durch Anbieter-Dokumentationen, Entwicklerforen, Reddit-Threads und GitHub-Issues gearbeitet, um die Longlist aufzubauen, und sie dann mit sechs Ausschlusskriterien reduziert:

1. **Kein Self-Service-Zugang:** Warteliste, Vertriebsgespräch oder keine Testphase
2. **Ausführung schlägt fehl:** Erfolgsquote unter 50 %, oder bricht mitten im Lauf ab
3. **Keine brauchbare Doku:** Aus der Dokumentation allein lässt sich keine funktionierende Anfrage bauen
4. **Unklare Preise:** Kosten pro 1K Bewertungen lassen sich nicht berechnen
5. **Falsche Daten:** liefert keine Daten auf Bewertungsebene
6. **Tot oder verwaist:** keine Reaktion, kaputte Infrastruktur, keine Pflege

👉 [Vollständige Ausschlusskriterien ansehen](https://github.com/Adamisrail001/trustpilot-api-benchmark/blob/main/IMPORTANT/criteria.md#3-elimination-criteria)

Fünf APIs haben es überlebt: **lobstr.io, Apify, DataForSEO, Outscraper und OpenWeb Ninja**.

Bei Apify ist der Actor in diesem Vergleich [`memo23/trustpilot-scraper-ppe`](https://apify.com/memo23/trustpilot-scraper-ppe), nicht der beliebteste Trustpilot-Actor im Store, `automation-lab/trustpilot`. Warum, erkläre ich im Apify-Abschnitt.

![Recherche zu Trustpilot-Reviews-APIs](https://d37gzvgyugjozl.cloudfront.net/trustpilot_reviews_api_research_1078b034eb.gif)

### Wie ich die APIs getestet habe

Jede API bekam dieselben 5 Unternehmen: **The Pearl Source, SHEIN, Temu, AliExpress und Halara**.

Der Basislauf verlangte **200 Bewertungen pro Unternehmen, 1.000 insgesamt**.

Jede API, die den Basislauf ohne Deckelung geschafft hat, bekam danach einen Tiefenlauf mit **1.000 Bewertungen pro Unternehmen, 5.000 insgesamt**.

![5 im Vergleich getestete Unternehmen](https://d37gzvgyugjozl.cloudfront.net/5_business_gif_f2badb6faf.gif)

Ich habe jede API nach sechs Kriterien bewertet:

1. **Zuverlässigkeit:** Hat sie jedes Mal geliefert, was ich angefragt habe?
2. **Datenqualität:** Waren die Daten korrekt und vollständig?
3. **Kosten:** Was kosteten 1K Bewertungen?
4. **Geschwindigkeit:** Wie schnell war der Lauf fertig?
5. **Skalierbarkeit:** Konnte sie mehr als 200 Bewertungen von einem Unternehmen holen?
6. **Benutzerfreundlichkeit:** Wie viel Aufwand ist die Integration?

Für die Datenqualität habe ich eine [Stichprobe von 20 Bewertungen von The Pearl Source](https://github.com/Adamisrail001/trustpilot-api-benchmark/blob/main/DATA/ground-truth/thepearlsource-sample.json) über 13 Felder von Hand geprüft und als Referenzwert für jede API genutzt.

![Referenz-Stichprobe](https://d37gzvgyugjozl.cloudfront.net/ground_truth_d8a60d8bf4.gif)

So haben sich die fünf geschlagen:

| | lobstr.io | Apify (`memo23`) | DataForSEO | Outscraper | OpenWeb Ninja |
| --- | --- | --- | --- | --- | --- |
| **Erhaltene / angefragte Bewertungen** | 5.000/5.000 | 5.000/5.000 | 999/1.000 | 1.000/1.000 | 0/1.000 (Rate-Limit) |
| **Kosten pro 1K Bewertungen** | 2,00 $ im 20-$-Plan, 0,50 $ bei Volumen | 0,63 bis 0,66 $ gemessen | 0,038 $ gemessen | 2,70 bis 3,00 $ geschätzt | Nicht berechenbar |
| **Geschwindigkeit** (Bewertungen/Min) | 272 bis 753 bei Concurrency 1, 1.424 bei Concurrency 10 | 1.648 in einem einzelnen 5-Unternehmen-Lauf | 142 bis 362 | 117 bis 174 | Kein abgeschlossener Lauf |
| **Über 200 Bewertungen pro Unternehmen hinaus?** | ✅ 1.000 pro Unternehmen bestätigt | ✅ 1.000 pro Unternehmen bestätigt | ❌ Harte Grenze bei 200 | ❌ Harte Grenze bei 200 | Nie erreicht |
| **Datenqualität** (13 Referenzfelder) | 13/13 | 12/13 | 11/13 | 12/13 | Nicht messbar |
| **Eingabe** | Bewertungs-URLs, Filter am Squid | `startUrls`-Array, `maxItems` pro URL | Eine Domain pro Task, 100 Tasks pro Anfrage | Bis zu 1.000 Domains pro Aufruf | Firmenname oder Domain |

## Beste Trustpilot-Reviews-API: lobstr.io

- **Nutzerbewertung: 5/5 ([Capterra](https://www.capterra.in/software/1063934/lobstr), 33 Bewertungen, Stand 13. August 2026)**
- **API-Typ: Asynchron**
- **Am besten für: jede Bewertung eines Unternehmens sammeln, in großem Umfang**

| **Vorteile**                                                                                                                     | **Nachteile**                                                          |
| ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Überwindet die 200-Bewertungen-Mauer: 5.000/5.000 in meinem Tiefentest, 0 Duplikate                                             | Nur asynchron: Squid → Task → Run → Polling → Ergebnisse, bevor du eine Bewertung siehst |
| 35 Felder pro Bewertung, die meisten von allen getesteten APIs                                                                  |                                                                          |
| 100 % Übereinstimmung mit der Referenz, 13/13 Felder                                                                            |                                                                          |
| Filter nach Sternen, Sprache, Verifizierung, Antworten, Stichwort, Themen und Datum (`fetch_since`)                             |                                                                          |
| Eingebautes [Scheduling](https://help.lobstr.io/core-concepts/scheduling), kein Cron auf deiner Seite nötig                     |                                                                          |
| [Exporte](https://help.lobstr.io/data/download-results) als JSON, JSONL, XLSX, CSV                                              |                                                                          |
| Direkte Integrationen: [Google Sheets](https://help.lobstr.io/integrations/google-sheets), [S3](https://help.lobstr.io/integrations/amazon-s3), [n8n](https://help.lobstr.io/integrations/n8n), [Make](https://help.lobstr.io/integrations/make), MCP, Webhooks, [Claude](https://help.lobstr.io/integrations/claude), [ChatGPT](https://help.lobstr.io/integrations/chatgpt) |                                                                          |
| Python-SDK, CLI, Doku-MCP und durchgerechnete Beispiele                                                                         |                                                                          |

### Was ist lobstr.io?

[lobstr.io](https://www.lobstr.io) ist eine No-Code-Cloud-Scraping-Plattform mit über 50 fertigen Scrapern, alle über eine REST-API erreichbar. Der, um den es hier geht, ist der **Trustpilot Reviews Scraper**.

![lobstr.io Trustpilot Reviews Scraper](https://d37gzvgyugjozl.cloudfront.net/lobstr_io_trutpilot_reviews_store_page_57f2026eab.png "width=1573;height=718")

[Alle Trustpilot-Bewertungen eines beliebigen Unternehmens abgreifen](https://www.lobstr.io/store/trustpilot-reviews-scraper#cta-link)

### Preise

lobstr.io läuft als monatliches Abo mit [Plänen](https://www.lobstr.io/pricing) von **20 $ bis 1.000 $**.

Jeder Plan gibt dir [Credits](https://help.lobstr.io/core-concepts/credits), und **1 Credit = 1 einzigartige Trustpilot-Bewertung**. Ich habe das Verhältnis selbst geprüft: 1.000 Credits, 1.000 Bewertungen.

![lobstr.io Pläne](https://d37gzvgyugjozl.cloudfront.net/lobstr_io_plans_f5dd963110.png "width=1352;height=597")

**Kosten pro 1K Bewertungen**

- **2,00 $ pro 1K** im 20-$-Starter-Plan
- **0,50 $ pro 1K** bei Volumen

![lobstr.io Trustpilot Reviews Simulator](https://d37gzvgyugjozl.cloudfront.net/lobstr_io_trustpilot_reviews_simulator_f0589d176e.gif)

### Daten

Ein Bewertungsobjekt aus einem echten Lauf:

```json
{
  "id": 11313,
  "object": "result",
  "run": "4c2e07bd3b9b4c9386661edb8ef58174",
  "author_id": "5cf2ae01d0f74610485343de",
  "author_image": null,
  "author_name": "customer",
  "business_unit_id": "4be2ffa600006400050873c2",
  "company_category": "Jewelry Store",
  "company_name": "The Pearl Source",
  "company_page_url": "https://www.trustpilot.com/review/www.thepearlsource.com",
  "consumer_country_code": "GB",
  "consumer_reviews_on_domain": 1,
  "date_published": "2026-07-22T08:44:49Z",
  "experience_date": "2026-07-21T22:00:00Z",
  "functions": null,
  "is_author_verified": false,
  "is_review_verified": true,
  "likes": 0,
  "native_id": 11313,
  "number_of_reviews": 7,
  "owner_reply": "Knowing you're happy with your pearl earrings truly means a lot to us. Thank you for your feedback.",
  "owner_reply_date": "2026-07-23T01:22:26Z",
  "owner_reply_updated_date": null,
  "page_number": 2,
  "rating_value": 5,
  "report": null,
  "review_body": "Very nice and delicate pearl earrings. Looks amazing. I like it.",
  "review_headline": "Very nice and delicate pearl earrings",
  "review_language": "en",
  "review_link": "https://www.trustpilot.com/reviews/6a6083012bbe4c893e5ec3d3",
  "review_sentiment": null,
  "review_source": "InvitationLinkApi",
  "review_url": "6a6083012bbe4c893e5ec3d3",
  "review_verification_source": "self-invited",
  "reviews_count": 17586,
  "scraping_time": "2026-07-29T10:56:25.056Z",
  "stars": 5.0,
  "trust_score": 4.8,
  "updated_date": null,
  "verification_level": "invited"
}
```

Das gibt dir **35 aussagekräftige Datenpunkte pro Bewertung**: die Bewertung selbst, den Bewertenden, das Unternehmen, den Verifizierungsstatus und Trustpilot-Metadaten, alles in einem Objekt.

Drei davon waren nicht in jeder API verfügbar, die ich getestet habe: **`experience_date`**, **`verification_level`** und der **`trust_score`** des Unternehmens.

**Datenqualität**

- **Feldabdeckung:** 13/13 Referenzfelder
- **Genauigkeit:** 20/20 Bewertungen stimmten überein
- **Schema-Konsistenz:** 0 fehlende Felder bei 1.000 Bewertungen
- **Aktualität:** Live-Daten. Die einzigen Unterschiede zur Referenz betrafen die Anzahl der Bewertungen pro Nutzer und den Antwortstatus, die sich in den 8 Tagen zwischen den beiden Erfassungen auf Trustpilot geändert hatten

### Geschwindigkeit

Vier Läufe, gleicher Squid, Concurrency 1:

| **Lauf** | **Gesammelte Bewertungen** | **Laufzeit** | **Bewertungen/Min** |
| --- | --- | --- | --- |
| Lauf 1 | 1.000/1.000 | 1 Min 39 s | 604 |
| Lauf 2 | 1.000/1.000 | 3 Min 41 s | 272 |
| Lauf 3 | 2.000/2.000 | 5 Min 34 s | 359 |
| Lauf 4 | 5.000/5.000 | 6 Min 39 s | 753 |

Das ergibt eine Spanne von **272 bis 753 Bewertungen pro Minute**, im Schnitt etwa **497**.

Concurrency 1 ist die Standardeinstellung, nicht das Limit.

Jeder Squid kann mehrere Tasks parallel ausführen, einen pro [Slot](https://help.lobstr.io/core-concepts/slots), also habe ich den 5-Unternehmen-1.000-Bewertungen-Job bei Concurrency 10 nochmal laufen lassen, um zu sehen, was Slots bringen.

| **Concurrency** | **Bewertungen** | **Gesamtzeit** | **Bewertungen/Min** | **Latenz pro Anfrage (Median / p95)** |
| --- | --- | --- | --- | --- |
| 1 | 1.000/1.000 | 1 Min 34 s | 641 | 547 / 1.969 ms |
| 10 | 1.000/1.000 | 42 s | 1.424 | 562 / 2.109 ms |

### Benutzerfreundlichkeit

lobstr.io läuft nach einem asynchronen Modell: **Squid → Task → Run → Ergebnisse**.

> Ein [Squid](https://help.lobstr.io/core-concepts/squids) ist die Scraper-Instanz, [Tasks](https://help.lobstr.io/core-concepts/tasks) sind die Trustpilot-URLs, ein [Run](https://help.lobstr.io/core-concepts/runs) führt sie aus, und du holst dir die Ergebnisse, indem du die Run-ID abfragst.

Die Basis-URL ist `https://api.lobstr.io/v1`, und jede Anfrage trägt `Authorization: Token $LOBSTR_API_KEY`. Ein statisches Token aus deinem [API-Dashboard](https://app.lobstr.io/dashboard/api) (hier steht, [wo du es findest](https://help.lobstr.io/getting-started/api-key)), kein OAuth.

![lobstr.io API-Dokumentation](https://d37gzvgyugjozl.cloudfront.net/lobstr_io_doc_65de813a6a.gif "width=1811;height=869")

[lobstr.io-Dokumentation ansehen](https://docs.lobstr.io#cta-link)

Hier ist der Ablauf, mit den Anfragen, die ich tatsächlich gestellt habe.

### 1. Squid erstellen oder wiederverwenden

Ein Squid ist eine wiederverwendbare Scraper-Instanz, die an einen Crawler gebunden ist. Der `crawler`-Wert ist die ID des Trustpilot Reviews Scraper aus dem Endpunkt [list crawlers](https://docs.lobstr.io/docs/list-crawlers).

Erstelle den Squid einmal und nutze ihn dann für spätere Läufe wieder.

```bash
curl --request POST \
  --url "https://api.lobstr.io/v1/squids" \
  --header "Authorization: Token $LOBSTR_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "crawler": "b3362ab52c6fab3d8897af79cbba380e",
    "name": "Trustpilot Reviews Job"
  }'
```

Antwort, gekürzt auf die relevanten Felder:

```json
{
  "id": "0f6ac4ffea6b4b5d89b4093ffc51ef55",
  "crawler": "b3362ab52c6fab3d8897af79cbba380e",
  "concurrency": 1,
  "is_active": true,
  "to_complete": false,
  "params": {
    "max_results": null,
    "max_unique_results_per_run": null,
    "stars": "all",
    "language": "All languages",
    "replies": false,
    "verified": false,
    "topics": null,
    "search": null,
    "fetch_since": null,
    "fetch_since_timezone": null,
    "hours_back": null,
    "start_page": 1
  }
}
```

Die `id` ist das, worauf sich jeder spätere Aufruf bezieht. `concurrency` gibt an, wie viele Tasks der Squid gleichzeitig ausführt, und `params` ist mit Standardwerten vorausgefüllt, sodass du nur überschreibst, was dich interessiert.

### 2. Tasks und Einstellungen hinzufügen

Ein Task ist eine **Trustpilot-Bewertungs-URL**. Filter und Limits liegen am Squid, jeder Task darin teilt sich also dieselbe Konfiguration.

```bash
curl --request POST \
  --url "https://api.lobstr.io/v1/tasks" \
  --header "Authorization: Token $LOBSTR_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "squid": "0f6ac4ffea6b4b5d89b4093ffc51ef55",
    "tasks": [
      {
        "url": "https://www.trustpilot.com/review/www.thepearlsource.com"
      }
    ]
  }'
```

Antwort:

```json
{
  "duplicated_count": 0,
  "tasks": [
    {
      "id": "b31de96590d88c602f73bc973570aa76",
      "created_at": "2026-09-04T12:25:56.433371",
      "is_active": true,
      "params": {
        "url": "https://www.trustpilot.com/review/www.thepearlsource.com"
      },
      "module": 217,
      "object": "task"
    }
  ]
}
```

`duplicated_count` sagt dir, ob eine Task-URL schon am Squid hing, was dich vor versehentlichen Doppeleinreichungen bewahrt.

Die Flexibilität steckt in den `params` des Squid:

```json
"params": {
  "stars": "",                       // Sternebewertung zum Filtern der Bewertungen (z. B. 1-5)
  "search": "",                      // Stichwort, nach dem im Bewertungstext gesucht wird
  "topics": "",                      // Trustpilot-Thema/-Kategorie, nach der gefiltert wird
  "replies": "",                     // Ob Antworten des Unternehmens einbezogen werden
  "language": "",                    // Sprache, nach der Bewertungen gefiltert werden
  "verified": "",                    // Ob nur verifizierte Bewertungen einbezogen werden
  "start_page": "",                  // Seitenzahl, ab der Ergebnisse abgerufen werden
  "fetch_since": "",                 // Relatives Zeitfenster für Bewertungen (z. B. "4w" = letzte 4 Wochen)
  "max_results": "",                 // Maximale Anzahl an zurückgegebenen Ergebnissen
  "fetch_since_timezone": "",        // Zeitzone zur Auslegung des fetch_since-Fensters
  "max_unique_results_per_run": ""   // Obergrenze für eindeutige Ergebnisse pro Scraper-Lauf
}
```

`fetch_since` ist das Feld, das ich hervorheben würde. Setz es auf `7d`, und ein geplanter Lauf sammelt nur die Bewertungen der letzten Woche, was Review-Monitoring in einem einzigen Parameter ist.

### 3. Den Lauf starten

```bash
curl --request POST \
  --url "https://api.lobstr.io/v1/runs" \
  --header "Authorization: Token $LOBSTR_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "squid": "0f6ac4ffea6b4b5d89b4093ffc51ef55"
  }'
```

Antwort:

```json
{
  "id": "48d40927b5bf4437b5a9591e7c9bf210",
  "object": "run",
  "squid": "0f6ac4ffea6b4b5d89b4093ffc51ef55",
  "status": "pending",
  "is_done": false,
  "total_results": 0,
  "total_unique_results": 0,
  "credit_used": 0,
  "started_at": "2026-09-04T12:25:56Z",
  "ended_at": null
}
```

Die `id` hier ist die **Run-ID**. Polling und Ergebnisse nutzen sie, nicht die Squid-ID, damit die Ergebnisse an den konkreten Lauf gebunden bleiben.

### 4. Den Run-Status abfragen

```bash
curl --request GET \
  --url "https://api.lobstr.io/v1/runs/48d40927b5bf4437b5a9591e7c9bf210" \
  --header "Authorization: Token $LOBSTR_API_KEY"
```

Die finale Antwort enthält `done_reason: "tasks_done"`, was bestätigt, dass der Lauf normal beendet wurde.

> Wenn du kein Polling machen willst, richte stattdessen einen [Webhook](https://docs.lobstr.io/docs/configure-webhook-delivery) auf das `run.done`-Event ein.

### 5. Ergebnisse abrufen

```bash
curl --request GET \
  --url "https://api.lobstr.io/v1/results?run=48d40927b5bf4437b5a9591e7c9bf210&page=1&page_size=1000" \
  --header "Authorization: Token $LOBSTR_API_KEY"
```

Antwort:

```json
{
  "total_results": 1000,
  "limit": 1000,
  "page": 1,
  "total_pages": 1,
  "result_from": 1,
  "result_to": 1000,
  "next": "https://api.lobstr.io/v1/results?page=2&page_size=1000&run=48d40927b5bf4437b5a9591e7c9bf210",
  "previous": null,
  "data": [
    "1000 review objects"
  ]
}
```

`page_size` bestimmt, wie viele Bewertungen pro Seite zurückkommen, und jedes Element in `data` ist das Bewertungsobjekt aus dem Abschnitt Daten oben.

![Trustpilot Reviews API-Referenz](https://d37gzvgyugjozl.cloudfront.net/trustpilot_reviews_api_refrence_d08f7355bc.gif)

Für die Langversion dieser Anleitung, mit Filtern und Delivery-Setup, schau dir den [lobstr.io Trustpilot Reviews API Guide](https://www.lobstr.io/blog/trustpilot-reviews-api) an.

### Fazit

lobstr.io ist die richtige Wahl, wenn **die Tiefe der Bewertungen zählt**. Es war eine von nur zwei APIs, die über 200 Bewertungen pro Unternehmen hinauskamen, und die einzige, die das mit perfekter Übereinstimmung zur Referenz, dem breitesten Schema und vollständig betreutem Kundensupport geschafft hat.

## Apify über memo23: die andere API, die die 200 knackt

- **Nutzerbewertung: 4,8/5 (Capterra, 563 Bewertungen, Stand 26. August 2026), für die Apify-Plattform, nicht für den Actor**
- **API-Typ: Asynchron (Actor-Lauf)**
- **Am besten für: vollständige Tiefensammlung, wenn du schon auf Apify läufst**

| **Vorteile**                                                                | **Nachteile**                                                                     |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| Erreicht dieselbe Tiefe wie lobstr.io: 5.000/5.000 in einem einzelnen Lauf, 0 Duplikate | Keine Felder auf Unternehmensebene: kein Trust Score, keine Kategorie, keine Gesamtzahl der Bewertungen in der Ausgabe |
| Schnellster Einzellauf im Test: 5.000 Bewertungen in 3 Min 2 s                | Keine Filter nach Sternen, Sprache, Verifizierung oder Stichwörtern                   |
| `startUrls` nimmt alle deine Unternehmen in einem Lauf, `maxItems` gilt pro URL | Dünnere Actor-spezifische Doku als der Rest des Apify-Ökosystems                      |
| 12/13 Referenzfelder, 19/20 Bewertungen stimmten überein                      |                                                                                       |
| Apifys SDKs, CLI und MCP-Server funktionieren alle                            |                                                                                       |

### Was ist Apify?

[Apify](https://apify.com/) ist eine Actor-basierte Automatisierungsplattform. Du wählst einen vorgefertigten Actor aus dem Store und startest ihn über eine einheitliche Run-und-Dataset-API.

Suchst du im Store nach Trustpilot, ist das beliebteste Ergebnis **`automation-lab/trustpilot`**, ein community-gepflegter Actor wie jeder andere dort. Er ist nicht der Actor in diesem Vergleich. In meinen Läufen war er **exakt bei 200 Bewertungen pro Unternehmen gedeckelt**, egal was ich anfragte, und eines der fünf Unternehmen kam jedes Mal mit **0 Bewertungen und Status `SUCCEEDED`** zurück. Für eine Stichprobe okay, für Tiefe unbrauchbar.

Der Actor, der liefert, ist [**`memo23/trustpilot-scraper-ppe`**](https://apify.com/memo23/trustpilot-scraper-ppe), ein Actor, der speziell dafür gebaut wurde, Trustpilots 200-Bewertungen-Limit zu umgehen.

![Apify Trustpilot All Reviews Actor](https://d37gzvgyugjozl.cloudfront.net/apify_trustpilot_all_reviews_actor_7e3c043109.png "width=1341;height=594")

Und das tut er auch. Er lieferte **1.000 Bewertungen von jedem der 5 Unternehmen, 5.000 insgesamt, 0 Duplikate**, jede Bewertung korrekt dem richtigen Unternehmen zugeordnet.

### Preise

Apify läuft nach dem Modell **Abo plus Pay-as-you-go**, mit Plänen von **19 $/Monat** bis 999 $/Monat.

![Apify-Preise](https://d37gzvgyugjozl.cloudfront.net/apify_pricing_0a0f847fe2.png "width=1333;height=571")

**Kosten pro 1K Bewertungen** (`memo23`):

- **Veröffentlichter Preis:** ab 0,50 $ pro 1K Bewertungen
- **Gemessen:** **0,66 $ pro 1K** für den einzelnen 5.000-Bewertungen-Lauf (3,29 $ insgesamt), **0,63 $ pro 1K**, wenn ich denselben Job in 5 Läufe aufgeteilt habe (3,14 $ insgesamt)

### Daten

Ein Bewertungsobjekt aus der Live-Antwort:

```json
{
  "id": "6aa89d332cc378fe839d6ab8",
  "title": "Very quick shipping",
  "text": "Very quick shipping. Pearls came boxed excellent and looked fantastic.",
  "rating": 5,
  "language": "en",
  "source": "InvitationLinkApi",
  "isVerified": true,
  "verificationLevel": "invited",
  "publishedDate": "2026-09-15T03:19:47.000Z",
  "experiencedDate": "2026-09-06T00:00:00.000Z",
  "consumer": {
    "id": "588637d50000ff000a6f7bd9",
    "displayName": "Justme",
    "countryCode": "US",
    "numberOfReviews": 3
  },
  "reviewerName": "Justme",
  "reviewerCountry": "US",
  "reviewerNumberOfReviews": 3,
  "companyReply": {
    "text": "We're glad to hear that you were pleased with both the quick shipping and the presentation of your pearls. Thank you for sharing your feedback with us.",
    "publishedDate": "2026-09-15T19:26:32.000Z"
  },
  "url": "https://www.trustpilot.com/reviews/6aa89d332cc378fe839d6ab8",
  "businessUrl": "https://www.trustpilot.com/review/www.thepearlsource.com",
  "businessName": "The Pearl Source"
}
```

Details zum Bewertenden stecken unter `consumer` (und werden zusätzlich flach als `reviewerName`, `reviewerCountry`, `reviewerNumberOfReviews` dupliziert), und `companyReply` trägt den Antworttext samt Veröffentlichungsdatum, wann immer ein Unternehmen geantwortet hat. `businessUrl` bei jedem Eintrag heißt, dass du 5 Unternehmen in einem Dataset laufen lassen und trotzdem jede Bewertung ohne Join zuordnen kannst.

Was fehlt, ist die Unternehmensebene: kein Trust Score, keine Kategorie, keine Gesamtzahl der Bewertungen. Brauchst du die, musst du sie aus einer anderen Quelle ziehen.

**Datenqualität**

- **Feldabdeckung:** 12/13 Referenzfelder. Das fehlende ist der Typ Eingeladen-vs-Organisch, den du dir aus `verificationLevel` und `source` zusammenbauen kannst
- **Genauigkeit:** 19/20 Bewertungen stimmten überein, mit perfekten Treffern bei Autorenname, Land, Bewertung, Titel, Bewertungstext und Antworttext

### Geschwindigkeit

Zwei Konfigurationen, dieselben 5 Unternehmen, je 1.000 Bewertungen:

| **Konfiguration** | **Gesammelte Bewertungen** | **Laufzeit** | **Gemessene Kosten** |
| --- | --- | --- | --- |
| Einzellauf, alle 5 Unternehmen in `startUrls` | 5.000/5.000 | **3 Min 2 s** | 3,29 $ |
| 5 separate Läufe, je ein Unternehmen | 5.000/5.000 | 9 Min 55 s | 3,14 $ |

Der Einzellauf kommt auf etwa **1.648 Bewertungen pro Minute** und schlug lobstr.ios 5.000-Bewertungen-Lauf (6 Min 39 s). Der faire Vergleich ist der mit lobstr.io bei Concurrency 10, wo beide in derselben Größenordnung landen: `memo23` verarbeitet die 5 URLs standardmäßig parallel, lobstr.io tut das, sobald du dem Squid Slots gibst.

### Benutzerfreundlichkeit

Apifys Modell ist **Actor → Run → Dataset**. Du startest den Actor mit einem Input-Objekt, fragst den Run ab, bis er erfolgreich ist, und liest dann das Dataset, das er geschrieben hat.

![Apify API-Dokumentation](https://d37gzvgyugjozl.cloudfront.net/apify_doc_41a5546a9c.gif)

[Apify-Dokumentation ansehen](https://docs.apify.com/api/v2)

Die Basis-URL ist `https://api.apify.com/v2`, und jede Anfrage trägt einen Bearer-Token. Auch hier kein OAuth.

### 1. Den Actor-Lauf starten

Eine Anfrage deckt alle 5 Unternehmen ab, weil `startUrls` ein Array akzeptiert.

```bash
curl --request POST \
  --url "https://api.apify.com/v2/acts/memo23~trustpilot-scraper-ppe/runs" \
  --header "Authorization: Bearer $APIFY_API_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{
    "startUrls": [
      "https://www.trustpilot.com/review/www.thepearlsource.com",
      "https://www.trustpilot.com/review/www.shein.com",
      "https://www.trustpilot.com/review/temu.com",
      "https://www.trustpilot.com/review/www.aliexpress.com",
      "https://www.trustpilot.com/review/thehalara.com"
    ],
    "maxItems": 1000,
    "filterDateRange": "all"
  }'
```

Antwort:

```json
{
  "data": {
    "id": "4B9wLdy2hWaJvjto8",
    "status": "READY",
    "startedAt": "2026-09-16T07:31:46.656Z",
    "finishedAt": null,
    "defaultDatasetId": "H7poAv9kK9jiXwCKH",
    "usageTotalUsd": 0
  }
}
```

Speichere sowohl `id` (die Run-ID, zum Abfragen) als auch `defaultDatasetId` (wo die Ergebnisse landen).

`maxItems` ist eine **Obergrenze pro URL**, kein gemeinsamer Pool: 5 URLs mit `maxItems: 1000` lieferten exakt 1.000 pro Unternehmen. `filterDateRange` nimmt vorgegebene Zeitfenster, oder `"all"` für die komplette Historie.

### 2. Den Run-Status abfragen

```bash
curl --request GET \
  --url "https://api.apify.com/v2/actor-runs/4B9wLdy2hWaJvjto8" \
  --header "Authorization: Bearer $APIFY_API_TOKEN"
```

Der Run wechselt von `READY` → `RUNNING` → `SUCCEEDED`. Andere Endzustände sind `FAILED`, `ABORTED` und `TIMED-OUT`. Der 5.000-Bewertungen-Lauf brauchte 142 Sekunden im Actor; die 3 Min 2 s oben schließen mein Polling-Intervall mit ein.

### 3. Das Dataset abrufen

```bash
curl --request GET \
  --url "https://api.apify.com/v2/datasets/H7poAv9kK9jiXwCKH/items?format=json&clean=true&offset=0&limit=1000" \
  --header "Authorization: Bearer $APIFY_API_TOKEN"
```

Du bekommst ein flaches JSON-Array von Bewertungsobjekten. Pagination läuft über `offset` und `limit`, und der Response-Header `X-Apify-Pagination-Total` gibt dir die Gesamtzahl.

Die Apify-Doku deckt Endpunkte, Auth, Run-Zustände und Datasets gut ab. `memo23` liefert API-Beispiele und eine OpenAPI-Spec, aber die Actor-spezifische Doku ist dünner als die von Apify selbst, rechne also damit, einen Parameter oder zwei durch Ausprobieren zu bestätigen. Die Authentifizierung hat auf Anhieb funktioniert, und Apifys **offizielle SDKs, CLI und MCP-Server** funktionieren alle mit diesem Actor.

### Fazit

Wenn du schon auf Apify bist, bringt dir `memo23` dieselbe Tiefe wie lobstr.io, schneller bei einem Einzellauf und zu einem niedrigeren Preis pro 1K. Dafür verzichtest du auf Felder auf Unternehmensebene und lobstr.ios Filter.

## DataForSEO: die günstigste Trustpilot-Reviews-API

- **Nutzerbewertung: 4,8/5 (Capterra, 15 Bewertungen, Stand 26. August 2026)**
- **API-Typ: Asynchron (task-basiert)**
- **Am besten für: Sammlung zu geringsten Kosten, wenn 200 Bewertungen pro Unternehmen reichen**

| **Vorteile**                                                                | **Nachteile**                                                    |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| **0,038 $ pro 1K Bewertungen** gemessen, 50-mal günstiger als lobstr.ios Einstiegspreis | Harte **200-Bewertungen-Grenze** pro Unternehmen, keine Pagination darüber hinaus |
| Einfachste Eingabe: ein Domain-String plus `depth`                             | Eine Domain pro Task, keine Array-Eingabe                          |
| Doku entsprach dem tatsächlichen Verhalten, keine Überraschungen               | Fehlt der Bewertungstyp und die Anzahl hilfreicher Stimmen          |
| Offizieller MCP-Server                                                        |                                                                    |

### Was ist DataForSEO?

[DataForSEO](https://dataforseo.com/apis/reviews-api/trustpilot-reviews-api) verkauft SEO- und Business-Daten über APIs, eine davon ist eine dedizierte **Trustpilot Reviews API**.

![DataForSEO Trustpilot Reviews](https://d37gzvgyugjozl.cloudfront.net/data_for_seo_trustpilot_reviews_page_78b08c99cf.png "width=1341;height=609")

### Preise

Pay-as-you-go mit **mindestens 50 $ Kontoaufladung**. Der veröffentlichte Preis liegt bei **0,00075 $ pro 20 Bewertungen**, also **0,0375 $ pro 1K**. Gemessen habe ich **0,038 $ pro 1K** bei den tatsächlichen Läufen.

![DataForSEO-Preise](https://d37gzvgyugjozl.cloudfront.net/dataforseo_pricing_95fdf4ff28.png "width=874;height=575")

### Daten

Ein Bewertungsobjekt aus der Live-Antwort:

```json
{
  "type": "trustpilot_review_search",
  "rank_group": 5,
  "rank_absolute": 5,
  "position": "left",
  "url": "https://www.trustpilot.com/reviews/6a5cbee7d15cfd51e3c65e6b",
  "rating": {
    "rating_type": "Max5",
    "value": 5,
    "votes_count": null,
    "rating_max": 5
  },
  "verified": true,
  "language": "en",
  "timestamp": "2026-07-19 14:11:19 +00:00",
  "title": "Excellent service from ordering to delivery ",
  "review_text": "Superb service delivery from LA USA to UK in less than a week. Brilliant\nThe product is perfect and will make an ideal birthday present to match the pearl neclace I bought in May 2026 for our 30th wedding anniversary.\n\nThank you ",
  "review_images": null,
  "user_profile": {
    "name": "Stephen B",
    "url": "https://www.trustpilot.com/users/5e978a5aa222f44164634d22",
    "image_url": null,
    "location": "GB",
    "reviews_count": 14
  },
  "responses": [
    {
      "title": "Reply from The Pearl Source",
      "text": "Thank you for taking the time to share your experience. We're delighted to hear your order arrived in the UK so quickly and that your new piece is the perfect match for the pearl necklace you purchased for your 30th wedding anniversary. We truly appreciate your continued support.",
      "timestamp": "2026-07-19 22:58:42 +00:00"
    }
  ]
}
```

DataForSEO fügt `rank_absolute` und `rank_group` hinzu (die Position der Bewertung in der Liste) und versieht die Antwort des Unternehmens in `responses[].timestamp` mit einem Zeitstempel. Es legt außerdem `rating.votes_count` und `review_images` offen, beide waren aber bei allen 1.000 Bewertungen null.

**Datenqualität**

- **Feldabdeckung:** 11/13 Referenzfelder, die schmalste der fünf. Fehlend: der Typ Eingeladen-vs-Organisch und die Anzahl hilfreicher Stimmen
- **Genauigkeit:** 20/20 Bewertungen stimmten bei den tatsächlich zurückgegebenen Feldern überein
- **Schema-Konsistenz:** 0 fehlende Felder bei 1.000 Einträgen

### Geschwindigkeit

| **Lauf** | **Gesammelte Bewertungen** | **Laufzeit** | **Bewertungen/Min** |
| --- | --- | --- | --- |
| Lauf 1 | 1.000 roh / 999 eindeutig | 2 Min 46 s | 362 |
| Lauf 2 | 1.000/1.000 | 7 Min 1 s | 142 |

Eine Spanne von **142 bis 362 Bewertungen pro Minute**. Dieselben fünf `task_post`/`task_get`-Aufrufe, dieselbe Prioritätsstufe beide Male, die Lücke liegt also an DataForSEOs Warteschlange an dem Tag, nicht an etwas, das du steuern kannst. Es gibt keine Concurrency-Einstellung, und beide Läufe blieben deutlich innerhalb des dokumentierten **Worst Case von 45 Minuten** für Standardpriorität.

### Benutzerfreundlichkeit

DataForSEOs Modell ist **`task_post` → `task_get`**. Ein Aufruf erstellt und startet den Task, ein zweiter holt die Ergebnisse, sobald sie fertig sind.

![DataForSEO API-Dokumentation](https://d37gzvgyugjozl.cloudfront.net/data_for_seo_doc_7c4b2a9b8a.gif)

[DataForSEO-Dokumentation ansehen](https://docs.dataforseo.com/v3/business_data/trustpilot/reviews/)

Die Basis-URL ist `https://api.dataforseo.com/v3/business_data/trustpilot/reviews`, und die Authentifizierung läuft über **HTTP Basic** mit deinem Login und Passwort. Kein offizielles SDK, es sind also rohe HTTP-Aufrufe.

### 1. Den Task erstellen

`task_post` erstellt und startet den Job. Domain, Tiefe, Sortierung und Priorität gehen alle in dieselbe Anfrage.

```bash
curl --request POST \
  --url "https://api.dataforseo.com/v3/business_data/trustpilot/reviews/task_post" \
  --user "$DATAFORSEO_LOGIN:$DATAFORSEO_PASSWORD" \
  --header "Content-Type: application/json" \
  --data '[
    {
      "domain": "www.thepearlsource.com",
      "depth": 200,
      "sort_by": "recency",
      "priority": 1
    }
  ]'
```

Antwort:

```json
{
  "version": "0.1.20260717",
  "status_code": 20000,
  "status_message": "Ok.",
  "cost": 0.0075,
  "tasks_count": 1,
  "tasks_error": 0,
  "tasks": [
    {
      "id": "07211450-2117-0358-0000-be4f52a532ca",
      "status_code": 20100,
      "status_message": "Task Created.",
      "cost": 0.0075,
      "result_count": 0,
      "result": null
    }
  ]
}
```

`20100` heißt erstellt und in der Warteschlange, nicht fertig. Heb dir die `id` für `task_get` auf.

Eingaben sind `depth` (Standard 20, **maximal 200**), `sort_by` (`recency` oder `relevance`), `priority` (1 normal, 2 hoch), ein optionaler `tag`, und `postback_url`/`pingback_url`, falls dir eine Benachrichtigung lieber ist als Polling. Das deckt nur Umfang und Sortierung ab. Filter nach Sternen, Verifizierung oder Stichwörtern wie bei lobstr.io gibt es nicht.

### 2. Fertigstellung abfragen

```bash
curl --request GET \
  --url "https://api.dataforseo.com/v3/business_data/trustpilot/reviews/task_get/07211450-2117-0358-0000-be4f52a532ca" \
  --user "$DATAFORSEO_LOGIN:$DATAFORSEO_PASSWORD"
```

Ruf `task_get` so lange auf, bis `tasks[0].result` nicht mehr `null` ist. DataForSEO bietet außerdem einen `tasks_ready`-Endpunkt, der fertige Tasks auflistet, praktisch, wenn du mehrere gleichzeitig laufen hast.

### 3. Ergebnisse abrufen

Sobald fertig, trägt dieselbe `task_get`-Antwort die Bewertungen:

```json
{
  "status_code": 20000,
  "status_message": "Ok.",
  "tasks": [
    {
      "id": "07211450-2117-0358-0000-be4f52a532ca",
      "status_code": 20000,
      "status_message": "Ok.",
      "cost": 0,
      "result_count": 1,
      "result": [
        {
          "domain": "www.thepearlsource.com",
          "reviews_count": 17558,
          "rating": {
            "rating_type": "Max5",
            "value": 4.8,
            "votes_count": null,
            "rating_max": 5
          },
          "items_count": 200,
          "items": [ /* 200 Bewertungsobjekte */ ]
        }
      ]
    }
  ]
}
```

`reviews_count` ist die Gesamtzahl des Unternehmens auf Trustpilot (hier 17.558). `items_count` ist das, was du bekommen hast: **200**. Diese Lücke erzählt die ganze Geschichte dieser API.

Jeder Task nimmt eine Domain, aber du kannst bis zu **100 Tasks in einer einzigen `task_post`-Anfrage** einreichen, und DataForSEO liefert einen **offiziellen MCP-Server** für Workflows mit Claude, Cursor oder ChatGPT.

### Fazit

DataForSEO ist die richtige Wahl, wenn **Kosten und Einfachheit** wichtiger sind als Tiefe. Mit 0,038 $ pro 1K ist es die mit Abstand günstigste API hier, und der Workflow besteht aus zwei Aufrufen. Aber 200 Bewertungen pro Unternehmen sind eine harte Grenze, es ist also ein Stichproben-Tool, kein Sammel-Tool.

## Auch getestet: Outscraper und OpenWeb Ninja

Beide haben es auf die Shortlist geschafft. Keiner hat es in die Empfehlungen geschafft.

### Outscraper

![Outscraper](https://d37gzvgyugjozl.cloudfront.net/newarticle_outscraper_c87652d022.png "width=2400;height=1480")

**Outscraper** war zuverlässig: **1.000/1.000 Bewertungen, 0 Fehler, 12/13 Referenzfelder, 20/20 stimmten überein**, und es akzeptiert bis zu **1.000 Domains in einem Aufruf**, die größte Batch-Eingabe der fünf.

Die Doku warnt sogar vor Stolperfallen wie der, dass `skip` ein Vielfaches von 20 sein muss, bevor du reinläufst.

> Das Problem ist der Preis: **2,70 bis 3,00 $ pro 1K Bewertungen** (geschätzt aus der Preisliste, da es keinen Abrechnungs-Endpunkt gibt) für dieselbe **200-Bewertungen-Grenze**, die DataForSEO für 0,038 $ bietet. Du zahlst das 70-Fache für Batch-Eingabe.

### OpenWeb Ninja

![OpenWeb Ninja](https://d37gzvgyugjozl.cloudfront.net/newarticle_openweb_ninja_b78e9b48cb.png "width=2410;height=1140")

**OpenWeb Ninja** hat die breiteste SDK-Abdeckung der fünf (Shell, Ruby, Node.js, PHP, Python), und der erste Lauf lieferte 1.000/1.000.

> Ein späterer Lauf mit demselben Account lieferte **0/1.000 über alle 5 Unternehmen hinweg, mit 75 HTTP-429-Fehlern in etwa 37 Minuten**.

Eine API, die einmal funktioniert und dich dann per Rate-Limit ins Leere laufen lässt, kann ich nicht empfehlen.

## Welche Trustpilot-Reviews-API solltest du wählen?

### lobstr.io: jede Bewertung, jedes Unternehmen

Du brauchst alle Bewertungen eines Unternehmens, nicht nur die letzten 200. lobstr.io lieferte 5.000/5.000 mit 35 Feldern pro Bewertung und perfekter Übereinstimmung zur Referenz. 2,00 $ pro 1K im 20-$-Plan, 0,50 $ pro 1K bei Volumen. [Hier starten](https://www.lobstr.io/store/trustpilot-reviews-scraper#cta-link), wenn Tiefe deine Anforderung ist.

### Apify über memo23: Tiefe, wenn du schon auf Apify lebst

Dasselbe 5.000/5.000-Ergebnis, schneller bei einem Einzellauf, 0,63 bis 0,66 $ pro 1K gemessen. Lohnt sich, wenn deine Pipeline schon auf Apify-Actors läuft. Nicht genug Grund, um extra wegen dessen auf Apify umzusteigen.

### DataForSEO: günstige Stichproben

0,038 $ pro 1K und ein Workflow aus zwei Aufrufen. Wenn dir 200 Bewertungen pro Unternehmen sagen, was du wissen musst, kommt nichts anderes preislich ran.

Wenn du lieber gar keine API anfassen willst, deckt die [No-Code-Trustpilot-Scraper-Übersicht](https://www.lobstr.io/blog/trustpilot-scrapers) dasselbe Terrain für die Dashboard-Fraktion ab.

## FAQ

### Warum hören die meisten Trustpilot-APIs bei 200 Bewertungen auf?

Weil Trustpilot das auch tut. Listen zeigen 20 Bewertungen pro Seite, und der anonyme Zugriff endet bei Seite 10, danach leitet Trustpilot auf einen Login-Bildschirm um. Jede API, die auf den öffentlichen Seiten aufbaut, erbt diese Grenze. lobstr.io und `memo23` waren die einzigen zwei APIs in meinem Test, die darüber hinauskamen.

### Ist es legal, Trustpilot-Bewertungen zu scrapen?

Es gibt kein universelles Ja oder Nein. Trustpilots Nutzungsbedingungen verbieten unautorisiertes Scraping, und die Rechtslage hängt von deiner Jurisdiktion und davon ab, was du mit den Daten machst. Dieser Artikel hat getestet, ob APIs Trustpilot-Bewertungen technisch sammeln können; ob dein Anwendungsfall erlaubt ist, ist eine andere Frage. Prüf Trustpilots Bedingungen und das anwendbare Recht, bevor du die Daten kommerziell nutzt, und lies die [Rechtsreihe zum Thema Scraping](https://www.lobstr.io/blog/category/legal) für den Hintergrund. Das ist keine Rechtsberatung.

### Ist die Trustpilot-API kostenlos?

Nein. Für deine eigenen Bewertungen enthalten Trustpilots Business-Pläne Free, Starter und Plus keinen API-Zugang; Premium und Enterprise können das API-Modul als kostenpflichtige Zusatzoption dazubuchen, Preis auf Anfrage. Für Bewertungen anderer Unternehmen liegt die Data Solutions API hinter einer Warteliste, ohne veröffentlichte Preise.

### Warum wird Outscraper nicht empfohlen?

Wegen der Kosten. Es lieferte 1.000/1.000 ohne Fehler und mit exzellenter Doku, aber bei 2,70 bis 3,00 $ pro 1K ist es die teuerste API, die ich getestet habe, und es ist wie DataForSEO auf 200 Bewertungen pro Unternehmen gedeckelt, das denselben Job für 0,038 $ erledigt.

### Kann ich diese Ergebnisse nachvollziehen?

Ja. Jeder Lauf, mit rohen Anfragen, Antworten, Timings, Kosten und Fehlerberichten, liegt im [Forschungs-Repo](https://github.com/Adamisrail001/trustpilot-api-benchmark) unter `DATA/` und `SCRIPTS/`. Tausch deine eigenen API-Keys ein und lass das Provider-Skript laufen, das du prüfen willst, zum Beispiel `SCRIPTS/lobstr/benchmark.py`. Der 5.000-Bewertungen-Lauf über 5 Unternehmen mit lobstr.io liegt unter `DATA/lobstr/five-domain-multi-task-test-2026-09-04/`.

## Fazit

Ich habe 5 Trustpilot-Reviews-APIs unter denselben Bedingungen getestet. Zwei kamen über 200 Bewertungen pro Unternehmen hinaus: **lobstr.io und Apifys `memo23`-Actor**.

**lobstr.io ist meine Empfehlung** für eine Trustpilot-Reviews-API. Sie ist genau dafür gebaut, sie lieferte jede Bewertung, um die ich gebeten habe, mit dem breitesten Schema und perfekter Übereinstimmung zur Referenz, und das auf einem 20-$-Plan ohne böse Überraschungen bei den Stufen.

Bist du schon auf Apify, ist `memo23` eine legitime Alternative. Reichen dir 200 Bewertungen pro Unternehmen, ist DataForSEO mit 0,038 $ pro 1K die naheliegende Wahl.

Willst du die Tiefe selbst prüfen? [**Probier die Trustpilot Reviews API aus**](https://www.lobstr.io/store/trustpilot-reviews-scraper#cta-link).

**Hast du schon eine dieser APIs getestet? Wie waren deine Erfahrungen?** [Vernetz dich mit mir auf LinkedIn](https://www.linkedin.com/in/adamisrail).
