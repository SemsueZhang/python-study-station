"""Authoring source for the additional bank. Run from the repository root.

Every executable item carries an independently specified expected result.
The build checks those results with CPython, then emits static website data.
"""
import ast
import contextlib
import io
import json
from pathlib import Path
import random
import re

ROOT = Path(__file__).resolve().parents[1]
items = []
chapter = 1
section = 's1'


def add(prompt, correct, wrong, explanation, verification=None):
    assert len(wrong) == 3 and len(set([correct, *wrong])) == 4, prompt
    items.append(dict(chapter=chapter, sourceSection=section, prompt=prompt,
                      correct=correct, wrong=wrong, explanation=explanation,
                      verification=verification))


def concepts(rows):
    for row in rows.strip().splitlines():
        stem, right, a, b, c, explanation = row.split(' § ')
        add(stem, right, [a, b, c], explanation)


def execute(kind, code):
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            if kind == 'expression':
                return repr(eval(code, {}))
            exec(code, {})
        return output.getvalue().rstrip('\n')
    except Exception as error:
        return '!' + type(error).__name__


def expressions(rows):
    for row in rows.strip().splitlines():
        code, expected, wrong, explanation = row.split(' § ')
        if not expected.startswith('!'):
            expected = repr(ast.literal_eval(expected))
        actual = execute('expression', code)
        assert actual == expected, (code, expected, actual)
        fmt = lambda s: f'`{s[1:]}` 异常' if s.startswith('!') else f'`{s}`'
        add(f'计算下面的表达式，结果的表示形式或异常是哪一项？字符串保留引号，数值区分整数与浮点数写法。\n\n```python\n{code}\n```',
            fmt(expected), [fmt(w) for w in wrong.split(' ¦ ')], explanation,
            dict(kind='expression', code=code, expected=expected))


def programs(rows):
    for row in rows.strip().splitlines():
        code, expected, wrong, explanation = row.split(' § ')
        code = code.replace('↵', '\n')
        expected = ast.literal_eval(expected)
        actual = execute('program', code)
        assert actual == expected, (code, expected, actual)
        def fmt(s):
            if s.startswith('!'):
                return f'`{s[1:]}` 异常'
            return '（无输出）' if s == '' else f'```text\n{s}\n```'
        hints = []
        if '.__name__' in code:
            hints.append('`type(value).__name__` 返回类型名称字符串，例如 `int`、`str`。')
        if 'floor(' in code:
            hints.append('`floor(x)` 返回不大于 x 的最大整数。')
        if 'ceil(' in code:
            hints.append('`ceil(x)` 返回不小于 x 的最小整数。')
        if 'globals()' in code:
            hints.append('`"x" in globals()` 检查模块全局是否存在名称 x。')
        hint = '\n\n本题说明：' + ' '.join(hints) if hints else ''
        add('在 Python 3 中执行下面的完整程序，输出或异常是哪一项？'+hint+'\n\n```python\n'+code+'\n```',
            fmt(expected), [fmt(ast.literal_eval(w)) for w in wrong.split(' ¦ ')], explanation,
            dict(kind='program', code=code, expected=expected))


# Chapter 1: 50 scenario questions, all within the introductory chapter.
section = 's1'
concepts('''
筛选奖学金名单时，“成绩好”还没有量化。最先应补充哪条约定？ § 总分门槛及是否有单科限制 § 输出字体颜色 § 程序文件图标 § 编辑器窗口大小 § 先把筛选规则写成可判断的条件，才能把需求落实为处理步骤。
程序能正常运行，却把缺考人数计入了不应计入的分母。应优先检查哪里？ § 统计规则和需求是否一致 § 键盘是否接好 § 是否换了更大的显示器 § 是否把文件名改短 § 能执行不等于符合需求，分母的含义由统计约定决定。
通讯录程序把查到的电话号码存入文件，这一步说明什么？ § 存储文本也属于数据处理 § 只有加减乘除才是数据处理 § 字符串不能交给计算机处理 § 写文件一定属于算术运算 § 计算机处理的数据包括数字与文本，存储和查找也属于处理。
把一个求和算法分别写成中文步骤和 Python 程序，二者可保持什么相同？ § 输入到输出的计算规则 § 每个字符的编码 § 文件扩展名 § 对解释器的要求 § 算法是处理规则，中文步骤和程序是不同的表达方式。
某条二进制指令只能在支持相应指令集的 CPU 上执行，判断依据是什么？ § 机器指令编码依赖指令集 § 所有二进制文件都是图片 § 高级语言只能表示文字 § 指令集由屏幕分辨率决定 § 机器语言的具体编码与处理器支持的指令集相关。
“高级语言更接近问题本身”中的“高级”主要指什么？ § 抽象层次较高 § 每次运行都更快 § 软件售价更高 § 只能用于科研 § 变量、公式和函数等表达隐藏了许多底层细节，高级不保证运行速度。
把“语言生态”列为机器语言、汇编语言之后的第四个层次，有什么问题？ § 生态描述配套资源，不是语言抽象层次 § 生态专指二进制指令 § Python 没有任何库 § 汇编语言就是第三方库 § 语言生态包括库、工具和开发者资源，与语言层次的分类依据不同。
导入一个求平方根的函数前，应先核对哪组信息？ § 可接受的实参、返回值和使用条件 § 作者头像与下载页面颜色 § 本机壁纸与光标样式 § 代码注释是否押韵 § 接口约定决定如何正确调用已有功能。
有人把任意两个数直接传给 `sum(4, 8)` 求和。按本章介绍，问题在哪里？ § 第一个实参应是可迭代对象 § sum 只能计算字符串长度 § sum 必须先从 time 导入 § 函数名不能含三个字母 § sum 的第一个实参需要能逐项取出元素，整数4不符合该约定。
程序只要求比较两次测量结果，“相等”时输出什么没有说明。这属于什么缺口？ § 需求边界尚未明确 § CPU 不支持比较 § Python 不能输出文本 § 必须先安装绘图库 § 相等也是合法情形，需要确定其输出规则。
''')
section = 's2'
concepts('''
一个功能使用 `math`，另一个使用需另行安装的分析包。准备环境时怎样区分？ § 分别检查标准库可用性和第三方依赖安装情况 § 所有包都必须手工复制解释器源码 § 标准库只能在联网时运行 § 第三方包会自动成为语法关键字 § 标准库随 Python 提供，第三方包通常需要另外安装。
复制来的教程代码使用 Python 2 语法，本机是 Python 3。应先确认什么？ § 代码的版本要求与当前解释器是否兼容 § 是否能把屏幕亮度调高 § 文件是否超过十行 § 是否去掉所有括号 § 语言版本存在语法与行为差异，应核对版本后再修改或运行。
用现成库只写了三行，自己实现用了五十行，能直接得出什么结论？ § 两个版本的调用代码量不同 § 三行版本一定运行更快 § 五十行版本一定错误 § 两个版本一定不需要依赖 § 代码量可以直接比较，运行效率与正确性仍需结合实现和实际检查。
一个程序同时用函数组织步骤并使用已有对象，这说明什么？ § 一个程序可以结合多种组织方式 § Python 只能采用面向对象方式 § 使用函数后不能调用对象的方法 § 编程范式由文件大小决定 § Python 支持多种编程范式，实际程序可以组合使用。
为了完成日期转换而挑选库，合理的出发点是什么？ § 先明确日期输入和目标输出，再选接口 § 先安装所有能找到的库 § 只比较库名长短 § 优先选择没有文档的函数 § 功能要求和数据约定应指导工具选择。
''')
section = 's3'
concepts('''
在编辑器里按运行后提示找不到 Python，首先应检查什么？ § 当前项目是否选中了可用解释器 § 注释是否足够多 § 是否换成深色主题 § 变量名是否全部大写 § 编辑器提供编辑界面，执行代码仍需要解释器。
把教程中的 `>>> print("Hi")` 原样复制到 `.py` 文件出错，应如何处理？ § 去掉交互环境的提示符，保留代码 § 给每行再加一个 >>> § 把 print 改成中文 § 给文件换成图片扩展名 § >>> 是交互环境的提示符，不是程序文件中的代码。
刚修改程序但未保存，运行的仍是旧结果，应先做什么？ § 保存文件并确认运行的是该文件 § 删除所有变量 § 更换 CPU § 把运算符全部改成加号 § 文件式运行读取被执行文件中的已保存内容。
控制台停在要求输入姓名的位置，没有错误信息。合理解释是什么？ § 程序可能正在等待 input 的输入 § 程序必然陷入死循环 § 解释器已经被卸载 § Python 不支持中文姓名 § input 会等待用户在控制台输入并按回车。
同一个相对路径在两个启动位置表现不同，应该核对什么？ § 程序的工作目录 § 屏幕的物理尺寸 § Python 图标颜色 § 代码字体是否等宽 § 相对路径以工作目录为基准，工作目录不一定等于源文件目录。
想快速验证一个算术表达式，通常哪种方式便于即时观察？ § 在交互环境输入表达式并查看结果 § 每次先绘制完整流程图再开机 § 把表达式保存成照片 § 只修改文件名而不运行 § 交互式运行适合试算与验证短小表达式。
需要保留并反复修改一个完整脚本，哪种安排较合适？ § 保存为 .py 文件后重复运行 § 只把代码写在终端标题中 § 每次拍照后删除文本 § 把代码保存为解释器提示符 § 文件式运行适合保存和重复执行多条语句。
只安装了代码编辑器就认为程序一定可以运行，遗漏了什么？ § 解释器及项目依赖的准备 § 为文件挑选头像 § 给每个变量配图片 § 把显示器接入打印机 § 编辑器、解释器与依赖承担不同职责，安装编辑器本身不保证执行环境完整。
''')
section = 's4'
concepts('''
身高体重计算器从文件读取数据，而不调用 input。这些数据在 IPO 中属于什么？ § 输入 § 只能算输出 § 只能算算法名称 § 不属于 IPO § 输入描述数据来源，既可以来自键盘，也可以来自文件等渠道。
程序把统计结果作为函数返回值交给调用者，在该函数的 IPO 中属于什么？ § 输出 § 一定是键盘输入 § 源代码注释 § 解释器安装 § 输出可以是返回值，不局限于控制台显示。
一个程序只负责转换已经录好的数字，不负责识别图片，这项约定属于什么？ § 划分程序负责的边界 § 选择变量颜色 § 编译字节码 § 设置显示器刷新率 § 明确负责与不负责的任务，有助于确定输入范围与功能边界。
圆面积程序需要同时输出面积和单位，应把这个要求写在哪里？ § 输出约定 § 只写在解释器安装说明中 § 只写在 CPU 型号中 § 只写在编辑器快捷键中 § 输出约定包括结果含义、单位和格式。
价格计算中“折扣率”到底是八折还是减免八成尚未明确，为什么不能直接写公式？ § 两种含义对应不同的处理规则 § Python 不支持小数 § 价格只能用字符串保存 § 乘法必须先导入库 § 数据的业务含义需要先明确，否则公式可能实现另一种需求。
测试发现零条记录时平均分程序除以零，接下来最有帮助的步骤是什么？ § 先确定空数据应拒绝还是返回约定结果 § 只把异常提示隐藏 § 永久跳过所有测试 § 改成随机输出一个平均分 § 空数据处理属于需求边界，先确定期望行为再修改程序。
输入格式从两行数字改为一行带单位的文本，维护时应重点复查什么？ § 输入解析及它与计算部分的衔接 § 仅修改网页配色 § 仅把所有变量名缩短 § 仅调整注释顺序 § 输入协议变化会影响如何取得用于计算的数值。
''')
section = 's5'
concepts('''
算法步骤写成“不断猜，直到差不多”，最明显缺少什么？ § 明确的更新规则和结束条件 § 足够多的标点符号 § 文件扩展名 § 编程语言商标 § 算法的步骤需要明确可执行，并在约定条件下结束。
流程图中“读入半径”最适合放在哪类框内？ § 输入输出框 § 判断框 § 只表示结束的框 § 与流程无关的图例 § 读入数据属于输入操作，通常使用平行四边形输入输出框。
流程图矩形内写 `total = total + x`，它表达什么？ § 一次计算与赋值处理 § 一定是用户输入 § 一定是算法结束 § 一定是二选一判断 § 处理框用于表示计算、赋值等操作。
流程图出现返回上方判断框的箭头，阅读时应特别核对什么？ § 变量更新是否能让循环结束 § 箭头颜色是否统一 § 文本是否用了英文 § 框的宽度是否相同 § 回返箭头通常形成循环，应检查状态变化和终止条件。
同一求和任务可以用循环和公式实现，比较方案时应同时考虑什么？ § 正确性、输入范围和执行步骤 § 只比较文件名字数 § 只比较程序员年龄 § 只比较注释行数 § 同一任务可以有不同算法，方案评价需要结合任务条件和代价。
伪代码没有遵守 Python 缩进规则，是否必然有错？ § 否，只要步骤明确，伪代码不要求直接运行 § 是，所有伪代码必须能由 CPython 执行 § 是，伪代码只能写二进制 § 否，伪代码可以完全没有步骤含义 § 伪代码用于表达算法，不必符合某种可执行语言的全部语法。
''')
section = 's6'
concepts('''
公交票价计算只需要站数和计价规则，忽略车身颜色。这是哪一步？ § 选取与目标相关的信息建立模型 § 安装解释器 § 把文本编译成机器码 § 自动证明全部程序正确 § 抽象围绕计算目标保留必要信息，忽略无关细节。
已有准确计费规则，要处理一万次行程。把规则交给程序逐条执行体现什么？ § 自动化 § 只改变数据单位 § 仅仅是文本排版 § 删除问题的输入 § 自动化把明确规则转为机器可反复执行的步骤。
按每个姓名首字符划分姓氏时遇到复姓，说明应复查什么？ § 数据模型对姓名结构的假设 § 字符串能否保存文本 § 计算机是否支持加法 § 文件是否足够小 § 字符位置的取得不等于对真实姓名结构作出了正确判断。
预测输出与运行结果不同，最有效的排查方式是哪项？ § 按执行顺序记录变量变化，定位首次偏差 § 只反复运行而不看代码 § 把所有常量改为零 § 删除输出语句 § 逐步追踪可以发现理解与实际语义开始分离的位置。
只凭十组测试全对就断言算法对所有合法输入正确，缺少什么？ § 对一般输入的逻辑分析 § 更多的网页动画 § 更长的文件名 § 一台相同颜色的电脑 § 有限测试能提供证据，不能自动覆盖所有输入情形。
''')
section = 's7'
concepts('''
圆面积代码把直径直接当半径使用，结果正常显示但大了四倍。这说明什么？ § 输入量的含义与公式要求不一致 § 格式化必然改变了数值 § 乘法运算符在此失效 § Python 不支持圆面积计算 § 面积与半径平方成正比，直径误作半径会产生四倍结果。
斐波那契程序的上限刚好是数列中的一项，`<` 与 `<=` 的区别是什么？ § 是否输出等于上限的那一项 § 是否允许整数相加 § 是否可以调用 print § 是否保存程序文件 § 严格小于排除端点，小于等于包含端点。
''')
section = 's8'
concepts('''
某实现先生成字节码，再由虚拟机执行，是否矛盾？ § 不矛盾，编译与解释环节可以组合 § 矛盾，字节码就是所有 CPU 通用的机器码 § 矛盾，解释执行不能有任何预处理 § 不矛盾，因为类型检查完全不存在 § 编译是表示转换，生成中间表示后仍可由虚拟机执行。
“动态类型”是否意味着任意对象都能参加加法？ § 否，操作是否适用仍由实际对象类型决定 § 是，所有对象会自动变成整数 § 是，运行时完全不检查类型 § 否，因为变量名一旦赋值就不能改变 § 动态类型在运行中按对象类型判断操作，名称可重新绑定不代表任意操作都合法。
''')

