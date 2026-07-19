#!/bin/bash
# Install LLM terminal aliases to your shell
# Run this script to add convenient aliases to your ~/.bashrc

INSTALL_FILE="$HOME/projects/private/npu-agent/bash_aliases.sh"
BASHRC="$HOME/.bashrc"

echo "Local NPU AI Agent Alias Installer"
echo "==================================="
echo ""

# Check if already installed
if grep -q "Local AI Agent Aliases" "$BASHRC" 2>/dev/null; then
    echo "⚠️  Local AI Agent aliases already installed in ~/.bashrc"
    echo ""
    read -p "Reinstall anyway? (y/N): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    # Remove old installation
    sed -i '/# Local AI Agent Aliases/,/^$/d' "$BASHRC"
fi

# Add aliases to bashrc
echo "" >> "$BASHRC"
cat "$INSTALL_FILE" >> "$BASHRC"
echo "" >> "$BASHRC"

echo "✅ Aliases installed to ~/.bashrc"
echo ""
echo "To use them now, run:"
echo "  source ~/.bashrc"
echo ""
echo "Available commands:"
echo "  ai           - Interactive agent (qwen3.5-9b, tools)"
echo "  ai-fast      - Interactive agent (qwen3.5-4b, faster)"
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
