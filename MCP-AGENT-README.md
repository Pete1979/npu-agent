# MCP-Enabled AI Agent

🤖 **Local LLM with system management tools!**

## What is this?

An AI agent that combines your local NPU LLM (Lemonade Server + FastFlowLM, default `qwen3.5-9b-FLM`) with MCP-style tools to execute commands and manage your system — like a local Copilot. No cloud, no API keys; all inference runs on the AMD XDNA2 NPU.

**Features:**
- 🖥️ Linux system management (Sway, Waybar, NetworkManager incl. WiFi connect, Systemd)
- ⚙️ Multi-step native tool-calling (chains tools until the task is done)
- ☸️ Kubernetes cluster management
- ⚡ Fast local execution (no cloud, no API keys)
- 🔒 Safe with approval confirmations
- 🧠 Conversation memory

## 🚀 Quick Start

### Interactive mode (recommended):
```bash
./agent -i
```

Then ask things like:
- "show my waybar config"
- "restart waybar"
- "check for failing kubernetes pods"
- "show network connections"
- "check docker status"

### One-off commands:
```bash
./agent "check my disk space"
./agent "show sway keybindings"
./agent "list pods in grafana namespace"
```

## 🔧 Available Tools

See [TOOLS.md](TOOLS.md) for complete reference.

### 🪟 Sway Window Manager
- View config, list keybindings, add keybindings, reload

### 🎨 Waybar Status Bar
- View config, restart, reload

### 🌐 Network (NetworkManager)
- Show status, list connections, scan WiFi, configure DNS

### ⚙️ Systemd Services
- Status, restart, enable/disable, logs, list services

### ☸️ Kubernetes
- List pods/deployments/services, check health, view logs, describe resources

### 💻 System Commands
- Execute any bash command, read/write files, check system status

## 🛡️ Safety Features

**Dangerous operations require approval:**

```
🤖 LLM wants to:
Add Sway keybinding

Tool: sway
Arguments:
  action: add-keybinding
  key: Mod+d
  command: rofi -show drun

Allow this action? [y/N/show]:
```

**Safe operations auto-approve:**
```
✓ Auto-approved: Show Waybar configuration
```

### Auto-approve mode:
```bash
./agent -y "show disk space"  # Skip all confirmations (use carefully!)
```

## 📋 Command Line Options

```bash
./agent "your request"              # One-off request
./agent -i                          # Interactive mode
./agent -y "request"                # Auto-approve all (use with caution!)
./agent -m qwen2.5-coder:7b -i     # Use larger model
```

## 🎯 Example Use Cases

### System Management
```bash
./agent "show waybar config"
./agent "restart waybar"
./agent "add sway keybinding Mod+d to exec rofi -show drun"
```

### Network
```bash
./agent "show network status"
./agent "list wifi networks"
./agent "set DNS to 8.8.8.8 for Wired connection 1"
```

### Kubernetes
```bash
./agent "check for failing pods"
./agent "show pods in grafana namespace"
./agent "get logs for pod grafana-xxx in grafana namespace"
```

### Services
```bash
./agent "check docker status"
./agent "restart networkmanager"
./agent "show last 50 lines of sshd logs"
```

## 🎓 Tips

### Be specific:
✅ "show waybar config"
✅ "restart waybar"
✅ "check for failing pods"

### Use interactive mode for conversations:
```
You: check kubernetes cluster health
Agent: [shows pod status]
You: describe that failing pod
Agent: [shows detailed pod info]
```

## 🔒 Security

**Important:** The agent can execute commands!

Safety measures:
1. ✅ **Approval required** for dangerous operations
2. ✅ Shows exactly what it will do
3. ✅ Safe operations auto-approve (viewing configs, checking status)
4. ⚠️ Use `-y` auto-approve ONLY for trusted queries

## 🆚 vs Regular Chat

**Regular chat:**
```bash
./chat "how do I check disk space?"
# Returns: "Use df -h command..." (you copy and run it)
```

**With agent:**
```bash
./agent "check disk space"
# LLM generates command, auto-approves safe operations, shows results
```

## 🎨 Different Models

```bash
./agent -i                         # Default: 3b (fast)
./agent -m qwen2.5-coder:7b -i    # 7b (more capable, slower)
./agent -m qwen2.5-coder:14b -i   # 14b (most capable, slowest)
```

**Model comparison:**
- **3b** (default): Fast, works well for most tasks
- **7b**: Better reasoning, slower
- **14b**: Best quality, requires 16GB+ RAM
