import discord
from discord import app_commands
from discord.ext import tasks, commands
import asyncpg
import os

class SaveMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.history_channel_ids = [
            1024642680577331200,  # 雑談用フォーラム
            1150826225334505643,  # 新規用チャットルーム
            # 必要に応じて追加のチャンネルID
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
                threads = channel.threads
                blacklisted_thread_ids = [
                    1047822747398578207, 1168424579081961504, 1243545403371028480,
                    1149004841499234404, 1053007770103853199, 1033414785913589772,
                    1033359573039452300, 1029382666149187624, 1174711755834933368,
                    1306102576143532132
                ]
                for thread in threads:
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
            skip_count = 0  # スキップしたメッセージの数をカウント
            async for message in channel.history(limit=1000000):
                # メンションが含まれているメッセージは保存しない
                if message.mentions or message.role_mentions:
                    skip_count += 1
                    continue

                messages.append((message.id, message.author.id, message.content))

            await self.save_messages_to_db(messages)
            print(f"{len(messages)} 件のメッセージが保存されました - チャンネル: {channel.name}")
            print(f"{skip_count} 件のメッセージがメンションを含むためスキップされました - チャンネル: {channel.name}")

        except Exception as e:
            print(f"メッセージ取得エラー - チャンネル: {channel.name} エラー: {e}")

    async def fetch_and_save_thread_messages(self, thread):
        try:
            messages = []
            skip_count = 0  # スキップしたメッセージの数をカウント
            async for message in thread.history(limit=1000000):
                # メンションが含まれているメッセージは保存しない
                if message.mentions or message.role_mentions:
                    skip_count += 1
                    continue

                messages.append((message.id, message.author.id, message.content))

            await self.save_messages_to_db(messages)
            print(f"{len(messages)} 件のメッセージが保存されました - スレッド: {thread.name}")
            print(f"{skip_count} 件のメッセージがメンションを含むためスキップされました - スレッド: {thread.name}")

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

    @app_commands.command(name="reset_database", description="データベースを完全リセットします")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_database(self, interaction: discord.Interaction):
        conn = None
        try:
            conn = await asyncpg.connect(
                user=os.getenv('PGUSER'),
                password=os.getenv('PGPASSWORD'),
                database=os.getenv('PGDATABASE'),
                host=os.getenv('PGHOST'),
                port=os.getenv('PGPORT')
            )

            await conn.execute('TRUNCATE TABLE messages RESTART IDENTITY')
            await interaction.response.send_message("データベースがリセットされました。すべてのメッセージが削除されました。", ephemeral=True)

        except asyncpg.PostgresError as e:
            await interaction.response.send_message(f"データベースのリセット中にエラーが発生しました: {e}", ephemeral=True)
        finally:
            if conn:
                await conn.close()

    @reset_database.error
    async def reset_database_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("このコマンドを実行する権限がありません。", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SaveMessages(bot))
