import {chromium,expect} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const base=process.env.SITE_URL;if(!base)throw new Error('SITE_URL required');
const browser=await chromium.launch({headless:true,proxy:process.env.HTTPS_PROXY?{server:process.env.HTTPS_PROXY,bypass:'127.0.0.1,localhost'}:undefined});
const context=await browser.newContext({viewport:{width:1365,height:1000}});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));const checks=[];const record=text=>{checks.push(text);console.log('PASS',text)};
try{
 const response=await page.goto(base,{waitUntil:'networkidle'});assert.equal(response.status(),200);await expect(page.getByRole('heading',{name:/从好奇出发/ })).toBeVisible();record('匿名首页 HTTP 200、React 内容完整呈现');
 await page.goto(base+'#/chapter/1/s1');await page.reload();await expect(page.locator('.reader')).toContainText('计算机的功能性与可编程性');record('章节深链接直接打开与刷新');
 await expect(page.locator('.reader strong').filter({hasText:'直接写'})).toContainText('类型错误');await page.getByRole('button',{name:'动手运行'}).first().click();const runner=page.locator('.runner').first();await runner.getByRole('button',{name:'运行代码'}).click();await page.evaluate(()=>window.scrollBy(0,180));await page.waitForTimeout(500);await expect(runner.locator('.run-status')).toHaveText('运行完成',{timeout:180000});await expect(runner.locator('.output')).toHaveText('5\n');record('章节运行过程中滚动不丢失状态、Worker 实际输出 5');
 await page.goto(base+'#/lab');const stock=page.locator('.demo-section').filter({hasText:'股票数据处理'});await stock.getByRole('button',{name:'运行代码'}).click();await expect(stock.locator('.run-status')).toHaveText('运行完成',{timeout:180000});await expect(stock.locator('.output')).toContainText('return_pct');await expect(stock.locator('.plot-output')).toBeVisible();await stock.locator('.plot-output').screenshot({path:'qa/published-plot.png'});record('线上 pandas 数据计算和 matplotlib 实际绘图');
 await page.setViewportSize({width:390,height:844});await page.goto(base+'#/chapter/4/s2');await expect(page.locator('.reader')).toContainText('索引与切片');assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.screenshot({path:'qa/published-mobile-reader.png',fullPage:true});record('线上手机阅读无页面横向溢出');
 assert.equal(errors.length,0);await writeFile('qa/published-results.json',JSON.stringify({url:base,checks,errors,anonymous:true,passed:true},null,2));console.log(JSON.stringify({url:base,checks,errors,passed:true},null,2));
}finally{await browser.close()}
