#!/bin/bash
# Local NPU AI agent aliases (Lemonade + FastFlowLM on the AMD XDNA2 NPU).
#
# To install:
#   ~/projects/private/npu-agent/install-aliases.sh
#   # or: cat this file >> ~/.bashrc && source ~/.bashrc

# =============================================================================
# Local AI Agent Aliases
# =============================================================================

AGENT_DIR="$HOME/projects/private/npu-agent"

# Models (change with: export LOCAL_LLM_MODEL=... )
export LOCAL_LLM_MODEL="${LOCAL_LLM_MODEL:-qwen3.5-9b-FLM}"   # newest Qwen, daily driver
LOCAL_LLM_FAST="qwen3.5-4b-FLM"                              # faster, lighter

# --- Agent (tool-capable: shell, wifi, systemd, sway, k8s, files) ------------
alias agent="$AGENT_DIR/agent"                        # one-shot:  agent "check disk space"
alias ai="$AGENT_DIR/agent -i"                        # interactive agent (qwen3.5-9b)
alias ai-fast="$AGENT_DIR/agent -m $LOCAL_LLM_FAST -i" # interactive agent (qwen3.5-4b, faster)

# --- Plain chat / coding (no tools) ------------------------------------------
alias ask="$AGENT_DIR/ask"                           # ask "question"  (pipe-friendly)
alias chat="$AGENT_DIR/chat"                         # interactive
alias codehelp="$AGENT_DIR/code-helper"
alias llmfix="$AGENT_DIR/quick-fix"                  # cat error.log | llmfix

# --- Server + models ---------------------------------------------------------
alias llm-server="$AGENT_DIR/llm-server"             # start|stop|restart|status|logs
alias llmodels="$AGENT_DIR/models"                   # list|installed|pull|remove
alias llm-status="$AGENT_DIR/llm-server status"

# --- Helper functions --------------------------------------------------------
llm-help()    { cat "$AGENT_DIR/MCP-AGENT-README.md"; }
llm-context() { "$AGENT_DIR/get-system-context.sh"; }

# Quick piping examples
llm-review()    { cat "$1" | "$AGENT_DIR/ask" "Review this code for bugs and improvements"; }
llm-explain()   { cat "$1" | "$AGENT_DIR/ask" "Explain what this code does"; }
llm-summarize() { cat "$1" | "$AGENT_DIR/ask" "Summarize this text"; }
