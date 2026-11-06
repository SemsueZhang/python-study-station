import { useEffect, useRef, useState } from 'react';
import { Play, RotateCcw, Square, Terminal, ChevronDown, ChevronUp, Copy, Check, LoaderCircle } from 'lucide-react';
import type { Example } from '../types';
export function Runner({example,initiallyOpen=false}: {example: Example; initiallyOpen?: boolean}) {
 const [open,setOpen]=useState(initiallyOpen);
 const [code,setCode]=useState(example.code);
 const [input,setInput]=useState(example.input);
 const [output,setOutput]=useState('');
 const [images,setImages]=useState<string[]>([]);
 const [status,setStatus]=useState('');
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState(false);
 const worker=useRef<Worker|null>(null);
 const timer=useRef<ReturnType<typeof setTimeout>|null>(null);
 const cleanup=()=>{worker.current?.terminate();worker.current=null;if(timer.current)clearTimeout(timer.current);timer.current=null};
 useEffect(()=>()=>cleanup(),[]);
 function stop(message='已停止运行，可以修改代码后再试。') {cleanup();setBusy(false);setStatus(message)}
 function run() {
   cleanup();setOutput('');setImages([]);setError(false);setBusy(true);setStatus('正在启动 Python…');
   const current = new Worker(new URL('python-worker.js',document.baseURI));
   worker.current=current;
   timer.current=setTimeout(()=>stop('运行环境加载超过 90 秒，请检查网络后点击运行重试。'),90000);
   current.onmessage=({data})=>{
    if(data.type==='status')setStatus(data.text);
    if(data.type==='output')setOutput(old=>old+data.text);
    if(data.type==='image')setImages(old=>[...old,data.src]);
    if(data.type==='running'){if(timer.current)clearTimeout(timer.current);setStatus('运行中…');timer.current=setTimeout(()=>stop('运行超过 30 秒，已自动停止。请检查循环或缩小输入。'),30000)}
    if(data.type==='done'){cleanup();setBusy(false);setStatus('运行完成')}
    if(data.type==='error'){cleanup();setBusy(false);setError(true);setOutput(old=>old+data.text);setStatus('本次运行出现错误，可修改后重试')}
   };
   current.onerror=()=>{cleanup();setBusy(false);setError(true);setStatus('运行环境加载失败，请检查网络后点击运行重试。')};
   current.postMessage({code,input,files:example.files,packages:example.packages});
 }
 return <div className="runner">
  <button className="runner-toggle" onClick={()=>setOpen(!open)} aria-expanded={open}><span><Terminal size={16}/>动手运行</span>{open?<ChevronUp size={16}/>:<ChevronDown size={16}/>}</button>
  {open&&<div className="runner-body">
   {example.note&&<p className="runner-note">{example.note}</p>}
   {example.expectedError&&<p className="expected-error">错误示例 · 试调用预期触发 {example.expectedError}，结合正文观察原因。</p>}
   {Object.keys(example.files).length>0&&<details className="virtual-files"><summary>本次示例文件 · {Object.keys(example.files).join('、')}</summary>{Object.entries(example.files).map(([name,content])=><div key={name}><strong>{name}</strong><pre>{content}</pre></div>)}</details>}
   <label className="field-label" htmlFor={`${example.id}-code`}>Python 代码</label>
   <textarea id={`${example.id}-code`} className="code-editor" spellCheck={false} value={code} onChange={e=>setCode(e.target.value)} rows={Math.min(18,Math.max(5,code.split('\n').length))} onKeyDown={e=>{if(e.key===']'&&(e.ctrlKey||e.metaKey)){e.preventDefault();const el=e.currentTarget;const start=el.selectionStart;const end=el.selectionEnd;setCode(code.slice(0,start)+'    '+code.slice(end));requestAnimationFrame(()=>{el.selectionStart=el.selectionEnd=start+4})}if((e.ctrlKey||e.metaKey)&&e.key==='Enter'&&!busy){e.preventDefault();run()}}}/>
   <label className="field-label" htmlFor={`${example.id}-input`}>程序输入 <span>每行对应一次 input()</span></label>
   <textarea id={`${example.id}-input`} className="stdin" rows={2} value={input} onChange={e=>setInput(e.target.value)} placeholder="需要输入时，先在这里填写"/>
   <div className="runner-actions"><button className="button primary small" onClick={run} disabled={busy}>{busy?<LoaderCircle className="spin" size={15}/>:<Play size={15}/>}运行代码</button>{busy&&<button className="button small" onClick={()=>stop()}><Square size={14}/>停止</button>}<button className="button quiet small" disabled={busy} onClick={()=>{setCode(example.code);setInput(example.input);setOutput('');setImages([]);setStatus('已恢复原代码');setError(false)}}><RotateCcw size={14}/>恢复</button><span className="shortcut">⌘ / Ctrl + Enter</span></div>
   {status&&<p className={`run-status ${error?'error':''}`} role="status">{status}</p>}
   {(output||status==='运行完成')&&<pre className={`output ${error?'output-error':''}`} aria-label="运行输出">{output||'程序执行完成，没有文本输出。'}</pre>}
   {images.map((src,i)=><img key={i} className="plot-output" src={src} alt={`Python 实际生成的图表 ${i+1}`}/>)}
  </div>}
 </div>;
}
export function CodeBlock({code,language,example}: {code:string;language:string;example?:Example}) {
 const [copied,setCopied]=useState(false);
 async function copy(){try{await navigator.clipboard.writeText(code);setCopied(true);setTimeout(()=>setCopied(false),1800)}catch{setCopied(false)}}
 return <div className="code-block"><div className="code-caption"><span><i/>{language||'文本'}</span><button onClick={copy} aria-label="复制代码">{copied?<Check size={14}/>:<Copy size={14}/>} {copied?'已复制':'复制'}</button></div><pre><code>{code}</code></pre>{example&&<Runner example={example}/>}</div>;
}
