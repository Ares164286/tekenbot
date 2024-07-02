import asyncpg
import os
from discord.ext import tasks, commands

class PastSelf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.history_channel_id = 1024642680577331200  # 履歴を保存するチャンネルID
        self.fetch_messages_task.start()

    @tasks.loop(hours=12)
    async def fetch_messages_task(self):
        await self.fetch_and_save_messages(self.history_channel_id)

    async def fetch_and_save_messages(self, channel_id):
        channel = self.bot.get_channel(channel_id)
        if isinstance(channel, discord.ForumChannel):
            threads = [thread async for thread in channel.threads] + [thread async for thread in channel.archived_threads(limit=None)]
        else:
            threads = [channel]

        messages = []
        for thread in threads:
            async for message in thread.history(limit=10000):
                if message.author.bot:
                    continue
                messages.append({
                    "message_id": message.id,
                    "author_id": message.author.id,
                    "content": message.content,
                    "created_at": message.created_at
                })

        await self.save_messages_to_db(messages)

    async def save_messages_to_db(self, messages):
        conn = await asyncpg.connect(
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            database=os.getenv('PGDATABASE'),
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT')
        )

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id BIGINT PRIMARY KEY,
                author_id BIGINT,
                content TEXT,
                created_at TIMESTAMPTZ
            )
        ''')

        for message in messages:
            await conn.execute('''
                INSERT INTO messages (message_id, author_id, content, created_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (message_id) DO NOTHING
            ''', message['message_id'], message['author_id'], message['content'], message['created_at'])

        await conn.close()

async def setup(bot):
    await bot.add_cog(PastSelf(bot))
