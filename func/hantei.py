import discord
import random

async def hantei(ctx, *, message: str):
    responses = ["◎", "◯", "△", "✕"]
    response = random.choice(responses)
    await ctx.send(response)
