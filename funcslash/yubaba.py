import discord
from discord.ext import commands

class yubaba(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="湯婆婆", description="ユーザーの表示名を変更します。")
    async def yubaba(self, interaction: discord.Interaction, user: discord.Member, new_name: str):
        old_name = user.display_name
        try:
            await user.edit(nick=new_name)
            await interaction.response.send_message(f'「{old_name}」？贅沢な名だねぇ。今からお前の名は「{new_name}」だ')
        except discord.Forbidden:
            await interaction.response.send_message("表示名を変更する権限がありません。")
        except discord.HTTPException as e:
            await interaction.response.send_message(f"表示名の変更中にHTTPエラーが発生しました: {e.status} - {e.text}")
        except Exception as e:
            await interaction.response.send_message(f"表示名の変更中に予期しないエラーが発生しました: {e}")

async def setup(bot):
    await bot.add_cog(yubaba(bot))
