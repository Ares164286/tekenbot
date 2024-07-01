import discord
import random
from discord.ext import commands

class PastSelf(commands.Cog):
    def __init__(self, bot, target_channel_id, history_forum_id, exclude_thread_ids=None, history_limit=1000):
        self.bot = bot
        self.target_channel_id = target_channel_id
        self.history_forum_id = history_forum_id
        self.exclude_thread_ids = exclude_thread_ids or []
        self.history_limit = history_limit  # 履歴の読み取り範囲を設定

    async def fetch_messages(self, forum_channel, user_id):
        messages = []
        async for thread in forum_channel.threads:
            if thread.id in self.exclude_thread_ids:
                continue
            async for message in thread.history(limit=self.history_limit):
                if message.author.id == user_id:
                    messages.append(message)
        return messages

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.target_channel_id or message.author.bot:
            return

        # Fetch messages from the history forum
        history_forum = self.bot.get_channel(self.history_forum_id)
        if not history_forum:
            await message.channel.send("指定された履歴フォーラムが見つかりません。")
            return

        if not isinstance(history_forum, discord.ForumChannel):
            await message.channel.send("指定された履歴チャンネルはフォーラムではありません。")
            return

        messages = await self.fetch_messages(history_forum, message.author.id)
        
        if not messages:
            await message.channel.send("指定されたフォーラムに該当するユーザーのメッセージが見つかりませんでした。")
            return
        
        # Pick a random message
        random_message = random.choice(messages)

        # Create a webhook
        webhook = await message.channel.create_webhook(name=message.author.display_name)
        await webhook.send(random_message.content, username=message.author.display_name, avatar_url=message.author.avatar.url)
        await webhook.delete()

async def setup(bot):
    target_channel_id = 1247421345705492530  # 監視するチャンネルのIDを設定
    history_forum_id = 1024642680577331200  # 過去のメッセージを読み取るフォーラムチャンネルのIDを設定
    exclude_thread_ids = [123456789012345678, 987654321098765432]  # 除外するスレッドのIDを設定
    history_limit = 1000  # 読み取るメッセージの数を設定
    await bot.add_cog(PastSelf(bot, target_channel_id, history_forum_id, exclude_thread_ids, history_limit))
