# futurecoder 中文化分支说明

本分支 `zh-cn` 用于维护和验证 `futurecoder` 简体中文版。

## 目标

把 futurecoder 做成适合中文初学者使用的交互式 Python 学习平台，同时尽量保留上游项目结构和后续同步能力。

## 当前原则

- 不直接硬改英文课程源码。
- 优先使用上游已有的 `gettext` 翻译机制。
- 中文翻译资源放在 `translations/locales/zh/LC_MESSAGES/`。
- Python 关键字、变量名、函数名、代码块和特殊占位符保持原样。
- 编程专业术语每次出现都采用“中文术语（English term）”形式。
- 每次修改后运行目录同步、术语规范化、占位符检查、MO 编译和实际页面验证。

详细规则见：

```text
docs/zh-cn/TRANSLATION_STYLE_GUIDE.md
```

## 上游翻译机制

`core/translation.py` 中的 `set_language(language)` 会加载：

```text
translations/locales/<language>/LC_MESSAGES/futurecoder.mo
```

中文语言代码使用 `zh`，对应目录为：

```text
translations/locales/zh/LC_MESSAGES/
```

`scripts.generate_static_files` 读取：

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
scripts/zh_cn/sync_zh_catalog.py
scripts/zh_cn/apply_bilingual_terms.py
scripts/zh_cn/check_po_placeholders.py
scripts/zh_cn/build_zh.sh
translations/locales/zh/LC_MESSAGES/futurecoder.po
```

其中：

- `sync_zh_catalog.py`：把当前源码新增的翻译键同步进中文 PO。
- `apply_bilingual_terms.py`：把所有配置的编程术语统一为“中文术语（English term）”。
- `check_po_placeholders.py`：检查特殊占位符、Markdown 反引号和 PO 编译。
- `build_zh.sh`：按照正确顺序运行完整中文构建链路。

## 环境要求

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

脚本依次执行：

```text
生成当前英文翻译目录和代码块元数据
                ↓
同步中文 PO 与当前源码的翻译键
                ↓
全量应用中英双语专业术语
                ↓
验证术语转换具有幂等性
                ↓
检查 PO 并编译 futurecoder.mo
                ↓
生成中文前端课程数据
```

术语规范化会直接修改：

```text
translations/locales/zh/LC_MESSAGES/futurecoder.po
```

同时生成两个仅供本地检查的报告：

```text
translations/zh_missing_report.txt
translations/zh_bilingual_terms_report.txt
```

这两个报告已加入 `.gitignore`，不需要提交。

## 启动前端

构建成功后执行：

```bash
cd frontend
npm start
```

浏览器访问：

```text
http://localhost:3000/course/
```

前端依赖已经安装且 `package-lock.json` 未变化时，不需要重复执行 `npm ci`。

## 分步命令

需要单独检查术语时：

```bash
poetry run python scripts/zh_cn/apply_bilingual_terms.py \
  translations/locales/zh/LC_MESSAGES/futurecoder.po \
  --report translations/zh_bilingual_terms_report.txt
```

验证没有遗漏的裸中文术语：

```bash
poetry run python scripts/zh_cn/apply_bilingual_terms.py \
  translations/locales/zh/LC_MESSAGES/futurecoder.po \
  --check
```

检查并编译 PO：

```bash
poetry run python scripts/zh_cn/check_po_placeholders.py \
  translations/locales/zh/LC_MESSAGES/futurecoder.po \
  --compile
```

生成中文前端数据：

```bash
FIX_CORE_IMPORTS=1 \
FUTURECODER_LANGUAGE=zh \
poetry run python -m scripts.generate_static_files
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

## 构建后的提交范围

完成页面检查后，通常提交：

```text
translations/locales/zh/LC_MESSAGES/futurecoder.po
translations/locales/zh/LC_MESSAGES/futurecoder.mo
```

构建环境导致 `core/core_imports.txt` 出现无关变化时，可以恢复：

```bash
git restore core/core_imports.txt
```

然后检查并提交：

```bash
git status
git diff -- translations/locales/zh/LC_MESSAGES/futurecoder.po

git add translations/locales/zh/LC_MESSAGES/futurecoder.po \
        translations/locales/zh/LC_MESSAGES/futurecoder.mo

git commit -m "Apply bilingual terminology across Chinese translations"
git push origin zh-cn
```

## 页面验证重点

1. 首页、菜单、设置和按钮是否完整显示中文。
2. 页面标题和正文中的专业术语是否每次都保留中英文。
3. `__program__`、`__code0__` 等占位符是否正确展开。
4. 行内代码、代码块、变量名和函数名是否保持原样。
5. 输入代码后自动判题是否仍然正常。
6. Hint、错误解释和特殊错误消息是否正确显示。
7. f-string、字典字面量和大括号是否未被翻译逻辑破坏。
8. `AUTO-FALLBACK` 条目是否仍有需要翻译的英文正文。
