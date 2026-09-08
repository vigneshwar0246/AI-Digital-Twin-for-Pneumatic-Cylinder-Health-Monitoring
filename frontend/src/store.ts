import {create} from 'zustand';
import {api,ApiError,SimulationSocket} from './services/client';
import type {Fault,Health,Model,Simulation} from './types';
export type Mode='assembled'|'cutaway'|'exploded';
type State={health:Health|null;model:Model|null;connection:string;stream:string;error:string|null;busy:boolean;session:Simulation|null;samples:Simulation[];mode:Mode;selected:string|null;isolated:boolean;xray:boolean;check:()=>Promise<void>;createSession:(fault:Fault,seed:number)=>Promise<void>;start:()=>void;pause:()=>void;step:()=>Promise<void>;stop:()=>Promise<void>;reset:()=>Promise<void>;receive:(s:Simulation)=>void;setMode:(m:Mode)=>void};
export const useTwin=create<State>((set,get)=>({health:null,model:null,connection:'Checking',stream:'Paused',error:null,busy:false,session:null,samples:[],mode:'assembled',selected:null,isolated:false,xray:false,
 check:async()=>{set({connection:'Checking',error:null});try{const health=await api.health();set({health,connection:health.status==='ok'?'Connected':'Degraded'});try{set({model:await api.model()})}catch(e){set({error:String(e)})}}catch{set({connection:'Backend offline',health:null,error:'Cannot reach the backend. Check the server and CORS configuration.'})}},
 receive:session=>set(s=>({session,error:null,samples:session.prediction?[...s.samples,session].slice(-1000):s.samples})),
 createSession:async(fault,seed)=>{socket.disconnect();set({busy:true,error:null});try{const session=await api.create(`lab-${Date.now()}-${Math.random().toString(36).slice(2,6)}`,fault,seed);set({session,samples:[]})}catch(e){set({error:String(e)})}finally{set({busy:false})}},
 start:()=>{const s=get().session;if(s?.running)socket.connect(s.session_id)},pause:()=>socket.disconnect(),
 step:async()=>{socket.disconnect();const s=get().session;if(!s)return;set({busy:true,error:null});try{get().receive(await api.step(s.session_id))}catch(e){set({error:String(e)})}finally{set({busy:false})}},
 stop:async()=>{socket.disconnect();const s=get().session;if(!s)return;set({busy:true});try{set({session:await api.stop(s.session_id),error:null})}catch(e){set({error:String(e)})}finally{set({busy:false})}},
 reset:async()=>{socket.disconnect();const s=get().session;if(!s)return;set({busy:true});try{try{await api.reset(s.session_id)}catch(e){if(!(e instanceof ApiError&&e.status===404))throw e}set({session:null,samples:[],error:null,mode:'assembled',selected:null,isolated:false})}catch(e){set({error:String(e)})}finally{set({busy:false})}},
 setMode:mode=>set({mode,isolated:false})
}));
const socket=new SimulationSocket(s=>useTwin.getState().receive(s),stream=>useTwin.setState({stream}),error=>useTwin.setState({error}));
