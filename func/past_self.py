import discord
import asyncpg
import os
from discord.ext import commands

class PastSelf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.watch_channel_id = 1247421345705492530  # 監視するチャンネルID

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.watch_channel_id or message.author.bot:
            return

        try:
            user_message = await self.get_random_user_message(message.author.id)
            if user_message:
                webhook = await self.get_webhook(message.channel)
                if webhook:
                    member = message.guild.get_member(message.author.id)
                    avatar_url = member.display_avatar.url if member else None
                    await webhook.send(
                        content=user_message["content"],
                        username=member.display_name if member else message.author.display_name,
                        avatar_url=avatar_url
                    )
        except Exception as e:
            print(f"メッセージ送信中にエラーが発生しました: {e}")

    async def get_random_user_message(self, author_id):
        conn = None
        try:
            conn = await asyncpg.connect(
                user=os.getenv('PGUSER'),
                password=os.getenv('PGPASSWORD'),
                database=os.getenv('PGDATABASE'),
                host=os.getenv('PGHOST'),
                port=os.getenv('PGPORT')
            )

            message = await conn.fetchrow('''
                SELECT content
                FROM messages
                WHERE author_id = $1
                ORDER BY random()
                LIMIT 1
            ''', author_id)

            return message

        except asyncpg.PostgresError as e:
            print(f"データベース接続中にエラーが発生しました: {e}")
            return None
        finally:
            if conn:
                await conn.close()

    async def get_webhook(self, channel):
        try:
            webhooks = await channel.webhooks()
            if webhooks:
                return webhooks[0]

            webhook = await channel.create_webhook(name="PastSelfBot")
            return webhook

        except discord.DiscordException as e:
            print(f"Webhook操作中にエラーが発生しました: {e}")
            return None

async def setup(bot):
    await bot.add_cog(PastSelf(bot))
    print("PastSelf cog has been loaded")
