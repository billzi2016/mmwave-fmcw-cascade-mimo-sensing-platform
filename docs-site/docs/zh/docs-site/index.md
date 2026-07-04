# 文档站点

文档站点是 `docs-site/` 内的独立 MkDocs 工程。

## 目录结构

```text
docs-site/
├── mkdocs.yml
├── requirements.txt
├── docs/
│   ├── en/
│   └── zh/
└── .github/
    └── workflows/
```

英文内容放在 `docs/en/`，中文内容放在 `docs/zh/`。两个目录应保持相同的相对页面路径。

## 为什么这样组织

按语言分目录很容易检查和维护。维护者打开 `docs/en/processing-pipeline.md` 后，可以直接找到对应的 `docs/zh/processing-pipeline.md`。

这种结构也让文档站点和雷达代码保持分离。文档可以继续扩展，不需要改处理模块或仓库根目录 README。

## 维护规则

新增页面时：

1. 在 `docs/en/` 添加英文页面。
2. 在 `docs/zh/` 添加中文页面。
3. 在 `mkdocs.yml` 导航中添加一次。
4. 保持两种语言的标题和页面顺序一致。
