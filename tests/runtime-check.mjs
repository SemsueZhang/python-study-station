import {chromium} from '@playwright/test';
import {readFile,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const course=JSON.parse(await readFile('src/data/course.json','utf8'));
const browser=await chromium.launch({headless:true,proxy:process.env.HTTPS_PROXY?{server:process.env.HTTPS_PROXY,bypass:'127.0.0.1,localhost'}:undefined});
const page=await browser.newPage();
await page.goto(process.env.SITE_URL||'http://127.0.0.1:4173/');
const results=[];
try{
 for(const e of course.examples){
  const result=await page.evaluate(e=>new Promise(resolve=>{
   const worker=new Worker(new URL('python-worker.js',document.baseURI));let output='',images=0;let timer=setTimeout(()=>{worker.terminate();resolve({status:'loading-timeout',output,images})},180000);
   worker.onmessage=({data})=>{
    if(data.type==='output')output+=data.text;
    if(data.type==='image')images++;
    if(data.type==='running'){clearTimeout(timer);timer=setTimeout(()=>{worker.terminate();resolve({status:'execution-timeout',output,images})},30000)}
    if(data.type==='error'||data.type==='done'){clearTimeout(timer);worker.terminate();resolve({status:data.type,output:output+(data.text||''),images})}
   };worker.onerror=e=>{clearTimeout(timer);worker.terminate();resolve({status:'worker-error',output:String(e.message),images})};worker.postMessage(e);
  }),e);
  const passed=e.expectedError?result.status==='error'&&result.output.includes(e.expectedError):result.status==='done';
  results.push({id:e.id,passed,...result});
  console.log(`${results.length}/${course.examples.length} ${e.id} ${passed?'PASS':'FAIL'} images=${result.images}`);
  if(!passed)console.log(result.output.slice(-1500));
  await writeFile('qa/runtime-results.json',JSON.stringify(results,null,2));
 }
 assert(results.every(r=>r.passed),'部分示例未通过');
 assert(results.some(r=>r.images>0),'未产生实际图表');
 console.log(`全部 ${results.length} 个示例通过真实浏览器 Pyodide 执行。`);
}finally{await browser.close()}
