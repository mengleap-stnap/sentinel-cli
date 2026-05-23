import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from sentinelapex.models import Message, ChatSession
from sentinelapex.ui.console import console

class ChatExporter:
    """
    Utility class to save and load chat sessions in various formats.
    """

    @staticmethod
    def _ensure_directory(filepath: str) -> Path:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def save_to_json(session: ChatSession, filepath: str) -> bool:
        """Save session as structured JSON."""
        try:
            path = ChatExporter._ensure_directory(filepath)
            data = {
                "meta": {
                    "id": session.id,
                    "name": session.name,
                    "provider": session.provider,
                    "model": session.model,
                    "created_at": session.created_at,
                    "exported_at": datetime.now().isoformat()
                },
                "messages": [m.dict() for m in session.messages]
            }
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            console.print(f"[success]Chat saved to JSON: {path}[/success]")
            return True
        except Exception as e:
            console.print(f"[danger]Failed to save JSON: {e}[/danger]")
            return False

    @staticmethod
    def save_to_markdown(session: ChatSession, filepath: str) -> bool:
        """Save session as a readable Markdown file."""
        try:
            path = ChatExporter._ensure_directory(filepath)
            
            lines = []
            lines.append(f"# Chat Session: {session.name}")
            lines.append(f"**Date:** {session.created_at}")
            lines.append(f"**Model:** {session.provider}/{session.model}")
            lines.append("---\n")

            for msg in session.messages:
                if msg.role == "system":
                    continue # Skip system prompt in export usually
                
                role_emoji = "👤" if msg.role == "user" else "🤖"
                lines.append(f"### {role_emoji} {msg.role.capitalize()}")
                lines.append(f"{msg.content}\n")

            with open(path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            
            console.print(f"[success]Chat saved to Markdown: {path}[/success]")
            return True
        except Exception as e:
            console.print(f"[danger]Failed to save Markdown: {e}[/danger]")
            return False

    @staticmethod
    def save_to_text(session: ChatSession, filepath: str) -> bool:
        """Save session as plain text."""
        try:
            path = ChatExporter._ensure_directory(filepath)
            
            lines = []
            lines.append(f"SENTINELAPEX CHAT LOG")
            lines.append(f"Session: {session.name}")
            lines.append(f"Date: {session.created_at}")
            lines.append(f"Model: {session.provider}/{session.model}")
            lines.append("=" * 40 + "\n")

            for msg in session.messages:
                if msg.role == "system":
                    continue
                
                lines.append(f"[{msg.role.upper()}]:")
                lines.append(f"{msg.content}")
                lines.append("-" * 20)

            with open(path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            
            console.print(f"[success]Chat saved to Text: {path}[/success]")
            return True
        except Exception as e:
            console.print(f"[danger]Failed to save Text: {e}[/danger]")
            return False

    @staticmethod
    def save_chat(session: ChatSession, filename: Optional[str] = None, fmt: str = "md") -> bool:
        """
        Main entry point to save chat.
        fmt: 'json', 'md', 'txt'
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join([c if c.isalnum() else "_" for c in session.name])
            filename = f"{safe_name}_{timestamp}"

        # Add extension if missing
        if not filename.endswith(f".{fmt}"):
            filename += f".{fmt}"

        if fmt == "json":
            return ChatExporter.save_to_json(session, filename)
        elif fmt == "md":
            return ChatExporter.save_to_markdown(session, filename)
        elif fmt == "txt":
            return ChatExporter.save_to_text(session, filename)
        else:
            console.print(f"[danger]Unsupported format: {fmt}[/danger]")
            return False