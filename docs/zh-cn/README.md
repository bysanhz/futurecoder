# futurecoder 中文化分支说明

本分支 `zh-cn` 用于维护和验证 `futurecoder` 简体中文版。

## 当前状态

中文 gettext 文件已经存在：

```text
translations/locales/zh/LC_MESSAGES/futurecoder.po
```

当前检查结果：

```text
total entries      : 1581
translated entries : 1581
empty entries      : 0
coverage           : 100.00%
```

这表示所有现有 gettext 条目都有中文 `msgstr`。但 100% 覆盖不等于所有翻译都已完成运行时验证，仍需检查页面渲染、代码占位符、判题逻辑和中文表达质量。

## 目标

把 futurecoder 做成适合中文初学者使用的交互式 Python 学习平台，同时尽量保留上游项目结构和后续同步能力。

## 当前原则

- 不直接硬改英文源码文本。
- 优先使用上游已有的 `gettext` 翻译机制。
- 中文翻译资源放在 `translations/locales/zh/LC_MESSAGES/`。
- Python 关键字、内置函数、代码块、程序占位符默认保留英文。
- 每次修改一批内容后运行检查和实际页面验证。

## 上游翻译机制

`core/translation.py` 中的 `set_language(language)` 会加载：

```text
translations/locales/<language>/LC_MESSAGES/futurecoder.mo
```

中文语言代码使用：

```text
zh
```

对应目录为：

```text
translations/locales/zh/LC_MESSAGES/
```

`scripts.generate_static_files` 会读取环境变量：

```text
FUTURECODER_LANGUAGE=zh
```

并生成中文版本的：

```text
frontend/src/chapters.json
frontend/src/book/pages.json.load_by_url
frontend/src/terms.json
frontend/src/python_core.tar.load_by_url
```

## 中文化辅助文件

```text
docs/zh-cn/README.md
docs/zh-cn/TRANSLATION_STYLE_GUIDE.md
docs/zh-cn/TODO.md
scripts/zh_cn/check_po_placeholders.py
scripts/zh_cn/build_zh.sh
translations/locales/zh/LC_MESSAGES/futurecoder.po
```

## 环境准备

上游当前要求：

```text
Python 3.12.1
Poetry
Node.js >= 22.17.0
npm >= 10.9.2
```

首次安装 Python 依赖：

```bash
poetry install
```

首次安装前端依赖：

```bash
cd frontend
npm ci
cd ..
```

## 一键生成中文版

在仓库根目录执行：

```bash
bash scripts/zh_cn/build_zh.sh
```

脚本会依次执行：

```text
检查 futurecoder.po
        ↓
编译 futurecoder.mo
        ↓
设置 FUTURECODER_LANGUAGE=zh
        ↓
生成中文前端课程数据
```

生成完成后启动前端：

```bash
cd frontend
npm start
```

浏览器访问：

```text
http://localhost:3000/course/
```

## 分步命令

不使用一键脚本时，可以手动执行：

```bash
poetry run python scripts/zh_cn/check_po_placeholders.py \
  translations/locales/zh/LC_MESSAGES/futurecoder.po \
  --compile

FIX_CORE_IMPORTS=1 \
FUTURECODER_LANGUAGE=zh \
poetry run python -m scripts.generate_static_files

cd frontend
npm start
```

## 本地同步本分支

```bash
git fetch origin
git checkout zh-cn
git pull origin zh-cn
```

本地已有 `zh-cn` 但还没设置 upstream 时：

```bash
git branch --set-upstream-to=origin/zh-cn zh-cn
git pull
```

## 下一阶段验证重点

1. 首页、菜单、设置、按钮是否全部显示中文。
2. 第一章到最后一章的课程标题是否完整。
3. `__program__`、`__code0__` 等占位符是否正常渲染为代码块。
4. 输入代码后自动判题是否仍然正常。
5. Hint、错误解释、特殊错误消息是否显示中文。
6. f-string、字典字面量中的大括号是否没有被格式化逻辑误处理。
7. 中文标点、术语和语气是否统一。
8. 页面中是否仍存在不应出现的英文 UI 文本。
