#!/bin/bash
# Install LLM terminal aliases to your shell
# Run this script to add convenient aliases to your ~/.bashrc

INSTALL_FILE="$HOME/projects/ollama-mcp-agent/bash_aliases.sh"
BASHRC="$HOME/.bashrc"

echo "Ollama MCP Agent Alias Installer"
echo "================================="
echo ""

# Check if already installed
if grep -q "Ollama MCP Agent Aliases" "$BASHRC" 2>/dev/null; then
    echo "⚠️  Ollama MCP Agent aliases already installed in ~/.bashrc"
    echo ""
    read -p "Reinstall anyway? (y/N): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    # Remove old installation
    sed -i '/# Ollama MCP Agent Aliases/,/^$/d' "$BASHRC"
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
echo "  llm          - Start chat with default model"
echo "  llm-fast     - Chat with llama3.2:3b"
echo "  llm-smart    - Chat with llama3.1:8b"
echo "  llm-tiny     - Chat with llama3.2:1b"
echo "  ask          - Quick question"
echo "  codehelp     - Coding assistant"
echo "  llmfix       - Fix errors/issues"
echo "  llmodels     - Manage models"
echo "  llm-status   - Check status"
echo ""
echo "Try it:"
echo "  ask 'What is Docker?'"
