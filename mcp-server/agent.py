#!/usr/bin/env python3
"""
LLM Agent with MCP Integration
Connects Ollama LLM with MCP server for command execution
"""

import json
import subprocess
import sys
import os
import asyncio
from typing import Optional, Dict, Any

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

class MCPAgent:
    def __init__(self, model="qwen2.5-coder:3b", auto_approve=False):
        self.model = model
        self.auto_approve = auto_approve
        self.conversation_history = []
        self.system_context = self._get_system_context()
        
    def _get_system_context(self):
        """Get system context"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        context_script = os.path.join(script_dir, "..", "get-system-context.sh")
        
        try:
            result = subprocess.run(
                ["bash", context_script],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout
        except:
            return ""
    
    def _sway_tool(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Manage Sway window manager configuration"""
        action = args.get("action", "help")
        config_path = os.path.expanduser("~/.config/sway/config")
        
        if action == "show-config":
            try:
                with open(config_path, 'r') as f:
                    return {"content": f.read()}
            except FileNotFoundError:
                return {"error": f"Config file not found: {config_path}"}
        
        elif action == "list-keybindings":
            try:
                with open(config_path, 'r') as f:
                    lines = f.readlines()
                keybindings = [line.strip() for line in lines if line.strip().startswith('bindsym')]
                return {"keybindings": "\n".join(keybindings)}
            except FileNotFoundError:
                return {"error": f"Config file not found: {config_path}"}
        
        elif action == "add-keybinding":
            key = args.get("key")
            command = args.get("command")
            if not key or not command:
                return {"error": "Both 'key' and 'command' arguments required"}
            
            binding_line = f"bindsym {key} exec {command}\n"
            try:
                with open(config_path, 'a') as f:
                    f.write(binding_line)
                return {"status": "success", "message": f"Added: {binding_line.strip()}"}
            except Exception as e:
                return {"error": str(e)}
        
        elif action == "reload":
            result = subprocess.run(["swaymsg", "reload"], capture_output=True, text=True)
            return {"output": result.stdout, "status": "success" if result.returncode == 0 else "failed"}
        
        else:
            return {"error": f"Unknown action: {action}. Available: show-config, list-keybindings, add-keybinding, reload"}
    
    def _waybar_tool(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Manage Waybar configuration"""
        action = args.get("action", "help")
        config_path = os.path.expanduser("~/.config/waybar/config.jsonc")
        
        if action == "show-config":
            try:
                with open(config_path, 'r') as f:
                    return {"content": f.read()}
            except FileNotFoundError:
                # Try without .jsonc extension
                config_path = os.path.expanduser("~/.config/waybar/config")
                try:
                    with open(config_path, 'r') as f:
                        return {"content": f.read()}
                except FileNotFoundError:
                    return {"error": "Waybar config not found"}
        
        elif action == "restart":
            # Kill existing waybar
            subprocess.run(["killall", "waybar"], capture_output=True)
            # Start new one
            result = subprocess.run(["waybar", "&"], shell=True, capture_output=True, text=True)
            return {"status": "success", "message": "Waybar restarted"}
        
        elif action == "reload":
            subprocess.run(["killall", "-SIGUSR2", "waybar"], capture_output=True)
            return {"status": "success", "message": "Waybar reloaded"}
        
        else:
            return {"error": f"Unknown action: {action}. Available: show-config, restart, reload"}
    
    def _network_tool(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Manage network configuration"""
        action = args.get("action", "status")
        
        if action == "status":
            result = subprocess.run(["nmcli", "device", "status"], capture_output=True, text=True)
            return {"output": result.stdout}
        
        elif action == "connections":
            result = subprocess.run(["nmcli", "connection", "show"], capture_output=True, text=True)
            return {"output": result.stdout}
        
        elif action == "wifi-list":
            result = subprocess.run(["nmcli", "device", "wifi", "list"], capture_output=True, text=True)
            return {"output": result.stdout}
        
        elif action == "set-dns":
            connection = args.get("connection")
            dns = args.get("dns")
            if not connection or not dns:
                return {"error": "Both 'connection' and 'dns' required"}
            
            result = subprocess.run(
                ["nmcli", "connection", "modify", connection, "ipv4.dns", dns],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                # Reload connection
                subprocess.run(["nmcli", "connection", "up", connection], capture_output=True)
                return {"status": "success", "message": f"DNS set to {dns} for {connection}"}
            return {"error": result.stderr}
        
        else:
            return {"error": f"Unknown action: {action}. Available: status, connections, wifi-list, set-dns"}
    
    def _systemd_tool(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Manage systemd services"""
        action = args.get("action", "status")
        service = args.get("service", "")
        
        if action == "status":
            if not service:
                return {"error": "Service name required"}
            result = subprocess.run(["systemctl", "status", service], capture_output=True, text=True)
            return {"output": result.stdout}
        
        elif action == "restart":
            if not service:
                return {"error": "Service name required"}
            result = subprocess.run(["systemctl", "restart", service], capture_output=True, text=True)
            return {"status": "success" if result.returncode == 0 else "failed", "output": result.stderr}
        
        elif action == "enable":
            if not service:
                return {"error": "Service name required"}
            result = subprocess.run(["systemctl", "enable", service], capture_output=True, text=True)
            return {"status": "success" if result.returncode == 0 else "failed", "output": result.stdout}
        
        elif action == "disable":
            if not service:
                return {"error": "Service name required"}
            result = subprocess.run(["systemctl", "disable", service], capture_output=True, text=True)
            return {"status": "success" if result.returncode == 0 else "failed", "output": result.stdout}
        
        elif action == "logs":
            if not service:
                return {"error": "Service name required"}
            lines = args.get("lines", "50")
            result = subprocess.run(["journalctl", "-u", service, "-n", str(lines)], capture_output=True, text=True)
            return {"output": result.stdout}
        
        elif action == "list":
            result = subprocess.run(["systemctl", "list-units", "--type=service", "--all"], capture_output=True, text=True)
            return {"output": result.stdout}
        
        else:
            return {"error": f"Unknown action: {action}. Available: status, restart, enable, disable, logs, list"}
    
    def _ask_llm(self, prompt: str) -> str:
        """Ask the LLM a question"""
        # Build conversation history
        history_context = ""
        if self.conversation_history:
            history_context = "\n\nPrevious conversation:\n"
            for entry in self.conversation_history[-3:]:  # Last 3 exchanges
                history_context += f"\nUser: {entry['user']}\n"
                if 'tool_result' in entry:
                    history_context += f"Tool result: {entry['tool_result'][:500]}...\n"  # Truncate long outputs
        
        full_prompt = f"""{self.system_context}
{history_context}

You are a helpful AI assistant with access to system tools via MCP (Model Context Protocol).

IMPORTANT: Only use tools when the user wants to DO or CHECK something on the system.
For general questions, conversations, explanations, or requests like jokes/advice, RESPOND NATURALLY without using tools.

When a tool is needed, respond with a JSON tool call in this format:
{{
  "tool": "tool_name",
  "arguments": {{"arg1": "value1"}},
  "explanation": "what this will do"
}}

Examples of when NOT to use tools:
- "tell me a joke" → Just tell a joke naturally
- "how do I optimize Docker?" → Provide advice naturally
- "what's the best way to..." → Answer conversationally
- "explain kubernetes" → Explain naturally

Examples of when TO use tools:
- "check my disk space" → Use execute_command or system_status
- "show my wifi connection" → Use network tool
- "read the config file" → Use read_file
- "restart docker" → Use systemd tool

Available tools:
- execute_command: Run bash commands (args: command, working_dir)
  Example: {{"tool": "execute_command", "arguments": {{"command": "cat /etc/os-release"}}, "explanation": "Check OS version"}}
  Example: {{"tool": "execute_command", "arguments": {{"command": "df -h"}}, "explanation": "Check disk space"}}
  Example: {{"tool": "execute_command", "arguments": {{"command": "ls -la ~/projects"}}, "explanation": "List files in projects directory"}}
  Use this for: OS version, hostname, date/time, uptime, running processes, custom commands

- read_file: Read file contents (args: path)
  Example: {{"tool": "read_file", "arguments": {{"path": "/etc/hostname"}}, "explanation": "Read hostname file"}}
  Example: {{"tool": "read_file", "arguments": {{"path": "~/.bashrc"}}, "explanation": "Read bash configuration"}}
  Example: {{"tool": "read_file", "arguments": {{"path": "/home/peter/projects/myapp/config.yml"}}, "explanation": "Read application config"}}
  Use this for: Reading configuration files, log files, source code, any text file

- write_file: Write to files (args: path, content)
  Example: {{"tool": "write_file", "arguments": {{"path": "~/test.txt", "content": "Hello World"}}, "explanation": "Create test file"}}
  Use this for: Creating or updating configuration files, scripts, documents

- sway: Manage Sway window manager (args: action = show-config|list-keybindings|add-keybinding|reload, key = for add-keybinding, command = for add-keybinding)
  Example: {{"tool": "sway", "arguments": {{"action": "show-config"}}, "explanation": "Show Sway configuration file"}}
  Example: {{"tool": "sway", "arguments": {{"action": "list-keybindings"}}, "explanation": "List all Sway keybindings"}}
  Example: {{"tool": "sway", "arguments": {{"action": "add-keybinding", "key": "Mod+d", "command": "rofi -show drun"}}, "explanation": "Add Mod+d keybinding for rofi"}}
  Example: {{"tool": "sway", "arguments": {{"action": "reload"}}, "explanation": "Reload Sway configuration"}}

- waybar: Manage Waybar status bar (args: action = show-config|restart|reload)
  Example: {{"tool": "waybar", "arguments": {{"action": "show-config"}}, "explanation": "Show Waybar configuration"}}
  Example: {{"tool": "waybar", "arguments": {{"action": "restart"}}, "explanation": "Restart Waybar"}}
  Example: {{"tool": "waybar", "arguments": {{"action": "reload"}}, "explanation": "Reload Waybar config without restarting"}}

- network: Manage network configuration (args: action = status|connections|wifi-list|set-dns, connection = for set-dns, dns = for set-dns)
  Example: {{"tool": "network", "arguments": {{"action": "status"}}, "explanation": "Show network device status"}}
  Example: {{"tool": "network", "arguments": {{"action": "connections"}}, "explanation": "List network connections"}}
  Example: {{"tool": "network", "arguments": {{"action": "set-dns", "connection": "Wired connection 1", "dns": "8.8.8.8"}}, "explanation": "Set DNS to Google DNS"}}

- systemd: Manage system services (args: action = status|restart|enable|disable|logs|list, service = service name, lines = for logs)
  Example: {{"tool": "systemd", "arguments": {{"action": "status", "service": "docker"}}, "explanation": "Check Docker service status"}}
  Example: {{"tool": "systemd", "arguments": {{"action": "restart", "service": "networkmanager"}}, "explanation": "Restart NetworkManager"}}
  Example: {{"tool": "systemd", "arguments": {{"action": "logs", "service": "sshd", "lines": "100"}}, "explanation": "Show last 100 lines of SSH logs"}}
  Example: {{"tool": "systemd", "arguments": {{"action": "list"}}, "explanation": "List all systemd services"}}

- kubernetes: Manage Kubernetes resources (args: action = pods|deployments|services|namespaces|all|check-health|logs|describe, namespace = optional|all, pod = required for logs/describe, tail = optional for logs, resource = optional)
  Example: {{"tool": "kubernetes", "arguments": {{"action": "pods", "namespace": "grafana"}}, "explanation": "Get pods in grafana namespace"}}
  Example: {{"tool": "kubernetes", "arguments": {{"action": "pods", "namespace": "all"}}, "explanation": "Get pods in all namespaces"}}
  Example: {{"tool": "kubernetes", "arguments": {{"action": "check-health"}}, "explanation": "Check for any pods with issues across entire cluster"}}
  Example: {{"tool": "kubernetes", "arguments": {{"action": "logs", "pod": "grafana-6cf4bffb9-9mlkq", "namespace": "grafana", "tail": "50"}}, "explanation": "Get last 50 logs from grafana pod"}}
  Example: {{"tool": "kubernetes", "arguments": {{"action": "describe", "pod": "gpu-operator-node-feature-discovery-prune-nf4tp", "namespace": "gpu-operator"}}, "explanation": "Describe pod to see why it's in error state"}}
  Use action "check-health" when user asks about problems, issues, or health status.
  IMPORTANT: When showing logs or describing a pod, use the SAME namespace where that pod was found!

- system_status: Check system resources ONLY (args: component = cpu|memory|disk|network|docker|kubernetes|all)
  Example: {{"tool": "system_status", "arguments": {{"component": "disk"}}, "explanation": "Check disk usage"}}
  Use this ONLY for: memory usage, disk space summary, CPU info
  DO NOT use this for OS version - use execute_command with "cat /etc/os-release" instead

Current user request: {prompt}

DECISION GUIDE:
- If the request is conversational (jokes, advice, questions, explanations) → Respond naturally in plain text
- If the request requires system action or information (check, show, list, restart, read file) → Use a tool with JSON format

Respond appropriately based on the request type.
"""
        
        result = subprocess.run(
            ["ollama", "run", self.model, full_prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return result.stdout.strip()
    
    def _execute_tool(self, tool_call: dict) -> dict:
        """Execute an MCP tool"""
        tool = tool_call.get("tool")
        args = tool_call.get("arguments", {})
        
        if tool == "execute_command":
            cmd = args.get("command")
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        
        elif tool == "read_file":
            # Expand ~ to home directory
            file_path = os.path.expanduser(args["path"])
            with open(file_path, 'r') as f:
                return {"content": f.read()}
        
        elif tool == "write_file":
            # Expand ~ to home directory
            file_path = os.path.expanduser(args["path"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(args["content"])
            return {"status": "success"}
        
        elif tool == "network_info":
            result = subprocess.run(
                ["nmcli", "device", "status"],
                capture_output=True,
                text=True
            )
            return {"output": result.stdout}
        
        elif tool == "kubernetes":
            action = args.get("action", "status")
            namespace = args.get("namespace", "")
            resource = args.get("resource", "pods")
            
            # Special case for all namespaces
            if namespace == "all" or action == "check-health":
                ns_flag = ["--all-namespaces"]
            elif namespace:
                ns_flag = ["-n", namespace]
            else:
                ns_flag = []
            
            if action == "check-health":
                # Check for pods with issues across all namespaces
                result = subprocess.run(
                    ["kubectl", "get", "pods", "--all-namespaces", 
                     "--field-selector=status.phase!=Running,status.phase!=Succeeded"],
                    capture_output=True,
                    text=True
                )
                output = result.stdout
                if not output.strip() or "No resources found" in output:
                    # Also check for pods that are running but not ready
                    result2 = subprocess.run(
                        ["kubectl", "get", "pods", "--all-namespaces"],
                        capture_output=True,
                        text=True
                    )
                    lines = result2.stdout.split('\n')
                    issues = [lines[0]]  # header
                    for line in lines[1:]:
                        if line and 'Running' in line:
                            parts = line.split()
                            if len(parts) >= 3:
                                ready = parts[2]  # READY column
                                if '/' in ready:
                                    current, total = ready.split('/')
                                    if current != total:
                                        issues.append(line)
                    
                    if len(issues) > 1:
                        output = '\n'.join(issues)
                    else:
                        output = "All pods are healthy!"
                return {"output": output}
            
            elif action == "pods":
                result = subprocess.run(
                    ["kubectl", "get", "pods"] + ns_flag,
                    capture_output=True,
                    text=True
                )
            elif action == "deployments":
                result = subprocess.run(
                    ["kubectl", "get", "deployments"] + ns_flag,
                    capture_output=True,
                    text=True
                )
            elif action == "services":
                result = subprocess.run(
                    ["kubectl", "get", "services"] + ns_flag,
                    capture_output=True,
                    text=True
                )
            elif action == "logs":
                pod_name = args.get("pod", "")
                tail_lines = args.get("tail", "100")
                container = args.get("container", "")
                
                if not pod_name:
                    return {"error": "Pod name required for logs"}
                
                log_cmd = ["kubectl", "logs", pod_name] + ns_flag + ["--tail=" + str(tail_lines)]
                if container:
                    log_cmd.extend(["-c", container])
                
                result = subprocess.run(
                    log_cmd,
                    capture_output=True,
                    text=True
                )
            elif action == "describe":
                pod_name = args.get("pod", "")
                if not pod_name:
                    return {"error": "Pod name required for describe"}
                
                result = subprocess.run(
                    ["kubectl", "describe", "pod", pod_name] + ns_flag,
                    capture_output=True,
                    text=True
                )
            elif action == "namespaces":
                result = subprocess.run(
                    ["kubectl", "get", "namespaces"],
                    capture_output=True,
                    text=True
                )
            elif action == "all":
                result = subprocess.run(
                    ["kubectl", "get", "all"] + ns_flag,
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    ["kubectl", "get", resource] + ns_flag,
                    capture_output=True,
                    text=True
                )
            
            return {"output": result.stdout if result.returncode == 0 else result.stderr}
        
        elif tool == "system_status":
            component = args.get("component", "all")
            outputs = []
            
            if component in ["cpu", "all"]:
                result = subprocess.run(["lscpu"], capture_output=True, text=True)
                outputs.append("=== CPU Info ===\n" + result.stdout)
            
            if component in ["memory", "all"]:
                result = subprocess.run(["free", "-h"], capture_output=True, text=True)
                outputs.append("=== Memory ===\n" + result.stdout)
            
            if component in ["disk", "all"]:
                result = subprocess.run(["df", "-h"], capture_output=True, text=True)
                outputs.append("=== Disk ===\n" + result.stdout)
            
            if component in ["network", "all"]:
                result = subprocess.run(["nmcli", "device", "status"], capture_output=True, text=True)
                outputs.append("=== Network ===\n" + result.stdout)
            
            if component in ["docker", "all"]:
                result = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True)
                if result.returncode == 0:
                    outputs.append("=== Docker Containers ===\n" + result.stdout)
            
            if component in ["kubernetes", "all"]:
                # Get current context
                ctx_result = subprocess.run(["kubectl", "config", "current-context"], capture_output=True, text=True)
                # Get nodes
                nodes_result = subprocess.run(["kubectl", "get", "nodes"], capture_output=True, text=True)
                # Get pods in current namespace
                pods_result = subprocess.run(["kubectl", "get", "pods"], capture_output=True, text=True)
                
                k8s_info = "=== Kubernetes Cluster ===\n"
                if ctx_result.returncode == 0:
                    k8s_info += f"Context: {ctx_result.stdout.strip()}\n\n"
                if nodes_result.returncode == 0:
                    k8s_info += "Nodes:\n" + nodes_result.stdout + "\n"
                if pods_result.returncode == 0:
                    k8s_info += "Pods:\n" + pods_result.stdout
                
                outputs.append(k8s_info)
            
            return {"output": "\n\n".join(outputs) if outputs else "No data available"}
        
        elif tool == "sway":
            return self._sway_tool(args)
        
        elif tool == "waybar":
            return self._waybar_tool(args)
        
        elif tool == "network":
            return self._network_tool(args)
        
        elif tool == "systemd":
            return self._systemd_tool(args)
        
        else:
            return {"error": f"Unknown tool: {tool}"}
    
    def _confirm_action(self, tool_call: dict) -> bool:
        """Ask user to confirm action"""
        tool = tool_call.get('tool')
        args = tool_call.get('arguments', {})
        
        # Auto-approve if -y flag is set
        if self.auto_approve:
            return True
        
        # Always require confirmation for file write operations
        require_confirmation = tool == 'write_file'
        
        # Check for dangerous commands in execute_command
        if tool == 'execute_command':
            cmd = args.get('command', '')
            dangerous_patterns = ['rm ', 'rmdir', 'rm -', 'unlink', 'shred', 'dd ', 'mkfs', 'fdisk', 'parted']
            if any(pattern in cmd for pattern in dangerous_patterns):
                require_confirmation = True
        
        # Auto-approve safe operations
        if not require_confirmation:
            print(f"{GREEN}✓ Auto-approved:{RESET} {tool_call.get('explanation', tool)}")
            return True
        
        # Ask for confirmation on file writes
        print(f"\n{YELLOW}🤖 LLM wants to:{RESET}")
        print(f"{BOLD}{tool_call.get('explanation', 'Execute tool')}{RESET}")
        print(f"\n{BLUE}Tool:{RESET} {tool_call['tool']}")
        print(f"{BLUE}Arguments:{RESET}")
        for key, value in tool_call.get('arguments', {}).items():
            print(f"  {key}: {value}")
        
        print(f"\n{YELLOW}Allow this action? [y/N/show]:{RESET} ", end="")
        response = input().strip().lower()
        
        if response == 'show':
            print(f"\n{BLUE}Full tool call:{RESET}")
            print(json.dumps(tool_call, indent=2))
            print(f"\n{YELLOW}Allow? [y/N]:{RESET} ", end="")
            response = input().strip().lower()
        
        return response == 'y'
    
    def process_request(self, user_input: str):
        """Process user request"""
        print(f"\n{GREEN}🤔 Thinking...{RESET}")
        
        # Ask LLM
        response = self._ask_llm(user_input)
        
        # Check if response is a tool call
        try:
            # Strip markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```'):
                # Extract JSON from code block
                lines = cleaned_response.split('\n')
                # Remove first line (```json or ```) and last line (```)
                if lines[0].startswith('```'):
                    lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                cleaned_response = '\n'.join(lines).strip()
            
            # Try to parse as JSON
            if cleaned_response.startswith('{'):
                tool_call = json.loads(cleaned_response)
                
                if "tool" in tool_call:
                    # Confirm with user
                    if self._confirm_action(tool_call):
                        print(f"\n{GREEN}✓ Executing...{RESET}")
                        result = self._execute_tool(tool_call)
                        
                        print(f"\n{GREEN}✓ Result:{RESET}")
                        result_str = ""
                        if isinstance(result, dict):
                            for key, value in result.items():
                                if value:
                                    print(f"\n{BOLD}{key}:{RESET}")
                                    print(value)
                                    result_str += f"{key}: {value}\n"
                        else:
                            print(result)
                            result_str = str(result)
                        
                        # Store in conversation history
                        self.conversation_history.append({
                            'user': user_input,
                            'tool': tool_call['tool'],
                            'tool_result': result_str
                        })
                        
                        return result
                    else:
                        print(f"{RED}✗ Action cancelled{RESET}")
                        return None
        except json.JSONDecodeError:
            pass
        
        # Not a tool call, just print response
        print(f"\n{BLUE}💬 Response:{RESET}")
        print(response)
        
        # Store text response in history
        self.conversation_history.append({
            'user': user_input,
            'response': response
        })
        
        return response

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM Agent with MCP")
    parser.add_argument("request", nargs="*", help="Your request to the LLM")
    parser.add_argument("-m", "--model", default="qwen2.5-coder:3b", help="Ollama model to use")
    parser.add_argument("-y", "--yes", action="store_true", help="Auto-approve all actions (dangerous!)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    agent = MCPAgent(model=args.model, auto_approve=args.yes)
    
    if args.interactive:
        print(f"{BOLD}{GREEN}🤖 LLM Agent with MCP{RESET}")
        print(f"{BLUE}Model: {args.model}{RESET}")
        print(f"{YELLOW}Type 'exit' to quit{RESET}\n")
        
        while True:
            try:
                user_input = input(f"{BOLD}You:{RESET} ").strip()
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                if user_input:
                    agent.process_request(user_input)
            except KeyboardInterrupt:
                print(f"\n{YELLOW}Goodbye!{RESET}")
                break
            except Exception as e:
                print(f"{RED}Error: {e}{RESET}")
    else:
        if not args.request:
            parser.print_help()
            sys.exit(1)
        
        request = " ".join(args.request)
        agent.process_request(request)

if __name__ == "__main__":
    main()
