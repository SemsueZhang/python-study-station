import { adaptedExample } from './browser-adapters.mjs';
import { readFile, readdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import { toString } from 'mdast-util-to-string';
import { resolve } from 'node:path';
const source = resolve(process.argv[2] || './content');
const parser = unified().use(remarkParse);
const colors = ['#7558df','#3d86d6','#d88726','#1a9b91','#dd6b50','#a45bc8','#5377ca'];
const descriptions = ['从一个想法，到第一行代码','让变量、输入和输出一起工作','理解数字，发现运算的规律','把每个字符用得恰到好处','让程序学会选择与重复','把解决办法变成可复用的函数','从小问题出发，构建完整程序'];
const defaultInputs = {1:{3:'小林'},2:{11:'42',12:'3\n12.5',19:'82F',20:'25C',22:'RMB67.8',23:'2'},4:{18:'3'},5:{5:'12',6:'2',7:'1.75\n65',12:'-1\nabc\n3'}};
const suffixes = {2:{9:'print(fahrenheit)'},4:{0:'print(name, message, number_text)',20:'print("UTC", utc_time)\nprint("本地", local_time)\nprint(readable)'},5:{1:'print("已完成短路判断")'},6:{1:'print(factorial(5))',3:'print(message)',10:'print(collect(1))\nprint(collect(2))',13:'print(absolute_value(-5))',14:'print(first())\nprint(second())',19:'improve()',20:'print(score)'},7:{0:'print(factorial(5))',1:'print(bad_factorial(3))',2:'print(wrong_factorial(3))',3:'print(reverse_text("Python"))',5:'print(fibonacci(8))',6:'print(fibonacci_loop(8))',7:'hanoi(3, "A", "C", "B")'}};
const expectedErrors = {6:{19:'UnboundLocalError'},7:{1:'RecursionError',2:'TypeError'}};
const hash = code => createHash('sha256').update(code.trim()).digest('hex').slice(0,12);
// Hash anchors keep curated contexts attached to their original code when prose or block order changes.
const codeOrder=JSON.parse(await readFile(new URL('./example-anchors.json',import.meta.url),'utf8'));
const chapters=[];
const examples=[];
for (const filename of (await readdir(source)).filter(f=>/^第\d+章.*\.md$/.test(f)).sort()) {
 const text = await readFile(resolve(source,filename),'utf8');
 const number = Number(filename.match(/^第(\d+)/)[1]);
 const tree=parser.parse(text);
 const startOf = n=>n.position.start.offset;
 const heading = (n,depth,label)=>n.type==='heading' && n.depth===depth && toString(n).startsWith(label);
 const exerciseNode=tree.children.find(n=>heading(n,2,'练习题'));
 const answerNode=tree.children.find(n=>heading(n,2,'参考答案'));
 if(!exerciseNode||!answerNode) throw new Error(`${filename}: 练习区缺失`);
 const body=text.slice(0,startOf(exerciseNode));
 const bodyTree=parser.parse(body);
 const codeNodes=[];
 const visit=n=>{if(n.type==='code'&&n.lang==='python')codeNodes.push(n);if(n.children)n.children.forEach(visit)};
 visit(bodyTree);
 const currentCodes=codeNodes.map(n=>n.value);
 const codes=codeOrder[number].map(key=>currentCodes.find(code=>hash(code)===key));
 if(number===7&&codes.slice(10,20).some(code=>code===undefined))throw new Error('第7章模块代码已变更，请更新 example-anchors.json 与 browser-adapters.mjs 后重新验收');
 const title=toString(bodyTree.children[0]).replace(/^第\d+章\s*/, '');
 const topSections=bodyTree.children.filter(n=>n.type==='heading'&&n.depth===2);
 const introStart=bodyTree.children[0].position.end.offset;
 const sections=[{id:'intro',title:'开始这一章',markdown:body.slice(introStart,topSections.length?startOf(topSections[0]):body.length).trim()}];
 topSections.forEach((n,i)=>sections.push({id:`s${toString(n).match(/^([0-9]+)\./)?.[1]||hash(toString(n))}`,title:toString(n),markdown:body.slice(n.position.end.offset,topSections[i+1]?startOf(topSections[i+1]):body.length).trim()}));
 codeNodes.forEach((node)=>{
   const index=codeOrder[number].indexOf(hash(node.value));

   const original=node.value;
   const adapted=number===7?adaptedExample(index,codes):null;
   let setup=''; let files={};
   if(number===5&&index===10)files={'sample.txt':'第一行 Python\n第二行 学会循环\n'};
   if(number===6&&index===12)setup=codes[11].split('\nprint(')[0];
   if(number===6&&index===20)setup='score = 10';
   if(number===6&&index===27)setup=codes[26].split('\nprint(')[0];
   if(number===7&&index===4)setup=codes[3];
   if(number===7&&index===8)files={'study_tools.py':codes[6]};
   if(number===7&&index===20)files={'stock_analysis.py':'import pandas as pd\nimport math\n\n' + codes[16].slice(codes[16].indexOf('def calc_daily_return'))};
   const suffix=suffixes[number]?.[index] || '';
   const code=[setup?`# 补齐本节前文的运行上下文\n${setup}`:'',original,suffix?`# 调用示例，观察运行结果\n${suffix}`:''].filter(Boolean).join('\n\n');
   const section=sections.find(s=>s.markdown.includes(original));
   const id=`ch${number}-${hash(original)}`;
   examples.push({id,chapter:number,section:section?.id||'intro',title:section?.title||title,original,code,input:defaultInputs[number]?.[index]||'',files,expectedError:expectedErrors[number]?.[index]||'',packages:number===7&&index===20?['pandas']:[],note:setup||suffix?'运行代码已补齐上下文或示例调用，可在编辑器中查看。':Object.keys(files).length?'所需文件已放入本次运行的虚拟目录。':'',...adapted});
 });
 const questionsText=text.slice(exerciseNode.position.end.offset,startOf(answerNode));
 const questionTree=parser.parse(questionsText);
 const qHeadings=questionTree.children.filter(n=>heading(n,3,'第'));
 const answerText=text.slice(answerNode.position.end.offset);
 const answerMatches=[...answerText.matchAll(/^\*\*第(\d+)题\s+([A-D])\*\*\s*$/gm)];
 const questions=qHeadings.map((node,i)=>{
   const qNumber=Number(toString(node).match(/第(\d+)题/)[1]);
   const chunk=questionsText.slice(node.position.end.offset,qHeadings[i+1]?.position.start.offset??questionsText.length).trim();
   let inFence=false;const options=[];let pos=0;
   for(const line of chunk.split('\n')) {if(/^```/.test(line))inFence=!inFence; if(!inFence&&/^[A-D]\.\s/.test(line)) options.push({label:line[0],start:pos});pos+=line.length+1}
   if(options.length!==4||options.map(o=>o.label).join('')!=='ABCD')throw new Error(`选项异常 ${number}/${qNumber}`);
   const answerIndex=answerMatches.findIndex(m=>Number(m[1])===qNumber); const match=answerMatches[answerIndex];
   if(!match)throw new Error(`答案缺失 ${number}/${qNumber}`);
   return {id:`ch${number}-q${qNumber}`,chapter:number,number:qNumber,prompt:chunk.slice(0,options[0].start).trim(),options:options.map((o,j)=>({label:o.label,markdown:chunk.slice(o.start+3,options[j+1]?.start??chunk.length).trim()})),answer:match[2],explanation:answerText.slice(match.index+match[0].length,answerMatches[answerIndex+1]?.index??answerText.length).trim(),context:null};
 });
 for(const q of questions){const ref=q.prompt.match(/第(\d+)题/);if(ref){const parent=questions.find(p=>p.number===Number(ref[1]));if(parent&&parent.id!==q.id)q.context={number:parent.number,prompt:parent.prompt};}}
 if(questions.some((q,i)=>q.number!==i+1||!q.explanation||!q.options.every(o=>o.markdown))||new Set(answerMatches.map(m=>m[1])).size!==20)throw new Error(`${filename}: 题号或解析异常`);
 if(questions.length!==20||answerMatches.length!==20)throw new Error(`${filename}: 题目或答案数量异常`);
 chapters.push({id:number,title,description:descriptions[number-1],color:colors[number-1],source:filename,sections,questions});
}
const aiCode=`def get_models():
    return ["demo-python-tutor"]


def call_tutor(question, model):
    if model not in get_models():
        raise ValueError("未知的演示模型")
    responses = {
        "函数": "函数把一组步骤封装起来，通过参数接收数据，通过 return 返回结果。",
        "递归": "递归需要基例，并且每次调用都要接近基例。",
    }
    for keyword, answer in responses.items():
        if keyword in question:
            return answer
    return "这是一条本地模拟响应。可以尝试输入含有‘函数’或‘递归’的问题。"


question = input("你的问题：")
print("[本地模拟数据]", call_tutor(question, get_models()[0]))`;
const stockCode=`import pandas as pd
import matplotlib.pyplot as plt

# 固定的教学示例数据，单位为元
prices = pd.DataFrame({
    "date": pd.date_range("2026-01-05", periods=6),
    "close": [100, 103, 101, 106, 108, 105],
})
prices["return_pct"] = prices["close"].pct_change() * 100
print(prices.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(9, 3.3))
axes[0].plot(prices["date"], prices["close"], "o-", color="#7057e8")
axes[0].set_title("Sample closing prices")
axes[1].bar(prices["date"], prices["return_pct"], color="#149b8c")
axes[1].set_title("Daily returns (%)")
for ax in axes:
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.15)
fig.tight_layout()
plt.show()`;
examples.push({id:'ch7-ai-demo',chapter:7,section:'s7',title:'AI 接口协作 · 模拟响应',original:'',code:aiCode,input:'什么是递归？',files:{},packages:[],expectedError:'',note:'此实验使用本地规则生成模拟响应，用来观察参数传递与模块协作。'});
examples.push({id:'ch7-stock-demo',chapter:7,section:'s8',title:'股票数据处理 · 示例数据',original:'',code:stockCode,input:'',files:{},packages:['pandas','matplotlib'],expectedError:'',note:'固定教学数据，通过 Python 实际计算收益率并绘图。'});
if(chapters.length!==7||new Set(examples.map(e=>e.id)).size!==examples.length)throw new Error('章节数量或示例 ID 异常');
await writeFile('src/data/course.json',JSON.stringify({version:1,chapters,examples},null,2)+'\n');
console.log(`已导入 ${chapters.length} 章、${chapters.reduce((n,c)=>n+c.questions.length,0)} 题、${examples.length} 个可运行示例。`);
