import discord
import asyncpg
import os
from discord.ext import commands

class EchoPastMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 監視対象のチャンネルID（例: 置き換えて使用）
        self.watch_channel_id = 1305836459256840273

    @commands.Cog.listener()
    async def on_message(self, message):
        # 自分自身やボットのメッセージ、監視対象外のチャンネルは無視
        if message.author.bot or message.channel.id != self.watch_channel_id:
            return

        # メッセージに基づいて過去のメッセージを検索
        past_message = await self.find_past_message(message.content)
        if past_message:
            # 過去のメッセージを発言者の名前で再送信
            await message.channel.send(
                content=past_message['content'],
                username=past_message['author_name'],
                avatar_url=past_message['author_avatar'] or message.guild.icon.url if message.guild.icon else None
            )

    async def find_past_message(self, content):
        """
        ユーザーのメッセージを部分一致で検索して、過去のメッセージから類似するものを取得する。
        """
        conn = None
        try:
            # データベースに接続
            conn = await asyncpg.connect(
                user=os.getenv('PGUSER'),
                password=os.getenv('PGPASSWORD'),
                database=os.getenv('PGDATABASE'),
                host=os.getenv('PGHOST'),
                port=os.getenv('PGPORT')
            )

            # メッセージに含まれる単語で部分一致検索
            query = '''
                SELECT content, author_id
                FROM messages
                WHERE content ILIKE $1
                ORDER BY random()
                LIMIT 1
            '''
            result = await conn.fetchrow(query, f"%{content}%")

            if result:
                # 発言者情報を取得
                author_id = result['author_id']
                content = result['content']

                # ボットのクライアントからメンバー情報を取得
                author = await self.bot.fetch_user(author_id)
                return {
                    'content': content,
                    'author_name': author.display_name,
                    'author_avatar': author.avatar.url if author.avatar else None
                }

        except asyncpg.PostgresError as e:
            print(f"データベースエラー: {e}")

        finally:
            if conn:
                await conn.close()

        return None

async def setup(bot):
    await bot.add_cog(EchoPastMessage(bot))
    print("EchoPastMessage cog が読み込まれました")
