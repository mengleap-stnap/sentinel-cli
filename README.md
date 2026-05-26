
<p align="center">
  <img src="Images/STNAP.png" width="300">
  <p align="center">
  <img src="https://img.shields.io/badge/AI-CLI-red.svg" />
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" />
  <img src="https://img.shields.io/badge/SENTINELAPEX-blue.svg" />
</p>



## SENTINELAPEX-AI
A secure, cross-platform CLI AI assistant with enterprise-grade key management, multi-provider streaming, and a cyberpunk terminal interface.

##  Features
Multi-Provider Support - OpenAI, Anthropic, Google Gemini, Groq, Mistral, Cohere, OpenRouter, Together AI, DeepSeek, HuggingFace, Ollama, LM Studio

Async Streaming - Real-time token streaming with httpx + asyncio. Zero UI lag.

Persistent Memory - SQLite-backed chat history, multi-session support, auto-save

##  Installation
Prerequisites
 - Python 3.10 or higher
 - Windows Terminal / macOS Terminal / GNOME Terminal (or any modern TTY)
1. Clone
```git
git clone https://github.com/mengleap-stnap/sentinel-cli.git
cd sentinel-cli
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
2. Launch
```bah
python main.py
# or if installed globally:
sentinelapex
```
## How to Use
First-Time Setup Wizard
 - When you run SENTINELAPEX-AI for the first time:
 - The Setup Wizard automatically launches.
 - Select a provider (e.g., openai, anthropic, ollama).
 - Paste your API key when prompted (input is masked).
 - The CLI validates the key against the provider's API.
 - Valid keys are encrypted and saved to ~/.sentinelapex/.env.
 Chat interface becomes available.

## Interactive Workflow
```hasha
[openai] (gpt-4o) > /help
[openai] (gpt-4o) > Explain quantum computing in 3 sentences.
[openai] (gpt-4o) > /model llama3
[ollama] (llama3) > Switched to ollama (llama3)
[ollama] (llama3) > Compare classical vs quantum bits.
[ollama] (llama3) > /save quantum_chat.md
```
## CLI Commands

| Command | Description | Example |
|---|---|---|
| `/help` | Show all available commands | `/help` |
| `/apikey` | Launch secure key manager | `/apikey` |
| `/provider` | Switch AI provider | `/provider anthropic` |
| `/model` | Change model version | `/model claude-3-5-sonnet` |
| `/system` | Set system prompt | `/system Act as a senior Python architect.` |
| `/temp` | Adjust creativity (0.0 – 1.0) | `/temp 0.2` |
| `/save` | Export chat to .md, .txt, .json | `/save my_chat` |
| `/history` | View recent sessions | `/history` |
| `/clear` | Clear current context | `/clear` |
| `/exit` | Quit application | `/exit` |

## Security Architecture
- Zero Hardcoded Keys: All keys are user-provided at runtime.
- Fernet Encryption: API keys are symmetrically encrypted before disk storage.
- Master Key Isolation: Stored at ~/.sentinelapex/master.key with 0600 permissions (owner-only read/write).
- Runtime Decryption: Keys are decrypted only in memory during API calls.
- Masked UI Output: Keys are never printed to terminal; shown as xxxxx.
  
💡 Best Practice: Use the /apikey command to manage keys. Avoid manual .env edits unless necessary.

## Advanced Configuration
- YAML Overrides (config.yaml)
```code
app:
  theme: "cyberpunk"
  max_history_length: 100
defaults:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.7
```
Enable/Disable SQLite
 - Set ENABLE_SQLITE=false in .env or enable_sqlite: false in config.yaml to run in memory-only mode.
 - Local Models (Ollama / LM Studio)
 - Start Ollama: ollama run llama3
 - In CLI: /provider ollama → /model llama3
 - No API key required. Runs entirely offline.
## License
MIT License. See LICENSE for details.

[![License](https://img.shields.io/badge/SENTINEL-APEX-blue.svg)]()
[![License](https://img.shields.io/badge/STNAP-brown.svg)]()
