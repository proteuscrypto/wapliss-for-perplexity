<p align="center">
  <img src="assets/icon.png" alt="Wapliss logo" width="120" />
</p>

<h1 align="center">Wapliss WhatsApp for Perplexity</h1>

<p align="center">
  <strong>Connect your own WhatsApp to Perplexity with the Wapliss MCP server.</strong><br />
  Read and summarize chats and groups, and send messages, files, locations and polls, always with your confirmation.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-25D366" alt="License: MIT" />
  <img src="https://img.shields.io/badge/MCP-2026--07--28%20%7C%202025--11--25-128C7E" alt="MCP" />
  <img src="https://img.shields.io/badge/Perplexity-plugin-20808D" alt="Perplexity" />
  <img src="https://img.shields.io/badge/version-1.0.0-25D366" alt="Version" />
  <img src="https://img.shields.io/badge/Agent%20Plugins-1.0-24292f" alt="Agent Plugins" />
</p>

<p align="center">
  <a href="https://wapliss.com/">Website</a> ·
  <a href="https://wapliss.com/integrations#perplexity">Perplexity guide</a> ·
  <a href="https://wapliss.com/integraciones#perplexity">Guía en español</a> ·
  <a href="#example-prompts">Examples</a> ·
  <a href="#faq">FAQ</a> ·
  <a href="#wapliss-plugins">Other assistants</a>
</p>

---

## What is Wapliss?

