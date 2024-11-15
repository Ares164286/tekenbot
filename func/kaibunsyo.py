import discord
import asyncpg
import os
from discord.ext import commands
from discord import app_commands

class Kaibunsyo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # チェック対象のカスタム絵文字IDと標準絵文字
        self.target_custom_emoji_ids = [1116539681606217799]  # カスタム絵文字IDを指定
        
        # チェック対象のテキストチャンネルIDとフォーラムチャンネルID
        self.target_channel_ids = [
            1150826225334505643,  # 新規用チャットルーム
        ]
        self.forum_channel_ids = [
            1024642680577331200,  # 雑談用フォーラム
            1174915955374174299,  # ゲーム用フォーラム
        ]

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        # カスタム絵文字の場合、IDが一致するかチェック
        if isinstance(reaction.emoji, discord.Emoji) and reaction.emoji.id in self.target_custom_emoji_ids:
            await self.save_message(reaction.message)
        # 標準絵文字の場合、名前が一致するかチェック
        elif isinstance(reaction.emoji, str) and reaction.emoji in self.target_standard_emojis:
            await self.save_message(reaction.message)

    async def save_message(self, message):
        """メッセージ内容と添付画像URLをデータベースに保存"""
        content = message.content
        attachments = [attachment.url for attachment in message.attachments]

        conn = None
        try:
            conn = await asyncpg.connect(
                user=os.getenv('PGUSER'),
                password=os.getenv('PGPASSWORD'),
                database="kaibunsyo",  # データベース「kaibunsyo」を指定
                host=os.getenv('PGHOST'),
                port=os.getenv('PGPORT')
            )

            await conn.execute('''
                INSERT INTO kaibunsyo (content, attachment_urls)
                VALUES ($1, $2)
            ''', content, attachments)

            await message.channel.send("怪文書として保存しました！")

        except asyncpg.PostgresError as e:
            print(f"データベースエラー: {e}")
        finally:
            if conn:
                await conn.close()

    @app_commands.command(name="check_past_reactions", description="過去のリアクション付きメッセージを検出して保存します")
    @app_commands.checks.has_permissions(administrator=True)
    async def check_past_reactions(self, interaction: discord.Interaction):
        """プログラム内で指定したチャンネルとフォーラム内のスレッドで、過去のリアクション付きメッセージを保存"""
        count = 0
        await interaction.response.send_message("指定されたチャンネルで過去のリアクションをチェックしています...", ephemeral=True)

        # 通常のテキストチャンネルを処理
        for channel_id in self.target_channel_ids:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                print(f"チャンネルID {channel_id} が見つかりませんでした。")
                continue

            count += await self.check_reactions_in_channel(channel)

        # フォーラムチャンネル内の各スレッドを処理
        for forum_id in self.forum_channel_ids:
            forum_channel = self.bot.get_channel(forum_id)
            if not forum_channel:
                print(f"フォーラムチャンネルID {forum_id} が見つかりませんでした。")
                continue

            if isinstance(forum_channel, discord.ForumChannel):
                for thread in forum_channel.threads:
                    count += await self.check_reactions_in_channel(thread)
            else:
                print(f"ID {forum_id} はフォーラムチャンネルではありません。")

        await interaction.followup.send(f"{count} 件のメッセージが保存されました。")

    async def check_reactions_in_channel(self, channel):
        """指定されたチャンネル内のリアクションをチェックして、指定の絵文字がついたメッセージを保存"""
        count = 0
        async for message in channel.history(limit=100):  # チェックするメッセージ数を調整可能
            for reaction in message.reactions:
                # カスタム絵文字の場合
                if isinstance(reaction.emoji, discord.Emoji) and reaction.emoji.id in self.target_custom_emoji_ids:
                    await self.save_message(message)
                    count += 1
                    break
                # 標準絵文字の場合
                elif isinstance(reaction.emoji, str) and reaction.emoji in self.target_standard_emojis:
                    await self.save_message(message)
                    count += 1
                    break
        return count

    @app_commands.command(name="怪文書", description="保存された怪文書をランダムに表示します")
    async def kaibunsyo(self, interaction: discord.Interaction):
        """データベースからランダムに怪文書を取得して表示"""
        conn = None
        try:
            conn = await asyncpg.connect(
                user=os.getenv('PGUSER'),
                password=os.getenv('PGPASSWORD'),
                database="kaibunsyo",  # データベース「kaibunsyo」を指定
                host=os.getenv('PGHOST'),
                port=os.getenv('PGPORT')
            )

            row = await conn.fetchrow('''
                SELECT content, attachment_urls
                FROM kaibunsyo
                ORDER BY random()
                LIMIT 1
            ''')

            if row:
                content = row['content']
                attachments = row['attachment_urls']
                message = content if content else "(メッセージなし)"
                if attachments:
                    message += "\n" + "\n".join(attachments)

                await interaction.response.send_message(message)
            else:
                await interaction.response.send_message("怪文書が保存されていません。", ephemeral=True)

        except asyncpg.PostgresError as e:
            print(f"データベースエラー: {e}")
            await interaction.response.send_message("怪文書の取得に失敗しました。", ephemeral=True)
        finally:
            if conn:
                await conn.close()

async def setup(bot):
    await bot.add_cog(Kaibunsyo(bot))
