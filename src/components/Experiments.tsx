import { useEffect, useState } from 'react';
import { Play, Pause, SkipForward, RotateCcw, ArrowDown, ArrowRight, Braces, Repeat2, Layers, Scissors } from 'lucide-react';
const names=['字符串切片','循环与变量','函数调用','递归调用栈'];
const icons=[Scissors,Repeat2,Braces,Layers];
export function Experiments({initial=0,embedded=false}: {initial?:number;embedded?:boolean}) {
 const [tab,setTab]=useState(initial);
 return <section className={`experiments ${embedded?'embedded':''}`}>
  {!embedded&&<><div className="eyebrow">LEARN BY DOING · 动手发现规律</div><h1>让知识，动起来<span className="accent-dot">。</span></h1><p className="page-lead">改一个参数，走一步代码。把看不见的执行过程，变成看得见的理解。</p></>}
  <div className="experiment-tabs" role="tablist" aria-label="互动演示">{names.map((name,i)=>{const Icon=icons[i];return <button key={name} role="tab" aria-selected={tab===i} tabIndex={tab===i?0:-1} onKeyDown={e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();const next=e.key==='Home'?0:e.key==='End'?3:(i+(e.key==='ArrowRight'?1:3))%4;setTab(next);(e.currentTarget.parentElement?.children[next] as HTMLButtonElement)?.focus()}}} onClick={()=>setTab(i)}><Icon size={18}/>{name}</button>})}</div>
  <div className="experiment-panel" role="tabpanel" aria-label={names[tab]}>{tab===0?<Slice/>:<Trace key={tab} kind={tab}/>}</div>
 </section>;
}
export function sliceIndices(length:number,start:number|null,stop:number|null,step:number) {
 if(!Number.isSafeInteger(step)||step===0)throw new Error('步长需要为非零整数');
 function normalize(value:number,negative:boolean){const index=value<0?value+length:value;return Math.max(negative?-1:0,Math.min(negative?length-1:length,index))}
 const negative=step<0;
 const a=start===null?(negative?length-1:0):normalize(start,negative);
 const b=stop===null?(negative?-1:length):normalize(stop,negative);
 const indices=[];
 for(let i=a;negative?i>b:i<b;i+=step)indices.push(i);
 return indices;
}
function Slice() {
 const [text,setText]=useState('Python');const [start,setStart]=useState('1');const [end,setEnd]=useState('5');const [step,setStep]=useState('2');
 const chars=Array.from(text);let indices:number[]=[];let error='';
 try {for(const value of [start,end,step])if(value!==''&&(!/^-?\d+$/.test(value)||!Number.isSafeInteger(Number(value))))throw new Error('索引和步长请输入整数');indices=sliceIndices(chars.length,start===''?null:Number(start),end===''?null:Number(end),step===''?1:Number(step))}catch(e){error=(e as Error).message}
 const expression=`s[${start}:${end}${step!==''?':'+step:''}]`;
 return <><div className="experiment-heading"><div><span className="pill teal">第 4 章</span><h2>选中字符的每一种可能</h2><p>起点包含，终点排除。试试把步长改为负数。</p></div><Scissors size={34}/></div>
 <div className="slice-controls"><label>字符串<input maxLength={24} value={text} onChange={e=>setText(e.target.value)}/></label><label>起点<input type="text" inputMode="numeric" value={start} placeholder="留空" onChange={e=>setStart(e.target.value)}/></label><label>终点<input type="text" inputMode="numeric" value={end} placeholder="留空" onChange={e=>setEnd(e.target.value)}/></label><label>步长<input type="text" inputMode="numeric" value={step} placeholder="1" onChange={e=>setStep(e.target.value)}/></label></div>
 <div className="character-track">{chars.map((char,i)=><div className={`character ${indices.includes(i)?'selected':''}`} key={i}><small>{i}</small><strong>{char===' '?'␣':char}</strong><small>{i-chars.length}</small>{indices.includes(i)&&<b>{indices.indexOf(i)+1}</b>}</div>)}{!chars.length&&<p>输入字符串，观察字符索引。</p>}</div>
 <div className="slice-result"><code>{expression}</code><ArrowRight size={20}/><strong>{error||JSON.stringify(indices.map(i=>chars[i]).join(''))}</strong></div>
 <div className="preset-buttons"><button onClick={()=>{setStart('');setEnd('');setStep('-1')}}>倒过来看看</button><button onClick={()=>{setStart('');setEnd('');setStep('2')}}>每隔一个字符</button><button onClick={()=>{setText('Python');setStart('1');setEnd('5');setStep('2')}}><RotateCcw size={13}/>恢复示例</button></div></>;
}
type Frame={line:number;description:string;values:Record<string,string|number>;stack?:{n:number;result?:number}[]};
function makeFrames(kind:number,n:number,factor:number): {code:string[];frames:Frame[]} {
 if(kind===1){const frames:Frame[]=[{line:0,description:'初始化累加器 total。',values:{total:0}}];let total=0;for(let i=1;i<=n;i++){frames.push({line:1,description:`循环取出 ${i}，赋给 i。`,values:{i,total}});total+=i;frames.push({line:2,description:`把 ${i} 加进 total。`,values:{i,total}})}frames.push({line:3,description:'循环结束，输出累加结果。',values:{total,输出:total}});return {code:['total = 0',`for i in range(1, ${n+1}):`,'    total += i','print(total)'],frames}}
 if(kind===2)return {code:['def scale(value, factor=2):','    result = value * factor','    return result','',`answer = scale(${n}, factor=${factor})`,'print(answer)'],frames:[{line:0,description:'执行函数定义，建立函数与名称的绑定。',values:{函数:'scale'}},{line:4,description:'调用函数，把实参传给形参。',values:{value:n,factor}},{line:1,description:'在函数局部环境中计算 result。',values:{value:n,factor,result:n*factor}},{line:2,description:'return 把计算结果交回调用处。',values:{返回值:n*factor}},{line:4,description:'调用完成，返回值赋给 answer。',values:{answer:n*factor}},{line:5,description:'在调用者的环境中输出 answer。',values:{answer:n*factor,输出:n*factor}}]};
 const frames:Frame[]=[];const stack:{n:number;result?:number}[]=[];
 for(let k=n;k>=0;k--){stack.push({n:k});frames.push({line:k===0?2:3,description:k===0?'到达基例，factorial(0) 返回 1。':`factorial(${k}) 等待 factorial(${k-1}) 的结果。`,values:{n:k},stack:stack.map(s=>({...s}))})}
 let result=1;stack.pop();for(let k=1;k<=n;k++){result*=k;if(stack.length)stack[stack.length-1].result=result;frames.push({line:3,description:`收到子调用结果，factorial(${k}) 返回 ${result}。`,values:{n:k,返回值:result},stack:stack.map(s=>({...s}))});stack.pop()}
 frames.push({line:4,description:'调用栈清空，输出最终结果。',values:{输出:result},stack:[]});return {code:['def factorial(n):','    if n == 0:','        return 1','    return n * factorial(n - 1)',`print(factorial(${n}))`],frames};
}
function Trace({kind}:{kind:number}) {
 const [n,setN]=useState(kind===2?3:4);const [factor,setFactor]=useState(2);const [index,setIndex]=useState(0);const [playing,setPlaying]=useState(false);
 const {code,frames}=makeFrames(kind,n,factor);const frame=frames[Math.min(index,frames.length-1)];
 useEffect(()=>{if(!playing)return;const timer=setInterval(()=>setIndex(old=>{if(old>=frames.length-1){setPlaying(false);return old}return old+1}),900);return()=>clearInterval(timer)},[playing,frames.length]);
 function changeN(value:number){setN(value);setIndex(0);setPlaying(false)}
 return <><div className="experiment-heading"><div><span className="pill purple">第 {kind+4} 章</span><h2>{kind===1?'每一步，都有迹可循':kind===2?'跟着参数，走进函数':'先展开，再一层层返回'}</h2><p>演示当前教学示例，彩色行表示正在执行的步骤。</p></div>{kind===3?<Layers size={34}/>:<Repeat2 size={34}/>}</div>
 <div className="trace-parameters"><label>{kind===1?'累加到':kind===2?'传入 value':'计算阶乘 n'}<input type="range" min={kind===3?0:1} max={kind===3?7:8} value={n} onChange={e=>changeN(Number(e.target.value))}/><strong>{n}</strong></label>{kind===2&&<label>factor<input type="range" min={1} max={5} value={factor} onChange={e=>{setFactor(Number(e.target.value));setIndex(0);setPlaying(false)}}/><strong>{factor}</strong></label>}</div>
 <div className="trace-grid"><div className="trace-code">{code.map((line,i)=><div key={i} className={frame.line===i?'active':''}><span>{i+1}</span><code>{line||' '}</code>{frame.line===i&&<ArrowRight size={14}/>}</div>)}</div><div className="state-board"><div className="state-caption">{kind===3?'当前调用栈':'当前变量'}</div>{kind===3?<div className="stack">{frame.stack?.length?frame.stack.map((s,i)=><div className="stack-frame" key={i}><code>factorial({s.n})</code><span>{s.result!==undefined?`返回 ${s.result}`:s.n===0?'基例':'等待子调用'}</span></div>):<div className="variable"><span>输出结果</span><strong>{frame.values['输出']}</strong></div>}</div>:<div className="variables">{Object.entries(frame.values).map(([key,value])=><div className="variable" key={key}><span>{key}</span><strong>{value}</strong></div>)}</div>}</div></div>
 <div className="step-description" aria-live="polite"><span>{index+1} / {frames.length}</span>{frame.description}</div>
 <div className="trace-actions"><button className="button primary" onClick={()=>{if(index>=frames.length-1)setIndex(0);setPlaying(!playing)}}>{playing?<Pause size={16}/>:<Play size={16}/>} {playing?'暂停':'播放过程'}</button><button className="button" disabled={index>=frames.length-1} onClick={()=>{setPlaying(false);setIndex(index+1)}}><SkipForward size={16}/>下一步</button><button className="button quiet" onClick={()=>{setIndex(0);setPlaying(false)}}><RotateCcw size={16}/>重置</button><ArrowDown className="trace-decoration" size={20}/></div></>;
}
