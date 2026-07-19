# npu-agent

A local, terminal-based AI agent that runs entirely on this laptop's **AMD XDNA2 NPU**
(via [Lemonade Server](https://github.com/lemonade-sdk/lemonade) + FastFlowLM) — like a
local GitHub Copilot for system administration and coding. No cloud, no API keys.

- **Engine:** Lemonade Server on the NPU, OpenAI-compatible API at `http://localhost:13305/api/v1`
- **Default model:** `qwen3.5-4b-FLM` (fast); more-capable tier `qwen3.5-9b-FLM`
- **Capabilities:** run shell commands, connect/scan WiFi, manage systemd / Sway / Waybar,
  inspect a Kubernetes cluster, read/write files — with approval prompts on anything that
  changes state.

## Quick start

```bash
# 1. Make sure the NPU server is running
./llm-server start          # start | stop | restart | status | logs

# 2. Talk to it
./agent -i                  # interactive agent (tools enabled)
./agent "list my wifi networks"     # one-shot task
./ask "how do I tar a folder?"      # quick Q&A, no tools
```

Install shell aliases (optional):

```bash
./install-aliases.sh && source ~/.bashrc
```

| Alias | What |
|---|---|
| `ai` | interactive agent (`qwen3.5-4b`, default) |
| `ai-big` | interactive agent (`qwen3.5-9b`, more capable) |
| `agent "..."` | one-shot agent task |
| `ask "..."` | quick question (no tools) |
| `chat` | interactive chat |
| `codehelp` | coding assistant |
| `llmfix` | `cat error.log \| llmfix` |
| `llm-server` | control the NPU server |
| `llmodels` | list / pull / remove NPU models |

## Model selection

Override the model per-invocation or globally:

```bash
./agent -m qwen3.5-4b-FLM -i
export LOCAL_LLM_MODEL=qwen3.5-4b-FLM
```

List / manage models (wraps Lemonade + FLM):

```bash
./models list         # NPU/FLM catalog
./models installed    # already downloaded
./models pull qwen3.5-4b-FLM
./models remove <name>
```

## Layout

| Path | Purpose |
|---|---|
| `agent` | main wrapper → `mcp-server/agent.py` |
| `mcp-server/agent.py` | agent: OpenAI-native tool-calling loop + tools |
| `mcp-server/llm_complete.py` | one-shot completion helper (used by `ask`/`quick-fix`) |
| `ask`, `chat`, `code-helper`, `quick-fix` | thin chat wrappers |
| `llm-server` | start/stop the Lemonade NPU server |
| `models` | model management via Lemonade/FLM |
| `get-system-context.sh` | system context injected into prompts |
| `bash_aliases.sh` / `install-aliases.sh` | shell aliases |

## Tools

See [TOOLS.md](TOOLS.md) and [MCP-AGENT-README.md](MCP-AGENT-README.md).

State-changing actions (file writes, WiFi connect, systemd restart/enable, dangerous
shell commands) require confirmation. Use `-y` to auto-approve (careful).

## Requirements

- AMD Ryzen AI (XDNA2 NPU) with the `amdxdna` driver + XRT userspace + FLM v0.9.45
- Lemonade embeddable server (in `../local-llm/lemonade/`)
- Python 3 with `requests`
