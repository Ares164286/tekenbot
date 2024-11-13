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
        
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')  # 環境変数で指定

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.Thread):
            if message.channel.parent_id not in self.watch_channel_ids:
                return
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
            # 最大10回まで他のユーザーのメッセージを探す
            attempts = 0
            past_message = await self.find_past_message(message)
            while past_message and past_message['author_id'] == message.author.id:
                print("発言者自身のメッセージが見つかったため、次のメッセージを探します。")
                past_message = await self.find_past_message(message)
                attempts += 1
                if attempts >= 10:
                    print("他のユーザーのメッセージが見つからなかったため、返信を打ち切ります。")
                    past_message = None
                    break

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

    async def find_past_message(self, message):
        content = message.content
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

                # サーバー内のニックネームを取得
                author = message.guild.get_member(author_id)
                if author:
                    author_name = author.display_name  # ニックネームまたはデフォルトの表示名
                    author_avatar = author.avatar.url if author.avatar else None
                    return {
                        'content': content,
                        'author_id': author_id,
                        'author_name': author_name,
                        'author_avatar': author_avatar
                    }
                else:
                    print("指定されたメンバーが見つかりません。")
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
