import asyncio
import sys
import os

# add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram_service import leave_chat

async def main():
    if len(sys.argv) < 2:
        print("usage: python scripts/leave_chat.py <chat_id>")
        sys.exit(1)
        
    chat_id = sys.argv[1]
    success = await leave_chat(chat_id)
    
    if success:
        print(f"✅ bot successfully left chat {chat_id}")
    else:
        print(f"❌ failed to leave chat {chat_id}. check logs.")

if __name__ == "__main__":
    asyncio.run(main())
