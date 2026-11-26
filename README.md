# MUSE-PI-PRO 嵌入式机器人教程

百问科技《基于 MUSE-PI-PRO 嵌入式机器人教程手册》的 Markdown 文档站，沿用 [dshanpi/Docs](https://github.com/dshanpi/Docs) 的 Docusaurus 3 框架、Classic 主题、配色和中文本地搜索。

- 本地验收：<http://127.0.0.1:3000/>（启动预览服务后访问）
- 在线阅读：<https://dshanpi.github.io/ros2-docs/>
- 规划域名：<https://ros2.100ask.net>（待配置 DNS 后切换）
- 原稿结构：15 章、53 个二级章节、270 个各级标题。
- 网站内容：69 个页面、17 张表格、465 个代码块、2 个公式。
- 原始图片：189 张 PNG，直接从 Word ZIP 内提取，未缩放、转码或有损压缩。正文图片可点击打开原图。

## 本地运行

需要 Node.js 20 或更新版本（自动部署使用 Node.js 22）。

```sh
npm ci
npm start
```

```sh
npm run check
npm run serve
```

`check` 依次验证 Markdown 与图片校验值、执行严格链接检查和生产构建、验证全部生成页面及图片。默认本地站点按自定义域名的根路径运行。

## 内容结构

`docs/intro.md` 是教程首页。`docs/chapter-01/` 至 `docs/chapter-15/` 按原稿章节排列，每章 `index.md` 保留章前说明并提供目录，`section-XX.md` 对应原稿二级章节。三级和四级标题保留在相应页面中。

`static/img/manual/` 保存 Word 内嵌图片的原始字节。页眉 Logo 和封面装饰也完整保留；封面整页装饰不在正文中铺开，以避免无内容的大片空白。

`migration/manifest.json` 记录原稿 SHA-256、模板提交、章节映射、内容统计和每张原图的 SHA-256、字节数及像素尺寸。Markdown 页面也有校验值，便于检查迁移完整性。

## 重新转换 Word

```sh
python -m pip install lxml Pillow
python scripts/convert_docx.py /path/to/manual.docx
npm run check
```

转换脚本只读取文档，不执行教程中的命令。它保留正文顺序、标题编号、图注、表格合并单元格与公式；代码里的不间断空格转换为普通空格，原有制表符和换行保持不变。Word 页码、分页符、空白排版段落及重复的兼容性文本框不作为网页正文。

转换完成后，本地 `.work/source-audit.json` 用于逐段验证渲染页面是否完整保留原稿内容与顺序；该中间文件不提交。原稿中的技术表述和示例按原样保留，格式迁移不包含技术内容修订。

日常手动编辑 Markdown 后，确认修改无误，再更新清单中的页面哈希：

```sh
node scripts/update-page-hashes.cjs
npm run check
```

## 自动部署与自定义域名

推送到 `main` 后，GitHub Actions 自动检查、构建并发布到 GitHub Pages；拉取请求只构建检查。部署不需要额外的第三方 Token。

当前使用 GitHub Pages 默认地址，构建工作流从仓库 Actions 变量读取可选的 `DOCS_SITE_URL` 和 `DOCS_BASE_URL`。

切换 `ros2.100ask.net`：

1. 在域名服务商处添加 CNAME：`ros2` → `dshanpi.github.io`。
2. 在仓库 Settings → Pages 中将 Custom domain 设置为 `ros2.100ask.net`。
3. 在仓库 Settings → Secrets and variables → Actions → Variables 中设置 `DOCS_SITE_URL=https://ros2.100ask.net`、`DOCS_BASE_URL=/`。
4. 重新运行部署工作流；证书签发后启用 Enforce HTTPS。

`docusaurus.config.js` 与 `static/CNAME` 已包含目标域名配置。使用 Actions 发布时，域名实际绑定以 Pages 设置为准，单独的 CNAME 文件不会替代该设置。
