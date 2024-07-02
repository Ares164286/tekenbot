import discord
import asyncpg
import os
from discord.ext import tasks, commands

class PastSelf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.history_channel_id = 1024642680577331200  # 履歴を保存するチャンネルID
        self.watch_channel_id = 1247421345705492530  # 監視するチャンネルID
        self.fetch_messages_task.start()

    @tasks.loop(hours=12)
    async def fetch_messages_task(self):
        await self.fetch_and_save_messages(self.history_channel_id)

    @fetch_messages_task.before_loop
    async def before_fetch_messages_task(self):
        await self.bot.wait_until_ready()

    async def fetch_and_save_messages(self, channel_id):
        channel = self.bot.get_channel(channel_id)
        threads = []
        if isinstance(channel, discord.ForumChannel):
            threads = await self.fetch_all_threads(channel)
        else:
            threads.append(channel)

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

    async def fetch_all_threads(self, forum_channel):
        threads = []
        async for thread in forum_channel.threads():
            threads.append(thread)
        async for archived_thread in forum_channel.archived_threads(limit=None):
            threads.append(archived_thread)
        return threads

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

    @commands.command(name="save_history_cmd")
    async def save_history(self, ctx):
        await self.fetch_and_save_messages(self.history_channel_id)
        await ctx.send("メッセージ履歴の保存が完了しました。")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.watch_channel_id or message.author.bot:
            return

        user_message = await self.get_random_user_message(message.author.id)
        if user_message:
            webhook = await self.get_webhook(message.channel)
            await webhook.send(
                content=user_message["content"],
                username=message.author.display_name,
                avatar_url=message.author.avatar_url
            )

    async def get_random_user_message(self, author_id):
        conn = await asyncpg.connect(
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            database=os.getenv('PGDATABASE'),
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT')
        )

        message = await conn.fetchrow('''
            SELECT content
            FROM messages
            WHERE author_id = $1
            ORDER BY random()
            LIMIT 1
        ''', author_id)

        await conn.close()
        return message

    async def get_webhook(self, channel):
        webhooks = await channel.webhooks()
        if webhooks:
            return webhooks[0]

        webhook = await channel.create_webhook(name="PastSelfBot")
        return webhook

async def setup(bot):
    await bot.add_cog(PastSelf(bot))
