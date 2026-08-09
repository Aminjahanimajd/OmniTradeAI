import type{AnalysisOptions,Budget,CatalogSuggestion,ReportData,ReportSummary,Run,RunActivity,RunConfiguration,UserProfile,ValidationResult,WorkflowRecord}from'./types';
const API='/api/v1';let token=localStorage.getItem('omnitrade-token')??'';
async function request<T>(path:string,options:RequestInit={}):Promise<T>{const response=await fetch(`${API}${path}`,{...options,headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`}:{}) ,...options.headers}});if(!response.ok)throw new Error((await response.text())||`Request failed: ${response.status}`);return response.status===204?undefined as T:response.json()}
export async function login(username:string,password:string){const data=await request<{access_token:string}>('/auth/login',{method:'POST',body:JSON.stringify({username,password})});token=data.access_token;localStorage.setItem('omnitrade-token',token);return data}
export const hasToken=()=>Boolean(token);export const logout=()=>{token='';localStorage.removeItem('omnitrade-token')};
export const listWorkflows=()=>request<WorkflowRecord[]>('/workflows');
export const createSample=()=>request<WorkflowRecord>('/workflows/sample',{method:'POST'});
export const validateWorkflow=(id:string)=>request<ValidationResult>(`/workflows/${id}/validate`,{method:'POST'});
export const publishWorkflow=(id:string)=>request<{id:string}>(`/workflows/${id}/publish`,{method:'POST'});
export const updateWorkflow=(id:string,definition:WorkflowRecord['definition'])=>request<WorkflowRecord>(`/workflows/${id}`,{method:'PUT',body:JSON.stringify(definition)});
export const createRun=(workflow_version_id:string,ticker:string,as_of:string,configuration:RunConfiguration,budget_override:Budget)=>request<Run>('/runs',{method:'POST',body:JSON.stringify({workflow_version_id,ticker,as_of,configuration,budget_override})});
export const listRuns=()=>request<Run[]>('/runs');
export const getRun=(id:string)=>request<Run>(`/runs/${id}`);
export const cancelRun=(id:string)=>request<Run>(`/runs/${id}/cancel`,{method:'POST'});
export const resumeRun=(id:string)=>request<Run>(`/runs/${id}/resume`,{method:'POST'});
export const getLineage=(id:string)=>request<Record<string,unknown>>(`/runs/${id}/lineage`);
export const getActivity=(id:string)=>request<RunActivity>(`/runs/${id}/activity`);
export const listReports=()=>request<ReportSummary[]>('/report-history');
export const getReport=(id:string)=>request<ReportData>(`/reports/${id}`);
export async function downloadReport(id:string,format:string){const response=await fetch(`${API}/reports/${id}/export/${format}`,{headers:{Authorization:`Bearer ${token}`}});if(!response.ok)throw new Error(await response.text());const blob=await response.blob();const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download=`omnitrade-${id}.${format}`;link.click();URL.revokeObjectURL(url)}
export const getProfile=()=>request<UserProfile>('/profile');
export const saveProfile=(profile:UserProfile)=>request<UserProfile>('/profile',{method:'PUT',body:JSON.stringify(profile)});
export const getAnalysisOptions=()=>request<AnalysisOptions>('/analysis-options');
export const getCatalog=()=>request<{count:number;nodes:Record<string,{group:string;description:string;inputs:Record<string,string>;outputs:Record<string,string>;suggested_targets:CatalogSuggestion[]}>}>('/catalog');
