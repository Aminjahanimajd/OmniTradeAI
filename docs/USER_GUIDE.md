# OmniTrade AI user guide

## 0–10: Start

1. Run `docker compose up --build -d` from the project folder.
2. Open `http://localhost:5173`.
3. Sign in with your local OmniTrade account.

## 10–25: Connect an AI provider

1. Open **Connections**.
2. Select an AI provider.
3. Enter its private credential and allowed model IDs.
4. Save the session connection.
5. Select a verification model and choose **Verify now**.

Amazon Bedrock supports a Bedrock bearer token or standard temporary AWS
credentials. A verified connection is required before its models appear in New
Analysis. Secrets are not returned by the API and are not stored in reports.

## 25–35: Connect data

Use **Connect all keyless data sources** for Yahoo Finance, Polymarket, Reddit,
and StockTwits. A provider is marked ready only after a real request succeeds.
FRED and Alpha Vantage require their own API keys. An unavailable provider is
not replaced with fake data.

## 35–45: Set the profile

Open **Profile** and select a default stock. Set the investment horizon,
experience, acceptable loss, maximum position size, and excluded sectors.
These policy values change risk checks and report explanations.

## 45–65: Configure an analysis

Open **New Analysis** and choose the stock, date, analyst branches, provider
chains, quick model, deep model, research depth, risk profile, report detail,
language, currency, and evidence freshness. A choice with only one valid value
is applied automatically instead of being shown as a useless dropdown.

## 65–75: Review safety budgets

Check maximum runtime, model calls, provider calls, tokens, and parallel nodes.
Then select **Start customized real analysis**.

## 75–85: Follow the agents

Agent Room shows evidence collection, each specialist, bull and bear research,
risk views, the manager decision, retries, failures, and completion events.

## 85–95: Read and export

Open **Reports** to read every agent point of view, evidence source, final
decision, warning, and lineage record. Export JSON or PDF when needed.

## 95–100: Advanced workflow editing

Workflow Lab is optional. Edit the graph, use undo when needed, validate it,
and publish a new version. Only a valid published version can run.

## Troubleshooting

- Empty model choices: verify an AI connection and configure at least one model ID.
- Missing macro choices: verify FRED or Polymarket.
- Provider unavailable: check its key, network access, quota, and rate limit.
- Expired login: sign in again.
- No report yet: open Agent Room and check the failed or running node.

OmniTrade AI is financial decision support only. It never executes a trade.
