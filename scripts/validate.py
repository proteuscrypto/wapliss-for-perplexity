#!/usr/bin/env python3
"""Validate Wapliss WhatsApp for Perplexity.

Checks the package against Perplexity's custom plugin rules (Perplexity Help
Center: "Create or upload a custom plugin" and "Troubleshooting plugins") and
the Agent Plugins 1.0 conventions shared by the other Wapliss plugins.
Created by netdigitaltech.

  python3 scripts/validate.py          # static checks
  python3 scripts/validate.py --live   # + public endpoint and OAuth metadata
"""
import json, pathlib, re, struct, sys, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAIL = []
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
ALLOWED = {"$schema", "name", "version", "description", "author", "homepage", "repository", "license", "keywords", "extensions"}
NAME_RE = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
TOOLS = {"send_text_message", "send_image", "send_document", "send_audio", "send_video", "send_location",
         "send_contact", "send_poll", "forward_messages", "get_chats", "get_chat_history", "get_message",
         "get_last_incoming_messages", "get_last_outgoing_messages", "get_group", "get_account_status"}
# Files that go into the uploaded package (same set build_zip.py packs).
PACKAGE = ["plugin.json", "mcp.json", "README.md", "LICENSE", "CHANGELOG.md", "assets", "skills"]


def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond or extra == "" else f"  -> {extra}"))
    if not cond:
        FAIL.append(name)


def package_files():
    out = []
    for item in PACKAGE:
        p = ROOT / item
        out += [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file()]
    return out


