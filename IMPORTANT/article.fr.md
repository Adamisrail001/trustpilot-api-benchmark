> **lobstr.io est la meilleure API pour récupérer des avis Trustpilot à grande échelle.** Je lui ai demandé 1 000 avis pour chacune de 5 entreprises, et elle m'a rendu les **5 000, sans doublon et sans erreur**. L'Actor `memo23` d'Apify est la seule autre API à avoir franchi le mur des 200 avis dans mes tests.

## ⚡ Résumé en 15 secondes

1. **Le problème :** Trustpilot bloque les visiteurs anonymes après la page 10 des avis, à 20 avis par page. La plupart des APIs s'arrêtent pile à **200 avis par entreprise** à cause de ça.
2. **Comment j'ai testé :** **5 APIs, 5 entreprises, 200 avis chacune** comme référence (1 000 au total), puis **1 000 par entreprise (5 000 au total)** pour les APIs qui ont passé le mur. Chaque run brut est dans un [dépôt public](https://github.com/Adamisrail001/trustpilot-api-benchmark).
3. **lobstr.io :** **5 000/5 000**, 0 doublon, 100 % de couverture des champs, 35 champs par avis. **2,00 $ pour 1K avis** sur le plan à 20 $, **0,50 $ pour 1K** en volume. Fonctionnement asynchrone, donc compte cinq appels API avant de voir un seul avis.
4. **Apify via `memo23` :** **5 000/5 000**, 0 doublon, **0,63 à 0,66 $ pour 1K** mesurés. Plus rapide que lobstr.io sur un run unique, mais aucun champ au niveau entreprise et aucun filtre.
5. **DataForSEO :** **0,038 $ pour 1K**, de loin le moins cher, mais plafonné dur à **200 avis par entreprise**, impossible de contourner.

