import discord
import os
import psycopg2
import random
from discord.ext import tasks, commands
from discord.ext.commands import Bot

# 環境変数からデータベース情報を取得
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

class PastSelf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fetch_messages_task.start()

    @tasks.loop(hours=12)
    async def fetch_messages_task(self):
        # ここで対象チャンネルを指定
        history_channel_id = 1024642680577331200
        await self.fetch_and_save_messages(history_channel_id)

    async def fetch_and_save_messages(self, forum_channel_id):
        forum_channel = self.bot.get_channel(forum_channel_id)
        if not forum_channel:
            print(f"フォーラムチャンネルが見つかりません: {forum_channel_id}")
            return

        messages = []
        async for thread in forum_channel.threads:
            async for message in thread.history(limit=1000):
                messages.append(message)

        async for thread in forum_channel.archived_threads(limit=None):
            async for message in thread.history(limit=10000):
                messages.append(message)

        # データベースにメッセージを保存
        self.save_messages_to_db(messages)

    def save_messages_to_db(self, messages):
        try:
            connection = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            cursor = connection.cursor()

            for message in messages:
                cursor.execute("""
                    INSERT INTO messages (message_id, author_id, content, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (message_id) DO NOTHING;
                """, (message.id, message.author.id, message.content, message.created_at))

            connection.commit()
            cursor.close()
            connection.close()
        except Exception as e:
            print(f"データベースへの保存中にエラーが発生しました: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != 1247421345705492530:
            return

        if message.author == self.bot.user:
            return

        response_channel_id = 1024642680577331200
        response_channel = self.bot.get_channel(response_channel_id)
        if not response_channel:
            print(f"応答チャンネルが見つかりません: {response_channel_id}")
            return

        past_messages = self.fetch_messages_from_db(message.author.id)
        if not past_messages:
            await message.channel.send("過去のメッセージが見つかりませんでした。")
            return

        past_message = random.choice(past_messages)
        webhook = await self.get_webhook(response_channel)
        await webhook.send(
            past_message[2],  # content
            username=message.author.display_name,
            avatar_url=message.author.avatar.url
        )

    def fetch_messages_from_db(self, author_id):
        try:
            connection = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            cursor = connection.cursor()

            cursor.execute("""
                SELECT message_id, author_id, content, created_at
                FROM messages
                WHERE author_id = %s
                ORDER BY random()
                LIMIT 1000;
            """, (author_id,))
            messages = cursor.fetchall()
            cursor.close()
            connection.close()
            return messages
        except Exception as e:
            print(f"データベースからのメッセージ取得中にエラーが発生しました: {e}")
            return []

    async def get_webhook(self, channel):
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.user == self.bot.user:
                return webhook
        return await channel.create_webhook(name="PastSelfWebhook")

async def setup(bot):
    await bot.add_cog(PastSelf(bot))
