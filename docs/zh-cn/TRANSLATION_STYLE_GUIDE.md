# 中文翻译规范

## 目标读者

中文零基础或低基础 Python 学习者。翻译应尽量降低挫败感，解释清楚每一步为什么这样做。

## 总体风格

- 中文表达要自然、直接、短句优先。
- 不要机械直译英文。
- 面向初学者时，优先解释“为什么”和“下一步该做什么”。
- 遇到错误提示时，语气要具体、可操作，避免责备。

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

## 专有名词处理

建议采用“英文术语 + 中文解释”的第一次出现形式：

```text
variable（变量）
function（函数）
loop（循环）
list（列表）
dictionary（字典）
traceback（错误追踪信息）
```

后续可直接使用中文或英文，视上下文自然程度决定。

## 错误提示翻译原则

英文：

```text
Your code didn't produce the expected output.
```

推荐：

```text
你的代码运行了，但输出结果和预期不一致。先检查 print() 的内容、顺序和大小写。
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

| English | 中文建议 |
|---|---|
| variable | 变量 |
| string | 字符串 |
| integer | 整数 |
| float | 浮点数 |
| list | 列表 |
| dictionary | 字典 |
| loop | 循环 |
| function | 函数 |
| argument | 实参 |
| parameter | 形参 / 参数 |
| return value | 返回值 |
| traceback | 错误追踪信息 |
| shell | 交互式 shell |
| editor | 代码编辑器 |
| expression | 表达式 |
| statement | 语句 |
| indentation | 缩进 |
| boolean | 布尔值 |

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