def static():
    # Perplexity: plugin.json at the package root, with name and description (<= 1,024 UTF-8 bytes).
    check("plugin.json at the package root", (ROOT / "plugin.json").is_file())
    m = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    name = m.get("name", "")
    desc = m.get("description", "")
    check("Perplexity: manifest has a name", isinstance(name, str) and bool(name.strip()))
    check("Perplexity: description is a string <= 1,024 UTF-8 bytes",
          isinstance(desc, str) and 40 <= len(desc.encode("utf-8")) <= 1024, len(desc.encode("utf-8")))
    check("no .claude-plugin/ or .codex-plugin/ manifest competing with the root one",
          not (ROOT / ".claude-plugin").exists() and not (ROOT / ".codex-plugin").exists())
    # Shared Wapliss conventions (Agent Plugins 1.0, same as the Copilot and ChatGPT packages).
    check("$schema is Agent Plugins 1.0.0", m.get("$schema") == PLUGIN_SCHEMA, m.get("$schema"))
    check("only Agent Plugins 1.0 top-level fields", set(m) <= ALLOWED, set(m) - ALLOWED)
    check("name 1-64 chars, lowercase, no -- or ..", 1 <= len(name) <= 64 and bool(NAME_RE.match(name)), name)
    check("version is SemVer", bool(SEMVER.match(m.get("version", ""))), m.get("version"))
    a = m.get("author", {})
    check("author.name netdigitaltech, only name/email/url strings",
          a.get("name") == "netdigitaltech" and set(a) <= {"name", "email", "url"} and all(isinstance(v, str) for v in a.values()), a)
    check("no personal email in the manifest", "email" not in a)
    check("repository is an HTTPS GitHub URL", str(m.get("repository", "")).startswith("https://github.com/"))
    check("license MIT + LICENSE file", m.get("license") == "MIT" and (ROOT / "LICENSE").is_file())
    kw = m.get("keywords", [])
    check("keywords are lowercase hyphenated tags", bool(kw) and all(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", k) for k in kw), kw)
    check("no MCP config inline in plugin.json (Perplexity reads mcp.json)", "mcpServers" not in json.dumps(m))

    # Perplexity: connectors come from mcp.json (or .mcp.json) at the root; remote HTTP only.
    check("exactly one MCP file at the root (mcp.json, no .mcp.json)",
          (ROOT / "mcp.json").is_file() and not (ROOT / ".mcp.json").exists())
    mc = json.loads((ROOT / "mcp.json").read_text(encoding="utf-8"))
    check("mcp.json $schema matches the manifest version", mc.get("$schema") == MCP_SCHEMA, mc.get("$schema"))
    servers = mc.get("mcpServers", {})
    check("Perplexity: 1-15 MCP servers", 1 <= len(servers) <= 15, len(servers))
    for key, srv in servers.items():
        url = str(srv.get("url", ""))
        check(f"Perplexity: {key} has type streamable-http, http or sse", srv.get("type") in {"streamable-http", "http", "sse"}, srv.get("type"))
        check(f"Perplexity: {key} URL is HTTPS", url.startswith("https://"), url)
        check(f"Perplexity: {key} has no fixed headers", "headers" not in srv, list(srv))
        check(f"Perplexity: {key} has no stdio command", "command" not in srv and "args" not in srv, list(srv))
        check(f"Perplexity: {key} URL has no unresolved placeholders", not re.search(r"\$\{|\{\{|<[^>]+>", url), url)
    srv = servers.get("wapliss", {})
    check("server wapliss: streamable-http https://wapliss.com/mcp/v1",
          srv.get("type") == "streamable-http" and srv.get("url") == "https://wapliss.com/mcp/v1", srv)

    # Perplexity: each skill is a folder with SKILL.md (YAML frontmatter: name, description); <= 32 skills.
    skills = [d for d in (ROOT / "skills").iterdir() if (d / "SKILL.md").is_file()]
    check("Perplexity: 1-32 skills", 1 <= len(skills) <= 32, len(skills))
    for d in skills:
        text = (d / "SKILL.md").read_text(encoding="utf-8")
        fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        check(f"{d.name}: YAML frontmatter", bool(fm))
        if fm:
            name_m = re.search(r"^name:\s*(\S+)", fm.group(1), re.M)
            check(f"{d.name}: name matches directory", bool(name_m) and name_m.group(1) == d.name)
            check(f"{d.name}: description present", "description:" in fm.group(1))
        missing = [t for t in TOOLS if f"`{t}`" not in text]
        check(f"{d.name}: documents all 16 tools", not missing, missing)

    # Perplexity: <= 1,000 files and <= 20 MB uncompressed.
    files = package_files()
    size = sum(f.stat().st_size for f in files)
    check("Perplexity: package <= 1,000 files", len(files) <= 1000, len(files))
    check("Perplexity: package <= 20 MB uncompressed", size <= 20 * 1024 * 1024, size)

    icon = ROOT / "assets" / "icon.png"
    b = icon.read_bytes() if icon.is_file() else b""
    ok = b[:8] == b"\x89PNG\r\n\x1a\n"
    w, h = struct.unpack(">II", b[16:24]) if ok else (0, 0)
    check("assets/icon.png is a square PNG >= 256 px", ok and w == h and w >= 256, f"{w}x{h}")
    check("Perplexity: icon <= 128 KB (custom connector form limit)", 0 < len(b) <= 128 * 1024, len(b))

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    check("README: GitHub import URL, connector URL and creator",
          "https://github.com/proteuscrypto/wapliss-for-perplexity" in readme
          and "https://wapliss.com/mcp/v1" in readme and "netdigitaltech" in readme)
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    check("CHANGELOG has the current version", f"## {m.get('version')} " in changelog, m.get("version"))


def live():
    url = "https://wapliss.com/mcp/v1"
    req = urllib.request.Request(url, data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}', method="POST",
                                 headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    try:
        urllib.request.urlopen(req, timeout=30)
        check("live: unauthenticated -> 401", False, "200")
    except urllib.error.HTTPError as e:
        www = e.headers.get("WWW-Authenticate", "")
        check("live: unauthenticated -> 401", e.code == 401, e.code)
        check("live: WWW-Authenticate resource_metadata for /mcp/v1", "oauth-protected-resource/mcp/v1" in www, www)
    # Perplexity discovers endpoints from /.well-known/oauth-authorization-server and needs DCR (no client ID to type).
    with urllib.request.urlopen("https://wapliss.com/.well-known/oauth-authorization-server", timeout=30) as r:
        meta = json.loads(r.read())
    check("live: dynamic client registration endpoint", bool(meta.get("registration_endpoint")))
    check("live: authorization code flow", "code" in meta.get("response_types_supported", []))
    check("live: PKCE S256", "S256" in meta.get("code_challenge_methods_supported", []))


if __name__ == "__main__":
    static()
    if "--live" in sys.argv:
        live()
    print("\nRESULT:", "ALL PASS" if not FAIL else f"{len(FAIL)} FAILED")
    sys.exit(1 if FAIL else 0)
