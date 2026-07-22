#!/bin/bash
# Install LLM terminal aliases to your shell
# Run this script to add convenient aliases to your ~/.bashrc

INSTALL_FILE="$HOME/projects/private/npu-agent/bash_aliases.sh"
BASHRC="$HOME/.bashrc"
BEGIN="# >>> npu-agent aliases >>>"
END="# <<< npu-agent aliases <<<"

echo "Local NPU AI Agent Alias Installer"
echo "==================================="
echo ""

# Remove any previous sentinel-wrapped block
if grep -qF "$BEGIN" "$BASHRC" 2>/dev/null; then
    sed -i "\|$BEGIN|,\|$END|d" "$BASHRC"
fi

# Append a fresh, sentinel-wrapped block
{
    echo ""
    echo "$BEGIN"
    cat "$INSTALL_FILE"
    echo "$END"
} >> "$BASHRC"

echo "✅ Aliases installed to ~/.bashrc"
echo ""
echo "To use them now, run:"
echo "  source ~/.bashrc"
echo ""
echo "Available commands:"
echo "  ai           - Interactive agent (qwen3.6-moe, default)"
echo "  ai-fast      - Interactive agent (qwen3.5-4b, faster prefill)"
echo "  agent \"...\"   - One-shot agent request"
echo "  ask \"...\"     - Quick question (no tools)"
echo "  chat         - Interactive chat"
echo "  codehelp     - Coding assistant"
echo "  llmfix       - Fix errors/issues"
echo "  llmodels     - Manage NPU models"
echo "  llm-server   - start|stop|status the NPU server"
echo "  llm-status   - Check status"
echo ""
echo "Try it:"
echo "  ai"
echo "  agent 'list my wifi networks'"
