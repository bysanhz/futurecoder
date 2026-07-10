# 中文翻译规范

## 目标读者

中文零基础或低基础 Python 学习者。翻译应尽量降低挫败感，解释清楚每一步为什么这样做。

## 总体风格

- 中文表达要自然、直接、短句优先。
- 不要机械直译英文。
- 面向初学者时，优先解释“为什么”和“下一步该做什么”。
- 遇到错误提示时，语气要具体、可操作，避免责备。
- 专业术语每次出现都采用“中文术语（英文原词）”形式，帮助学习者持续对应英文资料。

## 代码相关内容

### 不翻译的内容

以下内容默认不翻译：

```text
print
input
for
while
if
elif
else
def
return
class
import
from
True
False
None
list
dict
range
len
str
int
float
```

### 变量名

默认不翻译变量名。原因：

- 中文变量名会增加输入法切换负担。
- Python 初学者需要尽早熟悉英文代码环境。
- 上游测试和判题逻辑往往依赖变量名。

如果必须翻译变量名，必须同步检查：

- `code_bits.*`
- step program
- hints
- disallowed messages
- tests
- Parsons problems

## 必须保留的特殊内容

翻译时不得破坏：

```text
__program__
__code0__
__code1__
__code2__
{占位符}
`inline code`
```python code blocks
Markdown 链接格式
Python 缩进
```

如果 `msgid` 和 `msgstr` 中特殊占位符不一致，`core/translation.py` 会触发检查错误。

## 专有名词与双语术语

### 基本格式

页面标题、章节标题、正文、提示、要求、评估信息和错误说明中，只要出现规定的编程专业术语，都采用：

```text
中文术语（English term）
```

例如：

```text
变量（variable）
函数（function）
循环（loop）
列表（list）
字典（dictionary）
字符串（string）
表达式（expression）
语句（statement）
错误追踪信息（traceback）
```

中文放在前面，方便中文初学者阅读；英文原词放在全角括号中，方便学习者查阅 Python 官方文档、英文教程和报错信息。

### 使用频率

- 专业术语每次出现都必须保留中英文，不限于首次出现。
- 同一句或同一段中重复出现同一术语时，也仍使用完整的双语形式。
- 页面标题已经包含双语术语时，正文再次出现该术语仍应保留中英文。
- 不得为了缩短句子而省略英文原词。

推荐：

```text
这些值称为变量（variable）。变量（variable）可以在程序运行过程中保存和引用数据。
```

不推荐：

```text
这些值称为变量（variable）。变量可以在程序运行过程中保存和引用数据。
```

也不推荐：

```text
这些值称为变量。变量可以在程序运行过程中保存和引用数据。
```

### Python 代码名称

Python 关键字、内置函数、类型名、变量名、函数名和类名保持英文代码形式，不作为普通术语翻译：

```text
使用 `print()` 函数（function）输出内容。
`word` 是变量（variable）名。
`list` 是 Python 的内置类型（type）。
```

概念名称始终中英并列，实际代码名称必须保持原样：

```text
列表（list）是一种按顺序保存多个值的数据结构（data structure）。
使用 `list()` 可以创建列表（list）。
```

### 大小写与标点

- 英文术语保留标准大小写。
- 中文与括号之间不加空格：`变量（variable）`。
- 使用中文全角括号 `（ ）`，不使用半角括号 `( )`。
- 行内代码仍使用反引号，例如 `print()`、`word`、`list`。

## 错误提示翻译原则

英文：

```text
Your code didn't produce the expected output.
```

推荐：

```text
你的代码运行了，但输出结果和预期不一致。先检查 `print()` 的内容、顺序和大小写。
```

不推荐：

```text
你的代码是错的。
```

## hint 翻译原则

hint 应该逐步给线索，而不是直接暴露答案。

推荐结构：

```text
1. 先提示要观察哪里。
2. 再提示可能要用哪个语法。
3. 最后才接近答案。
```

## 术语统一表

| English | 中文建议 | 强制使用形式 |
|---|---|---|
| variable | 变量 | 变量（variable） |
| string | 字符串 | 字符串（string） |
| integer | 整数 | 整数（integer） |
| float | 浮点数 | 浮点数（float） |
| list | 列表 | 列表（list） |
| dictionary | 字典 | 字典（dictionary） |
| loop | 循环 | 循环（loop） |
| function | 函数 | 函数（function） |
| argument | 实参 | 实参（argument） |
| parameter | 形参 / 参数 | 形参（parameter） |
| return value | 返回值 | 返回值（return value） |
| traceback | 错误追踪信息 | 错误追踪信息（traceback） |
| shell | 交互式 Shell | 交互式 Shell（shell） |
| editor | 代码编辑器 | 代码编辑器（editor） |
| expression | 表达式 | 表达式（expression） |
| statement | 语句 | 语句（statement） |
| indentation | 缩进 | 缩进（indentation） |
| boolean | 布尔值 | 布尔值（Boolean） |
| type | 类型 | 类型（type） |
| data structure | 数据结构 | 数据结构（data structure） |

## 提交要求

每次提交建议只覆盖一类内容：

```text
Translate homepage UI
Translate chapter 1 first pass
Translate chapter 2 strings
Translate beginner traceback messages
Fix zh placeholders
```

不要一次性混合大量章节和代码改动。
