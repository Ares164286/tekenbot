import discord
import asyncpg
import os
from discord.ext import tasks, commands

class SaveMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.history_channel_ids = [
            1024642680577331200,  # 雑談用フォーラム
            1150826225334505643,  # 新規用チャットルーム
            # 他のチャンネルIDを追加
        ]
        self.fetch_messages_task.start()

    @tasks.loop(hours=12)
    async def fetch_messages_task(self):
        for channel_id in self.history_channel_ids:
            await self.fetch_and_save_messages(channel_id)

    @commands.command(name="履歴を保存")
    async def save_history_cmd(self, ctx):
        for channel_id in self.history_channel_ids:
            await self.fetch_and_save_messages(channel_id)
        await ctx.send("メッセージ履歴の保存が完了しました。")

    async def fetch_and_save_messages(self, channel_id):
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                print(f"チャンネルが見つかりません: {channel_id}")
                return

            if isinstance(channel, discord.ForumChannel):
                threads = await self.fetch_all_threads(channel)
                for thread in threads:
                    await self.fetch_and_save_thread_messages(thread)
            else:
                await self.fetch_and_save_channel_messages(channel)

        except Exception as e:
            print(f"メッセージ取得中にエラーが発生しました: {e}")

    async def fetch_and_save_channel_messages(self, channel):
        try:
            messages = []
            async for message in channel.history(limit=10000):
                messages.append((message.id, message.author.id, message.content))

            await self.save_messages_to_db(messages)
            print(f"メッセージを保存しました: {len(messages)}件 - チャンネル: {channel.name}")
        except Exception as e:
            print(f"チャンネル {channel.name} からのメッセージ取得中にエラーが発生しました: {e}")

    async def fetch_and_save_thread_messages(self, thread):
        try:
            messages = []
            async for message in thread.history(limit=10000):
                messages.append((message.id, message.author.id, message.content))

            await self.save_messages_to_db(messages)
            print(f"メッセージを保存しました: {len(messages)}件 - スレッド: {thread.name}")
        except Exception as e:
            print(f"スレッド {thread.name} からのメッセージ取得中にエラーが発生しました: {e}")

    async def fetch_all_threads(self, forum_channel):
        try:
            threads = [thread async for thread in forum_channel.threads]
            archived_threads = [thread async for thread in forum_channel.archived_threads(limit=None)]
            return threads + archived_threads
        except Exception as e:
            print(f"フォーラムチャンネル {forum_channel.name} からのスレッド取得中にエラーが発生しました: {e}")
            return []

    async def save_messages_to_db(self, messages):
        conn = None
        try:
            conn = await asyncpg.connect(
                user=os.getenv('PGUSER'),
                password=os.getenv('PGPASSWORD'),
                database=os.getenv('PGDATABASE'),
                host=os.getenv('PGHOST'),
                port=os.getenv('PGPORT')
            )

            # テーブルが存在しない場合に作成する
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    message_id BIGINT PRIMARY KEY,
                    author_id BIGINT,
                    content TEXT
                )
            ''')

            async with conn.transaction():
                await conn.executemany('''
                    INSERT INTO messages(message_id, author_id, content)
                    VALUES($1, $2, $3)
                    ON CONFLICT (message_id) DO NOTHING
                ''', messages)

            print("メッセージの保存が完了しました")
        except asyncpg.PostgresError as e:
            print(f"データベース保存中にエラーが発生しました: {e}")
        finally:
            if conn:
                await conn.close()

async def setup(bot):
    await bot.add_cog(SaveMessages(bot))
    print("SaveMessages cog has been loaded")
