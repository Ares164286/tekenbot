import discord
from discord.ext import tasks, commands
import psycopg2
import os

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

class PastSelf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fetch_messages_task.start()

    @tasks.loop(hours=12)
    async def fetch_messages_task(self):
        history_channel_id = 1024642680577331200  # 履歴を保存するチャンネルのID
        await self.fetch_and_save_messages(history_channel_id)

    async def fetch_and_save_messages(self, channel_id):
        try:
            channel = self.bot.get_channel(channel_id)
            messages = []
            async for message in channel.history(limit=10000):
                messages.append(message)

            if messages:
                self.save_messages_to_db(messages)
        except Exception as e:
            print(f"メッセージ取得中にエラーが発生しました: {e}")

    def save_messages_to_db(self, messages):
        try:
            connection = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            cursor = connection.cursor()
            for message in messages:
                cursor.execute("""
                    INSERT INTO messages (message_id, author_id, content, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (message_id) DO NOTHING;
                """, (message.id, message.author.id, message.content, message.created_at))
            connection.commit()
            cursor.close()
            connection.close()
        except Exception as e:
            print(f"データベースへのメッセージ保存中にエラーが発生しました: {e}")

    async def fetch_messages(self, forum_channel, author_id):
        try:
            messages = []
            threads = [thread async for thread in forum_channel.archived_threads(limit=None)] + forum_channel.threads
            for thread in threads:
                async for message in thread.history(limit=10000):
                    if message.author.id == author_id:
                        messages.append(message)
            return messages
        except Exception as e:
            print(f"データベースからのメッセージ取得中にエラーが発生しました: {e}")
            return []

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        history_forum_id = 1024642680577331200
        history_forum = self.bot.get_channel(history_forum_id)
        if message.channel.id in [1245562745269780531, 1117864819442335824, 1117859740970651798, 1247166684121268266]:
            messages = await self.fetch_messages(history_forum, message.author.id)
            if messages:
                random_message = random.choice(messages)
                webhook = await message.channel.create_webhook(name=random_message.author.display_name)
                await webhook.send(random_message.content, username=random_message.author.display_name, avatar_url=random_message.author.avatar_url)
                await webhook.delete()

async def setup(bot):
    await bot.add_cog(PastSelf(bot))

# 手動でメッセージを保存するための関数
async def save_messages_to_db(channel_id):
    past_self = PastSelf(commands.Bot(command_prefix='/'))
    await past_self.fetch_and_save_messages(channel_id)
