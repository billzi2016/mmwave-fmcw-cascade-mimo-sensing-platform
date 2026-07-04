# 部署模板

站点内包含一个 GitHub Actions 工作流模板：

```text
docs-site/.github/workflows/deploy-docs.yml
```

它放在 `docs-site/` 内，是因为本次任务只修改文档站点目录。

## 如何启用

如果要在真实 GitHub 仓库中启用部署，可以把该工作流复制到：

```text
.github/workflows/deploy-docs.yml
```

工作流会从 `docs-site/` 构建 MkDocs 站点，并将生成的静态站点部署到 GitHub Pages。

## 触发策略

模板默认只在文档站点相关文件变化时运行：

- `docs-site/**`
- 部署工作流本身

这样可以避免雷达代码变化时反复触发文档构建。

## 构建命令

工作流使用：

```bash
mkdocs build --strict
```

严格模式可以尽早发现链接、导航和配置问题。
