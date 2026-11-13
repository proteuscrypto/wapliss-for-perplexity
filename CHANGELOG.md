# Changelog

All notable changes to Wapliss WhatsApp for Perplexity. Created and
maintained by netdigitaltech.

## 1.0.0 (2026-11-12)

- First release: custom plugin for Perplexity Computer, importable from GitHub
  or uploaded as a `.zip`. Remote MCP connector `https://wapliss.com/mcp/v1`
  (16 tools, OAuth 2.0 with dynamic client registration and PKCE S256) and the
  `wapliss-whatsapp` Agent Skill.
- Step-by-step values for adding Wapliss as a custom remote connector without
  the plugin.
- `scripts/validate.py` checks Perplexity's package rules (manifest at the
  root, name and description, remote HTTP servers only, no fixed headers,
  limits) and `scripts/build_zip.py` builds the upload package.
