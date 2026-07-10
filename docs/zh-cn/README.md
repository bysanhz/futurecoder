# futurecoder 中文化分支说明

本分支 `zh-cn` 用于把 `futurecoder` 逐步中文化。

## 目标

把 futurecoder 做成适合中文初学者使用的交互式 Python 学习平台，同时尽量保留上游项目的结构和可升级性。

## 当前原则

- 不直接硬改英文源码文本。
- 优先使用上游已有的 `gettext` 翻译机制。
- 中文翻译资源放在 `translations/locales/zh/LC_MESSAGES/`。
- Python 关键字、内置函数、代码块、程序占位符默认保留英文。
- 每次翻译一小批内容后运行检查，避免破坏交互判题。

## 上游翻译机制

`core/translation.py` 中的 `set_language(language)` 会加载：

```text
translations/locales/<language>/LC_MESSAGES/futurecoder.mo
```

因此中文语言代码先使用：

```text
zh
```

对应目录为：

```text
translations/locales/zh/LC_MESSAGES/
```

## 本分支初始文件

```text
docs/zh-cn/README.md
docs/zh-cn/TRANSLATION_STYLE_GUIDE.md
scripts/zh_cn/check_po_placeholders.py
translations/locales/zh/LC_MESSAGES/futurecoder.po
```

## 推荐开发流程

1. 先确认英文原版能正常运行。
2. 补充 `futurecoder.po` 中的中文翻译。
3. 编译 `futurecoder.po` 为 `futurecoder.mo`。
4. 用 `lang=zh` 或项目入口中的语言配置加载中文。
5. 运行页面，检查 UI、课程正文、提示和判题逻辑。
6. 每次只翻译一批内容，提交一个清晰 commit。

## 本地同步本分支

如果远程分支已经存在，执行：

```bash
git fetch origin
git checkout zh-cn
git pull origin zh-cn
```

如果本地已有 `zh-cn` 分支但没设置 upstream：

```bash
git branch --set-upstream-to=origin/zh-cn zh-cn
git pull
```
