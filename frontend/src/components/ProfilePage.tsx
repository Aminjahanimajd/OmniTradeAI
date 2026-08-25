import{useEffect,useState}from'react';
import{Alert,Autocomplete,Button,Card,CardContent,Divider,MenuItem,Stack,TextField,Typography}from'@mui/material';
import SaveIcon from'@mui/icons-material/Save';
import{getAnalysisOptions,getProfile,saveProfile}from'../api';
import type{UserProfile}from'../types';

export default function ProfilePage(){
  const[profile,setProfile]=useState<UserProfile>();
  const[tickers,setTickers]=useState<string[]>([]);
  const[message,setMessage]=useState('');
  useEffect(()=>{void Promise.all([getProfile(),getAnalysisOptions()]).then(([value,options])=>{setProfile({...value,default_configuration:{...value.default_configuration,data_mode:'live'}});setTickers(options.tickers)}).catch(error=>setMessage(String(error)))},[]);
  if(!profile)return<Alert severity="info">Loading profile...</Alert>;
  const config=profile.default_configuration;
  const policy=profile.investor_policy;
  const updatePolicy=(key:keyof typeof policy,value:string|number|string[])=>setProfile({...profile,investor_policy:{...policy,[key]:value}});
  return<Stack spacing={2} sx={{maxWidth:850}}>
    <Typography variant="h4" fontWeight={800}>Profile and Investment Policy</Typography>
    <Typography color="text.secondary">Defaults fill the analysis form. Investment limits are copied into each run and change its risk validation.</Typography>
    {message&&<Alert severity={message==='Profile saved'?'success':'error'}>{message}</Alert>}
    <Card><CardContent><Stack spacing={2}>
      <Typography variant="h6">Identity and defaults</Typography>
      <TextField label="Display name" value={profile.display_name} onChange={event=>setProfile({...profile,display_name:event.target.value})}/>
      <TextField label="Email (not used for decisions)" value={profile.email} onChange={event=>setProfile({...profile,email:event.target.value})}/>
      <Autocomplete disableClearable options={tickers} value={profile.default_ticker} onChange={(_,value)=>setProfile({...profile,default_ticker:value})} renderInput={params=><TextField {...params} label="Default stock ticker" helperText="Choose a supported stock symbol"/>}/>
      <Alert severity="success">All normal analyses use verified real provider data. There is no fake-data mode to select.</Alert>
      <TextField select label="Default risk profile" value={config.risk_profile} onChange={event=>setProfile({...profile,default_configuration:{...config,risk_profile:event.target.value}})}><MenuItem value="conservative">Conservative</MenuItem><MenuItem value="balanced">Balanced</MenuItem><MenuItem value="aggressive">Aggressive</MenuItem></TextField>
      <TextField type="number" label="Default research depth" value={config.research_depth} onChange={event=>setProfile({...profile,default_configuration:{...config,research_depth:Number(event.target.value)}})}/>
      <TextField select label="Default report detail" value={config.report_detail} onChange={event=>setProfile({...profile,default_configuration:{...config,report_detail:event.target.value}})}><MenuItem value="summary">Summary</MenuItem><MenuItem value="standard">Standard</MenuItem><MenuItem value="detailed">Detailed</MenuItem></TextField>
      <Divider/>
      <Typography variant="h6">Investment policy used by the risk agents</Typography>
      <TextField select label="Investment horizon" value={policy.investment_horizon} onChange={event=>updatePolicy('investment_horizon',event.target.value)}><MenuItem value="short">Short term</MenuItem><MenuItem value="medium">Medium term</MenuItem><MenuItem value="long">Long term</MenuItem></TextField>
      <TextField select label="Experience level" value={policy.experience_level} onChange={event=>updatePolicy('experience_level',event.target.value)}><MenuItem value="beginner">Beginner</MenuItem><MenuItem value="intermediate">Intermediate</MenuItem><MenuItem value="advanced">Advanced</MenuItem></TextField>
      <TextField type="number" label="Maximum acceptable loss (%)" inputProps={{min:1,max:50}} value={policy.maximum_loss_percent} onChange={event=>updatePolicy('maximum_loss_percent',Number(event.target.value))}/>
      <TextField type="number" label="Maximum position size (%)" inputProps={{min:1,max:100}} value={policy.maximum_position_percent} onChange={event=>updatePolicy('maximum_position_percent',Number(event.target.value))}/>
      <TextField label="Excluded sectors (comma separated)" value={policy.excluded_sectors.join(', ')} onChange={event=>updatePolicy('excluded_sectors',event.target.value.split(',').map(value=>value.trim()).filter(Boolean))}/>
      <Alert severity="info">Only investment preferences affect decisions. Your name and email never change a recommendation.</Alert>
      <Button variant="contained" startIcon={<SaveIcon/>} onClick={async()=>{try{setProfile(await saveProfile(profile));setMessage('Profile saved')}catch(error){setMessage(String(error))}}}>Save profile</Button>
    </Stack></CardContent></Card>
  </Stack>;
}
