import discord
import asyncio
import random
from discord import app_commands
from discord.ext import commands

class wakeup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="起きろ", description="指定したユーザーに起きるようメンションします")
    @app_commands.describe(member="メンションするユーザー")
    async def wakeup(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f'{member.mention} 起きろ！')
        for _ in range(9):
            await interaction.followup.send(f'{member.mention} 起きろ！')
            await asyncio.sleep(random.uniform(0.5, 2))

async def setup(bot):
    await bot.add_cog(wakeup(bot))
