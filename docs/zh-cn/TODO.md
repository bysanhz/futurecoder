# futurecoder 中文化 TODO

## 0. 当前已确认

- `bysanhz/futurecoder` fork 已创建。
- `origin` 指向 `https://github.com/bysanhz/futurecoder.git`。
- `upstream` 指向 `https://github.com/alexmojaki/futurecoder.git`。
- 远程分支 `zh-cn` 已创建。
- 仓库中已经存在中文 PO 文件：

```text
translations/locales/zh/LC_MESSAGES/futurecoder.po
```

该文件已有部分中文翻译，不是空文件。

## 1. 本地同步远程 zh-cn 分支

如果你已经在本地创建了 `zh-cn` 分支，执行：

```bash
git fetch origin
git branch --set-upstream-to=origin/zh-cn zh-cn
git pull
```

如果本地没有该分支，执行：

```bash
git fetch origin
git checkout -b zh-cn origin/zh-cn
```

## 2. 本地安装依赖

项目使用 Poetry。建议先按上游 README 跑通英文原版，再处理中文。

```bash
poetry install
```

如果只想先检查 PO 文件，可确保安装 `polib`：

```bash
python -m pip install polib
```

## 3. 检查中文 PO 占位符

运行：

```bash
python scripts/zh_cn/check_po_placeholders.py translations/locales/zh/LC_MESSAGES/futurecoder.po
```

重点检查：

```text
__program__
__code0__
__code1__
__no_auto_translate__
{placeholders}
`inline code`
```

严格错误必须修；inline code 警告需要人工判断。

## 4. 编译 futurecoder.mo

`core/translation.py` 加载的是 `.mo` 文件，不是 `.po` 文件。

目标路径：

```text
translations/locales/zh/LC_MESSAGES/futurecoder.mo
```

可使用 Python + polib 编译：

```bash
python - <<'PY'
import polib
po_path = 'translations/locales/zh/LC_MESSAGES/futurecoder.po'
mo_path = 'translations/locales/zh/LC_MESSAGES/futurecoder.mo'
po = polib.pofile(po_path)
po.save_as_mofile(mo_path)
print(mo_path)
PY
```

## 5. 验证翻译加载

`core/init_pyodide.py` 中 `init(lang)` 会在 `lang` 不是空且不是 `en` 时调用 `t.set_language(lang)`。

因此需要验证：

```text
lang = zh
        ↓
t.set_language('zh')
        ↓
gettext 加载 translations/locales/zh/LC_MESSAGES/futurecoder.mo
        ↓
课程文本显示中文
```

## 6. 分批完善翻译

建议顺序：

```text
Phase 1: 首页、导航、按钮、通用 UI
Phase 2: Getting Started / Introducing The Shell
Phase 3: strings / numbers / variables
Phase 4: for loops / if statements / lists / dicts
Phase 5: functions / errors / nested data
Phase 6: hints / requirements / disallowed messages
Phase 7: tracebacks beginner-friendly explanations
Phase 8: 全站中文润色
```

## 7. 每批翻译后的检查

每次翻译后至少做：

```bash
python scripts/zh_cn/check_po_placeholders.py translations/locales/zh/LC_MESSAGES/futurecoder.po
```

然后重新编译 `.mo` 并运行页面。

## 8. 后续可做的工程化改造

- 增加 `make zh-check`。
- 增加 `make zh-compile`。
- 在 README 中增加中文版启动方式。
- 增加 GitHub Actions 检查 PO 占位符。
- 添加中文翻译进度统计脚本。
