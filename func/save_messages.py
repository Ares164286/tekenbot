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
            # 追加のチャンネルID
        ]
        self.fetch_messages_task.start()

    @tasks.loop(hours=12)
    async def fetch_messages_task(self):
        for channel_id in self.history_channel_ids:
            await self.fetch_and_save_messages(channel_id)

    @commands.command(name="save_history_cmd")
    async def save_history_cmd(self, ctx):
        for channel_id in self.history_channel_ids:
            await self.fetch_and_save_messages(channel_id)
        await ctx.send("履歴が保存されました！")

    async def fetch_and_save_messages(self, channel_id):
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                print(f"チャンネルが見つかりません: {channel_id}")
                return

            if isinstance(channel, discord.ForumChannel):
                threads = channel.threads  # () を付けずリストとして取得

                blacklisted_thread_ids = [123456789012345678, 987654321098765432]  # ブラックリストのスレッドID

                for thread in threads:
                    # スレッドIDがブラックリストに含まれている場合はスキップ
                    if thread.id in blacklisted_thread_ids:
                        print(f"スレッド {thread.name} はブラックリストに含まれているためスキップします")
                        continue
                    
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
            print(f"{len(messages)} 件のメッセージが保存されました - チャンネル: {channel.name}")

        except Exception as e:
            print(f"メッセージ取得エラー - チャンネル: {channel.name} エラー: {e}")

    async def fetch_and_save_thread_messages(self, thread):
        try:
            messages = []
            async for message in thread.history(limit=10000):
                messages.append((message.id, message.author.id, message.content))

            await self.save_messages_to_db(messages)
            print(f"{len(messages)} 件のメッセージが保存されました - スレッド: {thread.name}")

        except Exception as e:
            print(f"メッセージ取得エラー - スレッド: {thread.name} エラー: {e}")

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

            async with conn.transaction():
                await conn.executemany('''
                    INSERT INTO messages (message_id, author_id, content)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (message_id) DO NOTHING
                ''', messages)

            print("メッセージがデータベースに保存されました")

        except asyncpg.PostgresError as e:
            print(f"データベースエラー: {e}")
        finally:
            if conn:
                await conn.close()

async def setup(bot):
    await bot.add_cog(SaveMessages(bot))
    print("SaveMessages cog が読み込まれました")
