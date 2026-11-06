import { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkCjkFriendly from 'remark-cjk-friendly';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { remarkTermCards } from '../remarkTermCards';
import { CodeBlock } from './Runner';
import type { Example } from '../types';
export const Markdown = memo(function Markdown({text,examples=[]}: {text:string;examples?:Example[]}) {
 return <div className="markdown"><ReactMarkdown remarkPlugins={[remarkGfm,remarkMath,remarkCjkFriendly,remarkTermCards]} rehypePlugins={[rehypeKatex]} components={{
  pre:({children})=><>{children}</>,
  code:({className,children})=>{const code=String(children).replace(/\n$/,'');const language=/language-(\w+)/.exec(className||'')?.[1];if(language||code.includes('\n'))return <CodeBlock code={code} language={language||'text'} example={examples.find(e=>e.original.trim()===code.trim())}/>;return <code>{children}</code>},
  a:({href,children})=>{
   let decoded=href||'';
   try{decoded=decodeURIComponent(decoded)}catch{/* Leave malformed links unchanged. */}
   const chapter=/^第(\d+)章_[^/]+\.md#(\d+)-/.exec(decoded);
   if(chapter)return <a href={`#/chapter/${chapter[1]}/s${chapter[2]}`}>{children}</a>;
   if(href?.startsWith('#'))return <a href={href}>{children}</a>;
   return <a href={href} target="_blank" rel="noreferrer">{children}</a>;
  },
  table:({children})=><div className="table-scroll" tabIndex={0} role="region" aria-label="可横向滚动的表格"><table>{children}</table></div>
 }}>{text}</ReactMarkdown></div>;
}, (a,b)=>a.text===b.text&&(a.examples?.length||0)===(b.examples?.length||0)&&(a.examples||[]).every((example,i)=>example===b.examples?.[i]));
