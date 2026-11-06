# Python 学习站

公开网址：https://semsuezhang.github.io/python-study-station/

React + TypeScript + Vite 静态学习网站。内容来自仓库内的 `content/`，包含 7 章、72 个阅读小节、140 道单选题、149 段正文 Python 代码和 2 个补充实验。

## 本地使用

```sh
cd python-study-station
npm ci
npm run dev
```

开发服务默认只监听本机。构建与预览：

```sh
npm run sync-content
npm run check-content
npm run build
npm run preview
```

`dist/` 是静态构建产物，路由使用 `#/chapter/4/s2` 等哈希路径，不需要服务器重写规则。GitHub Pages 使用 `.github/workflows/pages.yml` 自动构建和发布。

## 内容更新

修改 `content/第N章_*.md` 后重新导入、检查、构建。也可用 `npm run sync-content -- /绝对路径/学习笔记` 指定来源。

- `src/data/course.json` 是纳入发布源码的完整生成数据，发布后无需访问原笔记目录。
- `src/data/run-manifest.json` 是运行清单，由内容检查命令生成。
- 章节以原章号识别，小节以原数字标题识别，题目以原章号和题号识别。示例以原代码的 SHA-256 摘要识别，因此重新导入、修改说明文字或调整同章内容顺序不会改变原代码的标识。
- `scripts/import-content.mjs` 保存默认输入、补齐的前置定义、调用示例与预期异常。这些配置通过 `scripts/example-anchors.json` 中的内容摘要锚定，不会因插入代码块而错位。修改被适配的代码时应同步更新锚点和适配，再重新运行示例测试。第 7 章依赖模块发生变化时，导入会主动报错以避免拼接不完整模块。
- `scripts/browser-adapters.mjs` 保存第 7 章离线客户端与合成行情适配。网页保留原正文，运行编辑器展示实际执行的适配代码，文件区展示虚拟模块。
- 导入时校验 20 题/章、ABCD 选项、唯一题号、答案与非空解析。内容检查进一步与原始 Markdown 逐项比较，覆盖正文、缩进、表格、公式和跨题引用。

## Python 运行

`public/python-worker.js` 在点击运行后才加载 Pyodide 0.29.3。运行环境来自 jsDelivr，pandas、matplotlib 等包同样按需加载，因此首次运行需要网络。阅读与题目无需等待解释器。

每次运行新建 Worker，代码与模块文件写入该次运行的虚拟文件系统。每次运行具有独立变量和模块环境，停止、出错、完成后释放 Worker。执行阶段超过 30 秒终止，加载超过 90 秒可重试。输出限制为 50,000 字符，防止无界输出拖慢页面。

输入框的每一行对应一次 `input()`，输入用尽时产生 EOFError。代码编辑器支持 Ctrl/Cmd+Enter 运行，Ctrl/Cmd+] 插入四个空格，Tab 正常切换焦点。绘图使用 Agg 后端，在 Python 中生成 PNG 并显示在运行区。

AI 示例使用 `mock_openai.py` 的固定响应，不调用真实 AI 服务。股票示例的 `sample_market.py` 返回明确标注的合成行情，原数据处理与绘图函数仍在 Pyodide 中执行。无需填写密钥，也不会保存密钥。

## 预计学习时间

首页显示全课程和各章参考时长，阅读页显示当前小节时长。估算根据正文长度、示例代码量和习题数量自动计算，全章包含阅读、动手运行与答题，小节只包含阅读和示例练习。章节按半小时区间取整，课程总时长为各章区间之和。这是初次学习的安排参考，不是实测用时，也不表示达到熟练程度所需的时间。

## 学习记录

使用 `localStorage` 的 `python-study-progress-v1` 键，保存完成小节、最近章节与滚动位置、每题最近答案、累计作答和答对次数。

阅读完成度按手动标记的小节计算。答题正确率为所有提交中答对次数/总作答次数。错题本包含最近一次答错的题，重练答对后移出。随机练习每轮无放回抽取 20 题。本轮题序和未提交选择保存在当前页面内，重新进入随机练习会开始新一轮。

记录仅属于当前浏览器和站点域名，不跨设备同步。清除浏览器网站数据会清除记录。存储失败时页面显示提示并继续提供学习功能。

## 验收脚本

```sh
npm run check-content
npx playwright install chromium --only-shell
node tests/browser-check.mjs
node tests/runtime-check.mjs
node tests/interaction-check.mjs
```

默认测试生产预览 `http://127.0.0.1:4173/`。可用 `SITE_URL` 指定已发布网址。`PLAYWRIGHT_BROWSERS_PATH` 可指定浏览器安装位置，`HTTPS_PROXY` 可指定测试网络代理。

- `browser-check.mjs` 生成桌面/手机截图与 axe WCAG 检查结果。
- `runtime-check.mjs` 在真实浏览器 Worker 中执行全部运行清单，检查成功或预期异常，并确认实际生成图表。
- `interaction-check.mjs` 覆盖学习进度、全文搜索、答题、随机题、错题、互动演示、输入输出、变量隔离、手动停止、真实 30 秒超时及下载失败重试。
- 测试结果保存在 `qa/`。本地有限测试不代表所有浏览器或所有修改后的任意 Python 程序都已验证。

## 发布

推送到 `main` 后，GitHub Actions 自动安装依赖、导入内容、校验 7 章与 140 道题、构建并发布到 GitHub Pages。首次需要在仓库 Settings → Pages 中选择 GitHub Actions。

部署地址：https://semsuezhang.github.io/python-study-station/

网站采用相对资源路径，Worker 与字体均从当前项目子目录加载。原 Sites 网址继续保留。不同域名的浏览器学习记录互相独立，不会自动迁移。
