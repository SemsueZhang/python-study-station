import { chromium } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';

const course = JSON.parse(await readFile('src/data/course.json', 'utf8'));
const base = process.env.SITE_URL || 'http://127.0.0.1:4173/';
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
const result = { cards: 0, links: 0, sections: 0, examples: 0, accessibility: [], errors };
try {
  for (const chapter of course.chapters) {
    for (const section of chapter.sections) {
      await page.goto(`${base}#/chapter/${chapter.id}/${section.id}`);
      const body = page.locator('.reader > .markdown');
      await body.waitFor();
      const cards = body.locator('details.term-card');
      const expected = (section.markdown.match(/<details>/g) || []).length;
      assert.equal(await cards.count(), expected, `cards in ${chapter.id}/${section.id}`);
      assert.equal(await body.locator('details[open]').count(), 0);
      assert(!(await body.innerText()).includes('<details>'));
      for (let i = 0; i < expected; i++) {
        const card = cards.nth(i);
        assert.equal(await card.locator('p').first().isVisible(), false);
        await card.locator('summary').click();
        assert.equal(await card.locator('p').first().isVisible(), true);
        await card.locator('summary').focus();
        await page.keyboard.press('Enter');
        assert.equal(await card.getAttribute('open'), null);
        await page.keyboard.press('Space');
        assert.notEqual(await card.getAttribute('open'), null);
      }
      const links = body.locator('a[href^="#/chapter/"]');
      for (const link of await links.all()) {
        const href = await link.getAttribute('href');
        const [, chapterId, sectionId] = href.match(/^#\/chapter\/(\d+)\/(s\d+)$/);
        assert(course.chapters.find(c => c.id === Number(chapterId))?.sections.some(s => s.id === sectionId));
        assert.equal(await link.getAttribute('target'), null);
      }
      result.cards += expected;
      result.links += await links.count();
      result.sections++;
      const codeCount = (section.markdown.match(/^```python$/gm) || []).length;
      result.examples += codeCount;
      assert.equal(await body.locator('.code-block').count(), (section.markdown.match(/^```[^\n]*$/gm) || []).length / 2);
    }
  }
  await page.goto(`${base}#/chapter/1/intro`);
  await page.locator('.reader > .markdown a[href="#/chapter/4/s2"]').click();
  assert.equal(new URL(page.url()).hash, '#/chapter/4/s2');
  await page.goBack();
  assert.equal(new URL(page.url()).hash, '#/chapter/1/intro');
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 1100 });
    for (const route of ['1/s1', '6/s6', '7/s7']) {
      await page.goto(`${base}#/chapter/${route}`);
      for (const summary of await page.locator('.term-card > summary').all()) await summary.click();
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `overflow ${width}/${route}`);
      const a11y = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
      result.accessibility.push({ width, route, violations: a11y.violations.map(v => v.id) });
      assert.equal(a11y.violations.length, 0, JSON.stringify(a11y.violations.map(v => v.id)));
      if (route === '1/s1') {
        await page.locator('.term-card').first().scrollIntoViewIfNeeded();
        await page.screenshot({ path: `qa/learning-notes-${width}.png` });
      }
    }
  }
  assert.equal(errors.length, 0);
  assert.equal(result.cards, 33);
  assert.equal(result.examples, 149);
  await writeFile('qa/learning-notes.json', JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result, null, 2));
} finally {
  await browser.close();
}
