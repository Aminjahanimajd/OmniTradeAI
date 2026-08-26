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

Use **Connect supported keyless sources** for Yahoo Finance and Polymarket. A
provider is marked ready only after a real request succeeds. FRED and Alpha
Vantage require their own API keys. StockTwits and Reddit are optional public
feeds. Their public endpoints may reject or rate-limit anonymous requests, so
they are never auto-connected. Select either one manually only when you want to
test its live availability. A failed connection is not replaced with fake data.

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
and publish a new version. Only a valid published version can run. New Analysis
automatically uses the latest publication from Workflow Lab, so it does not ask
the user to choose a second workflow.

## Professor demo: show that a graph change affects the output

1. Run AAPL with all four analysts and keep the first report as the baseline.
2. Open **Workflow Lab**.
3. Select the `sentiment analyst` node and press Delete. Delete its connected
   edges too.
4. Select **Validate**. When the graph is valid, select **Publish**.
5. Open **New Analysis**. It now uses the new published version automatically.
6. Keep the same ticker, date, AI models, data providers, risk profile, report
   detail, and budgets. Start the second run.
7. Open **Reports** and compare both reports.

The second report must show a different workflow version and no Sentiment
Analyst point of view. Agent Room must also show a different event path. The
remaining agents and final manager decision now work without sentiment-agent
input. The final Buy/Hold/Sell action may change, but this is not guaranteed.
The clear proof is the changed workflow version, event path, agent list, and
report content.

## Troubleshooting

- Empty model choices: verify an AI connection and configure at least one model ID.
- Missing macro choices: verify FRED or Polymarket.
- StockTwits or Reddit unavailable: these are optional public feeds. No action
  is required; use another verified sentiment source or try manual verification later.
- Provider unavailable: check its key, network access, quota, and rate limit.
- Expired login: sign in again.
- No report yet: open Agent Room and check the failed or running node.

OmniTrade AI is financial decision support only. It never executes a trade.
