import discord
import random
from discord.ext import commands

class PastSelf(commands.Cog):
    def __init__(self, bot, target_channel_id, history_limit):
        self.bot = bot
        self.target_channel_id = target_channel_id
        self.history_limit = history_limit  # 履歴の読み取り範囲を設定

    async def fetch_messages(self, channel, user_id):
        messages = []
        async for message in channel.history(limit=self.history_limit):
            if message.author.id == user_id:
                messages.append(message)
        return messages

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.target_channel_id or message.author.bot:
            return

        # Fetch messages from the target channel
        target_channel = self.bot.get_channel(self.target_channel_id)
        messages = await self.fetch_messages(target_channel, message.author.id)
        
        if not messages:
            return
        
        # Pick a random message
        random_message = random.choice(messages)

        # Create a webhook
        webhook = await message.channel.create_webhook(name=message.author.display_name)
        await webhook.send(random_message.content, username=message.author.display_name, avatar_url=message.author.avatar.url)
        await webhook.delete()

async def setup(bot):
    target_channel_id = 1247421345705492530  # 監視するチャンネルのIDを設定
    history_limit = 1000  # 読み取るメッセージの数を設定
    await bot.add_cog(PastSelf(bot, target_channel_id, history_limit))