# Chapter 2: 65 questions.
chapter, section = 2, 's2'
concepts('''
变量名 `student-count` 不能作为一个普通标识符，原因是什么？ § 连字符会被当作减号 § 标识符必须全大写 § 标识符不能超过七个字符 § 标识符必须包含数字 § 连字符不是标识符组成字符，Python 会把它解析为运算符。
为了保存姓名而执行 `input = "Lin"`，后续再调用 input() 有何风险？ § 内置函数名称被字符串遮蔽 § 字符串会自动变成函数 § input 是保留字，赋值必然语法错误 § 所有内置名称都不能绑定 § 内置名称可以被重新绑定，之后通过该名称调用时会访问新的对象。
`total_score` 和 `Total_score` 同时出现时应怎样理解？ § 它们是两个不同名称 § Python 会自动统一大小写 § 下划线会使它们成为同一个名称 § 两者都是保留字 § Python 的名称区分大小写。
把 `total = 12` 理解成永远成立的数学等式有什么问题？ § 赋值只在执行时建立绑定，之后可重新赋值 § Python 不允许用英文名称 § 赋值会同时改变所有同值对象 § total 一定是字符串 § 赋值是执行时的操作，不是对未来所有状态的约束。
“成绩=90”中的全角等号不能直接代替代码里的 `=`，说明什么？ § 源码标点需要使用语法要求的字符 § Python 不允许任何中文标识符 § 所有 Unicode 字符都是注释 § 赋值只能写在交互环境 § 中文名称可以合法，但运算符与标点必须符合 Python 语法。
''')
programs(r'''
left = 6↵right = left↵left = 10↵print(left - right) § '4' § '0' ¦ '10' ¦ '16' § right 绑定的是先前的整数6，left 重新赋值不会追溯修改 right。
x = 3↵x = x + 4↵x = x * 2↵print(x) § '14' § '10' ¦ '7' ¦ '6' § 两次赋值顺序执行，先得到7，再乘2得到14。
a, b, c = 1, 2, 3↵a, b, c = c, a, b↵print(a, b, c) § '3 1 2' § '3 3 3' ¦ '1 2 3' ¦ '2 3 1' § 解包赋值先求右侧旧值，再将三个结果依次绑定。
x = y = 8↵y = 3↵print(x, y) § '8 3' § '3 3' ¦ '8 8' ¦ '3 8' § 两个名称最初引用整数8，给 y 重新赋值不会改变 x。
value = 5↵value = "five"↵print(type(value).__name__) § 'str' § 'int' ¦ 'float' ¦ '!TypeError' § 名称可以重新绑定到不同类型的对象，此时 value 引用字符串。
count = 2↵Count = count + 5↵print(count, Count) § '2 7' § '7 7' ¦ '2 2' ¦ '!NameError' § count 与 Count 区分大小写，分别保存2与7。
a, b = 4, 9↵a = b↵b = a↵print(a, b) § '9 9' § '9 4' ¦ '4 9' ¦ '4 4' § 这是顺序赋值，第一条已经把 a 改成9，不能实现交换。
a, b = 4, 9↵temp = a↵a = b↵b = temp↵print(a, b) § '9 4' § '9 9' ¦ '4 9' ¦ '4 4' § 临时名称保存旧 a，最后把它交给 b，实现交换。
''')
section = 's3'
expressions(r'''
"7" * 2 + "!" § '77!' § '14!' ¦ '7!7!' ¦ !TypeError § 字符串乘整数表示重复，随后拼接感叹号。
str(7) + str(2) == str(7 + 2) § False § True ¦ 'False' ¦ !TypeError § 左侧是文本72，右侧是文本9，二者不相等。
"Python"[0] + "Python"[-2] § 'Po' § 'Pn' ¦ 'Py' ¦ 'on' § 首字符是 P，倒数第二个字符是 o，二者拼接为 Po。
"编号:K17"[3:] § 'K17' § ':K17' ¦ '17' ¦ '编号:' § 编号和冒号占前三个字符，切片从下标3开始到末尾。
"USD25.50"[3:-3] § '25' § '25.50' ¦ 'D25' ¦ '.50' § 下标3开始，终点为倒数第三个字符但不包含该字符。
"ab" in "cabd" § True § False ¦ 2 ¦ 'ab' § in 判断整个子串是否连续出现，这里 ab 连续出现。
"A" in "alpha" § False § True ¦ 'A' ¦ !TypeError § 字符串成员判断区分大小写，小写 alpha 不含大写 A。
"" in "code" § True § False ¦ None ¦ !ValueError § 空字符串被视为任意字符串的子串。
"xy"[1:1] § '' § 'x' ¦ 'y' ¦ !IndexError § 正向切片起点与终点相同，结果为空字符串。
len("编号" + "08") § 4 § 2 ¦ 6 ¦ 8 § 这里按字符串字符数计长度，两个汉字加两个数字共4个字符。
''')
section = 's4'
concepts('''
多行表达式放在一对圆括号中换行，通常有什么作用？ § 可以隐式续行 § 每行必须再加一个分号 § 会把表达式变成注释 § 会自动创建一个函数 § 括号尚未闭合时可以跨多行书写表达式。
`if` 语句头末尾漏写冒号，最直接影响什么？ § 不符合复合语句的语法 § 只改变输出字体 § 自动跳过该分支但不报错 § 自动把 if 变成变量 § if 语句头需要冒号，缺少时会产生语法错误。
一段文字放在三引号中但没有赋给名称，也没有输出。能否据此说它一定是 `#` 注释？ § 不能，它仍是字符串字面量 § 能，三引号会删除后续全部代码 § 能，三引号内不能出现换行 § 不能，因为字符串必须使用单引号 § 三引号用于表示字符串，独立字符串与井号注释的语法性质不同。
''')
programs(r'''
x = (1 +↵     2 +↵     3)↵print(x) § '6' § '1' ¦ '3' ¦ '!SyntaxError' § 圆括号内允许隐式续行，三项相加得到6。
value = 3 # value = 99↵print(value) § '3' § '99' ¦ '102' ¦ '!SyntaxError' § 井号之后的部分是注释，不会执行第二个赋值。
print("#不是注释") § '#不是注释' § '' ¦ '不是注释' ¦ '!SyntaxError' § 字符串内的井号是普通文本，不开始注释。
if False:↵    print("A")↵print("B") § 'B' § 'A' ¦ 'A\nB' ¦ '' § 只有缩进的语句属于条件块，未缩进的 B 输出仍会执行。
if True:↵    print("A")↵    print("B")↵print("C") § 'A\nB\nC' § 'A\nC' ¦ 'C' ¦ 'A B C' § 两条缩进语句均属于真分支，之后继续执行块外输出。
''')
section = 's5'
expressions(r'''
int("007") + 1 § 8 § '0071' ¦ 7 ¦ !ValueError § int 按十进制解析字符串007得到7，再加1得到8。
float(" 6.25 ") * 2 § 12.5 § 6.25 ¦ '6.256.25' ¦ !ValueError § float 允许数值文本两端有空白，转换后做数值乘法。
int(float("9.8")) § 9 § 10 ¦ 9.8 ¦ !ValueError § 先把文本转换成浮点数，再由 int 向零截断。
eval("2 + 3 * 4") § 14 § '2 + 3 * 4' ¦ 20 ¦ !SyntaxError § eval 按表达式求值，先乘后加得到14。
float("6e-2") § 0.06 § 0.6 ¦ 600.0 ¦ !ValueError § 科学计数法6乘10的负二次方等于0.06。
int("12") == float("12.0") § True § False ¦ 'True' ¦ !ValueError § 转换后的数值分别为整数12与浮点数12.0，它们数值相等。
str(float("5")) § '5.0' § '5' ¦ 5.0 ¦ !TypeError § 先得到浮点数5.0，再将其转换为显示文本5.0。
int("1e2") § !ValueError § 100 ¦ 1 ¦ 100.0 § int 的默认十进制字符串形式不直接接受科学计数法。
''')
concepts('''
用户输入邮政编码 `010001`，程序只需原样显示。哪种处理更合适？ § 保留 input 返回的字符串 § 必须先转 int 再显示 § 必须先计算平方 § 必须执行 eval § 邮政编码是标识文本，转成整数会丢失前导零。
程序要求用户输入十进制整数，而用户输入 `3+4`。`int()` 与 `eval()` 的差异是什么？ § int 拒绝该文本，eval 会尝试按表达式求值 § 两者都只原样返回字符串 § 两者都必然返回7 § int 会自动插入乘号 § int 解析整数文本，eval 的用途是求表达式的值，两者接受的输入范围不同。
''')
section = 's6'
programs(r'''
print("A", "B", "C", sep="-") § 'A-B-C' § 'A B C' ¦ 'ABC' ¦ 'A-B-C-' § sep 只放在多个输出对象之间，不追加到最后一个对象之后。
print("A", end="/")↵print("B", end="!") § 'A/B!' § 'A/\nB!' ¦ 'AB' ¦ 'A B' § end 替换每次 print 的默认换行，两个调用在同一行衔接。
print()↵print("X") § '\nX' § 'X' ¦ 'None\nX' ¦ ' X' § 无实参的 print 仍会输出默认换行，形成首个空行。
print("{}+{}={}".format(2, 5, 7)) § '2+5=7' § '{}+{}={}' ¦ '2 5 7' ¦ '!IndexError' § 三个替换字段按顺序接收三个实参。
print("{0}/{0}".format("go")) § 'go/go' § 'go/0' ¦ '0/0' ¦ '!IndexError' § 编号0可以重复引用第一个实参。
price = 3.5↵print(f"价格:{price:.1f}") § '价格:3.5' § '价格:price' ¦ '价格:3.50' ¦ '!SyntaxError' § f 字符串在替换字段中读取 price，并按一位小数显示。
print("第一行\n第二行") § '第一行\n第二行' § '第一行\\n第二行' ¦ '第一行 第二行' ¦ '!SyntaxError' § 字符串中的反斜杠n表示换行，单次 print 可以产生多行内容。
''')
section = 's7'
programs(r'''
text = "50C"↵value = float(text[:-1])↵print(value * 1.8 + 32) § '122.0' § '50.0' ¦ '90.0' ¦ '!ValueError' § 切去末尾单位后取得50摄氏度，再按华氏公式转换。
text = "F68"↵number = float(text[1:])↵print((number - 32) / 1.8) § '20.0' § '68.0' ¦ '37.77777777777778' ¦ '!ValueError' § 单位在前缀时应从下标1读取数值，68华氏度对应20摄氏度。
text = "20c"↵if text[-1] == "C":↵    print("convert")↵else:↵    print("reject") § 'reject' § 'convert' ¦ '20' ¦ '!IndexError' § 比较区分大小写，只检查大写 C 的代码不会接受小写 c。
text = "12C"↵print(text[0], text[-1], sep=":") § '1:C' § '12:C' ¦ '1:2' ¦ 'C:1' § 索引只取得单个字符，首字符是1，末字符是 C。
''')
section = 's8'
programs(r'''
text = "EUR40"↵rate = 8↵print(float(text[3:]) * rate) § '320.0' § '40.0' ¦ 'EUR40EUR40EUR40EUR40EUR40EUR40EUR40EUR40' ¦ '!ValueError' § 三字母币种占下标0至2，切片后转换数值并乘汇率。
radius = 2↵pi = 3↵print(2 * pi * radius)↵print(pi * radius ** 2) § '12\n12' § '12\n6' ¦ '6\n12' ¦ '12 12' § 周长与面积使用不同公式，这组常量下两个结果恰好都是12。
''')
section = 's9'
programs(r'''
import math↵print(math.floor(4.8)) § '4' § '5' ¦ '4.8' ¦ '!NameError' § import math 后通过模块名访问 floor，结果为不大于4.8的最大整数4。
from math import pi as p↵print(p > 3) § 'True' § 'False' ¦ '!ImportError' ¦ '!NameError' § as 将导入名称绑定为 p，圆周率大于3。
import math as m↵print(m.ceil(2.1)) § '3' § '2' ¦ '2.1' ¦ '!NameError' § 导入别名 m 引用 math 模块，ceil 向上取整得到3。
from math import sqrt as root↵print(root(81)) § '9.0' § '9' ¦ '81.0' ¦ '!NameError' § sqrt 以 root 为名称导入，返回浮点数9.0。
import math↵print(sqrt(25)) § '!NameError' § '5.0' ¦ '5' ¦ '!TypeError' § import math 不会把 sqrt 作为独立名称引入，应使用 math.sqrt。
from math import floor↵print(math.floor(2.9)) § '!NameError' § '2' ¦ '3' ¦ '!ImportError' § 只导入 floor 不会同时绑定模块名称 math。
''')


