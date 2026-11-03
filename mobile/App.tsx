import React,{useCallback,useEffect,useRef,useState} from 'react';
import {ActivityIndicator,AppState,Pressable,ScrollView,StatusBar,StyleSheet,TextInput,View} from 'react-native';
import {SafeAreaProvider,SafeAreaView} from 'react-native-safe-area-context';
import {GoogleSignin,isSuccessResponse,statusCodes,isErrorWithCode} from '@react-native-google-signin/google-signin';
import {RaTeXView} from 'ratex-react-native';
import {CONFIG} from './src/config';
import {api,type Me,type Model,type Result} from './src/api';
import {T,Heading,Paper,Plot,colors} from './src/Retro';
GoogleSignin.configure({webClientId:CONFIG.googleWebClientId,...(CONFIG.googleIOSClientId?{iosClientId:CONFIG.googleIOSClientId}:{}),offlineAccess:false});
function Button({title,onPress,disabled=false,active=false}:{title:string;onPress:()=>void;disabled?:boolean;active?:boolean}){return <Pressable accessibilityRole="button" accessibilityState={{disabled,selected:active}} disabled={disabled} onPress={onPress} style={({pressed})=>[s.button,active&&s.active,(disabled||pressed)&&{opacity:0.5}]}><T style={active?{color:colors.paper}:undefined}>{title}</T></Pressable>;}
export default function App(){return <SafeAreaProvider><Screen/></SafeAreaProvider>;}
function Screen(){
  const [signed,setSigned]=useState(false),[busy,setBusy]=useState(true),[message,setMessage]=useState('');
  const [models,setModels]=useState<Model[]>([]),[me,setMe]=useState<Me|null>(null),[tab,setTab]=useState<'mine'|'store'>('mine');
  const [area,setArea]=useState(''),[selected,setSelected]=useState<Model|null>(null),[inputs,setInputs]=useState<Record<string,string>>({}),[result,setResult]=useState<Result|null>(null);
  const generation=useRef(0),lock=useRef(false);
  const load=useCallback(async()=>{const ticket=generation.current;const [catalog,user]=await Promise.all([api<{models:Model[]}>('/v1/catalog'),api<Me>('/v1/me')]);if(ticket!==generation.current)return;setModels(catalog.models);setMe(user);setSelected(old=>old&&user.modelIds.includes(old.id)?old:null);setResult(null);},[]);
  const run=useCallback(async(fn:()=>Promise<void>)=>{if(lock.current)return;lock.current=true;setBusy(true);setMessage('');try{await fn();}catch(e){setMessage(e instanceof Error?e.message:'No fue posible completar la operación.');}finally{lock.current=false;setBusy(false);}},[]);
  useEffect(()=>{void run(async()=>{let restored=false;try{const response=await GoogleSignin.signInSilently();restored=response.type==='success';}catch{/* La primera sesión necesita selección explícita. */}if(restored){setSigned(true);await load();}});},[load,run]);
  useEffect(()=>{const sub=AppState.addEventListener('change',state=>{if(state==='active'&&signed)void run(load);});return()=>sub.remove();},[signed,load,run]);
  async function signIn(){await GoogleSignin.hasPlayServices({showPlayServicesUpdateDialog:true});try{const r=await GoogleSignin.signIn();if(isSuccessResponse(r)){generation.current++;setSigned(true);await load();}}catch(e){if(isErrorWithCode(e)&&e.code===statusCodes.SIGN_IN_CANCELLED)return;throw e;}}
  async function signOut(){generation.current++;try{await GoogleSignin.signOut();}finally{setSigned(false);setMe(null);setModels([]);setSelected(null);setInputs({});setResult(null);setArea('');setTab('mine');}}
  const visible=tab==='mine'?models.filter(m=>me?.modelIds.includes(m.id)):models;
  const areas=[...new Set(visible.map(m=>m.area))];
  const currentArea=areas.includes(area)?area:areas[0];
  function choose(m:Model){setSelected(m);setInputs({});setResult(null);setMessage('');}
  async function predict(){
    if(!selected)return;
    const entries=selected.fields.map(f=>{const raw=inputs[f.key]?.trim();const n=raw?Number(raw.replace(',','.')):NaN;if(!Number.isFinite(n)||n<f.min||n>f.max||(f.integer&&!Number.isInteger(n)))throw Error(`${f.label}: ingresa ${f.integer?'un entero':'un número'} entre ${f.min} y ${f.max}.`);return [f.key,n] as const;});
    const ticket=generation.current;setResult(null);
    try{const r=await api<Result>(`/v1/models/${selected.id}/predict`,{inputs:Object.fromEntries(entries)});if(ticket===generation.current)setResult(r);}catch(e){await load().catch(()=>{});throw e;}
  }
  return <SafeAreaView style={s.root}><StatusBar barStyle="dark-content" backgroundColor={colors.paper}/><Paper/><ScrollView contentContainerStyle={s.page} keyboardShouldPersistTaps="handled"><Heading/><T style={s.kicker}>MODELOS / ACCESO PERSONAL</T>
    {!signed?<View style={s.sheet}><T style={s.title}>Tu mesa de trabajo.</T><T>Inicia sesión con tu cuenta de Google Gmail para consultar la Store y tus modelos habilitados.</T><Button title="Continuar con Google" disabled={busy} onPress={()=>void run(signIn)}/></View>:<>
      <T numberOfLines={2}>{me?.email||'Sesión Google iniciada'}</T>
      <View style={s.row}><Button title="Mis modelos" active={tab==='mine'} disabled={busy} onPress={()=>{setTab('mine');setSelected(null);setResult(null);}}/><Button title="Store" active={tab==='store'} disabled={busy} onPress={()=>{setTab('store');setSelected(null);setResult(null);}}/></View>
      <View style={s.row}><Button title="Actualizar" disabled={busy} onPress={()=>void run(load)}/><Button title="Salir" disabled={busy} onPress={()=>void run(signOut)}/></View>
      {selected?<View style={s.sheet}><Button title="< Volver" disabled={busy} onPress={()=>{setSelected(null);setResult(null);}}/><T style={s.title}>{selected.name}</T><T style={s.id}>{selected.id}</T><T>{selected.description}</T>{selected.demo&&<T style={s.notice}>CALCULADORA DE SUMA</T>}
        <RaTeXView latex={selected.formula} fontSize={20} color={colors.ink} style={{height:70,marginVertical:12}} onError={()=>setMessage('No se pudo mostrar la fórmula de este modelo.')}/>
        {me?.modelIds.includes(selected.id)?<>{selected.fields.map(f=><View key={f.key} style={{marginVertical:8}}><T>{f.label}</T><T style={s.id}>{f.min} a {f.max}{f.integer?' / entero':''}</T><TextInput accessibilityLabel={f.label} editable={!busy} value={inputs[f.key]||''} onChangeText={v=>{setInputs(old=>({...old,[f.key]:v}));setResult(null);}} keyboardType="numbers-and-punctuation" autoCorrect={false} style={s.input}/></View>)}<T>Resultado en {selected.unit}</T><Button title="Sumar inputs" disabled={busy} onPress={()=>void run(predict)}/></>:<><T>Necesitas autorización para este ID.</T><Button title={me?.requested.includes(selected.id)?'Solicitud pendiente':'Solicitar acceso'} disabled={busy||!!me?.requested.includes(selected.id)} onPress={()=>void run(async()=>{await api('/v1/requests',{modelId:selected.id});await load();setMessage('Solicitud enviada. El administrador puede habilitar este ID.');})}/></>}
        {result&&<View style={s.result}><T style={s.title}>Resultado</T>{result.demo&&<T style={s.notice}>Suma de los inputs ingresados.</T>}<Plot values={result.values}/>{result.values.map((v,i)=><T selectable key={i}>{result.dates?.[i]||`Valor ${i+1}`}: {v.toLocaleString('es-CL',{maximumFractionDigits:3})} {result.unit}</T>)}</View>}
      </View>:<>{areas.length>0&&<View style={s.row}>{areas.map(a=><Button key={a} title={a} active={currentArea===a} disabled={busy} onPress={()=>setArea(a)}/>)}</View>}{visible.length===0&&<View style={s.sheet}><T>No tienes modelos habilitados. Solicita acceso desde la Store.</T></View>}{visible.filter(m=>m.area===currentArea).map(m=><View key={m.id} style={s.sheet}><T style={s.title}>{m.name}</T><T style={s.id}>{m.id}</T><T>{m.description}</T>{m.demo&&<T style={s.notice}>SUMA DE INPUTS</T>}<Button title={me?.modelIds.includes(m.id)?'Abrir modelo':'Ver y solicitar acceso'} disabled={busy} onPress={()=>choose(m)}/></View>)}</>}
    </>}
    {busy&&<ActivityIndicator accessibilityLabel="Procesando" color={colors.accent} style={{margin:20}}/>}{!!message&&<T accessibilityRole="alert" accessibilityLiveRegion="polite" style={s.message}>{message}</T>}<T style={s.footer}>AUTOMIND · EDICIÓN TYPEWRITER · 1984</T>
  </ScrollView></SafeAreaView>;
}
const s=StyleSheet.create({root:{flex:1,backgroundColor:colors.paper},page:{padding:30,paddingBottom:50,maxWidth:760,width:'100%',alignSelf:'center'},kicker:{fontSize:12,letterSpacing:2,marginBottom:22},title:{fontSize:24,lineHeight:30,marginBottom:10},sheet:{marginTop:20,padding:18,borderWidth:1,borderColor:colors.line,backgroundColor:'#f5f0e4'},row:{flexDirection:'row',flexWrap:'wrap',gap:8,marginTop:8},button:{borderWidth:1,borderColor:colors.ink,paddingHorizontal:12,paddingVertical:12,marginTop:10,minHeight:48,alignSelf:'flex-start'},active:{backgroundColor:colors.ink},id:{fontSize:13,color:colors.muted,lineHeight:19,marginBottom:10},notice:{fontSize:13,color:colors.accent,marginTop:12},input:{borderBottomWidth:1,borderColor:colors.ink,color:colors.ink,padding:10,minHeight:48,fontSize:18,fontFamily:'LMMono12-Regular'},result:{borderTopWidth:2,borderColor:colors.ink,marginTop:24,paddingTop:18},message:{marginTop:20,color:colors.accent,borderLeftWidth:3,borderColor:colors.accent,paddingLeft:12},footer:{fontSize:10,letterSpacing:1,marginTop:40,color:colors.muted}});
