import discord
import asyncpg
import os
from discord.ext import commands

class EchoPastMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 監視対象のフォーラムチャンネルおよび通常のテキストチャンネルIDのリスト
        self.watch_channel_ids = [
            1305836459256840273,  # テストチャンネル
            1306102576143532132,  # 例: チャンネルID2（テキストチャンネル）
        ]
        # WebhookのURLを環境変数から取得（スレッド用）
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')  # 環境変数で指定

    @commands.Cog.listener()
    async def on_message(self, message):
        # 自分自身やボットのメッセージを無視
        if message.author.bot:
            return

        # スレッド内のメッセージが親フォーラムチャンネルに含まれるか、通常のテキストチャンネルに含まれるか確認
        if isinstance(message.channel, discord.Thread):
            if message.channel.parent_id not in self.watch_channel_ids:
                return
            channel_type = 'スレッド'
        elif message.channel.id in self.watch_channel_ids:
            channel_type = '通常のテキストチャンネル'
        else:
            return  # 監視対象外のチャンネルには反応しない

        print(f"{channel_type}内のメッセージを検出しました: {message.content}")

        # メッセージに基づいて過去のメッセージを検索
        try:
            past_message = await self.find_past_message(message.content)
            if past_message:
                if channel_type == 'スレッド':
                    # Webhookを使用してスレッドにメッセージを送信
                    webhook = discord.Webhook.from_url(self.webhook_url, adapter=discord.RequestsWebhookAdapter())
                    await webhook.send(
                        content=past_message['content'],
                        username=past_message['author_name'],
                        avatar_url=past_message['author_avatar'],
                        thread=message.channel  # スレッドに送信
                    )
                else:
                    # 通常のテキストチャンネルに直接メッセージを送信
                    await message.channel.send(
                        content=past_message['content']
                    )
        except Exception as e:
            print(f"エラーハンドリング: メッセージ送信中にエラーが発生しました: {e}")
            await message.channel.send("エラーが発生しました。もう一度お試しください。")

    async def find_past_message(self, content):
        """
        ユーザーのメッセージを部分一致で検索して、過去のメッセージから類似するものを取得する。
        発言者がBotの場合は検索から除外します。
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

            # Botのメッセージを除外しつつ、メッセージに含まれる単語で部分一致検索
            query = '''
                SELECT content, author_id
                FROM messages
                WHERE content ILIKE $1
                AND author_id != $2
                ORDER BY random()
                LIMIT 1
            '''
            result = await conn.fetchrow(query, f"%{content}%", self.bot.user.id)

            if result:
                # 発言者情報を取得
                author_id = result['author_id']
                content = result['content']

                try:
                    # ボットのクライアントからメンバー情報を取得
                    author = await self.bot.fetch_user(author_id)
                    return {
                        'content': content,
                        'author_name': author.display_name,
                        'author_avatar': author.avatar.url if author.avatar else None
                    }
                except discord.DiscordException as e:
                    print(f"Discord APIエラー: ユーザー情報の取得中にエラーが発生しました: {e}")
                    return None

        except asyncpg.PostgresError as e:
            print(f"データベースエラー: {e}")

        finally:
            if conn:
                await conn.close()

        return None

    async def get_webhook(self, channel):
        """
        通常のチャンネル用: チャンネルにWebhookがなければ作成し、既存のものがあればそれを返す。
        """
        try:
            webhooks = await channel.webhooks()
            if webhooks:
                return webhooks[0]
            # Webhookがなければ新規作成
            return await channel.create_webhook(name="EchoPastMessageWebhook")

        except discord.DiscordException as e:
            print(f"Webhook エラー: {e}")
            return None

async def setup(bot):
    await bot.add_cog(EchoPastMessage(bot))
    print("EchoPastMessage cog が読み込まれました")