# Chapter 3: 85 questions on types, numeric expressions and models.
chapter, section = 3, 's1'
concepts('''
学号 `00028` 只用于标识学生，选择类型时优先考虑什么？ § 是否需要保留前导零和原始文本 § 数字字符必须都转 float § 只能按字符数量选择 § 任何学号都必须参加乘法 § 类型选择取决于数据含义，标识文本通常需要保留原始形式。
`type(8)` 与 `type("8")` 不同，直接原因是什么？ § 一个对象是整数，一个对象是字符串 § 名称长度不同 § 字符8不能作为整数 § 引号会让对象变成布尔值 § 对象的类型决定支持的操作，外观相同不代表类型相同。
一个 int 对象与一个 float 对象比较相等，能推出什么？ § 它们的数值可以相等而类型不同 § 它们一定引用同一个对象 § Python 不区分这两个类型 § 两者都会自动变为字符串 § 数值相等与类型相同是两个不同问题。
''')
section = 's2'
expressions(r'''
0b1011 + 0o11 § 20 § 101111 ¦ 22 ¦ 18 § 二进制1011是11，八进制11是9，相加得到20。
0x10 == 0b10000 § True § False ¦ 16 ¦ !SyntaxError § 十六进制10和二进制10000都表示整数16。
int("101", 2) + int("11", 8) § 14 § 112 ¦ 16 ¦ !ValueError § 指定进制解析，二进制101为5，八进制11为9。
bin(10)[2:] § '1010' § '0b1010' ¦ 1010 ¦ '10' § bin 返回带0b前缀的文本，切去前两个字符后得到1010。
hex(31).upper() § '0X1F' § '0x1f' ¦ '31' ¦ '1F' § hex 先返回0x1f，upper 将其中的英文字母转成大写。
int("ff", 16) - 0xF0 § 15 § 0 ¦ 255 ¦ !ValueError § ff按十六进制是255，F0是240，差为15。
10 ** 30 + 1 - 10 ** 30 § 1 § 0 ¦ 1.0 ¦ !OverflowError § 这里全部是整数运算，Python 整数可精确保留加上的1。
int("20", 3) § 6 § 20 ¦ 9 ¦ !ValueError § 三进制20表示2乘3加0，结果为6。
int("102", 2) § !ValueError § 6 ¦ 102 ¦ 4 § 二进制文本中不允许数字2，转换失败。
oct(16) § '0o20' § '0o16' ¦ 20 ¦ '0x10' § 十进制16对应八进制20，oct 返回带0o前缀的字符串。
''')
section = 's3'
expressions(r'''
1.25e2 / 10 § 12.5 § 125.0 ¦ 1.25 ¦ 0.125 § 1.25e2表示125.0，再除以10得到12.5。
type(4.0 + 2).__name__ § 'float' § 'int' ¦ 'str' ¦ 'complex' § 整数与浮点数进行该加法后得到浮点数6.0。
round(1.25, 1) § 1.2 § 1.3 ¦ 1 ¦ '1.2' § 1.25可精确表示，正好处于中点，round 选择末位为偶数的1.2。
round(1.75, 1) § 1.8 § 1.7 ¦ 2 ¦ '1.8' § 1.75是精确中点，末位偶数对应1.8。
abs((0.1 + 0.2) - 0.3) < 1e-12 § True § False ¦ 1e-12 ¦ !TypeError § 这次表示误差远小于给定阈值，因此误差比较为真。
round(12.3456, 3) § 12.346 § 12.345 ¦ 12.34 ¦ '12.346' § 保留三位小数时，下一位为6，结果约为12.346。
float("-0.5") + 1 § 0.5 § -1.5 ¦ '-0.51' ¦ 1.5 § 文本先转换为负的浮点数，再与整数1相加。
2.5e-3 * 1000 § 2.5 § 25.0 ¦ 0.0025 ¦ 2500.0 § 2.5乘10的负三次方，再乘1000，得到2.5。
round(1234, -2) § 1200 § 1230 ¦ 1300 ¦ 12 § 负的 ndigits 表示在小数点左侧舍入，这里取到百位。
round(-1.5) + round(-2.5) § -4 § -5 ¦ -3 ¦ 4 § 两个中点都舍入到偶数-2，相加为-4。
''')
concepts('''
程序把测量值保留两位小数输出，是否说明原计算没有误差？ § 否，显示位数不能消除数值表示与测量误差 § 是，小数少于三位都精确 § 是，print 会把所有计算改成精确有理数 § 否，因为整数也完全无法精确表示 § 输出格式决定显示形式，不能保证输入与计算本身无误差。
比较两个测量结果是否接近，误差阈值应怎样选择？ § 结合量级、单位和任务精度要求 § 永远固定为1 § 永远只比较文本长度 § 只要使用float就无需阈值 § 合理阈值取决于应用尺度和所允许的误差。
''')
section = 's4'
expressions(r'''
complex(2, 3) + complex(1, -3) § (3+0j) § (3+6j) ¦ 3 ¦ !TypeError § 复数分别按实部和虚部相加，虚部3与-3抵消。
(1j) ** 2 + 1 § 0j § 2j ¦ 2 ¦ -2 § 虚数单位的平方是-1，再加1得到复数零。
(2 + 5j).real - (2 + 5j).imag § -3.0 § 3.0 ¦ (2+5j) ¦ 7.0 § real和imag分别返回浮点实部2.0与虚部5.0，相减为-3.0。
abs(complex(5, -12)) + abs(-2) § 15.0 § 13.0 ¦ 11.0 ¦ (7-12j) § 复数模为13.0，另一个绝对值为2，相加为15.0。
bool("0") § True § False ¦ 0 ¦ !ValueError § 非空字符串为真，不会先按数值零解释。
bool(0.0) == bool(0j) § True § False ¦ 0.0 ¦ !TypeError § 数值零和复数零都为假，两个布尔值相等。
int(True) * 10 + int(False) § 10 § 11 ¦ 0 ¦ !TypeError § True转换为1，False转换为0，结果为10。
list(range(-2, 3, 2)) § [-2, 0, 2] § [-2, 0, 2, 3] ¦ [-2, -1, 0, 1, 2] ¦ [] § 从-2起每次加2，取值严格小于终点3。
len(range(2, 20, 4)) § 5 § 4 ¦ 6 ¦ 18 § 序列为2、6、10、14、18，共5项。
list(range(2, 8, -1)) § [] § [2, 1, 0] ¦ [2, 3, 4, 5, 6, 7] ¦ !ValueError § 负步长向小处走，起点已小于终点，因此序列为空。
list(range(3, -3, -2)) § [3, 1, -1] § [3, 1, -1, -3] ¦ [3, 2, 1, 0, -1, -2] ¦ [] § 从3每次减2，在严格大于-3时取值，终点不包含。
range(1, 5, 0) § !ValueError § [] ¦ [1, 2, 3, 4] ¦ None § range 的步长不能是零。
bool(None) § False § True ¦ None ¦ !TypeError § None 的真值为假，但它本身不是布尔对象False。
None == 0 § False § True ¦ None ¦ !TypeError § None 表示空值对象，与整数零不同。
str(None) § 'None' § '' ¦ None ¦ 'null' § 转换为字符串会得到四个字符组成的文本None。
''')
section = 's5'
expressions(r'''
17 // 5 * 5 + 17 % 5 § 17 § 15 ¦ 19 ¦ 3.4 § 商乘除数再加余数恢复被除数，3乘5加2等于17。
divmod(-11, 4) § (-3, 1) § (-2, -3) ¦ (-3, -1) ¦ (3, 1) § 向下取整得到商-3，余数1使-11等于-3乘4加1。
divmod(11, -4) § (-3, -1) § (-2, 3) ¦ (-3, 1) ¦ (2, 3) § 商向下取整为-3，余数与负除数同号，为-1。
(-3) ** 2 + -3 ** 2 § 0 § 18 ¦ -18 ¦ 9 § 括号内负数的平方为9，另一项先幂后负号得到-9。
2 ** -3 § 0.125 § -8 ¦ 8 ¦ !SyntaxError § 负指数表示倒数，2的负三次方为八分之一。
(2 ** 3) ** 2 § 64 § 512 ¦ 256 ¦ 12 § 显式括号先算2的三次方8，再平方为64。
18 / 3 // 2 § 3.0 § 3 ¦ 1.5 ¦ 6.0 § 两种除法同级从左到右，先得6.0，再整除2得到浮点3.0。
5 + 2 * 3 ** 2 § 23 § 63 ¦ 49 ¦ 19 § 先算幂9，再乘2，最后加5。
(-10) % 3 + 10 % 3 § 3 § 0 ¦ -1 ¦ 2 § -10除以3的余数为2，10除以3的余数为1。
7 % -3 § -2 § 1 ¦ 2 ¦ -1 § 商为-3，余数为-2，满足7等于-3乘-3再加-2。
3 ** 0 + 0 ** 3 § 1 § 0 ¦ 2 ¦ !ZeroDivisionError § 非零数的零次方是1，零的正整数次方是0。
0 ** 0 § 1 § 0 ¦ !ValueError ¦ !ZeroDivisionError § Python 的幂运算约定0的0次方返回1。
6 * (7 - 2) / 3 § 10.0 § 10 ¦ 40.0 ¦ 14.0 § 括号先得到5，乘6再做真除法得到浮点数10.0。
1 / 0 § !ZeroDivisionError § 0 ¦ None ¦ !ValueError § 除数为零会触发ZeroDivisionError。
3 + 2j * 2 § (3+4j) § (6+4j) ¦ (3+2j) ¦ !TypeError § 先进行复数乘法2j乘2，再加实数3。
''')
programs(r'''
x = 5↵x += 2↵x **= 2↵print(x) § '49' § '29' ¦ '25' ¦ '14' § 增强赋值依次把 x 更新成7和49。
x = 20↵x //= 3↵x %= 4↵print(x) § '2' § '6' ¦ '1' ¦ '0' § 先整除得到6，再取对4的余数2。
x = 3↵x /= 2↵print(x, type(x).__name__) § '1.5 float' § '1 int' ¦ '1.5 int' ¦ '1 float' § 真除法得到浮点数1.5，增强赋值重新绑定该结果。
''')
section = 's6'
expressions(r'''
min(4, -2, 7) + max(4, -2, 7) § 5 § 11 ¦ -14 ¦ 9 § 最小值为-2，最大值为7，相加得到5。
sum(range(1, 5)) § 10 § 15 ¦ 6 ¦ 5 § range取1至4，四项相加等于10。
pow(3, 4, 5) § 1 § 81 ¦ 4 ¦ 3 § 三参数pow计算3的4次方对5取余，81的余数是1。
abs(-7) - abs(3 - 8) § 2 § 12 ¦ -2 ¦ 7 § 两个绝对值分别为7和5，差为2。
round(abs(-2.75), 1) § 2.8 § 2.7 ¦ -2.8 ¦ 3 § 先取绝对值得2.75，再按偶数中点规则保留一位小数。
int(-8.99) + int(8.99) § 0 § -1 ¦ 1 ¦ !ValueError § int对浮点数向零截断，两个整数分别为-8和8。
float(3) / int(2.9) § 1.5 § 1.0 ¦ 1 ¦ !TypeError § int得到2，3.0除以2为1.5。
complex("2-3j").imag § -3.0 § 3.0 ¦ '2-3j' ¦ !ValueError § complex可以解析该复数字符串，虚部为-3.0。
sum([1, 2, 3], 10) § 16 § 6 ¦ 10 ¦ !TypeError § sum的第二个实参是起始累计值10，再加列表各项得到16。
max(range(-5, 0)) § -1 § 0 ¦ -5 ¦ 5 § range包含-5至-1，最大值为-1。
abs(3 - 4j) == 5 § True § False ¦ (3-4j) ¦ !TypeError § 复数模为5.0，与整数5数值相等。
int("-12") // 5 § -3 § -2 ¦ 3 ¦ !ValueError § 文本转为整数-12，整除5时向下取整为-3。
divmod(95, 60)[1] § 35 § 1 ¦ 60 ¦ 95 § divmod返回商1与余数35，索引1取得余数。
''')
section = 's7'
concepts('''
初始水平为1，连续三天每天增长10%，正确建模是哪项？ § 1.1 ** 3 § 1 + 0.1 * 3 总是精确等价 § 3 * 1.1 § 1.1 + 3 § 逐日增长以更新后的水平为基础，三天应连乘三个1.1。
工作日增长、休息日下降的模型中，初始值应在什么时候设置？ § 每次完整模拟开始时设置一次 § 每一天计算前都重置为1 § 仅在最后一天设为1 § 每遇到休息日都重置为0 § 初始状态应保留并逐日更新，重复重置会丢失累计效果。
按固定步长搜索到首个达标增长率，通常能直接说明什么？ § 它是本次离散候选序列中的首个达标值 § 它必定是所有实数中的精确最优值 § 搜索步长对结果没有影响 § 所有更小实数都必然不达标 § 离散搜索只访问候选点，结论应受搜索范围和步长限制。
模型中下降率为 down，某天下降后的水平应怎样更新？ § 乘以 1 - down § 减去固定的 down 无论当前水平多少 § 除以 down § 每天都乘以 down § 百分比下降相对于当前水平，更新因子为1减下降率。
''')

