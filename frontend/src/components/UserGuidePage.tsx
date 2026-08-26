import { Alert, Box, Card, CardContent, Chip, Grid, Stack, Typography } from '@mui/material';

const topics = [
  ['0–10', 'Start the website', 'Run Docker Compose, open http://localhost:5173, and sign in with your local account.'],
  ['10–25', 'Connect AI', 'Open Connections. Select an AI provider, enter its private credential, add allowed model IDs, save, and verify.'],
  ['25–35', 'Connect data', 'In Connections, use “Connect supported keyless sources”. Add and verify FRED or Alpha Vantage keys when available. StockTwits and Reddit are optional manual connections.'],
  ['35–45', 'Set your profile', 'Choose a default stock, horizon, experience, loss limit, position limit, and excluded sectors. Save the profile.'],
  ['45–65', 'Create an analysis', 'Open New Analysis. Choose the stock, date, analyst branches, provider chains, quick model, deep model, risk level, and report detail.'],
  ['65–75', 'Check safety limits', 'Review runtime, model-call, provider-call, token, and parallel-node budgets. Then start the analysis.'],
  ['75–85', 'Watch agents work', 'Agent Room shows each node, analyst output, debate, risk view, failure, retry, and final report event.'],
  ['85–95', 'Read the report', 'Reports shows the analyst points of view, bull and bear debate, risk views, evidence sources, decision, and warnings.'],
  ['95–100', 'Review or customize', 'Export PDF or JSON. Advanced users can edit Workflow Lab, validate the graph, publish a new version, and run it.'],
];

export default function UserGuidePage() {
  return <Stack spacing={2}>
    <Box>
      <Typography variant="h4" fontWeight={800}>How to Use OmniTrade AI</Typography>
      <Typography color="text.secondary">A simple path from first login to a complete real-data report.</Typography>
    </Box>
    <Alert severity="warning">OmniTrade gives financial decision support. It does not execute trades and its result is not a guarantee.</Alert>
    <Grid container spacing={2}>
      {topics.map(([progress, title, body]) => <Grid item xs={12} md={6} key={progress}>
        <Card sx={{ height: '100%' }}><CardContent>
          <Stack direction="row" spacing={1.5} alignItems="center" mb={1}>
            <Chip label={progress} color="primary"/>
            <Typography variant="h6" fontWeight={800}>{title}</Typography>
          </Stack>
          <Typography color="text.secondary">{body}</Typography>
        </CardContent></Card>
      </Grid>)}
    </Grid>
    <Card><CardContent>
      <Typography variant="h6" fontWeight={800} gutterBottom>When an option is missing</Typography>
      <Typography>Go to Connections and verify the required provider. New Analysis only shows providers and models that passed a real verification call. A provider that is down or blocked is never replaced with fake data.</Typography>
    </CardContent></Card>
    <Card><CardContent>
      <Typography variant="h6" fontWeight={800} gutterBottom>Professor demo: prove that the graph changes the report</Typography>
      <Stack component="ol" spacing={1} sx={{ pl: 2.5, color: 'text.secondary' }}>
        <li>Run AAPL once with all four analysts. Save this as the baseline report.</li>
        <li>Open Workflow Lab. Select the <b>sentiment analyst</b> node and press Delete. Delete its connected edges too.</li>
        <li>Select <b>Validate</b>. The graph must be valid. Then select <b>Publish</b>.</li>
        <li>Open New Analysis. It uses the new published graph automatically. Keep the same stock, date, models, data providers, risk profile, and budgets.</li>
        <li>Run it again. Compare the two reports in Reports.</li>
        <li>The second report has a new workflow version and no Sentiment Analyst point of view. The other agents and final decision now work without that input.</li>
      </Stack>
      <Alert severity="info" sx={{ mt: 2 }}>A different Buy/Hold/Sell result is possible, but not guaranteed. The defendable result is the changed workflow version, event path, agent list, and report content.</Alert>
    </CardContent></Card>
  </Stack>;
}
