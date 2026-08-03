# DataForSEO Trustpilot Benchmark

Target platform: Trustpilot
Benchmark strategy: 5 business domains × 200 reviews
Target records: 1,000 unique reviews
Sort order: Most recent
Language: English
Priority: Standard
Output formats: JSON and CSV
Domain configuration: benchmark-domains.json

## Ground-Truth Sample

Available ground-truth file:

- ground-truth/thepearlsource-sample.json

Ground-truth accuracy testing will be performed for The Pearl Source.

Accuracy for other domains will remain Pending unless separate manually
verified ground-truth samples are provided.

## Successful Review Definition

A successful review must:

- contain a unique review identifier
- contain a rating
- contain a review date
- contain review text
- contain reviewer information
- belong to the requested business domain
- not be a duplicate
- not be an empty or error object

## Required Measurements

- total requested records
- total returned records
- successful unique records
- records returned per domain
- failed requests
- empty responses
- partial responses
- duplicate reviews
- missing fields
- median latency
- p95 latency
- total wall-clock time
- task cost
- total benchmark cost
- cost per 1,000 successful records
- rate-limit responses
- retries

## Benchmark Completion Rule

The benchmark is complete only when:

- five different business domains are tested
- each domain is requested once with depth 200
- 1,000 valid and unique reviews are returned in total
- duplicate reviews are excluded
- missing or partial records are reported
- no identical paid task is repeated unnecessarily

If fewer than 1,000 unique reviews are returned, the benchmark must be
reported as partially completed with the exact shortfall and reason.