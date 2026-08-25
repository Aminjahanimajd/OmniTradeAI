import { useEffect, useMemo, useState } from 'react';
import {
  Alert, Box, Button, Card, CardContent, Chip, Grid, MenuItem, Stack,
  TextField, Typography,
} from '@mui/material';
import CableIcon from '@mui/icons-material/Cable';
import VerifiedIcon from '@mui/icons-material/Verified';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import {
  deleteConnection, getConnectionCatalog, listConnections, loadConnectionModels,
  saveConnection, verifyConnection,
} from '../api';
import type { ConnectionInput, ConnectionSpec, ConnectionStatus } from '../types';

const BEDROCK_REGIONS = [
  'us-east-1', 'us-west-2', 'eu-central-1', 'eu-west-1', 'eu-west-2',
  'eu-west-3', 'eu-north-1', 'eu-south-1', 'eu-south-2', 'ap-northeast-1',
  'ap-northeast-2', 'ap-northeast-3', 'ap-south-1', 'ap-south-2',
  'ap-southeast-1', 'ap-southeast-2', 'ca-central-1', 'sa-east-1',
];

function cleanModels(values: string[]): string[] {
  return [...new Set(values.map(value => value.trim()).filter(Boolean))];
}

export default function ConnectionsPage() {
  const [specs, setSpecs] = useState<Record<string, ConnectionSpec>>({});
  const [statuses, setStatuses] = useState<ConnectionStatus[]>([]);
  const [provider, setProvider] = useState('openai');
  const [form, setForm] = useState<ConnectionInput>({ provider: 'openai' });
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [loadedModels, setLoadedModels] = useState<Record<string, string[]>>({});
  const spec = specs[provider];
  const status = useMemo(
    () => statuses.find(item => item.provider === provider),
    [statuses, provider],
  );
  const modelChoices = cleanModels([
    ...(form.model_ids ?? []),
    ...(loadedModels[provider] ?? []),
    ...(status?.models ?? []),
    ...(spec?.models ?? []),
  ]);

  async function reload() {
    const [catalog, current] = await Promise.all([getConnectionCatalog(), listConnections()]);
    setSpecs(catalog.providers);
    setStatuses(current);
    const selectedSpec = catalog.providers[provider];
    const selectedStatus = current.find(item => item.provider === provider);
    setForm(value => value.provider === provider && Object.keys(value).length > 1 ? value : {
      provider,
      base_url: selectedStatus?.base_url ?? selectedSpec?.base_url ?? '',
      test_model: selectedStatus?.test_model ?? selectedStatus?.models[0] ?? selectedSpec?.models[0] ?? '',
      model_ids: selectedStatus?.models ?? selectedSpec?.models ?? [],
      region: provider === 'bedrock' ? 'us-east-1' : undefined,
      azure_api_version: provider === 'azure' ? '2024-10-21' : undefined,
    });
  }

  useEffect(() => { void reload().catch(error => setMessage(String(error))); }, []);

  function choose(name: string) {
    const next = specs[name];
    const saved = statuses.find(item => item.provider === name);
    setProvider(name);
    setForm({
      provider: name,
      base_url: saved?.base_url ?? next?.base_url ?? '',
      test_model: saved?.test_model ?? saved?.models[0] ?? next?.models?.[0] ?? '',
      model_ids: saved?.models ?? next?.models ?? [],
      region: name === 'bedrock' ? 'us-east-1' : undefined,
      azure_api_version: name === 'azure' ? '2024-10-21' : undefined,
    });
    setMessage('');
  }

  async function save() {
    setBusy(true);
    try {
      await saveConnection(provider, form);
      await reload();
      setMessage('Saved in this session. Now verify it.');
    } catch (error) {
      setMessage(String(error));
    } finally {
      setBusy(false);
    }
  }

  async function verify() {
    setBusy(true);
    try {
      await verifyConnection(provider);
      await reload();
      setMessage('Connection verified and ready.');
    } catch (error) {
      await reload();
      setMessage(String(error));
    } finally {
      setBusy(false);
    }
  }

  async function connectKeylessData() {
    setBusy(true);
    const candidates = Object.entries(specs)
      .filter(([, value]) => value.category === 'data' && value.key_optional);
    const results: string[] = [];
    for (const [name, value] of candidates) {
      try {
        await saveConnection(name, { provider: name, base_url: value.base_url });
        await verifyConnection(name);
        results.push(`${value.label}: ready`);
      } catch {
        results.push(`${value.label}: unavailable`);
      }
    }
    await reload();
    setMessage(results.join(' · '));
    setBusy(false);
  }

  return <Stack spacing={2}>
    <Box>
      <Typography variant="h4" fontWeight={800}>Real Data and Model Connections</Typography>
      <Typography color="text.secondary">Credentials stay in API memory for this session. They are never returned by the API or written into reports.</Typography>
    </Box>
    {message && <Alert severity={message.includes('verified and ready') ? 'success' : 'info'}>{message}</Alert>}
    <Grid container spacing={2}>
      <Grid item xs={12} md={7}>
        <Card><CardContent><Stack spacing={2}>
          <TextField select label="Provider" value={provider} onChange={event => choose(event.target.value)}>
            {Object.entries(specs).map(([key, value]) => <MenuItem key={key} value={key}>{value.category === 'model' ? 'AI · ' : 'Data · '}{value.label}</MenuItem>)}
          </TextField>
          {spec && <Alert severity="info">{spec.category === 'model' ? 'This provider writes agent explanations from grounded evidence.' : `Capabilities: ${spec.capabilities.join(', ')}`}</Alert>}

          {spec?.category === 'model' && <>
            {(provider === 'bedrock' || !spec.models.length) && <TextField
              multiline minRows={2} label="Allowed model IDs (one per line)"
              value={(form.model_ids ?? []).join('\n')}
              onChange={event => setForm({ ...form, model_ids: cleanModels(event.target.value.split('\n')) })}
              helperText="These become the model choices on New Analysis."
            />}
            <TextField
              select={Boolean(modelChoices.length)} label="Verification model / deployment ID"
              value={form.test_model ?? ''}
              onChange={event => setForm({ ...form, test_model: event.target.value })}
              helperText={modelChoices.length ? 'Choose one configured model for the live verification call.' : 'Enter an exact model or deployment ID.'}
            >
              {modelChoices.map(model => <MenuItem value={model} key={model}>{model}</MenuItem>)}
            </TextField>
            <Button disabled={!status?.configured || busy} onClick={async () => {
              try {
                const result = await loadConnectionModels(provider);
                setLoadedModels(current => ({ ...current, [provider]: result.models }));
                setForm(current => ({
                  ...current,
                  model_ids: result.models,
                  test_model: current.test_model || result.models[0] || '',
                }));
                setMessage(`Loaded ${result.models.length} available models.`);
              } catch (error) {
                setMessage(String(error));
              }
            }}>Load available models</Button>
          </>}

          {(spec?.base_url || ['azure', 'openai_compatible'].includes(provider)) && (
            <TextField label="API base URL" value={form.base_url ?? ''} onChange={event => setForm({ ...form, base_url: event.target.value })}/>
          )}
          {provider !== 'bedrock' && (!spec?.key_optional || spec?.category === 'model') && <TextField type="password" label={spec?.key_optional ? 'API key (optional)' : 'API key'} value={form.api_key ?? ''} onChange={event => setForm({ ...form, api_key: event.target.value })} autoComplete="off"/>}
          {provider === 'bedrock' && <>
            <TextField select label="AWS region" value={form.region ?? 'us-east-1'} onChange={event => setForm({ ...form, region: event.target.value })}>
              {BEDROCK_REGIONS.map(region => <MenuItem key={region} value={region}>{region}</MenuItem>)}
            </TextField>
            <TextField type="password" label="Bedrock bearer token (recommended)" value={form.aws_bearer_token_bedrock ?? ''} onChange={event => setForm({ ...form, aws_bearer_token_bedrock: event.target.value })} autoComplete="off"/>
            <Typography variant="caption" color="text.secondary">Or use standard temporary AWS credentials:</Typography>
            <TextField type="password" label="AWS access key ID" value={form.aws_access_key_id ?? ''} onChange={event => setForm({ ...form, aws_access_key_id: event.target.value })}/>
            <TextField type="password" label="AWS secret access key" value={form.aws_secret_access_key ?? ''} onChange={event => setForm({ ...form, aws_secret_access_key: event.target.value })}/>
            <TextField type="password" label="AWS session token (optional)" value={form.aws_session_token ?? ''} onChange={event => setForm({ ...form, aws_session_token: event.target.value })}/>
          </>}
          {provider === 'azure' && (
            <TextField label="Azure API version" value={form.azure_api_version ?? '2024-10-21'} onChange={event => setForm({ ...form, azure_api_version: event.target.value })}/>
          )}

          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Button variant="contained" startIcon={<CableIcon/>} disabled={busy} onClick={save}>Save session connection</Button>
            <Button variant="outlined" startIcon={<VerifiedIcon/>} disabled={busy || !status?.configured} onClick={verify}>Verify now</Button>
            <Button color="error" startIcon={<DeleteOutlineIcon/>} disabled={!status?.configured} onClick={async () => { await deleteConnection(provider); await reload(); }}>Remove</Button>
          </Stack>
          {status && (
            <Chip color={status.verified ? 'success' : status.configured ? 'warning' : 'default'} label={status.message}/>
          )}
        </Stack></CardContent></Card>
      </Grid>

      <Grid item xs={12} md={5}>
        <Card><CardContent>
          <Stack spacing={1.5}>
            <Typography variant="h6" fontWeight={800}>Session status</Typography>
            <Button startIcon={<AutoFixHighIcon/>} variant="outlined" disabled={busy || !Object.keys(specs).length} onClick={connectKeylessData}>Connect all keyless data sources</Button>
            {statuses.some(item => item.configured) ? statuses.filter(item => item.configured).map(item => <Box key={item.provider} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 1.2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <span>{specs[item.provider]?.label ?? item.provider}</span>
              <Chip size="small" color={item.verified ? 'success' : 'warning'} label={item.verified ? 'Verified' : 'Needs verification'}/>
            </Box>) : <Typography color="text.secondary">No connections saved in this session.</Typography>}
          </Stack>
        </CardContent></Card>
      </Grid>
    </Grid>
  </Stack>;
}
