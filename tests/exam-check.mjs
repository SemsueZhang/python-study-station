import {chromium, expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {createExam, drawQuestions, gradeExam, parseExam, EXAM_STORAGE_KEY} from '../src/examState.ts';

const bank = JSON.parse(await readFile('src/data/question-bank.json', 'utf8')).questions;
const byId = new Map(bank.map(q => [q.id, q]));
const base = process.env.SITE_URL || 'http://127.0.0.1:4173/';
const checks = [];
const browser = await chromium.launch({headless: true});
const context = await browser.newContext({viewport: {width: 1365, height: 1000}});
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
async function check(name, fn) {
  try { await fn(); checks.push({name, passed: true}); console.log('PASS', name); }
  catch (error) { checks.push({name, passed: false, error: String(error)}); console.log('FAIL', name, String(error)); }
  await writeFile('qa/exam-results.json', JSON.stringify({base, checks, errors}, null, 2)+'\n');
}
async function stored() { return page.evaluate(key => JSON.parse(localStorage.getItem(key)), EXAM_STORAGE_KEY); }
async function choose(label) { await page.locator(`.question-card input[value="${label}"]`).check(); }
async function jump(index) { await page.locator('.exam-dots button').filter({hasText: new RegExp(`^${index+1}$`)}).click(); }

await check('抽题只来自新增500题，每卷恰为50个不同题号', async () => {
  const seen = new Set();
  for (let i = 0; i < 200; i++) {
    const ids = drawQuestions(bank);
    assert.equal(ids.length, 50); assert.equal(new Set(ids).size, 50);
    assert(ids.every(id => byId.has(id))); ids.forEach(id => seen.add(id));
  }
  assert(seen.size > 450);
  assert.throws(() => drawQuestions(bank.slice(0, 49)));
  assert.throws(() => drawQuestions([...bank.slice(0, 49), bank[0]]));
});
await check('评分边界与损坏存档恢复校验', async () => {
  const s = createExam(bank);
  assert.equal(gradeExam(s, bank).score, 0);
  assert.equal(gradeExam(s, bank).unanswered, 50);
  s.questionIds.forEach(id => s.answers[id] = byId.get(id).answer);
  assert.equal(gradeExam(s, bank).score, 100);
  assert.deepEqual(parseExam(JSON.stringify(s), bank), s);
  assert.equal(parseExam('bad json', bank), null);
  assert.equal(parseExam(JSON.stringify({...s, questionIds: Array(50).fill('bank-001')}), bank), null);
  assert.equal(parseExam(JSON.stringify({...s, answers: {'old-q1': 'A'}}), bank), null);
  assert.equal(parseExam(JSON.stringify({...s, index: -1}), bank), null);
  assert.equal(parseExam(JSON.stringify({...s, submittedAt: s.startedAt-1}), bank), null);
});
await check('新旧题库分开练习、搜索与640题统计', async () => {
  await page.goto(base+'#/');
  await page.evaluate(() => localStorage.setItem('python-study-progress-v1', JSON.stringify({version:1,completed:['ch1-intro'],lastRead:{chapter:1,section:'intro'},answers:{'ch1-q1':{selected:'B',correct:true,attempts:3,correctAttempts:2}}})));
  await page.reload();
  await expect(page.locator('.stats-row')).toContainText('/ 640');
  await page.goto(base+'#/practice/bank');
  assert.equal(await page.locator('.practice-chapter').count(), 7);
  const counts = await page.locator('.practice-chapter p').allTextContents();
  assert.deepEqual(counts.map(s => Number(s.match(/\d+/)[0])), [50,65,85,90,90,65,55]);
  await page.goto(base+'#/practice/chapter/1');
  assert.equal(await page.locator('.question-dots button').count(), 20);
  await page.goto(base+'#/practice/bank/all');
  assert.equal(await page.locator('.question-dots button').count(), 50);
  await page.getByRole('button',{name:'下一组题号'}).click();
  await expect(page.locator('.question-caption')).toContainText('新增第 51 题');
  await page.getByRole('textbox',{name:'搜索全部笔记与习题'}).fill('奖学金名单');
  await page.locator('.search-results a[href="#/practice/question/bank-001"]').click();
  await choose(bank[0].answer); await page.getByRole('button',{name:'提交答案',exact:true}).click();
  await expect(page.locator('.answer-explanation')).toContainText('答对了');
  assert.equal(await page.locator('.answer-details').getAttribute('open'), null);
  await page.locator('.answer-details summary').click();
  await expect(page.locator('.answer-details')).toContainText(bank[0].explanation);
});
await check('原题判分、跨题引用及两种20题随机练习回归', async () => {
  const isolated = await browser.newContext(), p = await isolated.newPage();
  await p.goto(base+'#/practice/chapter/1');
  await p.locator('input[value="A"]').check(); await p.getByRole('button',{name:'提交答案',exact:true}).click();
  await expect(p.locator('.answer-explanation')).toContainText('正确答案 B');
  await p.goto(base+'#/practice/wrong'); await p.locator('input[value="B"]').check();
  await p.getByRole('button',{name:'提交答案',exact:true}).click();
  await p.reload(); await expect(p.locator('main')).toContainText('暂时没有待复习的错题');
  for (const route of ['random','bank-random']) {
    await p.goto(base+'#/practice/'+route);
    const labels = await p.locator('.question-dots button').evaluateAll(nodes => nodes.map(n=>n.getAttribute('aria-label').split('，')[1]));
    assert.equal(labels.length,20); assert.equal(new Set(labels).size,20);
    if(route==='bank-random') assert(labels.every(label=>label.includes('新增')));
  }
  await p.goto(base+'#/practice/question/ch7-q3');
  await expect(p.locator('.question-context')).toContainText('fact(n)');
  await isolated.close();
});
let firstSession;
await check('开始考试、交卷前无答案、切题改选清除与标记', async () => {
  await page.goto(base+'#/exam');
  await page.screenshot({path:'qa/exam-intro-desktop.png',fullPage:true});
  await page.getByRole('button',{name:'开始考试',exact:true}).click();
  assert.equal(await page.locator('.exam-dots button').count(), 50);
  firstSession = await stored();
  assert.equal(new Set(firstSession.questionIds).size, 50);
  assert(firstSession.questionIds.every(id => byId.has(id)));
  assert.equal(await page.locator('.answer-explanation, .option.right, .option.wrong').count(), 0);
  await choose('A'); await choose('C');
  await page.getByRole('button',{name:'标记待检查',exact:true}).click();
  await jump(1); await choose('B'); await jump(0);
  await expect(page.locator('input[value="C"]')).toBeChecked();
  await expect(page.getByRole('button',{name:'取消待检查',exact:true})).toHaveAttribute('aria-pressed','true');
  await page.getByRole('button',{name:'清除本题选择',exact:true}).click();
  assert.equal(await page.locator('input:checked').count(), 0);
  const progress = await page.evaluate(() => JSON.parse(localStorage.getItem('python-study-progress-v1')));
  assert(!progress.examIds?.length);
  await page.screenshot({path:'qa/exam-active-desktop.png',fullPage:true});
});
await check('刷新、离开考试再返回仍保留题序选项标记和计时起点', async () => {
  const before = await stored(); await page.reload();
  assert.deepEqual(await stored(), before);
  await page.goto(base+'#/practice/bank'); await page.goto(base+'#/exam');
  assert.deepEqual(await stored(), before);
  await jump(1); await expect(page.locator('input[value="B"]')).toBeChecked();
});
await check('49题作答、未答确认、60分计分、答案锁定与错题入库', async () => {
  const s = await stored();
  for (let i=0; i<49; i++) {
    await jump(i); const q = byId.get(s.questionIds[i]);
    await choose(i < 30 ? q.answer : (q.answer === 'A' ? 'B' : 'A'));
  }
  await jump(49); await page.getByRole('button',{name:'提交试卷',exact:true}).click();
  await expect(page.locator('.exam-confirm')).toContainText('还有 1 题未答');
  await page.getByRole('button',{name:'取消，返回试卷'}).click();
  assert.equal((await stored()).submittedAt, null);
  await page.getByRole('button',{name:'提交试卷',exact:true}).click();
  await page.getByRole('button',{name:'确认交卷',exact:true}).click();
  await expect(page.locator('.exam-result h2')).toContainText('60');
  await expect(page.locator('.exam-result')).toContainText('答错 19 题 · 未答 1 题');
  assert.equal(await page.locator('.exam-chapters > span').count(), 7);
  assert.equal(await page.locator('input[type="radio"]:disabled').count(), 4);
  await expect(page.locator('.answer-explanation')).toContainText('本题未作答');
  await page.getByRole('button',{name:'只看错题与未答题',exact:true}).click();
  assert.equal(await page.locator('.exam-dots button').count(), 20);
  await expect(page.getByRole('button',{name:'上一题',exact:true})).toBeDisabled();
  await page.getByRole('button',{name:'下一题',exact:true}).click();
  await expect(page.locator('.question-caption')).toContainText(`新增第 ${byId.get(s.questionIds[31]).number} 题`);
  await page.getByRole('button',{name:'上一题',exact:true}).click();
  await page.locator('.answer-details summary').click();
  await expect(page.locator('.answer-details')).toContainText(byId.get(s.questionIds[30]).explanation);
  await page.screenshot({path:'qa/exam-result-desktop.png',fullPage:true});
  await page.reload();
  const p = await page.evaluate(() => JSON.parse(localStorage.getItem('python-study-progress-v1')));
  assert.equal(p.examIds.length, 1); assert.equal(p.answers['ch1-q1'].attempts,3);
  for (const id of s.questionIds) assert.equal(p.answers[id].attempts, id==='bank-001' ? 2 : 1);
  await page.goto(base+'#/practice/wrong');
  assert.equal(await page.locator('.question-dots button').count(), 20);
});
await check('错题重练后重新打开已交试卷不会重复计次或重新加入错题', async () => {
  const s = await stored(), id=s.questionIds[30];
  await page.goto(base+'#/practice/question/'+id);
  await choose(byId.get(id).answer); await page.getByRole('button',{name:'提交答案',exact:true}).click();
  await page.goto(base+'#/exam'); await page.reload();
  const p = await page.evaluate(() => JSON.parse(localStorage.getItem('python-study-progress-v1')));
  assert.equal(p.answers[id].attempts, id==='bank-001' ? 3 : 2); assert.equal(p.answers[id].correct,true);
  await page.goto(base+'#/practice/wrong'); assert.equal(await page.locator('.question-dots button').count(), 19);
});
await check('重新抽卷取消保留原卷，确认后新卷清空作答且不重复', async () => {
  await page.goto(base+'#/exam'); const before=await stored();
  await page.getByRole('button',{name:'重新抽卷',exact:true}).click();
  await page.getByRole('button',{name:'取消，返回试卷'}).click(); assert.deepEqual(await stored(),before);
  await page.getByRole('button',{name:'重新抽卷',exact:true}).click();
  await page.getByRole('button',{name:'确认重新抽卷',exact:true}).click();
  const after=await stored(); assert.notEqual(after.id,before.id);
  assert.notDeepEqual(after.questionIds,before.questionIds); assert.equal(new Set(after.questionIds).size,50);
  assert.deepEqual(after.answers,{}); assert.deepEqual(after.flagged,[]); assert.equal(after.submittedAt,null);
});
await check('桌面与手机可访问性、320/390px布局及键盘选择', async () => {
  for (const width of [1365,390,320]) {
    await page.setViewportSize({width,height:900});
    for (const hash of ['#/practice/bank','#/practice/bank/4','#/exam']) {
      await page.goto(base+hash);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth+1), width+hash);
      const axe = await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
      assert.equal(axe.violations.length,0,JSON.stringify(axe.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))));
    }
  }
  await page.setViewportSize({width:390,height:844});
  await page.locator('input[value="A"]').focus(); await page.keyboard.press('Space');
  await expect(page.locator('input[value="A"]')).toBeChecked();
  await page.evaluate(() => { document.activeElement?.blur(); window.scrollTo(0,0); });
  await page.screenshot({path:'qa/exam-mobile.png',fullPage:true});
});
await check('存储被禁用时明确提示，当前页仍能考试', async () => {
  const blocked=await browser.newContext();
  await blocked.addInitScript(() => { Storage.prototype.setItem = () => {throw new Error('disabled');}; });
  const p=await blocked.newPage(); await p.goto(base+'#/exam');
  await p.getByRole('button',{name:'开始考试',exact:true}).click();
  await expect(p.locator('.exam .notice')).toContainText('无法保存');
  await p.locator('input[value="B"]').check();
  await expect(p.locator('.exam-summary')).toContainText('已作答 1 / 50');
  await blocked.close();
});
await browser.close();
assert.equal(errors.length,0,errors.join('\n'));
assert(checks.every(c=>c.passed),'考试验收存在失败项');
