import discord
from discord.ext import commands, tasks
import random
import os
import psycopg2
from datetime import datetime

class PastSelf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_conn = self.connect_to_db()
        self.create_table()
        self.fetch_messages_task.start()

    def connect_to_db(self):
        return psycopg2.connect(
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT'),
            dbname=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD')
        )

    def create_table(self):
        with self.db_conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.db_conn.commit()

    def save_message(self, user_id, channel_id, message):
        with self.db_conn.cursor() as cur:
            cur.execute("""
                INSERT INTO messages (user_id, channel_id, message)
                VALUES (%s, %s, %s)
            """, (user_id, channel_id, message))
            self.db_conn.commit()

    async def fetch_and_save_messages(self, channel_id, limit=1000):
        channel = self.bot.get_channel(channel_id)
        if channel:
            messages = await channel.history(limit=limit).flatten()
            for message in messages:
                self.save_message(message.author.id, channel.id, message.content)

    async def fetch_and_save_forum_messages(self, forum_channel_id, limit=1000):
        forum_channel = self.bot.get_channel(forum_channel_id)
        if forum_channel:
            threads = await forum_channel.archived_threads(limit=None).flatten() + forum_channel.threads
            for thread in threads:
                messages = await thread.history(limit=limit).flatten()
                for message in messages:
                    self.save_message(message.author.id, thread.id, message.content)

    @tasks.loop(hours=12)  # 12時間ごとに実行
    async def fetch_messages_task(self):
        channel_ids = [1247421345705492530]  # 取得するチャンネルのID
        forum_channel_ids = [1024642680577331200]  # 取得するフォーラムのID
        for channel_id in channel_ids:
            await self.fetch_and_save_messages(channel_id)
        for forum_channel_id in forum_channel_ids:
            await self.fetch_and_save_forum_messages(forum_channel_id)

    @fetch_messages_task.before_loop
    async def before_fetch_messages_task(self):
        await self.bot.wait_until_ready()

    async def fetch_messages(self, forum_channel, user_id, limit=1000):
        messages = []
        threads = await forum_channel.archived_threads(limit=None).flatten() + forum_channel.threads
        for thread in threads:
            async for message in thread.history(limit=limit):
                if message.author.id == user_id:
                    messages.append(message)
        return messages

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        monitored_channel_id = 1247421345705492530
        history_forum = self.bot.get_channel(1024642680577331200)

        if message.channel.id != monitored_channel_id:
            return

        messages = await self.fetch_messages(history_forum, message.author.id)

        if messages:
            selected_message = random.choice(messages)
            webhook = await message.channel.create_webhook(name=message.author.display_name)

            await webhook.send(
                selected_message.content,
                username=selected_message.author.display_name,
                avatar_url=selected_message.author.avatar_url,
            )

            await webhook.delete()

async def setup(bot):
    await bot.add_cog(PastSelf(bot))