# Chapter 4: 90 questions on strings and time.
chapter, section = 4, 's1'
expressions(r'''
len("a\tb".replace("\t", "--")) § 4 § 3 ¦ 5 ¦ 2 § 原文本中的单个制表符被替换为两个短横线，新文本a--b共4个字符。
len(r"a\nb") § 4 § 3 ¦ 2 ¦ 5 § 原始字符串保留反斜杠与n两个字符，因此总长度为4。
"C:\\temp"[-4:] § 'temp' § '\\temp' ¦ 'emp' ¦ !SyntaxError § 转义后的字符串含一个反斜杠，末尾四个字符为temp。
"He said: \"Hi\"".count('"') § 2 § 0 ¦ 1 ¦ 4 § 转义双引号被包含在字符串中，共出现两次。
len("A\nB") § 3 § 2 ¦ 4 ¦ !SyntaxError § 转义序列表示的换行计为一个字符，与A和B共3个。
''')
section = 's2'
expressions(r'''
"abcdef"[-4:-1] § 'cde' § 'bcd' ¦ 'cdef' ¦ 'fed' § 负索引-4对应c，终点-1对应f且不包含，因此是cde。
"abcdef"[4:1:-1] § 'edc' § 'edcb' ¦ 'bcd' ¦ '' § 负步长从e向前取，终点b不包含。
"abcdef"[-1:0:-2] § 'fdb' § 'fdb a' ¦ 'fda' ¦ 'eca' § 下标依次为5、3、1，取到f、d、b。
"abcdef"[::3] § 'ad' § 'abc' ¦ 'cf' ¦ 'ade' § 默认从下标0开始，每次前进3，取得a和d。
"abcdef"[2:99] § 'cdef' § !IndexError ¦ 'cd' ¦ '' § 切片终点超过长度会被截到有效边界。
"abcdef"[99:100] § '' § !IndexError ¦ 'f' ¦ None § 切片区间落在字符串之后，结果为空而不产生索引异常。
"abcdef"[-99:2] § 'ab' § '' ¦ !IndexError ¦ 'abc' § 过小的正向切片起点调整到开头，终点2不包含。
"abcdef"[3:1] § '' § 'dc' ¦ 'bc' ¦ !IndexError § 默认正步长无法从下标3走到更小的终点1，结果为空。
"abcdef"[1:5:-1] § '' § 'bcde' ¦ 'edcb' ¦ !ValueError § 负步长与起终方向不一致，切片为空。
"abcdef"[::-2] § 'fdb' § 'eca' ¦ 'fedcba' ¦ 'bdf' § 从末尾开始每次向前两格，取f、d、b。
"abcdef"[::0] § !ValueError § '' ¦ 'abcdef' ¦ !IndexError § 切片步长不能为零。
"abcdef"[len("abcdef") - 1] § 'f' § 'e' ¦ !IndexError ¦ 'abcdef' § 最后一个合法正索引是长度减1，即5。
"abcdef"[-6] § 'a' § 'f' ¦ '' ¦ !IndexError § 长度为6时，负索引-6对应第一个字符。
"abcdef"[-7] § !IndexError § 'a' ¦ '' ¦ None § 单字符索引必须落在有效范围，-7已越界。
"星期一星期二星期三"[3:6] § '星期二' § '星期一' ¦ '期二星' ¦ '二星期' § 每组三个字符，第二组位于下标3至5。
''')
section = 's3'
programs(r'''
s = "cat"↵s[0] = "b"↵print(s) § '!TypeError' § 'bat' ¦ 'cat' ¦ '!IndexError' § 字符串不可变，不能通过单字符索引直接赋值。
s = "cat"↵s = "b" + s[1:]↵print(s) § 'bat' § 'cat' ¦ 'bcat' ¦ '!TypeError' § 拼接得到新字符串，再把 s 绑定到它，不修改旧字符串。
s = "go"↵print(s * 0, len(s), sep=":") § ':2' § 'go:2' ¦ ':0' ¦ '!ValueError' § 乘零产生空字符串，原 s 的长度仍为2。
a = "red"↵b = a.replace("r", "b")↵print(a, b) § 'red bed' § 'bed bed' ¦ 'red red' ¦ '!TypeError' § replace返回新字符串，原字符串和名称 a 不受改变。
''')
expressions(r'''
"ab" * 3 == "a" * 3 + "b" * 3 § False § True ¦ 'ababab' ¦ !TypeError § 左边交替重复为ababab，右边为aaabbb。
"12" + str(3 * 4) § '1212' § '24' ¦ 24 ¦ !TypeError § 先算出12并转成文本，再与原文本12拼接。
"a" < "b" § True § False ¦ 'ab' ¦ !TypeError § 字符串按字符编码顺序比较，a在b之前。
"9" > "10" § True § False ¦ 9 ¦ !ValueError § 字符串按字典序比较，首字符9大于1，不按整数大小比较。
''')
section = 's4'
expressions(r'''
"  PyThOn  ".strip().lower() § 'python' § '  python  ' ¦ 'PYTHON' ¦ 'PyThOn' § 先去掉两端空白，再转为小写。
"one two one".replace("one", "1", 1) § '1 two one' § '1 two 1' ¦ 'one two 1' ¦ !TypeError § 第三个实参限制只替换一次，从左向右处理。
"go".center(6, "=") § '==go==' § '=go=' ¦ 'go====' ¦ '====go' § 最小宽度6比原长度多4，两侧各补两个等号。
"study".center(3, "-") § 'study' § 'stu' ¦ '-study-' ¦ !ValueError § 宽度是最小值，不足以容纳原串时仍返回完整原串。
"go".center(6, "ab") § !TypeError § 'abgoab' ¦ 'abgogo' ¦ !ValueError § center的填充字符参数必须恰好是单个字符。
"a-b-c".split("-", 1) § ['a', 'b-c'] § ['a', 'b', 'c'] ¦ ['a-b', 'c'] ¦ ['a-b-c'] § maxsplit为1时只拆开最左侧的一处分隔符。
"a  b".split(" ") § ['a', '', 'b'] § ['a', 'b'] ¦ ['a  b'] ¦ !ValueError § 指定单个空格作分隔符，连续两个空格之间产生空字段。
" ".join(["red", "blue"]) § 'red blue' § 'redblue' ¦ ['red', 'blue'] ¦ ' red blue ' § join仅在两个元素之间插入空格。
"/".join(["", "a", ""]) § '/a/' § 'a' ¦ '/a' ¦ 'a/' § 两个连接位置各插入斜线，空字符串元素被保留。
"-".join([1, 2]) § !TypeError § '1-2' ¦ '12' ¦ [1, 2] § join要求元素本身是字符串，不会自动转换整数。
"mississippi".count("issi") § 1 § 2 ¦ 3 ¦ 0 § count按不重叠的方式计数，两处重叠的issi只能计入一次。
"xyxydataxy".strip("xy") § 'data' § 'xydata' ¦ 'dataxy' ¦ 'xyxydata' § strip参数表示可从两端移除的字符集合，不是一个完整前后缀。
"  A  ".strip().center(3, ".") § '.A.' § 'A' ¦ '..A' ¦ 'A..' § 先清理两端空格得到A，再居中到3个字符宽。
"..A..".strip(".").lower() § 'a' § 'A' ¦ '..a..' ¦ '' § 去掉两端点号后，再把大写A转为小写。
"abc".replace("", "-") § '-a-b-c-' § 'a-b-c' ¦ '-abc' ¦ !ValueError § 空子串在首尾及相邻字符间都有位置，全部插入连接文本。
"hello".upper().lower() § 'hello' § 'HELLO' ¦ 'Hello' ¦ !AttributeError § upper返回大写文本，随后lower再返回小写文本。
"2026-11-12".split("-")[1] § '11' § '12' ¦ '2026' ¦ 11 § split得到三段字符串，索引1取月份文本11。
"a,b,c".replace(",", "") § 'abc' § 'a b c' ¦ 'a,b,c' ¦ ['a', 'b', 'c'] § 将逗号替换为空字符串等于删除这些逗号。
ord("B") - ord("A") § 1 § 0 ¦ 2 ¦ 'BA' § 相邻大写英文字母编码相差1。
chr(ord("a") + 2) § 'c' § 'a2' ¦ 'b' ¦ 99 § a的编码加2对应小写c，chr再转回字符。
len("甲,乙,丙".split(",")) § 3 § 5 ¦ 2 ¦ 1 § 两个逗号把字符串划分为三个元素。
"a\nb\n".split("\n") § ['a', 'b', ''] § ['a', 'b'] ¦ ['ab'] ¦ ['a\nb\n'] § 指定换行分隔符时，末尾分隔符之后产生一个空字段。
''')
section = 's5'
expressions(r'''
"{:05d}".format(23) § '00023' § '23' ¦ '23   ' ¦ '00230' § 整数字段宽度为5，不足部分在左侧补零。
"{:>5}".format("Hi") § '   Hi' § 'Hi   ' ¦ ' Hi ' ¦ 'Hi' § 大于号指定右对齐，宽度5减去两个字符留下三个前导空格。
"{:<5}".format("Hi") § 'Hi   ' § '   Hi' ¦ ' Hi ' ¦ 'Hi' § 小于号指定左对齐，末尾补三个空格。
"{:*^6}".format("ab") § '**ab**' § 'ab****' ¦ '****ab' ¦ '*ab*' § 居中宽度6，两侧各补两个星号。
"{:+d}".format(8) § '+8' § '8+' ¦ '8' ¦ '!ValueError' § 加号格式要求正数也显示符号。
"{:x}".format(255) § 'ff' § '0xff' ¦ '255' ¦ 'FF' § x按小写十六进制显示，未指定前缀标志时不带0x。
"{:b}".format(10) § '1010' § '0b1010' ¦ '10' ¦ '12' § b表示二进制文本形式，不带0b前缀。
"{:08.2f}".format(3.5) § '00003.50' § '0003.50' ¦ '3.500000' ¦ '    3.50' § 总宽度8包含小数点，3.50占4位，左侧补4个零。
"{{{}}}".format("x") § '{x}' § '{{x}}' ¦ 'x' ¦ !ValueError § 双花括号表示字面花括号，中间字段替换为x。
"{name}:{score}".format(name="Lin", score=90) § 'Lin:90' § 'name:score' ¦ '90:Lin' ¦ !KeyError § 命名字段使用同名关键字实参填充。
"{:.0%}".format(0.375) § '38%' § '0%' ¦ '37%' ¦ '0.375%' § 百分比格式先乘100，37.5按中点偶数规则显示为38%。
"{:6.1f}".format(12.5) § '  12.5' § '12.500' ¦ ' 12.5 ' ¦ '12.5' § 一位小数的12.5占4个字符，字段宽度6留下两个前导空格。
"{0:.1f}/{0:.2f}".format(2.5) § '2.5/2.50' § '2.5/2.5' ¦ '2.50/2.5' ¦ !IndexError § 同一个实参可以按不同格式在两个字段中重复使用。
"{:,.0f}".format(12000) § '12,000' § '12000' ¦ '12.000' ¦ '12,000.0' § 逗号启用千位分隔，零位小数不显示小数部分。
''')
section = 's6'
programs(r'''
week = "一二三四五六日"↵day = 7↵print("星期" + week[day - 1]) § '星期日' § '星期六' ¦ '!IndexError' ¦ '星期一' § 输入采用1至7编号，索引需要减1，7对应下标6。
week = "MonTueWedThuFriSatSun"↵day = 3↵start = (day - 1) * 3↵print(week[start:start + 3]) § 'Wed' § 'Tue' ¦ 'Thu' ¦ 'Mon' § 每天占3个字符，第3天从下标6开始截取3个字符。
''')
section = 's7'
concepts('''
同一时间戳在两个时区显示了不同小时，最合理的解释是什么？ § 同一时刻的本地时间表示因时区不同而变化 § 时间戳被自动乘以时差 § 两台机器必有一台不支持整数 § 小时只能由字符串长度确定 § 时间戳可代表同一时刻，转换为本地时间时使用不同的时区规则。
想把 UTC 时间和本地时间比较，首先应保证什么？ § 它们对应同一时刻并明确时区 § 两段文本长度不同 § 都删除日期只保留秒 § 必须把时间戳转为字符串拼接 § 比较前要确认表示对象及其时区，避免把表示差异误当作时刻差异。
`time.time()` 返回的数值主要适合表示什么？ § 自纪元起的秒数形式的时间戳 § 当前月份的中文名称 § CPU 型号 § 当前源文件行号 § time.time返回以秒表示的墙上时间戳，通常带有小数部分。
结构化时间对象中的年份与时间戳之间是什么关系？ § 年份是按时间规则转换后的字段 § 时间戳最后四位必然就是年份 § 结构化时间只保存一个毫秒整数 § 年份只能从文件名读取 § 结构化时间把时刻分解为年、月、日、时等字段。
''')
section = 's8'
programs(r'''
import time↵t = time.strptime("2026/02/03 04:05", "%Y/%m/%d %H:%M")↵print(t.tm_mon, t.tm_mday, t.tm_min) § '2 3 5' § '3 2 4' ¦ '2 3 4' ¦ '!ValueError' § 模板中的%m、%d与%M分别解析月、日和分钟。
import time↵t = time.strptime("2024-02-29", "%Y-%m-%d")↵print(time.strftime("%m/%d", t)) § '02/29' § '29/02' ¦ '2/29' ¦ '!ValueError' § 先解析闰年合法日期，再按带前导零的月日模板输出。
import time↵t = time.strptime("2026-11-12", "%Y/%m/%d")↵print(t.tm_year) § '!ValueError' § '2026' ¦ '11' ¦ '12' § 输入使用横线而模板要求斜线，格式不匹配会报错。
import time↵t = time.strptime("07:08:09", "%H:%M:%S")↵print(time.strftime("%S-%M-%H", t)) § '09-08-07' § '07-08-09' ¦ '9-8-7' ¦ '!ValueError' § 解析后按秒、分钟、小时的顺序重新格式化。
''')
concepts('''
`strftime()` 与 `strptime()` 的数据流方向，哪项正确？ § 前者从时间字段生成文本，后者从文本解析时间字段 § 两者都只能生成随机时间 § 两者都只能睡眠指定秒数 § 前者只能读取文件，后者只能写文件 § 名称相近但方向不同，format与parse分别对应格式化和解析。
在模板中使用 `%x` 输出日期，跨区域设置时应注意什么？ § 结果样式可能随区域设置变化 § 永远固定为 YYYY-MM-DD § 一定只输出秒数 § 必定抛出异常 § %x使用本地化日期表示，若要求固定协议应使用明确的年月日模板。
''')
section = 's9'
concepts('''
使用 `perf_counter()` 测量一次操作耗时，应如何计算？ § 结束读数减开始读数 § 把两个读数拼成文本 § 结束读数除以开始读数后直接作为秒数 § 只读取当前分钟字段 § perf_counter适合测量时间间隔，差值表示这段期间的耗时。
执行 `time.sleep(0.2)` 后，能否保证下一句恰在0.2秒时执行？ § 不能，调度等因素可能使恢复更晚 § 能，操作系统调度不会产生延迟 § 能，sleep会停止全世界所有时钟 § 不能，因为sleep参数只能是整数 § sleep请求暂停一段时间，实际恢复还受系统调度影响。
计时前后各调用一次 `time.time()`，系统时钟在中间被调整，可能造成什么？ § 墙上时钟差值不再可靠地表示真实耗时 § Python会自动删除程序 § 差值必定保持不变 § 所有浮点数都会变成字符串 § 墙上时钟可能调整，测量短时耗时更适合使用性能计数器。
''')

