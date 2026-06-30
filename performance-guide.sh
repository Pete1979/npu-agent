#!/bin/bash
# Model Performance Guide & NPU Information

cat << 'EOF'
🚀 QWEN2.5-CODER MODEL COMPARISON
===================================

Your system: AMD Ryzen AI 9 HX PRO 375 (24 cores, 62GB RAM)
NPU Detected: AMD Strix/Krackan Neural Processing Unit

AVAILABLE QWEN2.5-CODER MODELS:
---------------------------------

🟢 qwen2.5-coder:1.5b (986 MB) - FASTEST
   - Speed: Very Fast (3-5x faster than 7b)
   - Quality: Good for most coding tasks
   - Use for: Quick questions, code completion, debugging
   - Best for: Quick lookups, fast responses

🟡 qwen2.5-coder:3b (1.9 GB) ⭐ DEFAULT - BALANCED
   - Speed: Fast (2-3x faster than 7b)
   - Quality: Better reasoning, still quick
   - Use for: Daily work, MCP agent, system diagnostics
   - Best for: General use, interactive coding, kubernetes ops

🔴 qwen2.5-coder:7b (4.7 GB) - SMARTEST
   - Speed: Slower but thorough
   - Quality: Best code quality and explanations
   - Use for: Complex algorithms, architecture decisions
   - Best for: Important code reviews, learning, complex troubleshooting

SPEED COMPARISON (approximate):
---------------------------------
1.5b: ████████████████████████ 24 tokens/sec
3b:   ████████████           12 tokens/sec  
7b:   ████████               8 tokens/sec

SWITCHING MODELS:
---------------------------------

Quick switch for one command:
  ./ask "question" qwen2.5-coder:7b
  ./chat qwen2.5-coder:1.5b
  ./agent -m qwen2.5-coder:7b "complex task"

Set environment variable:
  export QUICK_FIX_MODEL=qwen2.5-coder:7b
  ./quick-fix "error message"

Download a model:
  ollama pull qwen2.5-coder:1.5b

🎯 RECOMMENDED USAGE:
---------------------------------
Daily use & Agent:  qwen2.5-coder:3b (current default)
Speed priority:     qwen2.5-coder:1.5b
Complex tasks:      qwen2.5-coder:7b

Agent-specific:
  ./agent -i                          # Uses 3b (default, balanced)
  ./agent -m qwen2.5-coder:1.5b -i    # Fast operations
  ./agent -m qwen2.5-coder:7b -i      # Complex K8s troubleshooting

🔬 AMD NPU ACCELERATION - CURRENT STATUS
==========================================

Your NPU: AMD Strix/Krackan Neural Processing Unit
Status: ❌ Not currently supported by Ollama

WHY NPU ISN'T USED:
-------------------
Ollama currently supports:
  ✅ CPU (what you're using now)
  ✅ NVIDIA GPU (CUDA)
  ✅ AMD GPU (ROCm) - Your Radeon 890M could work!
  ✅ Apple Silicon (Metal)
  ❌ AMD NPU (not yet supported)

POTENTIAL NPU SOLUTIONS:
------------------------

1. AMD Ryzen AI Software (requires Windows currently)
   - Linux support is experimental
   
2. DirectML + ONNX Runtime
   - Requires converting models to ONNX format
   - Complex setup

3. Wait for Ollama NPU support
   - AMD is working on Linux NPU support
   - May come in future Ollama releases

🎮 GPU ACCELERATION OPTION:
---------------------------

Your Radeon 890M GPU might work with ROCm!

To try GPU acceleration:
  1. Install ROCm drivers: https://rocm.docs.amd.com/
  2. Restart Ollama
  3. It will auto-detect GPU

This could give 2-5x speedup vs CPU!

💡 CURRENT BEST PERFORMANCE TIPS:
----------------------------------

✅ Use 3b model by default (balanced, current default)
✅ Use 1.5b for simple questions: ./agent -m qwen2.5-coder:1.5b
✅ Skip system context for quick queries: ./ask "question" --no-context
✅ Agent auto-approves safe ops (faster workflow)
✅ Use conversation memory (no need to repeat context)
✅ Consider GPU acceleration (Radeon 890M)
⏳ Wait for AMD NPU support in Ollama

TRY IT NOW:
-----------
  # Fast simple question
  ./ask "Write a Python hello world" --no-context
  
  # Agent with fast model
  ./agent -m qwen2.5-coder:1.5b "check disk space"
  
  # Interactive with balanced model (default)
  ./agent -i

You should see significantly better response times with the right model!

EOF
