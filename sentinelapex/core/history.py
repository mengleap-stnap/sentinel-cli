import aiosqlite
import json
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from sentinelapex.models import Message, ChatSession
from sentinelapex.ui.console import console

class HistoryManager:
    def __init__(self, db_path: str, enabled: bool = True):
        self.db_path = Path(db_path)
        self.enabled = enabled
        self.current_session: Optional[ChatSession] = None
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def init_db(self):
        if not self.enabled:
            return
            
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    provider TEXT,
                    model TEXT,
                    messages_json TEXT
                )
            """)
            await db.commit()

    def new_session(self, name: str = "New Chat", provider: str = "openai", model: str = "gpt-4o") -> ChatSession:
        session_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        self.current_session = ChatSession(
            id=session_id,
            name=name,
            created_at=now,
            provider=provider,
            model=model,
            messages=[]
        )
        return self.current_session

    async def save_session(self, session: ChatSession):
        if not self.enabled or not session:
            return
            
        async with aiosqlite.connect(self.db_path) as db:
            # Serialize messages
            messages_json = json.dumps([m.dict() for m in session.messages])
            
            await db.execute("""
                INSERT OR REPLACE INTO sessions 
                (id, name, created_at, updated_at, provider, model, messages_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session.id,
                session.name,
                session.created_at,
                datetime.now().isoformat(),
                session.provider,
                session.model,
                messages_json
            ))
            await db.commit()

    async def load_session(self, session_id: str) -> Optional[ChatSession]:
        if not self.enabled:
            return None
            
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    # row indices: 0:id, 1:name, 2:created_at, 3:updated_at, 4:provider, 5:model, 6:messages_json
                    try:
                        messages_data = json.loads(row[6])
                        messages = [Message(**m) for m in messages_data]
                        
                        return ChatSession(
                            id=row[0],
                            name=row[1],
                            created_at=row[2],
                            provider=row[4],
                            model=row[5],
                            messages=messages
                        )
                    except Exception as e:
                        console.print(f"[danger]Error loading session data: {e}[/danger]")
                        return None
        return None

    async def list_sessions(self) -> List[dict]:
        if not self.enabled:
            return []
            
        sessions_list = []
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT id, name, created_at, provider, model FROM sessions ORDER BY updated_at DESC") as cursor:
                async for row in cursor:
                    sessions_list.append({
                        "id": row[0],
                        "name": row[1],
                        "date": row[2],
                        "provider": row[3],
                        "model": row[4]
                    })
        return sessions_list