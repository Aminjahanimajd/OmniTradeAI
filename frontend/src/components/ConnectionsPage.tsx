import { useEffect, useMemo, useState } from 'react';
import { Alert, Box, Button, Card, CardContent, Chip, Grid, MenuItem, Stack, TextField, Typography } from '@mui/material';
import CableIcon from '@mui/icons-material/Cable';
import VerifiedIcon from '@mui/icons-material/Verified';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import { deleteConnection, getConnectionCatalog, listConnections, loadConnectionModels, saveConnection, verifyConnection } from '../api';
import type { ConnectionInput, ConnectionSpec, ConnectionStatus } from '../types';

export default function ConnectionsPage(){
  const[specs,setSpecs]=useState<Record<string,ConnectionSpec>>({});
  const[statuses,setStatuses]=useState<ConnectionStatus[]>([]);
  const[provider,setProvider]=useState('openai');
  const[form,setForm]=useState<ConnectionInput>({provider:'openai'});
  const[message,setMessage]=useState(''); const[busy,setBusy]=useState(false);
  const[loadedModels,setLoadedModels]=useState<Record<string,string[]>>({});
  const spec=specs[provider];
  const status=useMemo(()=>statuses.find(item=>item.provider===provider),[statuses,provider]);
  async function reload(){const[catalog,current]=await Promise.all([getConnectionCatalog(),listConnections()]);setSpecs(catalog.providers);setStatuses(current);const initial=catalog.providers[provider];setForm(value=>value.test_model||value.base_url?value:{provider,base_url:initial?.base_url??'',test_model:initial?.models?.[0]??''});}
  useEffect(()=>{void reload().catch(error=>setMessage(String(error)))},[]);
  function choose(name:string){const next=specs[name];setProvider(name);setForm({provider:name,base_url:next?.base_url??'',test_model:next?.models?.[0]??'',azure_api_version:name==='azure'?'2024-10-21':undefined});setMessage('');}
  async function save(){setBusy(true);try{await saveConnection(provider,form);await reload();setMessage('Saved in this session. Now verify it.')}catch(error){setMessage(String(error))}finally{setBusy(false)}}
  async function verify(){setBusy(true);try{await verifyConnection(provider);await reload();setMessage('Connection verified and ready.')}catch(error){await reload();setMessage(String(error))}finally{setBusy(false)}}
  return <Stack spacing={2}>
    <Box><Typography variant="h4" fontWeight={800}>Real Data and Model Connections</Typography><Typography color="text.secondary">Credentials stay in API memory for this session. They are not saved in reports, runs, events, or the database.</Typography></Box>
    {message&&<Alert severity={message.includes('verified and ready')?'success':'info'}>{message}</Alert>}
    <Grid container spacing={2}>
      <Grid item xs={12} md={7}><Card><CardContent><Stack spacing={2}>
        <TextField select label="Provider" value={provider} onChange={event=>choose(event.target.value)}>
          {Object.entries(specs).map(([key,value])=><MenuItem key={key} value={key}>{value.category==='model'?'AI · ':'Data · '}{value.label}</MenuItem>)}
        </TextField>
        {spec&&<Alert severity="info">{spec.category==='model'?'This provider writes agent explanations from grounded evidence.':'Capabilities: '+spec.capabilities.join(', ')}</Alert>}
        {spec?.category==='model'&&<><TextField select={Boolean((loadedModels[provider]??spec.models).length)} label="Verification model / deployment ID" value={form.test_model??''} onChange={event=>setForm({...form,test_model:event.target.value})} helperText={(loadedModels[provider]??spec.models).length?'Choose a model reported for this provider.':'Enter the exact model or deployment ID for this provider.'}>{(loadedModels[provider]??spec.models).map(model=><MenuItem value={model} key={model}>{model}</MenuItem>)}</TextField><Button disabled={!status?.configured||busy} onClick={async()=>{try{const result=await loadConnectionModels(provider);setLoadedModels(current=>({...current,[provider]:result.models}));if(result.models[0])setForm(current=>({...current,test_model:result.models[0]}));setMessage(`Loaded ${result.models.length} available models.`)}catch(error){setMessage(String(error))}}}>Load available models</Button></>}
        {(spec?.base_url||['azure','openai_compatible'].includes(provider))&&(
          <TextField label="API base URL" value={form.base_url??''} onChange={event=>setForm({...form,base_url:event.target.value})}/>
        )}
        {provider!=='bedrock'&&<TextField type="password" label={spec?.key_optional?'API key (optional for local servers)':'API key'} value={form.api_key??''} onChange={event=>setForm({...form,api_key:event.target.value})} autoComplete="off"/>}
        {provider==='bedrock'&&<><TextField label="AWS region" value={form.region??'us-east-1'} onChange={event=>setForm({...form,region:event.target.value})}/><TextField type="password" label="AWS access key ID" value={form.aws_access_key_id??''} onChange={event=>setForm({...form,aws_access_key_id:event.target.value})}/><TextField type="password" label="AWS secret access key" value={form.aws_secret_access_key??''} onChange={event=>setForm({...form,aws_secret_access_key:event.target.value})}/><TextField type="password" label="AWS session token (optional)" value={form.aws_session_token??''} onChange={event=>setForm({...form,aws_session_token:event.target.value})}/></>}
        {provider==='azure'&&(
          <TextField label="Azure API version" value={form.azure_api_version??'2024-10-21'} onChange={event=>setForm({...form,azure_api_version:event.target.value})}/>
        )}
        <Stack direction="row" spacing={1} flexWrap="wrap"><Button variant="contained" startIcon={<CableIcon/>} disabled={busy} onClick={save}>Save session connection</Button><Button variant="outlined" startIcon={<VerifiedIcon/>} disabled={busy||!status?.configured} onClick={verify}>Verify now</Button><Button color="error" startIcon={<DeleteOutlineIcon/>} disabled={!status?.configured} onClick={async()=>{await deleteConnection(provider);await reload()}}>Remove</Button></Stack>
        {status&&(
          <Chip color={status.verified?'success':status.configured?'warning':'default'} label={status.message}/>
        )}
      </Stack></CardContent></Card></Grid>
      <Grid item xs={12} md={5}><Card><CardContent><Typography variant="h6" fontWeight={800}>Session status</Typography><Stack spacing={1} mt={2}>{statuses.some(item=>item.configured)?statuses.filter(item=>item.configured).map(item=><Box key={item.provider} sx={{display:'flex',justifyContent:'space-between',alignItems:'center',p:1.2,border:'1px solid',borderColor:'divider',borderRadius:2}}><span>{specs[item.provider]?.label??item.provider}</span><Chip size="small" color={item.verified?'success':'warning'} label={item.verified?'Verified':'Needs verification'}/></Box>):<Typography color="text.secondary">No connections saved in this session.</Typography>}</Stack></CardContent></Card></Grid>
    </Grid>
  </Stack>
}
