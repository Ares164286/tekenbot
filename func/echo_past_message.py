import discord
import asyncpg
import os
from discord.ext import commands

class EchoPastMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 監視対象のフォーラムチャンネルおよび通常のテキストチャンネルIDのリスト
        self.watch_channel_ids = [
            1305836459256840273,  # 例: フォーラムチャンネルID1
            1024642680577331200,  # 例: テキストチャンネルID
        ]
        # 返信を許可するスレッドIDのリスト
        self.allowed_thread_ids = [
            1306102576143532132,  # 例: スレッドID1
            # 必要に応じてスレッドIDを追加
        ]
        # WebhookのURLを環境変数から取得（スレッド用）
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')  # 環境変数で指定

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # スレッド内のメッセージが指定されたスレッドIDであるか確認
        if isinstance(message.channel, discord.Thread):
            # スレッドIDが許可リストにない場合は返信しない
            if message.channel.id not in self.allowed_thread_ids:
                print(f"スレッド {message.channel.id} は許可されていないため、返信をスキップします。")
                return
            channel_type = 'スレッド'
        elif message.channel.id in self.watch_channel_ids:
            channel_type = '通常のテキストチャンネル'
        else:
            return

        print(f"{channel_type}内のメッセージを検出しました: {message.content}")

        try:
            past_message = await self.find_past_message(message.content)
            if past_message:
                webhook = None
                if channel_type == 'スレッド':
                    webhook = await self.get_webhook(message.channel.parent)
                else:
                    webhook = await self.get_webhook(message.channel)

                if webhook is not None:
                    await webhook.send(
                        content=past_message['content'],
                        username=past_message['author_name'],
                        avatar_url=past_message['author_avatar'],
                        thread=message.channel if channel_type == 'スレッド' else None
                    )
                else:
                    print("Webhookが取得できなかったため、メッセージ送信をスキップしました。")
        except Exception as e:
            print(f"エラーハンドリング: メッセージ送信中にエラーが発生しました: {e}")
            await message.channel.send("エラーが発生しました。もう一度お試しください。")

    async def find_past_message(self, content):
        conn = None
        try:
            conn = await asyncpg.connect(
                user=os.getenv('PGUSER'),
                password=os.getenv('PGPASSWORD'),
                database=os.getenv('PGDATABASE'),
                host=os.getenv('PGHOST'),
                port=os.getenv('PGPORT')
            )

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
                author_id = result['author_id']
                content = result['content']

                try:
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
        try:
            webhooks = await channel.webhooks()
            if webhooks:
                return webhooks[0]
            return await channel.create_webhook(name="EchoPastMessageWebhook")

        except discord.Forbidden:
            print("Webhook エラー: Webhookを作成する権限がありません。")
            return None
        except discord.DiscordException as e:
            print(f"Webhook エラー: {e}")
            return None

async def setup(bot):
    await bot.add_cog(EchoPastMessage(bot))
    print("EchoPastMessage cog が読み込まれました")
