import {GoogleSignin} from '@react-native-google-signin/google-signin';
import {CONFIG} from './config';
export type Field={key:string;label:string;min:number;max:number;integer?:boolean};
export type Model={id:number;area:string;name:string;description:string;algorithm:string;formula:string;unit:string;fields:Field[];demo:boolean};
export type Me={email:string;modelIds:number[];requested:number[]};
export type Result={modelId:number;values:number[];dates?:string[];unit:string;demo:boolean};
export async function api<T>(path:string,body?:unknown):Promise<T>{
  if(CONFIG.apiUrl.includes('REEMPLAZAR')||!CONFIG.apiUrl.startsWith('https://'))throw Error('Configura src/config.ts con tu URL de Cloud Run y cliente OAuth.');
  const {idToken}=await GoogleSignin.getTokens();
  if(!idToken)throw Error('Vuelve a iniciar sesión con Google.');
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),65000);
  try{
    const r=await fetch(CONFIG.apiUrl+path,{method:body===undefined?'GET':'POST',headers:{Authorization:`Bearer ${idToken}`,'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body),signal:controller.signal});
    const data=await r.json();
    if(!r.ok)throw Error(data.error||`Error ${r.status}`);
    return data as T;
  }catch(e){if(e instanceof Error&&e.name==='AbortError')throw Error('La solicitud tardó demasiado. Inténtalo nuevamente.');throw e;}
  finally{clearTimeout(timer);}
}
