import random

async def hantei(ctx, *args):
    results = ["◎", "◯", "△", "✕"]
    result = random.choice(results)
    await ctx.send(result)
