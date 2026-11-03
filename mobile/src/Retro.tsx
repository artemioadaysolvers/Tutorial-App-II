import React,{useEffect,useState} from 'react';
import {AccessibilityInfo,Text as NativeText,StyleSheet,useWindowDimensions,View,type TextProps} from 'react-native';
import {Canvas,Line,Path,Skia,Text,useFont,vec} from '@shopify/react-native-skia';
export const colors={paper:'#eee8d8',ink:'#272920',muted:'#636659',accent:'#8b3828',line:'#c7c5b4'};
export function T(props:TextProps){return <NativeText {...props} style={[{fontFamily:'LMMono12-Regular',fontSize:17,color:colors.ink,lineHeight:24},props.style]}/>;}
export function Paper(){const {width,height}=useWindowDimensions();return <Canvas pointerEvents="none" style={StyleSheet.absoluteFill}>{Array.from({length:Math.ceil(height/28)},(_,i)=><Line key={i} p1={vec(0,i*28+12)} p2={vec(width,i*28+12)} color={colors.line} opacity={0.23} strokeWidth={0.5}/>)}<Line p1={vec(19,0)} p2={vec(19,height)} color={colors.accent} opacity={0.2} strokeWidth={1}/></Canvas>;}
export function Heading(){
  const font=useFont(require('../assets/fonts/lmmono12-regular.otf'),35);
  const [length,setLength]=useState(8);
  useEffect(()=>{let timer:ReturnType<typeof setInterval>|undefined;let alive=true;AccessibilityInfo.isReduceMotionEnabled().then(reduced=>{if(!alive||reduced)return;setLength(0);timer=setInterval(()=>setLength(n=>{if(n>=8&&timer)clearInterval(timer);return Math.min(8,n+1);}),95);});return()=>{alive=false;if(timer)clearInterval(timer);};},[]);
  return <View accessible accessibilityRole="header" accessibilityLabel="AutoMind" style={{height:64}}>{font?<Canvas style={{height:60}}><Text x={0} y={42} text={'AUTOMIND'.slice(0,length)} font={font} color={colors.ink}/><Line p1={vec(0,56)} p2={vec(275,56)} strokeWidth={2} color={colors.ink}/></Canvas>:<T style={{fontSize:32}}>AUTOMIND</T>}</View>;
}
export function Plot({values}:{values:number[]}){
  const {width}=useWindowDimensions(),w=Math.max(160,Math.min(width-80,520)),h=100;
  if(values.length<2)return null;
  const lo=Math.min(...values),range=Math.max(...values)-lo||1;
  const path=Skia.Path.Polygon(values.map((v,i)=>vec(8+i*(w-16)/(values.length-1),h-8-(v-lo)*(h-16)/range)),false);
  return <Canvas accessible accessibilityLabel="Gráfico de los valores pronosticados, detallados debajo" style={{width:w,height:h,marginVertical:12}}><Line p1={vec(4,h-3)} p2={vec(w,h-3)} color={colors.line} strokeWidth={1}/><Path path={path} style="stroke" color={colors.accent} strokeWidth={2}/></Canvas>;
}
