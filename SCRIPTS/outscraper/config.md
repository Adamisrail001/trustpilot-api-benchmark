# Outscraper Trustpilot Benchmark

Tool: Outscraper
Endpoint: GET /trustpilot-reviews
Benchmark target: 1,000 unique reviews
Dataset: 5 fixed Trustpilot domains
Target per domain: 200 reviews
Sort order: recency
Languages: all
Mode: async
Output formats: JSON and CSV

## Success Definition

A successful review must:

- contain a unique review ID
- contain a rating
- contain a review date
- contain review title or text
- contain reviewer information
- not be an empty or error object

## Required Metrics

- total requested
- total raw returned
- total valid
- total unique
- duplicates
- empty responses
- partial responses
- failed requests
- retries
- median latency
- p95 latency
- wall-clock time
- total usage
- total measured cost
- cost per 1,000 successful reviews