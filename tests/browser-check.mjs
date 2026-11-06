import {chromium} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import {writeFile} from 'node:fs/promises';
const browser=await chromium.launch({headless:true,proxy:process.env.HTTPS_PROXY?{server:process.env.HTTPS_PROXY,bypass:'127.0.0.1,localhost'}:undefined});
const context=await browser.newContext({viewport:{width:1440,height:1100},deviceScaleFactor:1});
const page=await context.newPage();
const errors=[];page.on('pageerror',e=>errors.push(String(e)));
await page.goto(process.env.SITE_URL||'http://127.0.0.1:4173/',{waitUntil:'networkidle'});
await page.screenshot({path:'qa/home-desktop.png',fullPage:true});
const results=[];
for(const route of ['#/','#/chapter/4/s2','#/chapter/7/s7','#/chapter/7/s8','#/practice/chapter/1','#/lab']){
 await page.goto((process.env.SITE_URL||'http://127.0.0.1:4173/')+route);
 await page.waitForTimeout(300);
 const a=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
 results.push({route,violations:a.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))});
}
for(const name of ['循环与变量','函数调用','递归调用栈']){
 await page.getByRole('tab',{name}).click();const a=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();results.push({route:'#/lab/'+name,violations:a.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))});}
await page.screenshot({path:'qa/lab-desktop.png',fullPage:true});
await page.locator('.code-editor').first().focus();await page.keyboard.press('Tab');if(await page.locator('.code-editor').first().evaluate(n=>n===document.activeElement))throw new Error('代码编辑器捕获了Tab键');
await page.setViewportSize({width:390,height:844});
await page.goto((process.env.SITE_URL||'http://127.0.0.1:4173/')+'#/');
await page.screenshot({path:'qa/home-mobile.png',fullPage:true});
for(const hash of ['#/','#/chapter/4/s2','#/practice/chapter/1','#/lab']){await page.goto((process.env.SITE_URL||'http://127.0.0.1:4173/')+hash);const a=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();results.push({route:'mobile '+hash,violations:a.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))});}
await writeFile('qa/accessibility.json',JSON.stringify({errors,results},null,2));
console.log(JSON.stringify({errors,results:results.map(r=>({route:r.route,violations:r.violations.map(v=>({id:v.id,nodes:v.nodes.length}))}))},null,2));
await browser.close();
