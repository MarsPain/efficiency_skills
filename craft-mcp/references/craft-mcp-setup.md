# Craft MCP（配置与注意事项）

## 官方配置入口（简述）

- Craft 将 MCP Server 以“链接”的方式提供；通常 URL 形如：
  - `https://mcp.craft.do/links/<id>/mcp`
- 在宿主应用里新增 MCP Server 时，常见需要填写：
  - 名称（例如 `H's craft`）
  - MCP URL（上面的链接）
  - 连接类型/传输方式（若需要选择，优先尝试 `streamable_http`）

参考 Craft 官方指引（中文）：
- https://www.craft.do/zh-CN/imagine/guide/mcp/other

## 安全与权限

- 该 MCP URL 往往等价于“空间访问凭证”：不要公开分享，不要写进公开仓库。
- 若你需要把 skill 分享给别人，先把 `agents/openai.yaml` 里的 `url` 改成占位符，或删除 `dependencies` 段落，让使用者自行配置。

