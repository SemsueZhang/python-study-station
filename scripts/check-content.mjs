import {readFile,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import {toString} from 'mdast-util-to-string';
const d=JSON.parse(await readFile('src/data/course.json','utf8'));
const source=process.argv[2]||'./content';
const parser=unified().use(remarkParse);
const ids=new Set();let bodyCodes=0,refs=0,tables=0;
function unique(id){assert(!ids.has(id),`重复 ID ${id}`);ids.add(id)}
function walk(node,fn){fn(node);node.children?.forEach(n=>walk(n,fn))}
assert.equal(d.chapters.length,7);assert.equal(d.examples.length,151);
for(const c of d.chapters){
 unique(`ch${c.id}`);assert.equal(c.questions.length,20);
 const text=await readFile(`${source}/${c.source}`,'utf8');
 const tree=parser.parse(text);
 const exercise=tree.children.find(n=>n.type==='heading'&&n.depth===2&&toString(n).startsWith('练习题'));
 const answer=tree.children.find(n=>n.type==='heading'&&n.depth===2&&toString(n).startsWith('参考答案'));
 const body=text.slice(0,exercise.position.start.offset);
 const bodyTree=parser.parse(body);
 const headings=bodyTree.children.filter(n=>n.type==='heading'&&n.depth===2);
 assert.equal(c.sections.length,headings.length+1);
 assert.equal(c.sections[0].markdown,body.slice(bodyTree.children[0].position.end.offset,headings[0].position.start.offset).trim());
 headings.forEach((h,i)=>assert.equal(c.sections[i+1].markdown,body.slice(h.position.end.offset,headings[i+1]?.position.start.offset??body.length).trim(),'正文须原样保留，包括代码缩进、表格、公式'));
 for(const s of c.sections){unique(`ch${c.id}-${s.id}`);tables+=(s.markdown.match(/^\|.*\|$/gm)||[]).length;}
 walk(bodyTree,n=>{if(n.type==='code'&&n.lang==='python'){bodyCodes++;const e=d.examples.find(e=>e.chapter===c.id&&e.original===n.value);assert(e,`缺少运行示例 ${c.id}: ${n.value.slice(0,50)}`);assert(c.sections.some(s=>s.id===e.section&&s.markdown.includes(e.original)));}});
 const qsource=text.slice(exercise.position.end.offset,answer.position.start.offset);
 const qt=parser.parse(qsource);const qh=qt.children.filter(n=>n.type==='heading'&&n.depth===3);
 const asource=text.slice(answer.position.end.offset);const answers=[...asource.matchAll(/^\*\*第(\d+)题\s+([A-D])\*\*\s*$/gm)];
 for(const [i,q] of c.questions.entries()){
  unique(q.id);assert.equal(q.number,i+1);assert.equal(q.options.map(o=>o.label).join(''),'ABCD');assert(q.options.every(o=>o.markdown));
  const chunk=qsource.slice(qh[i].position.end.offset,qh[i+1]?.position.start.offset??qsource.length).trim();
  // Recombine exactly, permitting only blank-line normalization between parts.
  const rebuilt=[q.prompt,...q.options.map(o=>`${o.label}. ${o.markdown}`)].join('\n\n');
  assert.equal(rebuilt.replace(/[ \t]+$/gm,'').replace(/\n{2,}/g,'\n'),chunk.replace(/[ \t]+$/gm,'').replace(/\n{2,}/g,'\n'),q.id+' 题干选项');
  const a=answers.find(a=>Number(a[1])===q.number);const ai=answers.indexOf(a);assert.equal(q.answer,a[2]);assert.equal(q.explanation,asource.slice(a.index+a[0].length,answers[ai+1]?.index??asource.length).trim());
  const ref=q.prompt.match(/第(\d+)题/);if(ref&&Number(ref[1])!==q.number){refs++;assert(q.context,q.id+' 跨题引用');assert.equal(q.context.prompt,c.questions[Number(ref[1])-1].prompt)}
 }
}
for(const e of d.examples){unique(e.id);assert(e.code.trim());assert(d.chapters.find(c=>c.id===e.chapter)?.sections.some(s=>s.id===e.section));assert(Object.keys(e.files).every(f=>!f.includes('/')&&!f.includes('..')))}
const manifest=d.examples.map(({id,chapter,section,expectedError,files,packages,note})=>({id,chapter,section,expectedError,files:Object.keys(files),packages,note}));
await writeFile('src/data/run-manifest.json',JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({chapters:d.chapters.length,questions:d.chapters.flatMap(c=>c.questions).length,sections:d.chapters.flatMap(c=>c.sections).length,bodyCodes,runnableExamples:d.examples.length,crossReferences:refs,tableRows:tables,status:'通过：源文、选项、答案、解析逐项一致'},null,2));
