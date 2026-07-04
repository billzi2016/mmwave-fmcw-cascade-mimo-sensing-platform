# 文档站点

本目录包含雷达感知平台的 MkDocs 文档站点。

发布后的站点地址：

https://billzi2016.github.io/mmwave-fmcw-cascade-mimo-sensing-platform/

内容按语言组织：

- `docs/en/`：英文文档
- `docs/zh/`：中文文档

站点使用 `mkdocs-static-i18n` 配置双语支持，并让中英文页面保持相同的结构。

## 本地构建

```bash
cd docs-site
python -m pip install -r requirements.txt
mkdocs serve
```

生产构建：

```bash
cd docs-site
mkdocs build --strict
```
