import {chromium,expect} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const browser=await chromium.launch({headless:true,proxy:process.env.HTTPS_PROXY?{server:process.env.HTTPS_PROXY,bypass:'127.0.0.1,localhost'}:undefined});
const context=await browser.newContext({viewport:{width:1280,height:900}});const page=await context.newPage();
const base=process.env.SITE_URL||'http://127.0.0.1:4173/';const results=[];
async function check(name,fn){try{await fn();results.push({name,passed:true});console.log('PASS',name)}catch(e){results.push({name,passed:false,error:String(e)});console.log('FAIL',name,String(e).slice(0,500))}await writeFile('qa/interaction-results.json',JSON.stringify(results,null,2))}
await check('章节深链接、完成标记和阅读位置刷新恢复',async()=>{
 await page.goto(base+'#/chapter/1/s1');await page.getByRole('button',{name:'标记本小节已完成'}).click();
 await page.evaluate(()=>window.scrollTo(0,400));await page.waitForTimeout(600);await page.reload();
 await expect(page.getByRole('button',{name:'已完成本小节 · 撤销'})).toBeVisible();
 await page.waitForTimeout(500);assert(Math.abs(await page.evaluate(()=>scrollY)-400)<25);
 await page.goto(base+'#/');await page.getByRole('link',{name:'继续上次学习'}).click();assert(page.url().endsWith('#/chapter/1/s1'));
});
await check('全文搜索与目标小节跳转',async()=>{
 await page.getByRole('textbox',{name:'搜索全部笔记与习题'}).fill('高内聚');
 await page.locator('.search-results a').first().click();await expect(page.locator('.reader')).toContainText('高内聚');
});
await check('按章答题、原解析、错题持久化及重练移出',async()=>{
 await page.goto(base+'#/practice/chapter/1');await page.getByRole('radio').nth(0).check();await page.getByRole('button',{name:'提交答案'}).click();
 await expect(page.locator('.answer-explanation')).toContainText('正确答案 B');
 await page.reload();await page.goto(base+'#/practice/wrong');await expect(page.locator('.question-caption')).toContainText('原第 1 题');
 await page.getByRole('radio').nth(1).check();await page.getByRole('button',{name:'提交答案'}).click();await expect(page.locator('.answer-explanation')).toContainText('答对了');
 await page.reload();await expect(page.locator('main')).toContainText('暂时没有待复习的错题');
 const p=await page.evaluate(()=>JSON.parse(localStorage.getItem('python-study-progress-v1')));assert.equal(p.answers['ch1-q1'].attempts,2);assert.equal(p.answers['ch1-q1'].correctAttempts,1);
});
await check('随机抽取20题无重复、跨题代码完整',async()=>{
 await page.goto(base+'#/practice/random');assert.equal(await page.locator('.question-dots button').count(),20);
 const labels=await page.locator('.question-dots button').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('aria-label')?.split('原')[1]));assert.equal(new Set(labels).size,20);
 const data=await import('../src/data/course.json',{with:{type:'json'}});const refs=data.default.chapters.flatMap(c=>c.questions).filter(q=>q.context);
 for(const q of refs){await page.goto(base+'#/practice/question/'+q.id);await expect(page.locator('.question-context')).toContainText('原第 '+q.context.number+' 题');assert(await page.locator('.question-context code').count()>0)}
});
await check('互动切片、循环、函数、递归单步播放重置',async()=>{
 await page.goto(base+'#/lab');await expect(page.locator('.slice-result')).toContainText('"yh"');await page.getByRole('button',{name:'倒过来看看'}).click();await expect(page.locator('.slice-result')).toContainText('"nohtyP"');
 for(const name of ['循环与变量','函数调用','递归调用栈']){await page.getByRole('tab',{name}).click();await page.getByRole('button',{name:'下一步',exact:true}).click();await expect(page.locator('.step-description')).toContainText('2 /');await page.getByRole('button',{name:'播放过程'}).click();await page.waitForTimeout(1100);await page.getByRole('button',{name:'暂停',exact:true}).click();await expect(page.locator('.step-description')).toContainText('3 /');await page.getByRole('button',{name:'重置',exact:true}).click();await expect(page.locator('.step-description')).toContainText('1 /')}
});
await check('Python首次加载、输入输出、连续运行及变量隔离',async()=>{
 await page.goto(base+'#/lab');const runner=page.locator('.runner').first();await runner.getByRole('button',{name:'运行代码'}).click();await expect(runner.locator('.run-status')).toHaveText('运行完成',{timeout:180000});await expect(runner.locator('.output')).toContainText('你好，小林');
 await runner.locator('.code-editor').fill('x = 123\nprint(x)');await runner.getByRole('button',{name:'运行代码'}).click();await expect(runner.locator('.run-status')).toHaveText('运行完成',{timeout:90000});await expect(runner.locator('.output')).toContainText('123');
 await runner.locator('.code-editor').fill('print("x" in globals())');await runner.getByRole('button',{name:'运行代码'}).click();await expect(runner.locator('.run-status')).toHaveText('运行完成',{timeout:90000});await expect(runner.locator('.output')).toContainText('False');
});
await check('停止死循环后恢复执行',async()=>{
 const runner=page.locator('.runner').first();await runner.locator('.code-editor').fill('while True:\n    pass');await runner.getByRole('button',{name:'运行代码'}).click();await expect(runner.locator('.run-status')).toHaveText('运行中…',{timeout:90000});await runner.getByRole('button',{name:'停止',exact:true}).click();await expect(runner.locator('.run-status')).toContainText('已停止');
 await runner.locator('.code-editor').fill('print("recovered")');await runner.getByRole('button',{name:'运行代码'}).click();await expect(runner.locator('.run-status')).toHaveText('运行完成',{timeout:90000});await expect(runner.locator('.output')).toContainText('recovered');
});
await check('30秒真实执行超时与重建恢复',async()=>{
 const runner=page.locator('.runner').first();await runner.locator('.code-editor').fill('while True:\n    pass');await runner.getByRole('button',{name:'运行代码'}).click();await expect(runner.locator('.run-status')).toHaveText('运行中…',{timeout:90000});const start=Date.now();await expect(runner.locator('.run-status')).toContainText('运行超过 30 秒',{timeout:35000});assert(Date.now()-start>=28500);
 await runner.getByRole('button',{name:'恢复',exact:true}).click();await runner.getByRole('button',{name:'运行代码'}).click();await expect(runner.locator('.run-status')).toHaveText('运行完成',{timeout:90000});
});
await check('解释器下载失败仍可阅读、解除故障后重试',async()=>{
 await context.route('**/pyodide.js',r=>r.abort());const runner=page.locator('.runner').first();await runner.getByRole('button',{name:'运行代码'}).click();await expect(runner.locator('.run-status')).toContainText('错误',{timeout:30000});
 await page.goto(base+'#/chapter/2/s1');await expect(page.locator('.reader')).toContainText('表达式');
 await context.unroute('**/pyodide.js');await page.goto(base+'#/lab');const retry=page.locator('.runner').first();await retry.getByRole('button',{name:'运行代码'}).click();await expect(retry.locator('.run-status')).toHaveText('运行完成',{timeout:90000});
});
await check('移动端目录、页面宽度、键盘和减少动态效果',async()=>{
 await page.setViewportSize({width:390,height:844});await page.emulateMedia({reducedMotion:'reduce'});
 for(const hash of ['#/','#/chapter/7/s8','#/practice/chapter/4','#/lab']){await page.goto(base+hash);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),hash+' 横向溢出')}
 await page.getByRole('button',{name:'展开目录'}).click();await expect(page.locator('.sidebar')).toBeVisible();await page.locator('.sidebar').getByRole('link',{name:'学习概览'}).click();await expect(page.locator('.sidebar')).not.toBeVisible();
 await page.keyboard.press('Tab');assert(await page.evaluate(()=>document.activeElement.tagName!=='BODY'));
 await page.goto(base+'#/lab');await page.getByRole('tab',{name:'字符串切片'}).focus();await page.keyboard.press('ArrowRight');await expect(page.getByRole('tab',{name:'循环与变量'})).toBeFocused();
 assert.equal(await page.evaluate(()=>matchMedia('(prefers-reduced-motion: reduce)').matches),true);
 await page.screenshot({path:'qa/lab-mobile.png',fullPage:true});
});
await browser.close();assert(results.every(r=>r.passed),'交互检查存在失败项');
