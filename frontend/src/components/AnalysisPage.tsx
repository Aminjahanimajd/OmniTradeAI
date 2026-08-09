import { useEffect, useState } from 'react';
import {
  Alert, Autocomplete, Box, Button, Card, CardContent, Checkbox,
  FormControlLabel, Grid, MenuItem, Slider, Stack, Switch, TextField, Typography,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { createRun, getAnalysisOptions, getProfile, listWorkflows } from '../api';
import type { AnalysisOptions, Budget, RunConfiguration, WorkflowRecord } from '../types';

const defaultConfig: RunConfiguration = {
  data_mode: 'recorded', analysts: ['market', 'fundamentals', 'news', 'sentiment'],
  research_depth: 2, risk_profile: 'balanced', report_detail: 'standard',
  output_language: 'English', base_currency: 'USD', allow_degraded: true,
  evidence_freshness_hours: 72, quick_model: 'deterministic-fixture',
  deep_model: 'deterministic-fixture',
};
const defaultBudget: Budget = {
  max_runtime_seconds: 180, max_model_calls: 30, max_provider_calls: 30,
  max_tokens: 40000, max_parallel_nodes: 8,
};
const emptyOptions: AnalysisOptions = {
  tickers: [], quick_models: [], deep_models: [], languages: [], currencies: [], data_modes: [],
};

export function latestPublishedWorkflows(items: WorkflowRecord[]): WorkflowRecord[] {
  const latest = new Map<string, WorkflowRecord>();
  for (const workflow of items) {
    if (!workflow.published_version_id) continue;
    const name = workflow.definition.name.trim().toLowerCase();
    const current = latest.get(name);
    if (!current || workflow.version >= current.version) latest.set(name, workflow);
  }
  return [...latest.values()].sort((left, right) => left.definition.name.localeCompare(right.definition.name));
}

export default function AnalysisPage({ onCreated }: { onCreated: (id: string) => void }) {
  const [workflows, setWorkflows] = useState<WorkflowRecord[]>([]);
  const [options, setOptions] = useState(emptyOptions);
  const [version, setVersion] = useState('');
  const [ticker, setTicker] = useState('AAPL');
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [config, setConfig] = useState(defaultConfig);
  const [budget, setBudget] = useState(defaultBudget);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    void Promise.all([listWorkflows(), getProfile(), getAnalysisOptions()])
      .then(([items, profile, available]) => {
        const published = latestPublishedWorkflows(items);
        setWorkflows(published);
        setVersion(published[0]?.published_version_id ?? '');
        setOptions(available);
        setTicker(available.tickers.includes(profile.default_ticker) ? profile.default_ticker : available.tickers[0] ?? 'AAPL');
        setConfig({
          ...profile.default_configuration,
          data_mode: available.data_modes.includes(profile.default_configuration.data_mode) ? profile.default_configuration.data_mode : available.data_modes[0] ?? 'recorded',
          quick_model: available.quick_models.includes(profile.default_configuration.quick_model) ? profile.default_configuration.quick_model : available.quick_models[0] ?? 'deterministic-fixture',
          deep_model: available.deep_models.includes(profile.default_configuration.deep_model) ? profile.default_configuration.deep_model : available.deep_models[0] ?? 'deterministic-fixture',
        });
      })
      .catch(error => setMessage(String(error)));
  }, []);

  const update = <K extends keyof RunConfiguration>(key: K, value: RunConfiguration[K]) =>
    setConfig(current => ({ ...current, [key]: value }));
  const toggleAnalyst = (name: string) => update(
    'analysts',
    config.analysts.includes(name)
      ? config.analysts.filter(value => value !== name)
      : [...config.analysts, name],
  );

  async function start() {
    setBusy(true);
    setMessage('');
    try {
      const run = await createRun(
        version, ticker, `${date}T00:00:00.000Z`, config, budget,
      );
      onCreated(run.id);
    } catch (error) {
      setMessage(String(error));
    } finally {
      setBusy(false);
    }
  }

  return <Stack spacing={2}>
    <Box>
      <Typography variant="h4" fontWeight={800}>New Analysis</Typography>
      <Typography color="text.secondary">Every option below is supported by the current backend. Free model and ticker input is not accepted.</Typography>
    </Box>
    {message && <Alert severity="error">{message}</Alert>}
    {!workflows.length && <Alert severity="warning">Publish a valid workflow before starting an analysis.</Alert>}
    <Grid container spacing={2}>
      <Grid item xs={12} md={6}>
        <Card><CardContent>
          <Typography variant="h6" fontWeight={800} gutterBottom>1. Instrument and workflow</Typography>
          <Stack spacing={2}>
            <TextField select label="Published workflow" value={version} onChange={event => setVersion(event.target.value)}>
              {workflows.map(workflow => <MenuItem key={workflow.published_version_id} value={workflow.published_version_id}>{workflow.definition.name} - version {workflow.version}</MenuItem>)}
            </TextField>
            <Autocomplete
              disableClearable options={options.tickers} value={ticker}
              onChange={(_, value) => setTicker(value)}
              renderInput={params => <TextField {...params} label="Stock ticker" helperText="Only supported stock symbols are listed" />}
            />
            <TextField label="Analysis date" type="date" value={date} inputProps={{ max: new Date().toISOString().slice(0, 10) }} onChange={event => setDate(event.target.value)} InputLabelProps={{ shrink: true }} />
            <TextField select label="Data mode" value={config.data_mode} onChange={event => update('data_mode', event.target.value)}>
              {options.data_modes.map(mode => <MenuItem value={mode} key={mode}>{mode === 'recorded' ? 'Recorded data - reproducible' : mode.replaceAll('_', ' ')}</MenuItem>)}
            </TextField>
          </Stack>
        </CardContent></Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card><CardContent>
          <Typography variant="h6" fontWeight={800}>2. Specialist branches</Typography>
          <Typography variant="body2" color="text.secondary">Selected agents are the only specialist nodes executed for this run.</Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr' }}>
            {['market', 'fundamentals', 'news', 'sentiment'].map(name => <FormControlLabel key={name} control={<Checkbox checked={config.analysts.includes(name)} onChange={() => toggleAnalyst(name)} />} label={name} />)}
          </Box>
          <Typography gutterBottom>Research depth: {config.research_depth} bounded rounds</Typography>
          <Slider min={1} max={5} marks value={config.research_depth} onChange={(_, value) => update('research_depth', value as number)} />
          <TextField fullWidth select label="Risk profile" value={config.risk_profile} onChange={event => update('risk_profile', event.target.value)}>
            <MenuItem value="conservative">Conservative</MenuItem><MenuItem value="balanced">Balanced</MenuItem><MenuItem value="aggressive">Aggressive</MenuItem>
          </TextField>
          <FormControlLabel control={<Switch checked={config.allow_degraded} onChange={event => update('allow_degraded', event.target.checked)} />} label="Allow a report when optional branches fail" />
        </CardContent></Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card><CardContent>
          <Typography variant="h6" fontWeight={800} gutterBottom>3. Models and report</Typography>
          <Stack spacing={2}>
            <TextField select label="Quick analysis model" value={config.quick_model} onChange={event => update('quick_model', event.target.value)}>
              {options.quick_models.map(model => <MenuItem value={model} key={model}>{model}</MenuItem>)}
            </TextField>
            <TextField select label="Deep reasoning model" value={config.deep_model} onChange={event => update('deep_model', event.target.value)}>
              {options.deep_models.map(model => <MenuItem value={model} key={model}>{model}</MenuItem>)}
            </TextField>
            <TextField select label="Report detail" value={config.report_detail} onChange={event => update('report_detail', event.target.value)}>
              <MenuItem value="summary">Summary</MenuItem><MenuItem value="standard">Standard</MenuItem><MenuItem value="detailed">Detailed</MenuItem>
            </TextField>
            <TextField select label="Output language" value={config.output_language} onChange={event => update('output_language', event.target.value)}>
              {options.languages.map(language => <MenuItem value={language} key={language}>{language}</MenuItem>)}
            </TextField>
            <TextField select label="Base currency" value={config.base_currency} onChange={event => update('base_currency', event.target.value)}>
              {options.currencies.map(currency => <MenuItem value={currency} key={currency}>{currency}</MenuItem>)}
            </TextField>
            <TextField type="number" label="Evidence freshness (hours)" value={config.evidence_freshness_hours} onChange={event => update('evidence_freshness_hours', Number(event.target.value))} />
          </Stack>
        </CardContent></Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card><CardContent>
          <Typography variant="h6" fontWeight={800} gutterBottom>4. Safety budgets</Typography>
          <Grid container spacing={1.5}>
            {([['max_runtime_seconds', 'Runtime seconds'], ['max_model_calls', 'Model calls'], ['max_provider_calls', 'Provider calls'], ['max_tokens', 'Token budget'], ['max_parallel_nodes', 'Parallel nodes']] as [keyof Budget, string][]).map(([key, label]) => <Grid item xs={6} key={key}><TextField fullWidth type="number" label={label} value={budget[key]} onChange={event => setBudget(current => ({ ...current, [key]: Number(event.target.value) }))} /></Grid>)}
          </Grid>
          <Alert severity="info" sx={{ mt: 2 }}>No broker is connected. The output is decision support only.</Alert>
        </CardContent></Card>
      </Grid>
    </Grid>
    <Button size="large" variant="contained" startIcon={<PlayArrowIcon />} disabled={busy || !version || !ticker || !config.analysts.length} onClick={start}>Start customized analysis</Button>
  </Stack>;
}