# Chapter 5: control flow, exceptions, iteration and random experiments.
chapter, section = 5, 's1'
expressions(r'''
not (3 < 2) and 4 <= 4 § True § False ¦ 4 ¦ !TypeError § 括号内为假，not得到真，另一个比较也为真。
1 < 3 < 5 § True § False ¦ 3 ¦ 5 § 连续比较相当于要求1小于3且3小于5。
1 < 3 > 2 § True § False ¦ 2 ¦ !SyntaxError § 连续比较允许比较方向变化，这里两次比较均成立。
3 == 3.0 and 3 != "3" § True § False ¦ 'True' ¦ !TypeError § 数字3与3.0相等，但与字符串3不相等。
not "" § True § False ¦ '' ¦ None § 空字符串真值为假，对其取not得到True。
[] or "fallback" § 'fallback' § [] ¦ True ¦ False § or在左操作数为假时返回右操作数本身。
"ready" and 0 § 0 § True ¦ False ¦ 'ready' § and在左边为真时返回右操作数，本例为整数0。
"first" or "second" § 'first' § 'second' ¦ True ¦ 'firstsecond' § or遇到第一个真值对象就返回它。
not 2 == 3 § True § False ¦ 2 ¦ !SyntaxError § 比较优先于not，先得到False再取反。
False and (1 / 0) § False § !ZeroDivisionError ¦ 0 ¦ None § and左边为假时短路，右侧除零不执行。
True or int("oops") § True § !ValueError ¦ False ¦ 'oops' § or左边为真时短路，不进行非法整数转换。
2 < 1 or 3 < 4 and 5 != 5 § False § True ¦ 4 ¦ 5 § 比较先算，and优先于or，最终为False。
(1 if "" else 2) + 3 § 5 § 4 ¦ 1 ¦ 2 § 空字符串条件为假，选择2，再加3。
0 <= -1 < 10 § False § True ¦ -1 ¦ !ValueError § 第一项比较0小于等于-1为假，整个连续比较为假。
bool([0]) and not bool([]) § True § False ¦ [0] ¦ [] § 非空列表为真，与其中元素是否为零无关，空列表为假。
''')
section = 's2'
programs(r'''
x = 0↵if x < 0:↵    print("negative")↵elif x == 0:↵    print("zero")↵else:↵    print("positive") § 'zero' § 'negative' ¦ 'positive' ¦ 'zero\npositive' § 第一分支不成立，第二分支成立，多分支只执行这一支。
age = 18↵if age < 18:↵    label = "child"↵else:↵    label = "adult"↵print(label) § 'adult' § 'child' ¦ 'child\nadult' ¦ '!NameError' § 18不满足严格小于18，执行else。
x = 5↵if x > 0:↵    if x % 2 == 0:↵        print("even")↵    else:↵        print("odd") § 'odd' § 'even' ¦ '' ¦ 'even\nodd' § x为正进入外层分支，内层偶数条件不成立，输出odd。
x = -2↵if x > 0:↵    print("P")↵if x < 0:↵    print("N")↵else:↵    print("Z") § 'N' § 'N\nZ' ¦ 'Z' ¦ '' § else与最近的同层if配对，第二个if成立时不执行else。
score = 80↵if score >= 90:↵    grade = "A"↵elif score >= 80:↵    grade = "B"↵elif score >= 60:↵    grade = "C"↵else:↵    grade = "D"↵print(grade) § 'B' § 'C' ¦ 'A' ¦ 'B\nC' § 按门槛从高到低检查，80属于第二档，并包含该档下端点。
x = 2↵if x > 1:↵    x += 3↵if x > 4:↵    x *= 2↵print(x) § '10' § '5' ¦ '4' ¦ '7' § 两个独立if依次执行，第二次判断使用更新后的5。
x = 2↵if x > 1:↵    x += 3↵elif x > 4:↵    x *= 2↵print(x) § '5' § '10' ¦ '4' ¦ '2' § if成立后整个if-elif结构结束，不再检查后续分支。
text = ""↵print(text[0] if text else "empty") § 'empty' § '!IndexError' ¦ '' ¦ 'None' § 条件表达式只求被选中的分支，空文本不会被索引。
value = -3↵label = "positive" if value > 0 else "nonpositive"↵print(label) § 'nonpositive' § 'positive' ¦ '-3' ¦ '!SyntaxError' § 条件为假时返回else后的表达式。
''')
concepts('''
某一档区间定义为 `18.5 <= bmi < 24`，值24应落在哪边？ § 不在这一档，应检查后续区间 § 必然还在这一档 § 同时属于这一档和所有更低档 § 不能使用浮点数比较 § 上端点采用严格小于，24被排除，需要由其他区间覆盖。
划分成绩区间时一段是 `score < 60`，另一段是 `score > 60`，遗漏了什么？ § score 等于60的情况 § 所有负数 § 所有整数 § score 等于59的情况 § 两边都是严格不等式，会遗漏公共边界60。
''')
section = 's3'
programs(r'''
try:↵    print(3 / 0)↵except ZeroDivisionError:↵    print("zero")↵print("done") § 'zero\ndone' § 'done' ¦ '!ZeroDivisionError' ¦ 'zero' § 匹配的except处理异常后，程序继续执行结构后的语句。
try:↵    int("bad")↵    print("after")↵except ValueError:↵    print("invalid") § 'invalid' § 'after\ninvalid' ¦ 'after' ¦ '!ValueError' § 异常发生后跳过try剩余语句，转入匹配的处理分支。
try:↵    int("bad")↵except TypeError:↵    print("type") § '!ValueError' § 'type' ¦ '' ¦ '!TypeError' § except类型不匹配，ValueError继续向外传播。
try:↵    print("A")↵except ValueError:↵    print("B")↵else:↵    print("C") § 'A\nC' § 'A\nB' ¦ 'C' ¦ 'A' § try正常完成后执行else，不执行except。
try:↵    int("bad")↵except ValueError:↵    print("B")↵finally:↵    print("C") § 'B\nC' § 'B' ¦ 'C' ¦ '!ValueError' § 匹配的处理分支输出B，之后finally仍会执行。
try:↵    int("bad")↵except ValueError:↵    value = 0↵print(value + 1) § '1' § '0' ¦ '!ValueError' ¦ '!NameError' § 处理分支为value赋默认值0，后续加1输出1。
try:↵    result = 10 / 2↵except ZeroDivisionError:↵    result = 0↵finally:↵    result += 1↵print(result) § '6.0' § '5.0' ¦ '1' ¦ '!NameError' § 正常运算得到5.0，finally将其加1。
try:↵    value = int("8")↵except ValueError:↵    print("bad")↵else:↵    print(value * 2)↵print("end") § '16\nend' § 'bad\nend' ¦ '8\nend' ¦ '16' § 转换成功，else使用转换结果输出16，随后输出end。
try:↵    print("abc"[9])↵except IndexError:↵    print("range")↵except ValueError:↵    print("value") § 'range' § 'value' ¦ '!IndexError' ¦ '' § 单字符索引越界产生IndexError，由第一个处理分支匹配。
''')
concepts('''
捕获输入转换异常后什么也不做，随后使用可能从未赋值的变量，有什么问题？ § 异常路径可能没有建立后续需要的状态 § except会自动创建所有变量 § 捕获异常必然使程序立即退出 § 所有变量会自动变成0 § 错误路径同样需要设计后续行为，不能假定失败的赋值已经完成。
''')
section = 's5'
programs(r'''
total = 0↵for x in [2, 4, 6]:↵    total += x↵print(total) § '12' § '6' ¦ '24' ¦ '0' § 累计器依次加2、4、6，最终为12。
result = ""↵for ch in "abc":↵    result = ch + result↵print(result) § 'cba' § 'abc' ¦ 'cc' ¦ '' § 每次把当前字符放到已有结果前面，逐步形成逆序文本。
count = 0↵for x in range(2, 9, 2):↵    count += 1↵print(count, x) § '4 8' § '5 10' ¦ '4 10' ¦ '3 6' § 依次取2、4、6、8，共4次，循环后x保留最后取值。
total = 10↵for x in range(0):↵    total += x↵print(total) § '10' § '0' ¦ '!NameError' ¦ '11' § range(0)为空，循环体不执行，原累计值10保持不变。
product = 1↵for x in range(1, 5):↵    product *= x↵print(product) § '24' § '120' ¦ '10' ¦ '0' § 依次乘1至4，初始乘积为1，最终为24。
count = 0↵for row in range(3):↵    for column in range(row):↵        count += 1↵print(count) § '3' § '6' ¦ '9' ¦ '0' § 内层分别执行0、1、2次，共3次。
total = 0↵for x in range(5):↵    if x % 2 == 0:↵        total += x↵print(total) § '6' § '10' ¦ '4' ¦ '9' § 在0至4中累加偶数0、2、4，得到6。
for x in "ab":↵    for y in "12":↵        print(x + y, end=" ") § 'a1 a2 b1 b2 ' § 'a1 b1 a2 b2 ' ¦ 'a1 b2 ' ¦ 'ab12 ' § 外层先固定a遍历两个数字，再固定b，end保留末尾空格。
total = 0↵for x in [1, 2, 3]:↵    total = x↵print(total) § '3' § '6' ¦ '0' ¦ '1' § 每轮都是覆盖赋值而非累加，因此留下最后一个元素3。
for x in range(1, 4):↵    print(x * x, end=",") § '1,4,9,' § '1,4,9' ¦ '0,1,4,' ¦ '1,2,3,' § range取1、2、3，逐项平方，最后仍输出end指定的逗号。
''')
section = 's6'
programs(r'''
n = 1↵count = 0↵while n < 10:↵    n *= 2↵    count += 1↵print(n, count) § '16 4' § '8 3' ¦ '10 4' ¦ '16 5' § n依次变成2、4、8、16，第四次更新后才不再满足条件。
n = 17↵digits = 0↵while n > 0:↵    n //= 10↵    digits += 1↵print(digits) § '2' § '1' ¦ '17' ¦ '3' § 每次整除10去掉一位，17经1到0，共两轮。
n = 123↵total = 0↵while n > 0:↵    total += n % 10↵    n //= 10↵print(total) § '6' § '123' ¦ '3' ¦ '321' § 每轮取末位并删除末位，累加3、2、1得到6。
x = 0↵while x:↵    x += 1↵print("end", x) § 'end 0' § 'end 1' ¦ '' ¦ '!ValueError' § 初始条件0为假，循环体一次也不执行。
n = 5↵while n > 1:↵    n -= 2↵print(n) § '1' § '0' ¦ '-1' ¦ '3' § 5减到3再减到1，下一次判断时退出。
balance = 1↵days = 0↵while balance < 8:↵    balance *= 2↵    days += 1↵print(days) § '3' § '2' ¦ '4' ¦ '8' § 连续三次翻倍为2、4、8，达到门槛后退出。
a, b = 0, 1↵while b < 8:↵    a, b = b, a + b↵print(a, b) § '5 8' § '8 13' ¦ '3 5' ¦ '5 10' § 同步更新产生相邻数列项，首次b不小于8时状态为5和8。
''')
section = 's7'
programs(r'''
for x in range(5):↵    if x == 2:↵        break↵    print(x, end="") § '01' § '012' ¦ '0134' ¦ '01234' § x等于2时先break，后面的print不再执行。
for x in range(5):↵    if x == 2:↵        continue↵    print(x, end="") § '0134' § '01' ¦ '01234' ¦ '034' § continue只跳过当前轮余下语句，后续3和4仍会处理。
for x in [2, 4, 6]:↵    if x % 2:↵        break↵else:↵    print("all even") § 'all even' § '' ¦ '!SyntaxError' ¦ '2 4 6' § 没有元素满足奇数条件，循环正常耗尽后执行else。
for x in [2, 3, 4]:↵    if x % 2:↵        print("odd")↵        break↵else:↵    print("all even") § 'odd' § 'odd\nall even' ¦ 'all even' ¦ '' § 在3处由break退出，循环else不执行。
n = 0↵while n < 2:↵    n += 1↵else:↵    print(n) § '2' § '1' ¦ '' ¦ '!SyntaxError' § while因条件变假正常结束，执行else。
n = 0↵while True:↵    n += 1↵    if n == 2:↵        break↵else:↵    print("normal")↵print(n) § '2' § 'normal\n2' ¦ '1' ¦ 'normal' § while由break退出，因此只执行结构后的输出。
count = 0↵for a in range(2):↵    for b in range(3):↵        break↵    count += 1↵print(count) § '2' § '1' ¦ '0' ¦ '6' § break退出最近的内层循环，外层仍执行两次。
n = 0↵total = 0↵while n < 4:↵    n += 1↵    if n == 2:↵        continue↵    total += n↵print(total) § '8' § '10' ¦ '6' ¦ '4' § 变量先更新，跳过n等于2的累加，其余1、3、4合计8。
for x in range(3):↵    if x < 2:↵        continue↵else:↵    print("done") § 'done' § '' ¦ '!SyntaxError' ¦ '2' § continue没有终止循环，正常耗尽时仍执行else。
''')
concepts('''
while 循环先检查某值，某条 continue 路径跳过了唯一的更新语句，可能发生什么？ § 状态不再推进，循环可能无法结束 § continue一定结束整个函数 § Python会自动增加该值 § else一定立即执行 § 需要逐条检查循环路径，保证每条需要继续的路径都能推进状态。
想找到首个符合条件的元素后立即停止扫描，应使用哪种安排？ § 在找到后记录结果并break § 每轮都先continue § 把循环条件永久设为真且不更新 § 无条件执行循环else § break能停止当前扫描，结果应在退出前保存。
''')
section = 's8'
concepts('''
`random.randint(1, 6)` 与 `random.randrange(1, 6)` 的取值边界有什么差别？ § 前者可取6，后者不取6 § 两者都不取1 § 前者不取1，后者可取6 § 两者都只返回浮点数 § randint包含两端，randrange遵守range的终点排除规则。
调用 `random.choice("ABC")`，可能的返回对象是什么？ § 一个字符字符串 § 三个字符组成的新列表 § 必定是整数下标 § 必定是布尔值 § choice从非空序列中选择一个元素，这里元素为字符。
想从20道不同题中抽5道且本轮不重复，应优先采用什么？ § random.sample(题目序列, 5) § 连续调用choice但不检查重复 § 取同一个题号重复五次 § 只打乱答案而不选择题目 § sample执行无放回抽样，适合本轮不重复的题目选择。
对3个不同元素执行 `random.sample(values, 4)` 会怎样？ § 抛出ValueError § 自动复制一个元素补足 § 返回4个相同元素 § 自动返回空字符串 § 无放回抽样不能请求超过总体数量的元素。
在相同环境里重设相同种子后，若多调用一次随机函数再做实验，会怎样？ § 后续随机序列位置可能改变 § 所有结果仍必须逐项完全相同 § 程序会成为语法错误 § 种子会把所有随机值变成零 § 可复现要求随机调用顺序也一致，多一次调用可能改变后续状态。
`random.random()` 的常用返回区间是哪一项？ § 大于等于0且小于1 § 大于0且小于等于1 § 包含0与1的所有整数 § 任意负整数 § random返回区间[0,1)中的伪随机浮点数。
需要打乱一份名单但保留原顺序副本，应该怎样做？ § 先复制名单，再对副本shuffle § 只把shuffle返回值当作新名单 § 把原名单转成同一个别名再shuffle § 不做复制直接shuffle原名单 § shuffle原地修改列表，独立副本才能保留原顺序。
判断 `random.randrange(3, 12, 4)` 的合法结果，应看哪个集合？ § 3、7、11 § 3、4、12 § 4、8、12 § 3至12的全部实数 § 取值规则与range(3,12,4)一致，终点12不包含。
''')
section = 's9'
concepts('''
随机撒点估计圆周率时，样本数增加，哪种表述合理？ § 通常可改善估计稳定性，但单次结果未必更接近真值 § 每增加一点误差都必然减小 § 达到100点就得到精确π § 样本数对随机误差完全无影响 § 随机估计存在波动，增加样本通常提高稳定性，但不保证每次单调改善。
四分之一圆撒点实验中，为什么用命中比例乘4？ § 单位正方形内四分之一单位圆面积为π/4 § 正方形有四条边所以任何比例都乘4 § 每个点必定被计算四次 § π被定义为任意命中数乘4 § 在均匀抽样前提下命中率估计面积比例π/4，因此乘4估计π。
若只在单位正方形左下角密集撒点，仍直接套用均匀撒点公式，有什么问题？ § 抽样分布不符合面积比例估计的前提 § 只会改变print输出宽度 § 点数会自动减半 § 所有非均匀抽样都精确得到π § 面积比例估计依赖合适的抽样分布，偏置采样会改变命中率的含义。
莱布尼茨级数计算π时只取有限项，结果应怎样理解？ § 是截断近似值，需要关注收敛和误差 § 是π的精确十进制表示 § 与项数完全无关 § 只要用float就不会有截断误差 § 有限求和是对无穷级数的截断，项数与数值误差都影响结果。
''')

