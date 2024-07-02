import discord
from discord.ext import tasks, commands
import asyncpg
import os

class PastSelf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.history_channel_id = 1024642680577331200
        self.target_channel_id = 1247421345705492530
        self.fetch_messages_task.start()

    @tasks.loop(hours=12)
    async def fetch_messages_task(self):
        await self.fetch_and_save_messages(self.history_channel_id)

    async def fetch_and_save_messages(self, channel_id):
        forum_channel = self.bot.get_channel(channel_id)
        if not forum_channel:
            print("フォーラムチャンネルが見つかりません")
            return

        async with asyncpg.create_pool(dsn=os.getenv("DATABASE_URL")) as pool:
            async with pool.acquire() as connection:
                await connection.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        message_id BIGINT PRIMARY KEY,
                        author_id BIGINT,
                        content TEXT,
                        created_at TIMESTAMP
                    )
                ''')

                threads = forum_channel.threads
                for thread in threads:
                    async for message in thread.history(limit=10000):
                        await connection.execute('''
                            INSERT INTO messages (message_id, author_id, content, created_at)
                            VALUES ($1, $2, $3, $4)
                            ON CONFLICT (message_id) DO NOTHING
                        ''', message.id, message.author.id, message.content, message.created_at)

    @commands.command(name='save_history')
    async def save_history(self, ctx):
        await self.fetch_and_save_messages(self.history_channel_id)
        await ctx.send("メッセージの保存が完了しました")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.target_channel_id or message.author.bot:
            return

        async with asyncpg.create_pool(dsn=os.getenv("DATABASE_URL")) as pool:
            async with pool.acquire() as connection:
                rows = await connection.fetch('''
                    SELECT content
                    FROM messages
                    WHERE author_id = $1
                    ORDER BY random()
                    LIMIT 1
                ''', message.author.id)

                if rows:
                    past_message = rows[0]['content']
                    webhook = await message.channel.create_webhook(name=message.author.display_name)
                    await webhook.send(past_message, username=message.author.display_name, avatar_url=message.author.avatar.url)
                    await webhook.delete()

async def setup(bot):
    await bot.add_cog(PastSelf(bot))