![Comparaison des APIs Trustpilot](https://d37gzvgyugjozl.cloudfront.net/main_trustpilot_apis_compariosn_d4baeaefa8.png "width=888;height=544")

Tous les projets de scraping Trustpilot que j'ai vus tombent sur le même mur. Tu demandes tous les avis, tu en reçois exactement 200. Pas d'erreur, pas d'avertissement, juste 200 et un statut `SUCCEEDED`.

L'API officielle est pire, mais autrement : tu ne peux même pas démarrer sans validation sur liste d'attente. Et les APIs tierces qui promettent "tous les avis" ne les livrent pas, la plupart du temps.

![⚡ Résumé en 15 secondes](https://d37gzvgyugjozl.cloudfront.net/newarticle_15_second_summary_72358e86bf.png "width=1876;height=450")

J'ai donc testé les principales APIs d'avis Trustpilot côte à côte, mêmes entreprises, même format de requête, même jour dans la mesure du possible.

Pour que ce soit reproductible, tout est dans un dépôt public, jusqu'aux réponses brutes et aux relevés de crédits.

[Benchmark des APIs de scraping d'avis Trustpilot](https://github.com/Adamisrail001/trustpilot-api-benchmark#cta-link)

Mais d'abord, la question que tout le monde pose... **pourquoi ne pas simplement utiliser l'API officielle de Trustpilot ?**

## Trustpilot a-t-il une API officielle pour les avis ?

Oui. Trustpilot propose plusieurs APIs (**Business Units, Product Reviews, Service Reviews, Data Solutions**), mais la plupart te permettent seulement de lire et de répondre à **tes propres** avis.

👉 [Consulter la documentation de l'API Trustpilot](https://developers.trustpilot.com/)

Pour récupérer les avis **d'autres entreprises**, la seule pertinente est la [Data Solutions API](https://developers.trustpilot.com/data-solutions-get-started). Elle expose les profils d'entreprises et les avis des consommateurs, avec comme endpoints clés **Get Latest Reviews** et **Get Service Reviews**, ce dernier paginant via `nextToken`.

```bash
curl -X GET "https://datasolutions.trustpilot.com/v1/business-units/{businessUnitId}/reviews" \
  -H "apikey: YOUR-API-KEY"
```

Un exemple de réponse tiré de la documentation officielle :

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

Le hic, c'est l'accès. Pas d'inscription, pas de clé API en libre-service.

Tu **t'inscris sur une liste d'attente**, Trustpilot décide si ton cas d'usage mérite une validation, et il n'y a aucun délai annoncé pour cette décision.

![Comment accéder à l'API Trustpilot Data Solutions](https://d37gzvgyugjozl.cloudfront.net/how_to_access_trutpilot_data_solution_api_2843090cbe.png "width=965;height=665")

Sauf si tu es une entreprise ou une association reconnue, tes chances sont minces. Je l'ai donc exclue de la comparaison sur le critère de **l'accessibilité**, pas des capacités.

Si tu veux le détail complet de ce que l'API officielle peut et ne peut pas faire, je l'ai couvert dans le [guide de l'API Trustpilot](https://www.lobstr.io/blog/trustpilot-reviews-api).

## Et l'API interne de Trustpilot ?

Les pages d'avis de Trustpilot récupèrent leurs données depuis un endpoint interne Next.js.

Ouvre les DevTools, va dans l'onglet **Network**, clique sur la page 2 de n'importe quelle liste, et tu verras une requête comme celle-ci pour The Pearl Source :

```text
/_next/data/businessunitprofile-consumersite-2.7799.0/review/www.thepearlsource.com.json?page=2&businessUnit=www.thepearlsource.com
```

![API interne de Trustpilot](https://d37gzvgyugjozl.cloudfront.net/internal_api_image_b367ed18df.png "width=1341;height=598")

La réponse est du JSON propre avec tout ce que la page affiche.

![Réponse de l'API interne de Trustpilot](https://d37gzvgyugjozl.cloudfront.net/internal_api_reponse_fd48f63881.png "width=1071;height=465")

Tentant, mais deux problèmes.

C'est un **endpoint interne non documenté**, donc le numéro de build dans le chemin et la forme de la réponse peuvent changer sans prévenir.

Et elle se heurte au même mur que ton navigateur : **Trustpilot force une connexion après la page 10**, donc l'API interne te donne un JSON plus propre pour exactement les mêmes 200 avis.

![La pagination Trustpilot redirige vers l'inscription](https://d37gzvgyugjozl.cloudfront.net/trutpilot_pagination_hell_fedec6c83e.png "width=1357;height=572")

Utile pour comprendre comment Trustpilot charge ses avis. Pas quelque chose sur quoi je bâtirais un pipeline de production.

Il reste deux options : construire ton propre scraper, ou utiliser une API tierce d'avis Trustpilot.

Construire son propre scraper marche pour le premier scrape. C'est le maintenir face aux changements de pages de Trustpilot, aux mesures anti-bot et à ce mur de connexion qui devient un travail à plein temps.
Pour cet article, j'ai opté pour les APIs tierces.

## Comment j'ai choisi et testé les APIs

J'ai passé en revue la documentation des fournisseurs, les forums de développeurs, les fils Reddit et les issues GitHub pour construire la liste longue, puis je l'ai réduite avec six règles d'élimination :

1. **Pas d'accès en libre-service :** liste d'attente, appel commercial ou pas d'essai
2. **Échec d'exécution :** taux de réussite sous 50 %, ou plante en cours de run
3. **Documentation inutilisable :** impossible de construire une requête fonctionnelle avec la seule documentation
4. **Tarification floue :** impossible de calculer le coût pour 1K avis
5. **Mauvaises données :** ne renvoie pas de données au niveau de l'avis
6. **Mort ou abandonné :** aucune réponse, infrastructure cassée, pas de maintenance

👉 [Voir les critères d'élimination complets](https://github.com/Adamisrail001/trustpilot-api-benchmark/blob/main/IMPORTANT/criteria.md#3-elimination-criteria)

Cinq APIs ont survécu : **lobstr.io, Apify, DataForSEO, Outscraper et OpenWeb Ninja**.

Pour Apify, l'Actor dans cette comparaison est [`memo23/trustpilot-scraper-ppe`](https://apify.com/memo23/trustpilot-scraper-ppe), pas l'Actor Trustpilot le plus populaire du Store, `automation-lab/trustpilot`. J'explique pourquoi dans la section Apify.

![Recherche sur les APIs d'avis Trustpilot](https://d37gzvgyugjozl.cloudfront.net/trustpilot_reviews_api_research_1078b034eb.gif)

### Comment j'ai testé les APIs

Chaque API a eu droit aux mêmes 5 entreprises : **The Pearl Source, SHEIN, Temu, AliExpress et Halara**.

Le run de référence demandait **200 avis par entreprise, 1 000 au total**.

Toute API qui passait la référence sans plafond a ensuite eu droit à un run en profondeur à **1 000 avis par entreprise, 5 000 au total**.

![5 entreprises testées dans la comparaison](https://d37gzvgyugjozl.cloudfront.net/5_business_gif_f2badb6faf.gif)

J'ai jugé chaque API sur six critères :

1. **Fiabilité :** a-t-elle renvoyé ce que je demandais, à chaque fois ?
2. **Qualité des données :** les données étaient-elles exactes et complètes ?
3. **Coût :** combien coûtaient 1K avis ?
4. **Vitesse :** en combien de temps le run se terminait-il ?
5. **Scalabilité :** pouvait-elle récupérer plus de 200 avis d'une seule entreprise ?
6. **Facilité d'utilisation :** combien de travail demande l'intégration ?

Pour la qualité des données, j'ai vérifié à la main un [échantillon de 20 avis de The Pearl Source](https://github.com/Adamisrail001/trustpilot-api-benchmark/blob/main/DATA/ground-truth/thepearlsource-sample.json) sur 13 champs, et je m'en suis servi comme référence pour chaque API.

![Échantillon de référence](https://d37gzvgyugjozl.cloudfront.net/ground_truth_d8a60d8bf4.gif)

Voici comment les cinq se sont classées :

| | lobstr.io | Apify (`memo23`) | DataForSEO | Outscraper | OpenWeb Ninja |
| --- | --- | --- | --- | --- | --- |
| **Avis reçus / demandés** | 5 000/5 000 | 5 000/5 000 | 999/1 000 | 1 000/1 000 | 0/1 000 (limité par rate limit) |
| **Coût pour 1K avis** | 2,00 $ sur le plan à 20 $, 0,50 $ en volume | 0,63 à 0,66 $ mesurés | 0,038 $ mesurés | 2,70 à 3,00 $ estimés | Non calculable |
| **Vitesse** (avis/min) | 272 à 753 en concurrence 1, 1 424 en concurrence 10 | 1 648 sur un run unique de 5 entreprises | 142 à 362 | 117 à 174 | Aucun run terminé |
| **Passe les 200 avis par entreprise ?** | ✅ 1 000 par entreprise confirmé | ✅ 1 000 par entreprise confirmé | ❌ Plafond dur à 200 | ❌ Plafond dur à 200 | Jamais atteint |
| **Qualité des données** (13 champs de référence) | 13/13 | 12/13 | 11/13 | 12/13 | Non mesurable |
| **Entrée** | URLs d'avis, filtres sur le Squid | Tableau `startUrls`, `maxItems` par URL | Un domaine par tâche, 100 tâches par requête | Jusqu'à 1 000 domaines par appel | Nom d'entreprise ou domaine |

## Meilleure API d'avis Trustpilot : lobstr.io

- **Note utilisateurs : 5/5 ([Capterra](https://www.capterra.in/software/1063934/lobstr), 33 avis, au 13 août 2026)**
- **Type d'API : Asynchrone**
- **Idéal pour : récupérer tous les avis d'une entreprise, à grande échelle**

| **Avantages**                                                                                                                    | **Inconvénients**                                                       |
| --------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Passe le mur des 200 avis : 5 000/5 000 dans mon test en profondeur, 0 doublon                                                    | Asynchrone uniquement : Squid → Task → Run → poll → résultats avant de voir un avis |
| 35 champs par avis, le plus grand nombre de toutes les APIs testées                                                               |                                                                         |
| Correspondance parfaite avec la référence, 13/13 champs                                                                           |                                                                         |
| Filtres sur les étoiles, la langue, la vérification, les réponses, les mots-clés, les sujets et la date (`fetch_since`)           |                                                                         |
| [Planification](https://help.lobstr.io/core-concepts/scheduling) intégrée, pas besoin de cron de ton côté                        |                                                                         |
| [Exports](https://help.lobstr.io/data/download-results) en JSON, JSONL, XLSX, CSV                                                 |                                                                         |
| Intégrations directes : [Google Sheets](https://help.lobstr.io/integrations/google-sheets), [S3](https://help.lobstr.io/integrations/amazon-s3), [n8n](https://help.lobstr.io/integrations/n8n), [Make](https://help.lobstr.io/integrations/make), MCP, webhooks, [Claude](https://help.lobstr.io/integrations/claude), [ChatGPT](https://help.lobstr.io/integrations/chatgpt) |                                                                         |
| SDK Python, CLI, MCP de doc et exemples concrets                                                                                  |                                                                         |

### Qu'est-ce que lobstr.io ?

[lobstr.io](https://www.lobstr.io) est une plateforme de scraping cloud sans code avec plus de 50 scrapers prêts à l'emploi, tous accessibles via une API REST. Celui qui nous intéresse ici, c'est le **Trustpilot Reviews Scraper**.

![Trustpilot Reviews Scraper de lobstr.io](https://d37gzvgyugjozl.cloudfront.net/lobstr_io_trutpilot_reviews_store_page_57f2026eab.png "width=1573;height=718")

[Récupérer tous les avis Trustpilot de n'importe quelle entreprise](https://www.lobstr.io/store/trustpilot-reviews-scraper#cta-link)

### Tarification

lobstr.io fonctionne par abonnement mensuel, avec des [plans](https://www.lobstr.io/pricing) de **20 $ à 1 000 $**.

Chaque plan te donne des [crédits](https://help.lobstr.io/core-concepts/credits), et **1 crédit = 1 avis Trustpilot unique**. J'ai vérifié le ratio moi-même : 1 000 crédits, 1 000 avis.

![Plans lobstr.io](https://d37gzvgyugjozl.cloudfront.net/lobstr_io_plans_f5dd963110.png "width=1352;height=597")

**Coût pour 1K avis**

- **2,00 $ pour 1K** sur le plan Starter à 20 $
- **0,50 $ pour 1K** en volume

![Simulateur lobstr.io pour Trustpilot Reviews](https://d37gzvgyugjozl.cloudfront.net/lobstr_io_trustpilot_reviews_simulator_f0589d176e.gif)

### Données

Un objet avis tiré d'un run réel :

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

Ça te donne **35 points de données pertinents par avis** : l'avis lui-même, l'auteur, l'entreprise, le statut de vérification et les métadonnées Trustpilot, le tout dans un seul objet.

Trois de ces champs n'étaient pas disponibles dans toutes les APIs que j'ai testées : **`experience_date`**, **`verification_level`** et le **`trust_score`** de l'entreprise.

**Qualité des données**

- **Couverture des champs :** 13/13 champs de référence
- **Précision :** 20/20 avis correspondants
- **Cohérence du schéma :** 0 champ manquant sur 1 000 avis
- **Fraîcheur :** données en direct. Les seules différences avec la référence portaient sur le nombre d'avis du reviewer et le statut de réponse, qui ont changé sur Trustpilot pendant les 8 jours séparant les deux captures

### Vitesse

Quatre runs, même Squid, concurrence 1 :

| **Run** | **Avis collectés** | **Temps d'exécution** | **Avis/min** |
| --- | --- | --- | --- |
| Run 1 | 1 000/1 000 | 1 min 39 s | 604 |
| Run 2 | 1 000/1 000 | 3 min 41 s | 272 |
| Run 3 | 2 000/2 000 | 5 min 34 s | 359 |
| Run 4 | 5 000/5 000 | 6 min 39 s | 753 |

Ça donne une fourchette de **272 à 753 avis par minute**, avec une moyenne autour de **497**.

La concurrence 1 est le réglage par défaut, pas la limite.

Chaque Squid peut exécuter plusieurs tâches en parallèle, une par [Slot](https://help.lobstr.io/core-concepts/slots), donc j'ai relancé le job à 5 entreprises et 1 000 avis en concurrence 10 pour voir ce que les Slots apportent.

| **Concurrence** | **Avis** | **Temps total** | **Avis/min** | **Latence par requête (médiane / p95)** |
| --- | --- | --- | --- | --- |
| 1 | 1 000/1 000 | 1 min 34 s | 641 | 547 / 1 969 ms |
| 10 | 1 000/1 000 | 42 s | 1 424 | 562 / 2 109 ms |

### Facilité d'utilisation

lobstr.io fonctionne sur un modèle asynchrone : **Squid → Task → Run → Résultats**.

> Un [Squid](https://help.lobstr.io/core-concepts/squids) est l'instance du scraper, les [Tasks](https://help.lobstr.io/core-concepts/tasks) sont les URLs Trustpilot, un [Run](https://help.lobstr.io/core-concepts/runs) les exécute, et tu récupères les résultats en interrogeant l'ID du Run.

L'URL de base est `https://api.lobstr.io/v1` et chaque requête porte `Authorization: Token $LOBSTR_API_KEY`. Un token statique depuis ton [dashboard API](https://app.lobstr.io/dashboard/api) (voici [où le trouver](https://help.lobstr.io/getting-started/api-key)), pas d'OAuth.

![Documentation de l'API lobstr.io](https://d37gzvgyugjozl.cloudfront.net/lobstr_io_doc_65de813a6a.gif "width=1811;height=869")

[Consulter la documentation lobstr.io](https://docs.lobstr.io#cta-link)

Voici le déroulé, avec les requêtes que j'ai réellement lancées.

### 1. Créer ou réutiliser un Squid

Un Squid est une instance de scraper réutilisable, liée à un crawler. La valeur `crawler` est l'ID du Trustpilot Reviews Scraper, récupérable via l'endpoint [list crawlers](https://docs.lobstr.io/docs/list-crawlers).

Crée le Squid une fois, puis réutilise-le pour les prochains runs.

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

Réponse, réduite aux champs qui comptent :

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

L'`id` est ce que toutes les autres requêtes vont référencer. `concurrency` indique combien de tâches le Squid exécute en même temps, et `params` arrive préremplie avec des valeurs par défaut, donc tu ne modifies que ce qui t'intéresse.

### 2. Ajouter des tâches et des réglages

Une tâche est une **URL d'avis Trustpilot**. Les filtres et limites vivent sur le Squid, donc chaque tâche qu'il contient partage la même configuration.

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

Réponse :

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

`duplicated_count` t'indique si une URL de tâche existait déjà sur le Squid, ce qui t'évite les doublons accidentels.

C'est dans les `params` du Squid que se trouve la flexibilité :

```json
"params": {
  "stars": "",                       // Note en étoiles pour filtrer les avis (ex. 1-5)
  "search": "",                      // Mot-clé à rechercher dans le texte des avis Trustpilot
  "topics": "",                      // Sujet/catégorie d'avis Trustpilot à filtrer
  "replies": "",                     // Inclure ou non les réponses de l'entreprise aux avis
  "language": "",                    // Langue pour filtrer les avis
  "verified": "",                    // Inclure uniquement les avis vérifiés ou non
  "start_page": "",                  // Numéro de page à partir duquel récupérer les résultats
  "fetch_since": "",                 // Fenêtre temporelle relative pour récupérer les avis (ex. "4w" = 4 dernières semaines)
  "max_results": "",                 // Nombre maximum de résultats à renvoyer
  "fetch_since_timezone": "",        // Fuseau horaire utilisé pour interpréter la fenêtre fetch_since
  "max_unique_results_per_run": ""   // Plafond de résultats uniques par run du scraper
}
```

`fetch_since` est celui que je te conseille de retenir. Mets-le à `7d` et un run planifié ne récupère que les avis reçus par l'entreprise la semaine passée, ce qui fait du monitoring d'avis en un seul paramètre.

### 3. Lancer le run

```bash
curl --request POST \
  --url "https://api.lobstr.io/v1/runs" \
  --header "Authorization: Token $LOBSTR_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "squid": "0f6ac4ffea6b4b5d89b4093ffc51ef55"
  }'
```

Réponse :

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

L'`id` ici, c'est le **Run ID**. Le polling et les résultats l'utilisent, pas l'ID du Squid, pour que les résultats restent rattachés au run précis.

### 4. Vérifier le statut du run

```bash
curl --request GET \
  --url "https://api.lobstr.io/v1/runs/48d40927b5bf4437b5a9591e7c9bf210" \
  --header "Authorization: Token $LOBSTR_API_KEY"
```

La réponse finale inclut `done_reason: "tasks_done"`, ce qui confirme que le run s'est terminé normalement.

> Si tu préfères éviter le polling, configure plutôt un [webhook](https://docs.lobstr.io/docs/configure-webhook-delivery) sur l'événement `run.done`.

### 5. Récupérer les résultats

```bash
curl --request GET \
  --url "https://api.lobstr.io/v1/results?run=48d40927b5bf4437b5a9591e7c9bf210&page=1&page_size=1000" \
  --header "Authorization: Token $LOBSTR_API_KEY"
```

Réponse :

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

`page_size` contrôle combien d'avis reviennent par page, et chaque élément de `data` est l'objet avis décrit dans la section Données ci-dessus.

![Référence de l'API Trustpilot Reviews](https://d37gzvgyugjozl.cloudfront.net/trustpilot_reviews_api_refrence_d08f7355bc.gif)

Pour la version longue de ce guide, avec les filtres et la configuration de livraison, va voir le [guide de l'API Trustpilot Reviews de lobstr.io](https://www.lobstr.io/blog/trustpilot-reviews-api).

### Verdict

lobstr.io est le bon choix quand **la profondeur des avis compte**. C'est l'une des deux seules APIs à dépasser les 200 avis par entreprise, et la seule à le faire avec une correspondance parfaite à la référence, le schéma le plus large, et un support client entièrement géré.

## Apify via memo23 : l'autre API qui passe les 200

- **Note utilisateurs : 4,8/5 (Capterra, 563 avis, au 26 août 2026), pour la plateforme Apify, pas pour l'Actor**
- **Type d'API : Asynchrone (run d'Actor)**
- **Idéal pour : la collecte en profondeur si tu es déjà sur Apify**

| **Avantages**                                                                | **Inconvénients**                                                                     |
| ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| Égalise la profondeur de lobstr.io : 5 000/5 000 en un seul run, 0 doublon      | Aucun champ au niveau entreprise : pas de Trust Score, de catégorie ni de nombre total d'avis dans la sortie |
| Le run le plus rapide du test : 5 000 avis en 3 min 2 s                        | Aucun filtre sur les étoiles, la langue, la vérification ou les mots-clés               |
| `startUrls` prend toutes tes entreprises en un seul run, `maxItems` s'applique par URL | Documentation spécifique à l'Actor plus légère que le reste de l'écosystème Apify        |
| 12/13 champs de référence, 19/20 avis correspondants                          |                                                                                         |
| Les SDKs, la CLI et le serveur MCP d'Apify s'appliquent tous                    |                                                                                         |

### Qu'est-ce qu'Apify ?

[Apify](https://apify.com/) est une plateforme d'automatisation basée sur des Actors. Tu choisis un Actor préconstruit dans son Store et tu le lances via une API unifiée de run et de dataset.

Cherche "Trustpilot" dans le Store et le résultat le plus populaire est **`automation-lab/trustpilot`**, un Actor communautaire comme tous les autres qu'on y trouve. Ce n'est pas celui de cette comparaison. Dans mes runs, il **plafonnait à exactement 200 avis par entreprise** peu importe ce que je demandais, et l'une des cinq entreprises revenait systématiquement avec **0 avis et un statut `SUCCEEDED`**. Correct pour un échantillon, inutile pour la profondeur.

L'Actor qui livre, c'est [**`memo23/trustpilot-scraper-ppe`**](https://apify.com/memo23/trustpilot-scraper-ppe), un Actor conçu spécifiquement pour dépasser la limite des 200 avis de Trustpilot.

![Actor Apify pour tous les avis Trustpilot](https://d37gzvgyugjozl.cloudfront.net/apify_trustpilot_all_reviews_actor_7e3c043109.png "width=1341;height=594")

Et il tient sa promesse. Il a renvoyé **1 000 avis pour chacune des 5 entreprises, 5 000 au total, 0 doublon**, chaque avis correctement attribué à la bonne entreprise.

### Tarification

Apify fonctionne en **abonnement plus paiement à l'usage**, avec des plans de **19 $/mois** à 999 $/mois.

![Tarifs Apify](https://d37gzvgyugjozl.cloudfront.net/apify_pricing_0a0f847fe2.png "width=1333;height=571")

**Coût pour 1K avis** (`memo23`) :

- **Tarif publié :** à partir de 0,50 $ pour 1K avis
- **Mesuré :** **0,66 $ pour 1K** pour le run unique de 5 000 avis (3,29 $ au total), **0,63 $ pour 1K** en découpant le même job en 5 runs (3,14 $ au total)

### Données

Un objet avis tiré de la réponse en direct :

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

Le détail du reviewer est niché sous `consumer` (et dupliqué à plat dans `reviewerName`, `reviewerCountry`, `reviewerNumberOfReviews`), et `companyReply` porte le texte de la réponse et sa date de publication à chaque fois qu'une entreprise a répondu. `businessUrl` sur chaque élément veut dire que tu peux lancer 5 entreprises dans un seul dataset et quand même attribuer chaque avis sans jointure.

Ce qui manque, c'est le niveau entreprise : pas de Trust Score, pas de catégorie, pas de nombre total d'avis. Si tu en as besoin, il faudra les récupérer ailleurs.

**Qualité des données**

- **Couverture des champs :** 12/13 champs de référence. Le champ manquant est le type d'avis invité vs organique, que `verificationLevel` et `source` te permettent de reconstituer
- **Précision :** 19/20 avis correspondants, avec des correspondances parfaites sur le nom de l'auteur, le pays, la note, le titre, le texte de l'avis et le texte de la réponse

### Vitesse

Deux configurations, mêmes 5 entreprises, 1 000 avis chacune :

| **Configuration** | **Avis collectés** | **Temps d'exécution** | **Coût mesuré** |
| --- | --- | --- | --- |
| Run unique, les 5 entreprises dans `startUrls` | 5 000/5 000 | **3 min 2 s** | 3,29 $ |
| 5 runs séparés, une entreprise chacun | 5 000/5 000 | 9 min 55 s | 3,14 $ |

Le run unique donne environ **1 648 avis par minute**, et il a battu le run à 5 000 avis de lobstr.io (6 min 39 s). La comparaison équitable, c'est face à lobstr.io en concurrence 10, où les deux se retrouvent dans le même ordre de grandeur : `memo23` traite les 5 URLs en parallèle par défaut, lobstr.io le fait quand tu donnes des Slots au Squid.

### Facilité d'utilisation

Le modèle d'Apify, c'est **Actor → Run → Dataset**. Tu lances l'Actor avec un objet d'entrée, tu interroges le run jusqu'à ce qu'il réussisse, puis tu lis le dataset qu'il a écrit.

![Documentation de l'API Apify](https://d37gzvgyugjozl.cloudfront.net/apify_doc_41a5546a9c.gif)

[Consulter la documentation Apify](https://docs.apify.com/api/v2)

L'URL de base est `https://api.apify.com/v2` et chaque requête porte un Bearer token. Pas d'OAuth ici non plus.

### 1. Lancer le run de l'Actor

Une seule requête couvre les 5 entreprises, car `startUrls` accepte un tableau.

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

Réponse :

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

Garde à la fois `id` (le Run ID, pour le polling) et `defaultDatasetId` (là où les résultats atterrissent).

`maxItems` est un **plafond par URL**, pas un pool partagé : 5 URLs à `maxItems: 1000` ont renvoyé exactement 1 000 par entreprise. `filterDateRange` accepte des préréglages de fenêtre temporelle, ou `"all"` pour tout l'historique.

### 2. Vérifier le statut du run

```bash
curl --request GET \
  --url "https://api.apify.com/v2/actor-runs/4B9wLdy2hWaJvjto8" \
  --header "Authorization: Bearer $APIFY_API_TOKEN"
```

Le run passe de `READY` → `RUNNING` → `SUCCEEDED`. Les autres statuts terminaux sont `FAILED`, `ABORTED` et `TIMED-OUT`. Le run à 5 000 avis a passé 142 secondes dans l'Actor ; les 3 min 2 s ci-dessus incluent mon intervalle de polling.

### 3. Récupérer le dataset

```bash
curl --request GET \
  --url "https://api.apify.com/v2/datasets/H7poAv9kK9jiXwCKH/items?format=json&clean=true&offset=0&limit=1000" \
  --header "Authorization: Bearer $APIFY_API_TOKEN"
```

Tu obtiens un tableau JSON plat d'objets avis. La pagination se fait via `offset` et `limit`, et l'en-tête de réponse `X-Apify-Pagination-Total` te donne le total.

La documentation Apify couvre bien les endpoints, l'authentification, les états de run et les datasets. `memo23` fournit des exemples d'API et une spec OpenAPI, mais sa documentation spécifique à l'Actor est plus légère que celle d'Apify elle-même, donc attends-toi à devoir confirmer un ou deux paramètres en le lançant. L'authentification a fonctionné du premier coup, et les **SDKs officiels, la CLI et le serveur MCP** d'Apify fonctionnent tous avec cet Actor.

### Verdict

Si tu es déjà sur Apify, `memo23` t'apporte la même profondeur que lobstr.io, plus vite sur un run unique et à un prix inférieur pour 1K. Tu perds les champs au niveau entreprise et les filtres de lobstr.io.

## DataForSEO : l'API d'avis Trustpilot la moins chère

- **Note utilisateurs : 4,8/5 (Capterra, 15 avis, au 26 août 2026)**
- **Type d'API : Asynchrone (basée sur des tâches)**
- **Idéal pour : la collecte au coût le plus bas quand 200 avis par entreprise suffisent**

| **Avantages**                                                               | **Inconvénients**                                            |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------- |
| **0,038 $ pour 1K avis** mesurés, 50 fois moins cher que le tarif d'entrée de lobstr.io | Plafond dur à **200 avis** par entreprise, pas de pagination au-delà |
| Entrée la plus simple : une chaîne de domaine plus `depth`                     | Un domaine par tâche, pas d'entrée en tableau                 |
| La documentation correspondait au comportement réel, sans surprise            | Manque le type d'avis et le compteur de votes utiles          |
| Serveur MCP officiel                                                          |                                                                |

### Qu'est-ce que DataForSEO ?

[DataForSEO](https://dataforseo.com/apis/reviews-api/trustpilot-reviews-api) vend des données SEO et business via des APIs, dont une dédiée à Trustpilot : la **Trustpilot Reviews API**.

![DataForSEO Trustpilot Reviews](https://d37gzvgyugjozl.cloudfront.net/data_for_seo_trustpilot_reviews_page_78b08c99cf.png "width=1341;height=609")

### Tarification

Paiement à l'usage avec un **financement minimum de compte de 50 $**. Le tarif publié est de **0,00075 $ pour 20 avis**, soit **0,0375 $ pour 1K**. J'ai mesuré **0,038 $ pour 1K** sur les runs réels.

![Tarifs DataForSEO](https://d37gzvgyugjozl.cloudfront.net/dataforseo_pricing_95fdf4ff28.png "width=874;height=575")

### Données

Un objet avis tiré de la réponse en direct :

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

DataForSEO ajoute `rank_absolute` et `rank_group` (la position de l'avis dans la liste) et horodate la réponse du propriétaire dans `responses[].timestamp`. Ça expose aussi `rating.votes_count` et `review_images`, mais les deux étaient nuls sur les 1 000 avis.

**Qualité des données**

- **Couverture des champs :** 11/13 champs de référence, la plus étroite des cinq. Manquants : le type d'avis invité vs organique et le compteur de votes utiles
- **Précision :** 20/20 avis correspondants sur les champs qu'elle renvoie effectivement
- **Cohérence du schéma :** 0 champ manquant sur 1 000 éléments

### Vitesse

| **Run** | **Avis collectés** | **Temps d'exécution** | **Avis/min** |
| --- | --- | --- | --- |
| Run 1 | 1 000 bruts / 999 uniques | 2 min 46 s | 362 |
| Run 2 | 1 000/1 000 | 7 min 1 s | 142 |

Une fourchette de **142 à 362 avis par minute**. Mêmes cinq appels `task_post`/`task_get`, même niveau de priorité les deux fois, donc l'écart vient de la file d'attente de DataForSEO ce jour-là, pas de quelque chose que tu contrôles. Il n'y a pas de réglage de concurrence, et les deux runs sont restés bien en deçà du **pire cas documenté de 45 minutes** pour la priorité standard.

### Facilité d'utilisation

Le modèle de DataForSEO, c'est **`task_post` → `task_get`**. Un appel crée et lance la tâche, un second récupère les résultats une fois prêts.

![Documentation de l'API DataForSEO](https://d37gzvgyugjozl.cloudfront.net/data_for_seo_doc_7c4b2a9b8a.gif)

[Consulter la documentation DataForSEO](https://docs.dataforseo.com/v3/business_data/trustpilot/reviews/)

L'URL de base est `https://api.dataforseo.com/v3/business_data/trustpilot/reviews` et l'authentification se fait en **HTTP Basic** avec ton login et ton mot de passe. Pas de SDK officiel, donc ce sont des appels HTTP bruts.

### 1. Créer la tâche

`task_post` crée et lance le job. Le domaine, la profondeur, le tri et la priorité vont tous dans la même requête.

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

Réponse :

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

`20100` veut dire créée et en file d'attente, pas terminée. Garde l'`id` pour `task_get`.

Les entrées sont `depth` (défaut 20, **max 200**), `sort_by` (`recency` ou `relevance`), `priority` (1 normal, 2 haute), un `tag` optionnel, et `postback_url`/`pingback_url` si tu préfères être notifié plutôt que de faire du polling. Ça se limite au volume et au tri. Aucun filtre sur les étoiles, la vérification ou les mots-clés comme chez lobstr.io.

### 2. Vérifier l'avancement

```bash
curl --request GET \
  --url "https://api.dataforseo.com/v3/business_data/trustpilot/reviews/task_get/07211450-2117-0358-0000-be4f52a532ca" \
  --user "$DATAFORSEO_LOGIN:$DATAFORSEO_PASSWORD"
```

Continue d'appeler `task_get` jusqu'à ce que `tasks[0].result` ne soit plus `null`. DataForSEO propose aussi un endpoint `tasks_ready` qui liste les tâches terminées, pratique si tu en fais tourner plusieurs en même temps.

### 3. Récupérer les résultats

Une fois prête, la même réponse `task_get` porte les avis :

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
          "items": [ /* 200 objets avis */ ]
        }
      ]
    }
  ]
}
```

`reviews_count`, c'est le total de l'entreprise sur Trustpilot (17 558 ici). `items_count`, c'est ce que tu as reçu : **200**. Cet écart résume toute l'histoire de cette API.

Chaque tâche prend un seul domaine, mais tu peux en soumettre jusqu'à **100 dans une seule requête `task_post`**, et DataForSEO fournit un **serveur MCP officiel** pour les workflows Claude, Cursor ou ChatGPT.

### Verdict

DataForSEO est le bon choix quand **le coût et la simplicité** comptent plus que la profondeur. À 0,038 $ pour 1K, c'est de loin l'API la moins chère du lot, et le workflow tient en deux appels. Mais 200 avis par entreprise, c'est un plafond dur, donc c'est un outil d'échantillonnage, pas de collecte.

## Aussi testés : Outscraper et OpenWeb Ninja

Les deux ont fait la liste courte. Aucun des deux n'a fait les recommandations.

### Outscraper

![Outscraper](https://d37gzvgyugjozl.cloudfront.net/newarticle_outscraper_c87652d022.png "width=2400;height=1480")

**Outscraper** était fiable : **1 000/1 000 avis, 0 erreur, 12/13 champs de référence, 20/20 correspondants**, et il accepte jusqu'à **1 000 domaines en un seul appel**, la plus large entrée en lot des cinq.

Sa documentation prévient même des pièges, comme le fait que `skip` doit être un multiple de 20, avant que tu ne tombes dedans.

> Le problème, c'est le prix : **2,70 à 3,00 $ pour 1K avis** (estimé à partir de la grille tarifaire, faute d'endpoint de facturation) pour le même **plafond de 200 avis** que DataForSEO offre à 0,038 $. Tu paies 70 fois plus pour l'entrée en lot.

### OpenWeb Ninja

![OpenWeb Ninja](https://d37gzvgyugjozl.cloudfront.net/newarticle_openweb_ninja_b78e9b48cb.png "width=2410;height=1140")

**OpenWeb Ninja** a la couverture SDK la plus large des cinq (Shell, Ruby, Node.js, PHP, Python) et son premier run a renvoyé 1 000/1 000.

> Un run ultérieur sur le même compte a renvoyé **0/1 000 sur les 5 entreprises, avec 75 erreurs HTTP 429 en environ 37 minutes**.

Une API qui marche une fois puis te limite jusqu'à zéro n'est pas une API que je peux recommander.

## Quelle API d'avis Trustpilot choisir ?

### lobstr.io : tous les avis, de toutes les entreprises

Tu as besoin de tous les avis d'une entreprise, pas seulement des 200 derniers. lobstr.io a renvoyé 5 000/5 000 avec 35 champs par avis et une correspondance parfaite à la référence. 2,00 $ pour 1K sur le plan à 20 $, 0,50 $ pour 1K en volume. [Commence ici](https://www.lobstr.io/store/trustpilot-reviews-scraper#cta-link) si la profondeur est ton critère.

### Apify via memo23 : la profondeur, si tu vis déjà sur Apify

Même résultat de 5 000/5 000, plus rapide sur un run unique, 0,63 à 0,66 $ pour 1K mesurés. Ça vaut le coup si ton pipeline tourne déjà sur des Actors Apify. Pas de quoi adopter Apify juste pour ça.

### DataForSEO : des échantillons pas chers

0,038 $ pour 1K et un workflow en deux appels. Si 200 avis par entreprise te disent ce que tu as besoin de savoir, rien d'autre n'approche ce prix.

Si tu préfères ne pas toucher à une API du tout, le [tour d'horizon des scrapers Trustpilot sans code](https://www.lobstr.io/blog/trustpilot-scrapers) couvre le même terrain pour les fans de dashboard.

## FAQ

### Pourquoi la plupart des APIs Trustpilot s'arrêtent-elles à 200 avis ?

Parce que Trustpilot aussi. Les listes affichent 20 avis par page et l'accès anonyme s'arrête à la page 10, après quoi Trustpilot redirige vers un écran de connexion. Toute API construite sur les pages publiques hérite de cette limite. lobstr.io et `memo23` étaient les deux seules APIs de mon test à la dépasser.

### Est-ce que scraper les avis Trustpilot est légal ?

Il n'y a pas de oui ou de non universel. Les conditions d'utilisation de Trustpilot interdisent le scraping non autorisé, et la légalité dépend de ta juridiction et de ce que tu fais des données. Cet article a testé si les APIs peuvent techniquement récupérer des avis Trustpilot ; savoir si ton usage est autorisé est une question à part. Vérifie les conditions de Trustpilot et le droit applicable avant d'utiliser les données à des fins commerciales, et lis la [série légale sur le scraping](https://www.lobstr.io/blog/category/legal) pour le contexte. Ceci n'est pas un avis juridique.

### L'API Trustpilot est-elle gratuite ?

Non. Pour tes propres avis, les plans business Free, Starter et Plus de Trustpilot n'incluent pas l'accès à l'API ; Premium et Enterprise peuvent ajouter le module API en option payante, avec un prix sur demande. Pour les avis d'autres entreprises, la Data Solutions API est derrière une liste d'attente, sans tarif publié.

### Pourquoi Outscraper n'est-il pas recommandé ?

Le coût. Il a livré 1 000/1 000 sans erreur et avec une excellente documentation, mais à 2,70-3,00 $ pour 1K, c'est l'API la plus chère que j'ai testée, et elle est plafonnée à 200 avis par entreprise comme DataForSEO, qui fait le même travail pour 0,038 $.

### Puis-je reproduire ces résultats ?

Oui. Chaque run, avec les requêtes brutes, les réponses, les timings, les coûts et les rapports d'erreur, se trouve dans le [dépôt de recherche](https://github.com/Adamisrail001/trustpilot-api-benchmark), sous `DATA/` et `SCRIPTS/`. Remplace par tes propres clés API et lance le script du fournisseur que tu veux vérifier, par exemple `SCRIPTS/lobstr/benchmark.py`. Le run lobstr.io à 5 000 avis sur 5 entreprises se trouve sous `DATA/lobstr/five-domain-multi-task-test-2026-09-04/`.

## Conclusion

J'ai testé 5 APIs d'avis Trustpilot dans les mêmes conditions. Deux ont dépassé les 200 avis par entreprise : **lobstr.io et l'Actor `memo23` d'Apify**.

**lobstr.io est ma recommandation** pour une API d'avis Trustpilot. Elle est conçue pour exactement ça, elle a renvoyé chaque avis que j'ai demandé avec le schéma le plus large et une correspondance parfaite à la référence, et elle l'a fait sur un plan à 20 $ sans mauvaise surprise de palier.

Si tu es déjà sur Apify, `memo23` est une alternative légitime. Si 200 avis par entreprise te suffisent, DataForSEO à 0,038 $ pour 1K est le choix évident.

Tu veux vérifier la profondeur toi-même ? [**Essaie la Trustpilot Reviews API**](https://www.lobstr.io/store/trustpilot-reviews-scraper#cta-link).

**Tu as déjà testé l'une de ces APIs ? Quelle a été ton expérience ?** [Retrouve-moi sur LinkedIn](https://www.linkedin.com/in/adamisrail).
