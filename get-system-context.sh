#!/bin/bash
# Generate system context for LLM to understand your environment
# This provides the LLM with information about your PC

get_system_context() {
    CONTEXT="You are a helpful AI assistant running locally on this system. Here is the current system information:

SYSTEM INFORMATION:
- Hostname: $(hostname)
- OS: $(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)
- Kernel: $(uname -r)
- Architecture: $(uname -m)
- User: $USER
- Home: $HOME
- Current Directory: $(pwd)
- Shell: $SHELL

HARDWARE:
- CPU: $(lscpu | grep "Model name" | cut -d':' -f2 | xargs)
- Cores: $(nproc) cores
- Memory: $(free -h | awk '/^Mem:/ {print $2}') total, $(free -h | awk '/^Mem:/ {print $7}') available
- GPU: $(lspci | grep -i vga | cut -d':' -f3 | xargs || echo "Not detected")
- NPU: $(lspci | grep -i "neural processing" | cut -d':' -f3 | xargs || echo "None")

KUBERNETES:
- Current Context: $(kubectl config current-context 2>/dev/null || echo "Not configured")
- Current Namespace: $(kubectl config view --minify --output 'jsonpath={..namespace}' 2>/dev/null || echo "default")

DOCKER:
- Docker installed: $(command -v docker &>/dev/null && echo "Yes ($(docker --version | cut -d' ' -f3 | tr -d ','))" || echo "No")
- Running containers: $(docker ps --format '{{.Names}}' 2>/dev/null | wc -l || echo "0")

DESKTOP ENVIRONMENT:
- Session Type: $(echo ${XDG_SESSION_TYPE:-Not detected})
- Desktop: $(echo ${XDG_CURRENT_DESKTOP:-Not detected})
- Window Manager: $(wmctrl -m 2>/dev/null | grep "Name:" | cut -d':' -f2 | xargs || echo "Not detected")
- Wayland Compositor: $(echo ${WAYLAND_DISPLAY:+Wayland} || echo "X11")

PROJECT DIRECTORIES:
$(ls -1 ~/projects 2>/dev/null | head -10 | sed 's/^/  - /' || echo "  None")

RECENT WORK:
- Working directory: $(pwd)
$(if [ -d .git ]; then echo "- Git repo: $(git remote get-url origin 2>/dev/null || echo 'local repo')"; echo "- Branch: $(git branch --show-current 2>/dev/null)"; fi)

Please use this context to provide relevant, system-specific advice."

    echo "$CONTEXT"
}

# Output the context
get_system_context