# Chapter 6: function calls, parameters, results and state.
chapter, section = 6, 's1'
concepts('''
三处代码使用同样的含税价公式，税率规则又经常调整。怎样组织更便于维护？ § 抽成函数并由三处调用 § 每次手工改三份且不检查一致性 § 只改注释不改公式 § 把三处变量名都改成同一个字母 § 函数封装共同规则，使修改集中在明确的位置。
把输入读取、纯计算、输出显示拆成三个函数，有什么直接好处？ § 可以单独给计算函数传入样例并检查返回值 § 自动保证所有结果正确 § 计算函数必须访问网络 § 以后完全不需要测试 § 明确输入输出边界使计算逻辑更容易单独调用与验证。
函数名称与函数调用表达式怎样区分？ § 名称引用函数对象，名称后加括号才表示调用 § 只要提到名称就会立即执行函数体 § 没有形参就不需要调用括号 § 括号只用于编写注释 § 函数可以作为对象被引用，调用则用括号和实参发起执行。
''')
section = 's2'
programs(r'''
def mark():↵    print("M")↵print("A")↵mark()↵mark() § 'A\nM\nM' § 'M\nA\nM\nM' ¦ 'A\nM' ¦ 'M\nM\nA' § 定义时不执行函数体，两个调用分别输出一次M。
def double(x):↵    return x * 2↵print(double(double(3))) § '12' § '6' ¦ '9' ¦ '!TypeError' § 内层调用先返回6，外层再将6乘2得到12。
def announce():↵    print("called")↵saved = announce↵print("ready")↵saved() § 'ready\ncalled' § 'called\nready' ¦ 'ready' ¦ '!NameError' § 把函数对象绑定给saved不会调用，saved()才执行函数体。
def add_one(x):↵    return x + 1↵value = 3↵print(add_one(value), value) § '4 3' § '4 4' ¦ '3 3' ¦ '!TypeError' § 返回计算结果不会自动修改调用处的整数名称value。
def show(x):↵    print(x)↵show("A")↵print("B")↵show("C") § 'A\nB\nC' § 'A\nC\nB' ¦ 'B\nA\nC' ¦ 'A B C' § 每次调用在当前位置执行，返回后继续下一条语句。
''')
section = 's3'
programs(r'''
def subtract(a, b):↵    return a - b↵print(subtract(b=2, a=7)) § '5' § '-5' ¦ '!SyntaxError' ¦ '!TypeError' § 关键字实参按名称对应，书写顺序不决定a和b的绑定。
def combine(a, b=2, c=3):↵    return a + b * c↵print(combine(1, c=4)) § '9' § '7' ¦ '12' ¦ '!TypeError' § a取1，b使用默认2，c被指定为4，得到1加8。
def combine(a, b=2, c=3):↵    return a + b * c↵print(combine(1, 4)) § '13' § '9' ¦ '7' ¦ '!TypeError' § 第二个位置实参绑定b为4，c仍为3。
def f(a, b=2):↵    return a + b↵print(f(1, a=3)) § '!TypeError' § '4' ¦ '3' ¦ '!SyntaxError' § a同时收到位置实参与关键字实参，属于重复绑定。
def f(a, b=2):↵    return a + b↵print(f(c=3)) § '!TypeError' § '5' ¦ '3' ¦ '!NameError' § c不是签名接受的关键字，并且必需形参a没有取得值。
def f(a, b=2):↵    return a + b↵print(f()) § '!TypeError' § '2' ¦ '0' ¦ 'None' § b有默认值不代表a也有默认值，缺少必需实参。
def f(a, b=2):↵    return a + b↵print(f(1, 2, 3)) § '!TypeError' § '6' ¦ '3' ¦ '5' § 签名只接受两个位置实参，传入三个会失败。
def power(base=2, exponent=3):↵    return base ** exponent↵print(power(exponent=4), power(3, 2)) § '16 9' § '8 9' ¦ '16 6' ¦ '!TypeError' § 第一次只覆盖指数，第二次按位置覆盖两个默认值。
offset = 2↵def f(x=offset + 1):↵    return x↵offset = 10↵print(f(), f(offset)) § '3 10' § '11 10' ¦ '3 3' ¦ '!NameError' § 默认表达式在定义时求值得3，显式实参则读取调用时的10。
def remember(x, values=[]):↵    values.append(x)↵    return len(values)↵print(remember(1), remember(2, []), remember(3)) § '1 1 2' § '1 1 1' ¦ '1 2 3' ¦ '1 2 2' § 显式传入的新列表不修改默认列表，默认列表由第一次和第三次调用共享。
def collect(x, values=None):↵    if values is None:↵        values = []↵    values.append(x)↵    return values↵print(collect(1), collect(2)) § '[1] [2]' § '[1, 2] [1, 2]' ¦ '[1] [1, 2]' ¦ '!AttributeError' § 每次未传入列表时在函数体内创建独立列表，避免共享默认可变对象。
def scale(x, factor=2):↵    return x * factor↵print(scale(3), scale(3, factor=0)) § '6 0' § '6 6' ¦ '3 0' ¦ '!TypeError' § 显式的0是有效实参，会覆盖默认因子2。
''')
concepts('''
为可选参数提供默认值后，调用者显式传入 None，会自动使用默认值吗？ § 不会，None本身就是实际传入的值 § 会，所有假值都会触发默认值 § 会，但只对字符串函数生效 § 不会，因为None不能作为实参 § 默认值用于省略对应实参的情况，显式传入None仍会绑定None。
设计函数 `area(radius)` 时，用形参接收半径比直接读取固定全局名称更适合哪种目标？ § 让不同调用者传入各自的半径 § 保证任何输入都合法 § 禁止函数返回结果 § 自动安装数学库 § 显式参数使数据依赖清楚，也便于复用和测试。
''')
section = 's4'
programs(r'''
def f(*values):↵    return len(values), sum(values)↵print(f(), f(2, 3)) § '(0, 0) (2, 5)' § '(1, 0) (2, 5)' ¦ '(0, 0) (5, 2)' ¦ '!TypeError' § 可变位置形参把额外实参收成元组，无实参时为空元组。
def f(a, *rest):↵    return a * len(rest)↵print(f(4), f(4, 8, 9)) § '0 8' § '4 12' ¦ '0 12' ¦ '!TypeError' § rest不包含已绑定给a的首个实参，两次长度分别为0和2。
def joiner(*parts):↵    return "-".join(parts)↵print(joiner("a", "b", "c")) § 'a-b-c' § 'abc' ¦ 'a-b-c-' ¦ '!TypeError' § parts为包含三个字符串的元组，join在相邻元素间插入短横线。
def f(a, *rest):↵    return rest↵print(f(7, 8)) § '(8,)' § '8' ¦ '(7, 8)' ¦ '[8]' § 额外实参只有8，仍用单元素元组表示，显示时带逗号。
def f(*numbers):↵    return max(numbers) - min(numbers)↵print(f(3, 9, -1)) § '10' § '8' ¦ '9' ¦ '!TypeError' § 最大值9减最小值-1得到10。
''')
section = 's5'
programs(r'''
def f(x):↵    if x < 0:↵        return "N"↵    return "P"↵print(f(-1), f(0)) § 'N P' § 'N N' ¦ 'P P' ¦ 'N\nP' § 负数路径提前返回，零走到后面的return。
def f():↵    return 1↵    print("unreachable")↵print(f()) § '1' § 'unreachable\n1' ¦ 'None' ¦ '!SyntaxError' § return立即结束本次调用，其后的输出语句不会执行。
def f(flag):↵    if flag:↵        return 7↵print(f(True), f(False)) § '7 None' § '7 0' ¦ '7 7' ¦ '!TypeError' § 真分支显式返回7，假分支运行到函数末尾隐式返回None。
def pair(x):↵    return x, x + 1↵a, b = pair(4)↵print(a * b) § '20' § '9' ¦ '(4, 5)' ¦ '!ValueError' § 两项返回值组成元组，再解包为4与5，相乘得到20。
def f():↵    print("A", end="")↵    return "B"↵print(f()) § 'AB' § 'A\nB' ¦ 'B' ¦ 'ABNone' § 函数先输出A且不换行，返回B后外层print将B接在同一行。
def f():↵    return print("A")↵result = f()↵print(result is None) § 'A\nTrue' § 'A\nFalse' ¦ 'True' ¦ 'A\nA' § print输出A并返回None，函数把这个None返回给调用者。
def f(x):↵    return x + 1↵f(3)↵print("done") § 'done' § '4\ndone' ¦ '3\ndone' ¦ '' § 文件式执行中，未使用且未打印的返回值不会自动显示。
def f():↵    return 1, 2, 3↵a, b = f()↵print(a, b) § '!ValueError' § '1 2' ¦ '1 (2, 3)' ¦ '!TypeError' § 返回三项却只使用两个普通目标解包，数量不匹配。
def f(x):↵    if x == 0:↵        return↵    return x * 2↵print(f(0) is None, f(2)) § 'True 4' § 'False 4' ¦ 'True 2' ¦ '!SyntaxError' § 不带表达式的return返回None，另一路返回计算结果。
''')
section = 's6'
programs(r'''
count = 0↵def tick():↵    global count↵    count += 1↵tick()↵tick()↵print(count) § '2' § '0' ¦ '1' ¦ '!UnboundLocalError' § global指定模块级名称，两次调用累计修改同一个count。
x = 4↵def f():↵    global x↵    x = x + 3↵    return x↵print(f(), x) § '7 7' § '7 4' ¦ '4 4' ¦ '!UnboundLocalError' § 函数中的赋值因global作用于全局x，返回后全局值已为7。
data = [1]↵def f(values):↵    values.append(2)↵    values = [9]↵    return values↵answer = f(data)↵print(data, answer) § '[1, 2] [9]' § '[9] [9]' ¦ '[1] [9]' ¦ '[1, 2, 9] [9]' § 先修改共享列表，再将局部名称重新绑定，新绑定不撤销先前修改。
data = [1]↵def f(values):↵    values = values + [2]↵    return values↵print(f(data), data) § '[1, 2] [1]' § '[1, 2] [1, 2]' ¦ '[1] [1]' ¦ '!TypeError' § 列表加法创建新列表，局部重新绑定不修改原列表。
text = "A"↵def f(value):↵    value += "B"↵    return value↵print(f(text), text) § 'AB A' § 'AB AB' ¦ 'A A' ¦ '!TypeError' § 字符串不可变，局部拼接产生新字符串，调用者名称仍引用A。
x = 2↵def f():↵    return x↵x = 8↵print(f()) § '8' § '2' ¦ '!UnboundLocalError' ¦ '!NameError' § 函数体在调用时读取全局x，此时全局值已经变成8。
def f(x):↵    x += 1↵    return x↵a = 5↵b = f(a)↵c = f(a)↵print(a, b, c) § '5 6 6' § '7 6 7' ¦ '5 6 7' ¦ '6 6 6' § 两次都传入原来的整数5，每次局部计算返回6。
values = []↵def add(x):↵    values.append(x)↵add(2)↵add(3)↵print(values) § '[2, 3]' § '[]' ¦ '[3]' ¦ '!UnboundLocalError' § 这里只读取全局名称并修改其对象，没有重新绑定values，因此不需要global。
def f(x):↵    return x + 1↵value = f(2)↵print("x" in globals()) § 'False' § 'True' ¦ '3' ¦ '!NameError' § 函数形参是该调用的局部名称，不会自动在模块全局创建x。
''')
section = 's7'
expressions(r'''
(lambda x, y: x * 10 + y)(2, 3) § 23 § 32 ¦ 5 ¦ !SyntaxError § 两个位置实参依次绑定x和y，计算20加3。
(lambda x=4: x + 1)() § 5 § 4 ¦ None ¦ !TypeError § lambda可以包含默认形参，无实参时x取4。
(lambda text: text[0] + text[-1])("code") § 'ce' § 'co' ¦ 'de' ¦ 'code' § lambda返回字符串首尾两个字符的拼接。
(lambda x: x if x >= 0 else -x)(-7) § 7 § -7 ¦ True ¦ !SyntaxError § lambda主体为条件表达式，负数输入选择-x。
(lambda a, b=3: a ** b)(2, 2) § 4 § 8 ¦ 6 ¦ !TypeError § 第二个显式实参覆盖默认指数3，计算2的平方。
''')
concepts('''
lambda 主体里直接放两条用分号隔开的赋值语句，为什么不合适？ § lambda主体要求一个表达式 § lambda不能有任何形参 § lambda只能返回字符串 § lambda创建后不能调用 § lambda用于单个表达式，复杂的多条语句逻辑应使用def。
函数封装逐日变化时，把 up、down、days 都作为参数，直接改善什么？ § 不同规则可通过实参清楚地传入 § 所有增长模型都自动正确 § 函数必定比循环快 § 任何非法输入都会自动修正 § 参数让变化规则显式可配置，模型正确性仍需核对。
''')

