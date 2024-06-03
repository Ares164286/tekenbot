import discord
from discord import app_commands
from discord.ext import commands

class ActivityReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="活動報告", description="活動報告を規格化します")
    @app_commands.describe(
        datetime="活動日時を入力してください",
        system="使用したシステムを入力してください",
        scenario="シナリオ名を入力してください",
        participants="参加人数を入力してください",
        format="実施形式を入力してください",
        other="その他の情報を入力してください"
    )
    async def activity_report(self, interaction: discord.Interaction, datetime: str, system: str, scenario: str, participants: int, format: str, other: str = "なし"):
        report = f"日　　時：{datetime}\nシステム：{system}\nシナリオ：{scenario}\n参加人数：{participants}\n実施形式：{format}\nその他：{other}"
        await interaction.response.send_message(report)

async def setup(bot):
    await bot.add_cog(ActivityReport(bot))
