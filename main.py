#!/usr/bin/env python3
"""
SENTINELAPEX-AI
Secure, Cross-Platform CLI AI Assistant.

Entry Point:
    python main.py
"""

from sentinelapex.cli import app

if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        print("\n[!] Session terminated by user.")
    except Exception as e:
        print(f"\n[!] Critical Error: {e}")
        import traceback
        traceback.print_exc()