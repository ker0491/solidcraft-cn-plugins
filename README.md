# SolidCraft 中文插件仓库

把社区插件的展示文本汉化，执行组件原样保留，并跟随上游版本自动更新。

## 原理

SolidCraft 的插件包由 `plugin.json` 和一个 WebAssembly 组件组成。插件不携带 UI 代码——对话框由宿主根据 manifest 里的 JSON Schema 现场绘制。因此只需要改 `plugin.json` 中的字符串字段，`.wasm` 可以逐字节原样搬运，不必 fork 作者的源码。

构建脚本会比对翻译前后的 manifest：只允许白名单内的文本字段发生变化。若翻译表误写了 `id`、`capabilities`、`runtime.commands`、`slots[].name` 或任何 JSON 键名，构建直接失败。

## 目录结构

```
plugins/<id>/upstream.json          上游插件登记信息
translations/<id>.zh-CN.json        唯一需要人工维护的译文
upstream.lock.json                  上游版本与哈希锁文件（自动生成）
scripts/common.py                   共享工具
scripts/sync.py                     检查上游更新，刷新锁文件
scripts/build.py                    生成汉化包与校验报告
scripts/build_site_data.py          合并社区插件目录、译文与汉化包，生成网站数据
site/                               中文插件站（纯静态 HTML/CSS/JS）
.github/workflows/sync.yml          每天定时同步，有新版本自动开 PR
.github/workflows/release.yml       构建汉化包、更新网站并发布
dist/                               构建产物（不入库）
```

## 新增一个插件

1. 在 `plugins/<id>/upstream.json` 登记作者仓库、Release 资产匹配规则和 zip 内目录名。
2. 在 `translations/<id>.zh-CN.json` 写译文。`strings` 的 key 用**字段路径**，不要用英文原文：

   ```json
   "entries.make-gear.input_schema.module.title": "模数",
   "entries.make-gear.input_schema.module.description": "模数 m。分度圆直径 = 模数 × 齿数"
   ```

   用字段路径而非原文作 key，上游改措辞时已有译文不会丢失。

3. 运行同步与构建：

   ```bash
   python scripts/sync.py
   python scripts/build.py --all
   ```

脚本只用 Python 标准库，无需安装依赖。设置 `GITHUB_TOKEN` 可提高 API 限额，不设置也能工作。

## 中文插件站

`site/` 是一个纯静态网站。插件目录复用 [tharje/solidcraft-plugins](https://github.com/tharje/solidcraft-plugins)（MIT）每日更新的列表，本地只维护译文。页面显示每个插件的汉化状态：已汉化的提供中文包下载和 wasm 校验信息，未汉化的保留原版下载链接。因此目录全量可用，汉化可以逐个推进。

```bash
python scripts/build_site_data.py
python -m http.server 8765 --directory site
```

然后打开 `http://localhost:8765`。推送到 `main` 后，GitHub Actions 会自动刷新数据并部署到 GitHub Pages。

### 使用自己的域名

1. 仓库 Settings → Pages → Build and deployment，Source 选择 `gh-pages` 分支。
2. 仓库 Settings → Secrets and variables → Variables，新建 `SITE_DOMAIN`，值为你的域名（例如 `plugins.example.com`）。
3. DNS 添加一条 CNAME 记录，把该域名指向 `<你的用户名>.github.io`。
4. 推送一次到 `main`，工作流会把域名写入 `CNAME` 文件，HTTPS 证书由 GitHub 自动签发和续期。

中文包 zip 发布到 GitHub Releases；`site/packages/` 由工作流在部署前生成，不提交到 `main`，因此源码仓库保持轻量。若以后改用 VPS，只需把构建后的 `site/` 目录同步到 VPS，源码与构建流程无需改动。

## 版本与产物

版本号格式为 `<上游版本>-zh.<译文修订号>`，例如 `0.1.1-zh.2`。修订号在翻译表的 `_meta.revision` 中手动递增，与上游版本独立，避免版本错乱。

每次构建产出：

- `dist/<id>/<id>-<version>.zip`：可直接安装的插件包，zip 内目录结构与上游一致。
- `dist/<id>/report.json`：包含上游 wasm 与构建包 wasm 的 SHA-256 对照、译文覆盖率、改动字段清单。

## 安装

解压 zip，把其中的 `<id>` 文件夹复制到 SolidCraft 插件目录：

- Windows：`%LOCALAPPDATA%\SolidCraft\plugins`
- macOS：`~/Library/Application Support/SolidCraft/plugins`
- Linux：`${XDG_DATA_HOME:-~/.local/share}/solidcraft/plugins`

然后在 Preferences › Plugins 中启用。因为汉化改动了 manifest，安装批准哈希与上游包不同，SolidCraft 会要求重新确认一次——这是预期行为。可用 `report.json` 中的 wasm 哈希对照确认执行代码未被改动。

## 边界

- 只汉化顶层 `name`、`description`，以及 `input_schema` 中字段的 `title` 与 `description`。
- 不翻译 `entries[].name`：SolidCraft 会把这个名字作为参数传给 wasm 组件的 `execute(entry, params)`，它是程序标识符而非展示文案，改了会导致插件找不到入口。
- 不翻译 `slots[].name`：它是宿主槽位标识（如 `Plugins`），不是展示文案，改了会影响菜单位置。
- 不翻译 wasm 内部的错误文本（例如 `"the model has no solids"`）。这部分编译在组件里，要翻译就得重编译，维护成本会回到 fork 模式。
- manifest 体积上限为 `max(16 KiB, 上游原始大小 + 1 KiB)`，`name` 不超过 80 字符、`description` 不超过 240 字符，构建脚本会检查。
- 缺少译文的字段回退英文，不会阻塞发布；CI 会在同步 PR 中提示复核。

## 许可证

本仓库的脚本与译文采用 MIT 许可证，见 `LICENSE`。汉化插件包沿用各自上游插件的许可证，原始 `LICENSE` 文件保留在 zip 内。添加新插件时请自行复核上游许可证是否允许再分发。