# Chapter 7: recursion and composition.
chapter, section = 7, 's1'
concepts('''
一个递归函数有 `n == 0` 基例，但正数输入每次调用 `f(n + 2)`，问题是什么？ § 对这些输入无法朝基例推进 § 只要存在基例就一定终止 § 函数名不能调用自身 § 递归形参必须是字符串 § 基例与递归推进方向需要匹配，正数不断增大不能到达零。
递归证明中“假设规模更小的问题能正确求解”对应哪一步？ § 用子问题正确性说明当前组合规则正确 § 跳过所有基例检查 § 保证任何Python程序都不会异常 § 把全部输入都逐个运行 § 递归正确性通常需要基例、规模下降与组合步骤一起说明。
一个递归过程每次把正整数除以2向下取整，与每次减1相比，有什么差别？ § 子问题规模的缩小速度不同 § 两者每层一定使用完全相同的值 § 除以2一定不能到达基例 § 减1一定只调用一次 § 递归深度由规模变化决定，两种缩小方式的调用链长度不同。
对非负整数函数只写 `if n == 1` 作为基例，却允许输入0，应先检查什么？ § 零输入是否能沿合法路径终止 § 是否把函数名改成英文大写 § 是否必须加入绘图 § 是否每个参数都改为浮点数 § 输入范围与基例必须一致，零值若不被覆盖可能导致错误递归。
''')
section = 's2'
programs(r'''
def total(n):↵    if n == 0:↵        return 0↵    return n + total(n - 1)↵print(total(4) - total(2)) § '7' § '10' ¦ '3' ¦ '6' § 两次递归分别得到10和3，差为7。
def power(n):↵    if n == 0:↵        return 1↵    return 2 * power(n - 1)↵print(power(4)) § '16' § '8' ¦ '24' ¦ '5' § 基例为1，每回溯一层乘2，四层得到16。
def product(n):↵    if n <= 1:↵        return 1↵    return n * product(n - 2)↵print(product(5)) § '15' § '120' ¦ '5' ¦ '8' § 递归参数依次为5、3、1，返回5乘3乘1。
def f(n):↵    if n == 0:↵        return 1↵    return f(n - 1) + n * n↵print(f(3)) § '15' § '14' ¦ '7' ¦ '9' § 基例贡献1，随后加1、4、9得到15。
def f(n):↵    if n < 2:↵        return n↵    return f(n // 2) + 1↵print(f(8)) § '4' § '3' ¦ '8' ¦ '2' § 参数依次为8、4、2、1，基例返回1，回溯三次各加1。
def f(n):↵    if n == 0:↵        return 9↵    return f(n - 1)↵print(f(4)) § '9' § '4' ¦ '0' ¦ 'None' § 每层都原样返回更小调用的结果，最终全部传回基例值9。
def f(n):↵    if n == 0:↵        return 1↵    value = f(n - 1)↵    return value * 3↵print(f(3)) § '27' § '9' ¦ '6' ¦ '3' § 基例1经过三层各乘3，得到27。
def f(n):↵    if n == 0:↵        return 0↵    f(n - 1)↵    return n↵print(f(3)) § '3' § '0' ¦ 'None' ¦ '6' § 子调用虽被执行，其返回值未用于最终结果，最外层返回自己的n即3。
def f(n):↵    if n == 0:↵        return 0↵    return n + f(n - 1)↵print(f(0), f(1)) § '0 1' § '1 1' ¦ '0 0' ¦ '!RecursionError' § 零输入直接返回基例，1输入经过一次递归得到1加0。
''')
section = 's3'
programs(r'''
def reverse(s):↵    if len(s) <= 1:↵        return s↵    return reverse(s[1:]) + s[0]↵print(reverse("abc"), reverse("")) § 'cba ' § 'abc ' ¦ 'cba None' ¦ '!IndexError' § 非空串按尾部反转后接首字符，空串直接返回空字符串，print分隔空格保留。
def f(s):↵    if s == "":↵        return 0↵    return 1 + f(s[1:])↵print(f("Python")) § '6' § '5' ¦ '7' ¦ '!RecursionError' § 每层切去一个字符并加1，直到空串，结果为字符数6。
def f(s):↵    if s == "":↵        return ""↵    return s[0] + f(s[1:])↵print(f("abc")) § 'abc' § 'cba' ¦ 'aaa' ¦ '' § 首字符仍放在前面，递归重建原顺序而非反转。
def f(s):↵    if s == "":↵        return ""↵    return f(s[1:]) + s[0] * 2↵print(f("ab")) § 'bbaa' § 'aabb' ¦ 'baba' ¦ 'abab' § 先返回后缀反转结果，再追加双份首字符，得到bbaa。
def f(s):↵    if len(s) <= 1:↵        return s↵    return f(s[1:-1])↵print(f("abcde")) § 'c' § 'abcde' ¦ 'edcba' ¦ '' § 每次去掉首尾字符，abcde变bcd再变c。
''')
section = 's4'
programs(r'''
calls = 0↵def fib(n):↵    global calls↵    calls += 1↵    if n <= 2:↵        return 1↵    return fib(n - 1) + fib(n - 2)↵print(fib(4), calls) § '3 5' § '3 3' ¦ '5 5' ¦ '3 4' § fib4调用fib3和fib2，fib3再调用fib2和fib1，连根共5次。
def fib(n):↵    a, b = 1, 1↵    for i in range(n - 1):↵        a, b = b, a + b↵    return a↵print(fib(1), fib(5)) § '1 5' § '1 8' ¦ '0 5' ¦ '1 3' § 初始a为第一项，每次更新前进一项，n为5时更新四次得到5。
def ways(n):↵    if n == 0:↵        return 1↵    if n == 1:↵        return 1↵    return ways(n - 1) + ways(n - 2)↵print(ways(4)) § '5' § '3' ¦ '4' ¦ '8' § 两个基例均为1，后续依次为2、3、5。
''')
concepts('''
用循环保存斐波那契的相邻两项，为什么可减少朴素递归中的重复工作？ § 已计算的相邻结果被保留并用于下一步 § 循环会跳过全部加法 § 递归每次都必须读取网络 § 所有递归都比循环错误 § 朴素递归会反复计算相同子问题，循环直接复用已有状态。
斐波那契递归的结果正确但在大输入上很慢，应怎样描述？ § 正确性与计算代价需要分别评价 § 运行慢就等于数学结果错误 § 只要正确就无需考虑输入规模 § 函数只要调用自身就只做一次工作 § 结果是否符合定义与付出的计算量是不同维度。
''')
section = 's5'
concepts('''
汉诺塔从n层拆成三个阶段，中间那一步是什么？ § 将最大盘从源柱移到目标柱 § 同时移动所有盘 § 把小盘压在大盘下面 § 把最大盘移到已放小盘的辅助柱 § 先把上方n-1盘移开，再移动最大盘，最后把小盘移到目标柱。
汉诺塔移动次数满足 T(n)=2T(n-1)+1 且 T(0)=0，T(3)是多少？ § 7 § 3 § 6 § 8 § 依次计算T1为1、T2为3、T3为7。
汉诺塔递归调用时辅助柱与目标柱的位置会交换，这意味着什么？ § 形参角色取决于当前子任务 § 盘子的大小会自动改变 § 所有递归层共享一个局部形参槽 § 每层都必须使用相同目标柱 § 子任务有自己的源、辅助与目标角色，实参顺序表达角色变化。
''')
section = 's6'
concepts('''
一个“计算折扣”函数既请求网络又弹出窗口，还修改全局名单，复用困难的主要原因是什么？ § 混合了多种职责和隐式依赖 § 函数名超过四个字符 § 返回结果不是字符串 § 形参不是中文 § 把不相关的工作绑在一起会增加调用条件和维护负担。
价格获取模块改用另一家数据源，如果调用接口保持一致，理想情况下哪些部分可以少改？ § 仅通过该接口使用数据的计算模块 § 所有源代码都必须重新写 § Python保留字都要改名 § 计算公式必须改变 § 清晰稳定的模块边界可让内部实现变化少影响调用者。
测试收益率函数时，直接传入固定价格列表有何价值？ § 能在不依赖实时网络的情况下核对计算逻辑 § 证明任何数据源都永不出错 § 自动保证收益率模型符合所有业务需求 § 使浮点数变成无限精确 § 控制输入能独立检验计算，结论仍受样例与模型范围限制。
模块内几个函数都围绕同一种数据处理任务协作，主要体现什么？ § 职责相关、内聚较高 § 每个函数都应访问所有全局变量 § 不允许函数之间传参 § 只能写成一个无限长函数 § 高内聚强调模块内部功能围绕共同职责组织。
需要降低模块间耦合，哪种做法更合适？ § 通过明确参数和返回值传递必要数据 § 让模块读取彼此未约定的内部变量 § 让每个模块复制对方所有代码 § 每次改动都要求同步修改所有调用者 § 依赖稳定接口而非未约定内部状态，有助于降低耦合。
一个名为 `main()` 的普通Python函数为什么不会只因名字而自动运行？ § 仍需要在合适位置显式调用 § main是不能执行的保留字 § main只能返回浮点数 § Python不允许定义main § 名称main只是惯例，函数的执行需要调用安排。
函数封装和模块封装的层次关系，哪项合理？ § 模块可以组织一组相关函数与配置 § 一个模块只能包含一个表达式 § 函数不能出现在模块中 § 使用模块后不需要接口约定 § 模块提供更大范围的组织单元，可包含函数和必要配置。
''')
section = 's7'
concepts('''
查询模型列表成功，但筛选结果为空。应该核对哪组条件？ § 服务返回的模型、本地允许列表及任务分组的交集 § 只看网页背景色 § 只看程序文件大小 § 只看是否使用了print § 本章的筛选由多个条件共同决定，列表成功返回不保证交集非空。
一个接口成功返回对象，但调用代码读取的字段名不存在，应优先检查什么？ § 响应结构与取字段代码是否一致 § 是否给屏幕设置暗色模式 § 是否多加一个sleep § 是否把所有整数转为复数 § 接口使用需要核对返回结构，成功请求不代表任意字段都存在。
复用已创建的客户端对象，调用方应怎样传递它？ § 按函数接口约定把客户端作为实参传入 § 把它转换成随机整数 § 每次覆盖为None并假设仍复用 § 只在注释中写客户端名字 § 复用依赖显式对象传递及接口支持，不会凭注释自动发生。
文本问答函数接收 prompt，接口层负责请求。把请求地址写死在纯文本拼接函数中有什么缺点？ § 增加了与外部服务配置的无关依赖 § 会让字符串变成机器码 § Python禁止字符串含网址 § 函数不能返回拼接结果 § 文本处理与外部配置分工清晰时更易独立调用和替换。
网页示例明确使用固定模拟响应，运行成功能说明什么？ § 本次模拟条件下的调用与展示流程可工作 § 真实服务一定永不失败 § 任何真实密钥都有效 § 外部模型一定返回相同答案 § 模拟响应适合演示接口流程，不能替代真实服务环境的验证。
一个库名包含某服务品牌，能否仅凭库名确认实际请求地址？ § 不能，还需检查客户端的地址配置 § 能，库名会覆盖所有配置 § 能，URL没有实际作用 § 不能，因为所有请求都只发到本机 § 兼容接口的客户端可能被配置到不同服务，地址配置决定请求目标。
''')
section = 's8'
concepts('''
价格从100变成110，本章简单收益率公式得到什么？ § 0.1 § 10 § 1.1 § -0.1 § 简单收益率为新价除旧价减1，即110除100减1。
第一期价格没有更早的价格作为分母，计算逐期收益率时应怎样处理？ § 按约定标记缺失或排除该期变化 § 无条件把收益率写成100% § 把日期字符相加 § 假定前一价格永远为1 § 第一项缺少前项，必须遵循明确的数据约定处理。
处理单只股票图表时，为什么要核对绘图函数返回的 axes 形式？ § 单图与多图情况下返回对象的组织可能不同 § 单只股票不能绘图 § axes必定是价格列表 § 绘图函数一定返回整数0 § 本章示例强调零只、一只和多只情况，调用者应适配返回结构。
没有股票需要绘制时，主流程应如何安排？ § 先处理空输入，避免假定至少存在一张图 § 必须凭空创建一只股票的数据 § 把空列表当成一个价格 § 一定要访问axes[0] § 空数据属于边界情形，不能沿用要求非空的处理路径。
批量请求之间设置 sleep 的直接作用是什么？ § 在相邻请求间加入暂停 § 保证任何服务都不限制请求 § 自动修复所有网络错误 § 把请求变成无网络计算 § 暂停控制调用节奏，不等同于请求必定成功。
下载模块已经提供日期有序的价格，计算模块仍需要核对什么？ § 价格含义、缺失值和收益率约定 § 只核对图例字体大小 § 只核对股票名称长度 § 不需要任何数据约定 § 模块协作依赖数据协议，日期顺序只是其中一个条件。
''')

