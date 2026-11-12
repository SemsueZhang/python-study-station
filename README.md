# Python 学习站

公开网址：https://semsuezhang.github.io/python-study-station/

React + TypeScript + Vite 静态学习网站。内容来自仓库内的 `content/`，包含 7 章、72 个阅读小节、原有 140 道与新增 500 道单选题、149 段正文 Python 代码和 2 个补充实验。

## 新增题库与考试

新增题库位于 `src/data/question-bank.json`，与原有 140 题独立保存。第1至7章分别新增50、65、85、90、90、65、55题，每题有四个选项、唯一答案、解析和对应阅读小节。入口为 `#/practice/bank`，可按章、顺序或随机20题练习，也纳入搜索与错题本。

`scripts/build-question-bank.py` 是题目编写源文件，生成时核对363道表达式及程序题的预先指定结果。`npm run check-bank` 独立检查发布数据中的结果、题号、选项、答案和知识点引用，并与原题检查规范化题干及代码重复。137道概念与情境题的解析写在题库中。ABCD正确选项各125题，题目不依赖别的题目的题干。

考试入口为 `#/exam`。每场从新增500题中无放回随机抽取50题，每题2分，共100分，不限时并记录用时。考生可切题、改选、清除选择和标记待检查。交卷前不展示答案，交卷需确认，未答题计0分。交卷后显示成绩、各章答对数及折叠解析，支持仅查看错题与未答题。这50题计入学习记录，错题与未答题进入错题本，同一场考试不会因刷新而重复计次。

当前试卷使用 `localStorage` 的 `python-study-exam-v1` 键保存，刷新、离开页面或重新打开同一浏览器可以继续，用时包含离开期间。重新抽卷会替换当前试卷并清空本场选择，已计入的学习统计保留。记录不跨设备同步。存储不可用时会提示并允许继续在当前页面作答。

验证新功能：

```sh
npm run check-bank
npm run build
npm run preview
# 另一个终端，先准备本机 Playwright 浏览器
npm run test:exam
```

`tests/exam-check.mjs` 覆盖无重复抽题、评分、损坏存档、刷新续答、答案锁定、错题记录、重复计次、重抽确认、手机布局和可访问性。`qa/question-bank-validation.json` 与 `qa/exam-results.json` 保存最近的验证结果。

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

## 阅读提示与术语解释

七章正文在提前使用新语法的位置说明当前学习要求，并链接到对应章节。术语解释用 `<details>` 与 `<summary>` 书写，网页默认折叠，支持鼠标、Enter 和空格展开。跨章链接在当前页面切换小节，原代码示例标识及学习记录沿用现有规则。

`src/remarkTermCards.ts` 只识别这类折叠容器，正文仍按 Markdown 渲染。导入内容时应保留标签后的空行，使解释中的列表、强调和链接正常解析。

本地运行 `node tests/learning-notes-check.mjs` 检查全部阅读小节、折叠交互、章节链接和桌面/手机可访问性。默认预览地址为 `http://127.0.0.1:4173/`，可通过 `SITE_URL` 指定其他地址。

## Python 运行

`public/python-worker.js` 在点击运行后才加载 Pyodide 0.29.3。运行环境来自 jsDelivr，pandas、matplotlib 等包同样按需加载，因此首次运行需要网络。阅读与题目无需等待解释器。

每次运行新建 Worker，代码与模块文件写入该次运行的虚拟文件系统。每次运行具有独立变量和模块环境，停止、出错、完成后释放 Worker。执行阶段超过 30 秒终止，加载超过 90 秒可重试。输出限制为 50,000 字符，防止无界输出拖慢页面。

输入框的每一行对应一次 `input()`，输入用尽时产生 EOFError。代码编辑器支持 Ctrl/Cmd+Enter 运行，Ctrl/Cmd+] 插入四个空格，Tab 正常切换焦点。绘图使用 Agg 后端，在 Python 中生成 PNG 并显示在运行区。

AI 示例使用 `mock_openai.py` 的固定响应，不调用真实 AI 服务。股票示例的 `sample_market.py` 返回明确标注的合成行情，原数据处理与绘图函数仍在 Pyodide 中执行。无需填写密钥，也不会保存密钥。

## 预计学习时间

首页显示全课程和各章参考时长，阅读页显示当前小节时长。估算根据正文长度、示例代码量和习题数量自动计算，全章包含阅读、动手运行与答题，小节只包含阅读和示例练习。各处统一显示估算区间的中点，小节取整到分钟，课程总时长为各章中点之和。这是初次学习的安排参考，不是实测用时，也不表示达到熟练程度所需的时间。

## 学习记录

使用 `localStorage` 的 `python-study-progress-v1` 键，保存完成小节、最近章节与滚动位置、每题最近答案、累计作答和答对次数。

阅读完成度按手动标记的小节计算。答题正确率为所有提交中答对次数/总作答次数。错题本包含最近一次答错的题，重练答对后移出。随机练习从全部640题中无放回抽取20题，新增题库也提供只抽新增题的20题练习。本轮练习题序和未提交选择保存在当前页面内，重新进入随机练习会开始新一轮。考试模式单独保存当前试卷与选择。

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

推送到 `main` 后，GitHub Actions 自动安装依赖、导入内容、校验7章原有140题及新增500题、构建并发布到 GitHub Pages。首次需要在仓库 Settings → Pages 中选择 GitHub Actions。

部署地址：https://semsuezhang.github.io/python-study-station/

网站采用相对资源路径，Worker 与字体均从当前项目子目录加载。原 Sites 网址继续保留。不同域名的浏览器学习记录互相独立，不会自动迁移。
