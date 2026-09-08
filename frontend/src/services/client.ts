import type {Fault,Health,Model,Prediction,Reading,Simulation,Stored} from '../types';
export const baseURL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '');
export class ApiError extends Error { constructor(public status:number,public code:string,message:string,public details:unknown=null){super(message)} }
export async function request<T>(path:string,method='GET',body?:unknown):Promise<T>{
 const response=await fetch(`${baseURL}/api/v1${path}`,{method,headers:body?{'Content-Type':'application/json'}:undefined,body:body?JSON.stringify(body):undefined,signal:AbortSignal.timeout(12000)});
 const data=await response.json(); if(!response.ok) throw new ApiError(response.status,data.error?.code||'request_failed',data.error?.message||response.statusText,data.error?.details); return data;
}
export const api={health:()=>request<Health>('/health'),model:()=>request<Model>('/model/info'),create:(session_id:string,planned_fault:Fault,seed:number)=>request<Simulation>('/simulations','POST',{session_id,planned_fault,seed}),state:(id:string)=>request<Simulation>(`/simulations/${encodeURIComponent(id)}`),step:(id:string)=>request<Simulation>(`/simulations/${encodeURIComponent(id)}/step`,'POST'),stop:(id:string)=>request<Simulation>(`/simulations/${encodeURIComponent(id)}/stop`,'POST'),reset:(id:string)=>request(`/simulations/${encodeURIComponent(id)}`,'DELETE'),history:(id='')=>request<{items:Stored[];limit:number}>(`/history?limit=1000${id?`&session_id=${encodeURIComponent(id)}`:''}`),predict:(session_id:string,reading:Reading)=>request<Prediction>('/predict','POST',{session_id,reading}),batch:(session_id:string,readings:Reading[],reset_buffer=false)=>request<{session_id:string;predictions:Prediction[]}>('/predict/batch','POST',{session_id,readings,reset_buffer})};
export function socketURL(id:string,base=baseURL){const url=new URL(`${base}/api/v1/ws/simulations/${encodeURIComponent(id)}`);url.protocol=url.protocol==='https:'?'wss:':'ws:';return url.toString()}
export class SimulationSocket {
 private socket:WebSocket|null=null; private timer:ReturnType<typeof setTimeout>|undefined; private active=false; private attempts=0;
 constructor(private receive:(data:Simulation)=>void,private status:(value:string)=>void,private error:(message:string)=>void){}
 connect(id:string){this.disconnect();this.active=true;this.attempts=0;this.open(id)}
 private open(id:string){if(!this.active)return;this.status(this.attempts?'Reconnecting':'Connecting');const socket=new WebSocket(socketURL(id));this.socket=socket;
 socket.onopen=()=>{if(this.socket!==socket)return;this.attempts=0;this.status('Streaming')};
 socket.onmessage=event=>{if(this.socket!==socket)return;try{const message=JSON.parse(event.data);if(message.type!=='simulation_update'||!message.data?.true_simulated_state||typeof message.data.step!=='number')throw Error('Invalid telemetry message');this.receive(message.data);if(!message.data.running)this.disconnect()}catch{this.error('Invalid telemetry message received.')}};
 socket.onerror=()=>{if(this.socket===socket)this.error('Telemetry connection interrupted.')};
 socket.onclose=()=>{if(!this.active||this.socket!==socket)return;this.status('Reconnecting');this.timer=setTimeout(async()=>{try{const state=await api.state(id);if(!this.active||this.socket!==socket)return;if(!state.running){this.disconnect();this.receive(state);return}this.open(id)}catch(e){if(!this.active||this.socket!==socket)return;if(e instanceof ApiError&&(e.status===404||e.status===409)){this.disconnect();this.error(e.message)}else this.open(id)}},Math.min(1000*2**this.attempts++,15000))};
 }
 disconnect(){this.active=false;clearTimeout(this.timer);const old=this.socket;this.socket=null;if(old){old.onclose=null;old.close()}this.status('Paused')}
}