# Additional distinct boundary and composition cases complete each chapter.
chapter, section = 1, 's4'
concepts('''
“计算每月水费”只给出了用水量，没有说明阶梯单价，IPO中缺少什么？ § 从输入到结果的处理规则 § 是否安装键盘驱动 § 文件的图标 § 是否需要源代码 § 用水量是输入，水费是输出，但仍需明确如何计价。
同一份合法输入每次都应产生相同结果，测试却不同，应先复查什么？ § 是否存在未约定的随机性或外部状态依赖 § 是否把文件名写成中文 § 是否使用了加法 § 是否只有一个print § 输出不只取决于可见输入时，需要检查隐含的随机与环境依赖。
''')
section = 's8'
concepts('''
发现程序用了字节码，能否据此判断它采用静态类型检查？ § 不能，执行机制与类型检查属于不同维度 § 能，字节码只能来自静态类型语言 § 能，所有虚拟机禁止动态类型 § 不能，因为字节码不是程序表示 § 生成字节码说明执行链中的表示转换，不直接决定类型检查方式。
脚本在一台电脑正常运行，搬到另一台提示缺少模块。最直接应处理什么？ § 在目标解释器环境准备相应依赖 § 给源文件改成更长名称 § 把所有变量变为大写 § 删除全部导入后假设功能仍在 § 可移植运行仍依赖目标环境具备所需模块。
''')
section = 's5'
concepts('''
一个算法对所有正整数输入都正确，但题目还允许负数。采用它之前应做什么？ § 检查负数输入是否被定义并正确处理 § 直接把题目范围忽略 § 只要正数测试通过就宣布完成 § 把所有负号从输入中删除 § 正确性结论有适用范围，需要覆盖任务允许的全部输入。
''')
chapter, section = 2, 's5'
programs(r'''
text = "3.0"↵number = float(text)↵print(int(number), type(text).__name__) § '3 str' § '3.0 float' ¦ '3 int' ¦ '!ValueError' § 转换生成新对象，不会自动把原名称text绑定的字符串改成数值。
text = "8"↵print(text + "2", int(text) + 2) § '82 10' § '10 10' ¦ '82 82' ¦ '!TypeError' § 相同外观的字符参与拼接与数值相加时产生不同结果。
''')
section = 's2'
programs(r'''
x = 10↵y = x == 10↵x = 20↵print(y, x == 10) § 'True False' § 'False False' ¦ 'True True' ¦ '!SyntaxError' § y保存第一次比较得到的布尔值，不会随x重新赋值而重新计算。
a, b = "12"↵print(a, b, sep="-") § '1-2' § '12-' ¦ '12-12' ¦ '!TypeError' § 两字符字符串可逐字符解包，a与b分别为字符1和2。
a, b = "123"↵print(a, b) § '!ValueError' § '1 2' ¦ '1 23' ¦ '!TypeError' § 三个字符无法解包给两个普通目标，数量不匹配。
''')
chapter, section = 3, 's4'
expressions(r'''
list(range(6))[1::2] § [1, 3, 5] § [0, 2, 4] ¦ [1, 2, 3, 4, 5] ¦ [1, 3] § 先生成0到5，再从索引1起隔一个取一个。
len(range(10, -1, -3)) § 4 § 3 ¦ 5 ¦ 0 § 取值为10、7、4、1，下一项-2越过终点。
(2 - 3j) * 1j § (3+2j) § (-3+2j) ¦ (2-3j) ¦ (3-2j) § 展开得2j减3j平方，j平方为-1，因此为3加2j。
bool("False") == False § False § True ¦ 'False' ¦ !TypeError § 非空字符串False的真值为True，和布尔False比较为假。
''')
section = 's6'
expressions(r'''
pow(10, 0, 3) § 1 § 0 ¦ 3 ¦ !ValueError § 10的零次方为1，再对3取余仍为1。
sum(range(2, 11, 2), -2) § 28 § 30 ¦ 20 ¦ 32 § 偶数2、4、6、8、10的和为30，加起始值-2得到28。
min(abs(-8), abs(3), abs(-5)) § 3 § -8 ¦ -5 ¦ 8 § 先分别取绝对值得8、3、5，再选最小值3。
int(7 / 2) == 7 // 2 § True § False ¦ 3.5 ¦ !TypeError § 对正数结果，向零截断与向下取整都得到3。
int(-7 / 2) == -7 // 2 § False § True ¦ -3.5 ¦ !ValueError § 左边向零截断为-3，右边向下取整为-4，两者不同。
''')
section = 's7'
programs(r'''
level = 1.0↵for day in range(2):↵    level *= 1.5↵    level *= 0.5↵print(level) § '0.5625' § '1.0' ¦ '0.75' ¦ '2.25' § 每轮的合并因子为0.75，两轮得到0.75的平方0.5625，涨跌不相互抵消。
''')
chapter, section = 4, 's4'
expressions(r'''
"a,b,,c".split(",", 2) § ['a', 'b', ',c'] § ['a', 'b', '', 'c'] ¦ ['a,b', '', 'c'] ¦ ['a', 'b', 'c'] § 最多拆分两次，剩余部分连同尚未拆开的逗号作为末项。
"xoxox".strip("x") § 'oxo' § 'ooo' ¦ 'xoxox' ¦ 'oxox' § strip只去掉两端的x，中间的x不受影响。
" red\tblue ".split() § ['red', 'blue'] § ['', 'red', 'blue', ''] ¦ ['red\tblue'] ¦ [' red', 'blue '] § 不给分隔符时按空白拆分并合并连续空白，首尾不保留空字段。
"level".count("l", 1, 4) § 0 § 1 ¦ 2 ¦ !ValueError § 只检查下标1到3的eve，其中没有l。
"ab".center(4, "0")[::-1] § '0ba0' § '0ab0' ¦ 'ba' ¦ '00ba' § 居中填充得到0ab0，再反转整个结果得到0ba0。
"123".replace("2", "22").count("2") § 2 § 1 ¦ 3 ¦ 4 § 替换后为1223，其中字符2出现两次。
"a:b:c".split(":")[-1] § 'c' § 'a' ¦ ':c' ¦ ['c'] § 拆成三个字符串，负索引-1取最后一个元素c。
''')
section = 's5'
expressions(r'''
"{:>2}".format("hello") § 'hello' § 'he' ¦ 'lo' ¦ !ValueError § 普通字段宽度是最小宽度，不会把更长的字符串截断。
"{:.3}".format("abcdef") § 'abc' § 'def' ¦ 'abcdef' ¦ !ValueError § 字符串格式中的精度3限制最多显示前三个字符。
''')
section = 's8'
programs(r'''
import time↵t = time.gmtime(3600)↵print(time.strftime("%H:%M", t)) § '01:00' § '00:01' ¦ '08:00' ¦ '00:00' § gmtime使用UTC，纪元后3600秒对应UTC时间01时00分。
import time↵t = time.strptime("23:59", "%H:%M")↵print(time.strftime("%H时%M分", t)) § '23时59分' § '11时59分' ¦ '23时05分' ¦ '!ValueError' § %H为24小时制小时，%M为分钟，按模板保留数字和中文文字。
''')
chapter, section = 5, 's5'
programs(r'''
best = -10↵for x in [-7, -3, -8]:↵    if x > best:↵        best = x↵print(best) § '-3' § '0' ¦ '-8' ¦ '-10' § 维护当前最大值，-7和-3先后更新，-8不会覆盖-3。
total = 0↵for x in range(1, 4):↵    total += x↵    print(total, end=",") § '1,3,6,' § '1,2,3,' ¦ '6,' ¦ '0,1,3,' § 输出位于循环体中，每次显示本轮累加后的部分和。
text = "a1b2c3"↵count = 0↵for ch in text:↵    if ch in "0123456789":↵        count += 1↵print(count) § '3' § '6' ¦ '2' ¦ '0' § 遍历文本并按成员判断计数，数字字符共有三个。
for x in range(2):↵    print("A", end="")↵print("B") § 'AAB' § 'ABAB' ¦ 'AA\nB' ¦ 'AB' § 只有A的输出在循环内，B在两轮结束后输出一次。
count = 0↵for a in range(3):↵    for b in range(3):↵        if a == b:↵            count += 1↵print(count) § '3' § '9' ¦ '6' ¦ '1' § 九组组合中相等的只有(0,0)、(1,1)、(2,2)。
''')
section = 's6'
programs(r'''
n = 100↵count = 0↵while n >= 10:↵    n //= 10↵    count += 1↵print(n, count) § '1 2' § '0 3' ¦ '10 1' ¦ '1 3' § 条件包含10，因此100到10后还会执行一轮，最终为1。
n = 5↵total = 0↵while n > 0:↵    total += n↵    n -= 2↵print(total, n) § '9 -1' § '9 0' ¦ '15 0' ¦ '8 1' § 依次累加5、3、1，最后n减到-1使条件为假。
text = "abcd"↵while len(text) > 2:↵    text = text[1:]↵print(text) § 'cd' § 'ab' ¦ 'd' ¦ '' § 每次删除首字符，长度降到2时停止，保留cd。
''')
section = 's7'
programs(r'''
for x in range(4):↵    if x == 1:↵        continue↵    if x == 3:↵        break↵    print(x, end="") § '02' § '012' ¦ '023' ¦ '0' § 1被continue跳过，3在输出前break，只有0和2被显示。
found = False↵for x in [1, 3, 5]:↵    if x % 2 == 0:↵        found = True↵        break↵print(found) § 'False' § 'True' ¦ '5' ¦ '!NameError' § 没有偶数使条件成立，found保持初始False。
for x in range(2):↵    for y in range(2):↵        if y == 0:↵            continue↵        print(x, y) § '0 1\n1 1' § '0 0\n1 0' ¦ '0 1' ¦ '' § continue只作用于内层本轮，每个外层值都输出一次y为1的组合。
''')
section = 's8'
concepts('''
从有重复值的列表中无放回抽取两个位置，是否保证两次取出的值不同？ § 不保证，位置不同仍可能保存相同值 § 保证，无放回会自动修改所有重复值 § 保证，sample只接受互异数据 § 不保证，因为无放回意味着每次都取同一位置 § 无放回针对总体中的元素位置，若输入本身有重复值，结果值仍可能相同。
对随机过程做可复现实验，除了种子，还应该记录什么？ § 环境、输入数据与随机函数调用顺序 § 只记录编辑器字体 § 只记录屏幕分辨率 § 只记录程序行数 § 随机序列与环境、调用过程有关，完整实验条件有助于复现。
''')
section = 's2'
concepts('''
`if 0 < x < 10` 的 else 分支覆盖哪些数值情况？ § x小于等于0或大于等于10 § 只有x等于0 § 只有x等于10 § 只有负数 § else覆盖整个条件的否定，两端边界都在其中。
''')
chapter, section = 6, 's5'
programs(r'''
def split_time(seconds):↵    return seconds // 60, seconds % 60↵minutes, seconds = split_time(125)↵print(minutes, seconds) § '2 5' § '2 25' ¦ '125 60' ¦ '!ValueError' § 商与余数分别表示整分钟和剩余秒数。
def twice(f, value):↵    return f(f(value))↵def inc(x):↵    return x + 2↵print(twice(inc, 1)) § '5' § '3' ¦ '4' ¦ '!TypeError' § 传入的函数先把1变3，再把3变5。
def choose(flag):↵    if flag:↵        print("yes")↵        return 1↵    print("no")↵    return 0↵print(choose(False) + choose(True)) § 'no\nyes\n1' § 'yes\nno\n1' ¦ '1' ¦ 'no\nyes\n0' § 加法按从左到右求实参结果，先输出no再输出yes，两个返回值之和为1。
def bounds(values):↵    return min(values), max(values)↵low, high = bounds([3, -1, 8])↵print(high - low) § '9' § '7' ¦ '8' ¦ '11' § 先返回最小与最大值-1和8，再用上界减下界。
''')
section = 's3'
programs(r'''
def greet(name, prefix="Hi"):↵    return prefix + "," + name↵print(greet("Lin", prefix="Hello")) § 'Hello,Lin' § 'Hi,Lin' ¦ 'Lin,Hello' ¦ '!TypeError' § 关键字prefix覆盖默认问候词，name由首个位置实参提供。
base = 3↵def f(x=base):↵    return x↵base = 9↵def g(x=base):↵    return x↵print(f(), g()) § '3 9' § '9 9' ¦ '3 3' ¦ '!NameError' § 两个函数在不同时间定义，各自保存当时的默认值。
def f(a, b=1):↵    return a + b↵print(f(b=4, a=2), f(2)) § '6 3' § '6 6' ¦ '3 3' ¦ '!SyntaxError' § 第一次按关键字绑定2和4，第二次b使用默认1。
''')
section = 's6'
programs(r'''
items = [1]↵def f(values):↵    values.append(2)↵    return len(values)↵a = f(items)↵b = f(items)↵print(a, b, items) § '2 3 [1, 2, 2]' § '2 2 [1]' ¦ '2 3 [1]' ¦ '2 2 [1, 2]' § 两次传入同一列表，各追加一个2，长度依次为2和3。
x = 1↵def f():↵    global x↵    x += 1↵    return x↵print(f() + f(), x) § '5 3' § '4 2' ¦ '6 3' ¦ '!UnboundLocalError' § 两次调用依次返回2和3，求和为5，全局x最后为3。
def f(values):↵    values[0] = 9↵data = [1, 2]↵copy = data[:]↵f(copy)↵print(data, copy) § '[1, 2] [9, 2]' § '[9, 2] [9, 2]' ¦ '[1, 2] [1, 2]' ¦ '!TypeError' § 切片复制创建独立列表，修改副本元素不会改动原列表。
def f(text):↵    return text.upper()↵word = "hi"↵f(word)↵print(word) § 'hi' § 'HI' ¦ 'None' ¦ '!AttributeError' § upper返回新字符串，调用结果未重新赋给word，原值保持hi。
''')
section = 's4'
programs(r'''
def f(first, *rest):↵    return first, len(rest)↵print(f([1, 2, 3])) § '([1, 2, 3], 0)' § '(1, 2)' ¦ '(1, 3)' ¦ '!TypeError' § 整个列表是一个实参，绑定first，没有额外位置实参。
''')
section = 's8'
concepts('''
测试逐日增长函数时，`days=0` 的结果应怎样推导？ § 未发生更新，应保持约定的初始水平 § 必须等于一天后的水平 § 必须返回空字符串 § 必须先执行一次增长 § 零次迭代不改变状态，这是检查循环边界的一个有用样例。
''')
chapter, section = 7, 's2'
programs(r'''
def trace(n):↵    print(n, end=" ")↵    if n > 0:↵        trace(n - 1)↵trace(2) § '2 1 0 ' § '0 1 2 ' ¦ '2 1 ' ¦ '2 0 ' § 输出发生在递归调用前，连基例0也会输出。
def trace(n):↵    if n == 0:↵        return↵    trace(n - 1)↵    print(n, end=" ")↵trace(3) § '1 2 3 ' § '3 2 1 ' ¦ '0 1 2 3 ' ¦ '3 ' § 输出放在子调用返回后，按调用栈回溯顺序显示1、2、3。
def f(n):↵    if n <= 0:↵        return 0↵    return n + f(n - 2)↵print(f(6)) § '12' § '21' ¦ '6' ¦ '9' § 参数依次为6、4、2、0，累加得到12。
def f(n):↵    if n < 10:↵        return n↵    return n % 10 + f(n // 10)↵print(f(204)) § '6' § '204' ¦ '24' ¦ '2' § 递归按末位拆数，累加4、0和2。
def f(n):↵    if n == 0:↵        return "Z"↵    return "L" + f(n - 1) + "R"↵print(f(2)) § 'LLZRR' § 'LRLRZ' ¦ 'LZRLZR' ¦ 'LLRR' § 每一层在子结果外包一对L和R，得到LLZRR。
''')
section = 's3'
concepts('''
递归反转字符串时，使用 `s[1:]` 是否会原地删除原串首字符？ § 不会，切片产生子串，原字符串保持不变 § 会，而且所有别名也缩短 § 会，字符串因此成为可变对象 § 不会，因为切片不能用于递归 § 字符串不可变，切片获得新的文本结果，不原地删除字符。
递归反转字符串代码写成 `s[0] + reverse(s[1:])`，为何没有反转？ § 首字符仍放在后缀结果前，保留了原次序 § 字符串不能拼接 § 递归函数不能有返回值 § 基例必须是整数1 § 反转需要先取得反转后缀，再把原首字符追加到末尾。
''')
section = 's6'
programs(r'''
def get_values():↵    return [2, 4, 6]↵def average(values):↵    return sum(values) / len(values)↵def main():↵    return average(get_values())↵print(main()) § '4.0' § '12' ¦ '3' ¦ 'None' § main串联取数据和计算两个模块化步骤，平均值12除3为4.0。
def transform(value):↵    return value * 2↵def report(value):↵    return "结果=" + str(value)↵print(report(transform(5))) § '结果=10' § '结果=5' ¦ '结果=55' ¦ '!TypeError' § 内层计算得到10，外层只负责把结果组织成文本。
''')
section = 's8'
concepts('''
某股票两期价格为50和45，按简单收益率公式，哪种解释正确？ § 收益率为-0.1，表示下跌10% § 收益率为0.1，表示上涨10% § 收益率为-5，表示下跌500% § 收益率为0.9，表示上涨90% § 45除50减1得到-0.1，负号表示相对前一期下跌。
''')

def write_bank():
    from collections import Counter
    counts = Counter(q['chapter'] for q in items)
    print('Chapter counts:', dict(counts), 'total:', len(items))
    assert counts == {1: 50, 2: 65, 3: 85, 4: 90, 5: 90, 6: 65, 7: 55}, counts
    old = json.loads((ROOT / 'src/data/course.json').read_text())
    normalize = lambda s: re.sub(r'\s+', '', s).replace('`', '').replace('，', ',').replace('？', '?')
    known = {normalize(q['prompt']) for c in old['chapters'] for q in c['questions']}
    slots = list(range(4)) * 125
    random.Random(20261112).shuffle(slots)
    result = []
    for i, q in enumerate(sorted(items, key=lambda q: q['chapter'])):
        signature = normalize(q['prompt'])
        assert signature not in known, ('Duplicate question', i + 1)
        known.add(signature)
        wrong = q.pop('wrong')
        random.Random(i + 500).shuffle(wrong)
        right = q.pop('correct')
        wrong.insert(slots[i], right)
        result.append(dict(id=f'bank-{i+1:03}', number=i+1, pool='expansion', context=None,
                           options=[dict(label=label, markdown=value) for label, value in zip('ABCD', wrong)],
                           answer='ABCD'[slots[i]], **q))
    payload = dict(version=1, title='前七章综合题库', questions=result)
    (ROOT / 'src/data/question-bank.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
    print('Wrote 500 unique additional questions.')


if __name__ == '__main__':
    write_bank()