[Wapliss](https://wapliss.com/), by [NetDigitalTech LLC](https://netdigitaltech.com/), is a WhatsApp gateway for AI assistants. You
link your WhatsApp number once with a QR code, authorize your assistant, and
the assistant can read your chats and groups and send WhatsApp messages for
you through a standard [Model Context Protocol](https://modelcontextprotocol.io/)
(MCP) server. A free plan is available, with no credit card required.

This repository is the official **Perplexity package** of Wapliss: a custom
plugin (a remote MCP connector plus an Agent Skill) for Perplexity Computer. It
only points Perplexity to the hosted Wapliss MCP server; it stores no account
data, messages or credentials.

## Compatibility

| Surface | How | What you need |
| --- | --- | --- |
| Perplexity Computer (plugin) | **Plugins → Add custom → Import plugin from GitHub** → `https://github.com/proteuscrypto/wapliss-for-perplexity`, or upload the `.zip` | The Plugins page, and a plan that includes Perplexity Computer for the skill |
| Perplexity (connector only) | **Plugins → Add custom → Connector → Remote** (or **Customize → Connectors → + Custom connector**) with the values below | A paid plan (Pro, Max or Enterprise) |
| Perplexity organizations | An admin adds the connector in **Organization settings → Connectors**, or the plugin in **Organization settings → Plugins and skills** | Admin role |
| Perplexity Agent API | Project **Add custom connector** → URL `https://wapliss.com/mcp/v1`, auth **API Key** (a personal Wapliss API key) | Not tested yet |

## Quick start

1. Create a free account at [wapliss.com](https://wapliss.com/) and link your
   phone once at [wapliss.com/app/connect](https://wapliss.com/app/connect).
2. In Perplexity, open **Plugins** in the sidebar (or
   [perplexity.ai/computer/plugins](https://www.perplexity.ai/computer/plugins)),
   select **Add custom → Import plugin from GitHub** and paste:

   ```text
   https://github.com/proteuscrypto/wapliss-for-perplexity
   ```

   Or download the `.zip` from the
   [releases](https://github.com/proteuscrypto/wapliss-for-perplexity/releases)
   and select **Add custom → Upload plugin or skill**.
3. Open the plugin and select **Connect** next to `wapliss`. Sign in to
   Wapliss in the browser and approve access (OAuth, no keys to copy).
   Installing a plugin does not connect its connectors by itself.
4. In a new thread type **/**, pick **Wapliss WhatsApp** under Plugins, and
   ask: *"Show me my latest WhatsApp messages"*.

### Only the connector (no plugin)

If you don't see **Plugins** yet, use **Customize → Connectors → + Custom
connector** and fill in:

| Field | Value |
| --- | --- |
| Name | `Wapliss WhatsApp` |
| MCP server URL | `https://wapliss.com/mcp/v1` |
| Description | `Read and send your WhatsApp messages with Wapliss` |
| Icon | [`assets/icon.png`](assets/icon.png) (512 × 512, under 128 KB) |
| Advanced → Authentication | **OAuth** (leave Client ID and Client Secret empty: Wapliss supports dynamic client registration) |
| Advanced → Transport | **Streamable HTTP** |
| Advanced → Network access | **Public** |

Check the risk acknowledgement, select **Add**, then select the connector card
to sign in and turn it on.

## Example prompts

| Goal | Ask |
| --- | --- |
| Catch up | "Show me my latest WhatsApp messages" |
| Summarize a group | "Summarize what was said today in my family group" |
| Read a chat | "Read my last 20 messages with Ana and tell me what she needs" |
| Research + WhatsApp | "Find the opening hours of the museum and send them to the family group" |
| Group info | "Who are the admins of the work group?" |
| Send a message | "Send 'On my way, 10 minutes' to +1 555 010 2030" |
| Send a file | "Send this PDF to Laura: https://example.com/quote.pdf" |
| Run a poll | "Create a poll in the team group: Friday or Monday?" |
| Check the account | "Check my Wapliss account and today's usage" |

Tips: name the chat or group as it appears in WhatsApp, or use the number with
country code. The assistant shows you the recipient and the text before
sending when anything is ambiguous.

## What it can do (16 tools)

| Area | Tools | What they do |
| --- | --- | --- |
| Chats and groups | `get_chats`, `get_chat_history`, `get_message` | List and search your conversations, read a chat or group in order, get one message |
| Latest activity | `get_last_incoming_messages`, `get_last_outgoing_messages` | What you received or sent recently, across all chats |
| Groups | `get_group` | Name, description, admins and participants |
| Send | `send_text_message`, `send_image`, `send_document`, `send_audio`, `send_video`, `send_location`, `send_contact`, `send_poll`, `forward_messages` | Text, files by public URL, locations, contact cards, polls and forwards |
| Account | `get_account_status` | Plan, linked number, daily usage and quota |

Every tool declares MCP annotations (`readOnlyHint`, `destructiveHint`,
`idempotentHint`, `openWorldHint`). Send tools are marked destructive, so the
assistant asks for confirmation. A successful send means the message was
**queued** (with a `queue_id`), not yet delivered.

## How it works

```text
Perplexity (web, desktop, mobile, Computer)
        |  OAuth 2.0: discovery, dynamic client registration, PKCE S256
        |  callback https://www.perplexity.ai/rest/connections/oauth_callback
        v
https://wapliss.com/mcp/v1   (Streamable HTTP, MCP 2026-07-28 and 2025-11-25)
        |
Wapliss WhatsApp engine  --->  WhatsApp
```

`mcp.json` (read by Perplexity from the package root):

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "wapliss": { "type": "streamable-http", "url": "https://wapliss.com/mcp/v1" }
  }
}
```

- Protected resource metadata: `https://wapliss.com/.well-known/oauth-protected-resource/mcp/v1`
- Authorization server metadata: `https://wapliss.com/.well-known/oauth-authorization-server`
- Scopes: `wapliss:mcp`, `whatsapp:read`, `whatsapp:write`
- `/mcp/v1` serves stable English tool definitions; the package contains no
  credentials and no `headers` (Perplexity skips servers with fixed headers).

## Security and privacy

- **Your own account only.** The assistant can reach only the WhatsApp account
  linked to your Wapliss account, and only when you ask.
- **No credentials in the chat.** Never paste passwords, API keys, QR data or
  session data into a conversation; this package contains none either.
- **Confirmation before sending.** Ambiguous recipients or texts are confirmed
  first; bulk or unsolicited messaging is not allowed.
- **Revocable at any time** from the Wapliss dashboard, or with **Disconnect**
  on the Perplexity Plugins page. Uninstalling the plugin does not disconnect
  the connector: disconnect it too if you want to remove access.
- **Limits:** daily plan quota and 60 MCP calls per minute per user.
- [Privacy policy](https://wapliss.com/privacy-policy) ·
  [Terms of service](https://wapliss.com/terms-of-service)

## FAQ

**Is it free?** Wapliss has a free plan to start, with no credit card. On the
Perplexity side, custom connectors need a paid plan, and plugin skills need a
plan that includes Perplexity Computer.

**Does it use the official WhatsApp Business Platform?** No. Wapliss links
your number as a WhatsApp linked device, like WhatsApp Web, so it works with
your personal or business number without a Meta Business account. Use it for
your own conversations and follow WhatsApp's terms.

**Can the assistant send messages on its own?** No. It only acts when you ask,
confirms ambiguous sends and refuses bulk or unsolicited messages.

**Where are my messages stored?** In your private Wapliss account, so the
assistant can read them when you ask. What the assistant reads is processed by
its AI provider. See the [privacy policy](https://wapliss.com/privacy-policy).

**Why does Perplexity say it cannot verify the connector?** Perplexity shows
that notice for every custom connector. Wapliss is not one of Perplexity's
built-in connectors yet.

**Can I use several assistants at once?** Yes. Each one is authorized
separately and can be revoked separately.

## Troubleshooting

| What you see | What it means | What to do |
| --- | --- | --- |
| Plugin shows **Connect** | The connector is installed but not signed in | Select **Connect** and sign in to Wapliss |
| Warning dot on the connector | The sign-in expired | Select **Reconnect** |
| **Upload plugin or skill** is greyed out | Your organization doesn't allow personal plugins | Ask your admin, or add only the connector |
| `account_awaiting_qr` / `instance_not_connected` | No phone is linked to this Wapliss account | Link it at [wapliss.com/app/connect](https://wapliss.com/app/connect) |
| `account_disconnected` | WhatsApp closed the linked session | Scan the QR code again |
| `quota_exceeded` | Daily message quota reached | Wait for the reset or upgrade the plan |
| Rate limit (`-32300` / HTTP 429) | More than 60 calls in a minute | Wait the seconds indicated |
| `chat_not_found` | No chat matches the name or number | Search with another name or the full number with country code |

## Package layout

```text
plugin.json                       Manifest at the package root (name + description, Agent Plugins 1.0 fields)
mcp.json                          Remote MCP connector (Streamable HTTP, OAuth handled by Perplexity)
skills/wapliss-whatsapp/SKILL.md  Agent Skill: when and how to use the tools safely
assets/icon.png                   512 × 512 icon (also for the custom connector form)
scripts/validate.py               Perplexity package rules + manifest, MCP and skill checks (--live checks the endpoint)
scripts/build_zip.py              Builds dist/wapliss-whatsapp-<version>.zip for upload
```

## Validate and build

```bash
python3 scripts/validate.py          # Perplexity package rules, manifest, mcp.json and skill
python3 scripts/validate.py --live   # + public endpoint and OAuth metadata
python3 scripts/build_zip.py         # dist/wapliss-whatsapp-1.0.0.zip (plugin.json at the root)
```

Bump `version` in `plugin.json` and add a `CHANGELOG.md` entry for every
release, and attach the `.zip` to a GitHub release (`v1.0.0`).

## Wapliss plugins

Wapliss works the same way in every assistant: one account, one linked phone,
the same 16 tools.

| Assistant | Where it works | Format | Get it |
| --- | --- | --- | --- |
| Claude | Claude.ai, Claude Desktop, Claude Code | Custom connector / Claude plugin | [github.com/proteuscrypto/wapliss-whatsapp-for-claude](https://github.com/proteuscrypto/wapliss-whatsapp-for-claude) |
| ChatGPT | ChatGPT web and desktop | ChatGPT plugin (Agent Plugins) / custom MCP connector | [github.com/proteuscrypto/wapliss-for-chatgpt](https://github.com/proteuscrypto/wapliss-for-chatgpt) |
| Gemini | Gemini app, Gemini CLI, Antigravity | Connected app, Gemini CLI extension, Antigravity plugin | [github.com/proteuscrypto/wapliss-for-gemini](https://github.com/proteuscrypto/wapliss-for-gemini) |
| DeepSeek | DeepSeek Harness (dsh) | dsh bundle | [github.com/proteuscrypto/wapliss-for-deepseek](https://github.com/proteuscrypto/wapliss-for-deepseek) |
| GitHub Copilot | VS Code, Copilot CLI, Copilot app | Agent Plugins 1.0 | [github.com/proteuscrypto/wapliss-for-copilot](https://github.com/proteuscrypto/wapliss-for-copilot) |
| Grok | Grok Build, grok.com connectors, xAI API | Grok Build plugin / custom MCP connector | [github.com/proteuscrypto/wapliss-for-grok](https://github.com/proteuscrypto/wapliss-for-grok) |
| Microsoft 365 Copilot | Microsoft 365 Copilot (work accounts), Teams, Outlook | Declarative agent with a remote MCP action | [github.com/proteuscrypto/wapliss-for-m365-copilot](https://github.com/proteuscrypto/wapliss-for-m365-copilot) |
| **Perplexity** | Perplexity web, desktop and mobile, Perplexity Computer | Custom plugin / custom remote connector | this repository |
| Any MCP client | Clients with remote MCP (Streamable HTTP) | OAuth 2.1, or a personal API key | [wapliss.com/integrations#mcp](https://wapliss.com/integrations#mcp) |

## Credits and support

- **Created and maintained by [NetDigitalTech LLC](https://netdigitaltech.com/)**
  ([GitHub](https://github.com/netdigitaltech)), the company that created and owns
  [Wapliss](https://wapliss.com/). NetDigitalTech builds web, mobile and AI
  applications. Albuquerque, New Mexico, USA · commerce@netdigitaltech.com
- Support: [open an issue](https://github.com/proteuscrypto/wapliss-for-perplexity/issues) in this repository.
- Integration guides: [English](https://wapliss.com/integrations#perplexity) ·
  [Español](https://wapliss.com/integraciones#perplexity)

## Español

**Wapliss WhatsApp para Perplexity**: conecta tu propio WhatsApp a Perplexity
con el servidor MCP de Wapliss. Lee y resume chats y grupos y envía mensajes,
archivos, ubicaciones y encuestas, siempre con tu confirmación.

Cómo empezar: crea tu cuenta gratis en wapliss.com y vincula tu teléfono. En
Perplexity abre **Plugins → Add custom → Import plugin from GitHub** y pega
`https://github.com/proteuscrypto/wapliss-for-perplexity`. Después toca
**Connect** junto a `wapliss`, inicia sesión en Wapliss y autoriza el acceso.
Si todavía no ves **Plugins**, agrega solo el conector en **Customize →
Connectors → + Custom connector** con la URL `https://wapliss.com/mcp/v1`,
autenticación **OAuth** (sin Client ID) y transporte **Streamable HTTP**.

Ejemplos: *"Muéstrame mis últimos mensajes de WhatsApp"*, *"Resume lo que se
habló hoy en el grupo de la familia"*, *"Envía 'Llego en 10 minutos' a
+54 9 11 5555 0100"*. Creado y mantenido por **[NetDigitalTech LLC](https://netdigitaltech.com/)**,
la empresa creadora y dueña de [Wapliss](https://wapliss.com/). Guía completa:
[wapliss.com/integraciones#perplexity](https://wapliss.com/integraciones#perplexity).

## Trademarks and license

Perplexity is a trademark of Perplexity AI, Inc. WhatsApp is a trademark of
Meta Platforms, Inc. Wapliss is an independent service and is not affiliated
with, sponsored or endorsed by Meta, WhatsApp or Perplexity AI.

Released under the [MIT License](LICENSE). © 2026 NetDigitalTech LLC, creator and owner of Wapliss.
