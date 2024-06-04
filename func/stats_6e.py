import discord
import random

async def send_stats(ctx, num: int = 1):
    for _ in range(num):
        stats = {
            "STR": random.randint(3, 18),
            "CON": random.randint(3, 18),
            "POW": random.randint(3, 18),
            "DEX": random.randint(3, 18),
            "APP": random.randint(3, 18),
            "SIZ": random.randint(8, 18),
            "INT": random.randint(8, 18),
            "EDU": random.randint(6, 21)
        }
    hp = (stats["CON"] + stats["SIZ"]) // 2
    mp = stats["POW"]
    san = stats["POW"] * 5
    ide = stats["INT"] * 5
    luk = stats["POW"] * 5
    kno = stats["EDU"] * 5
    db = stats["STR"] + stats["SIZ"]

    if db <= 12:
        db = "-1d6"
    elif db <= 16:
        db = "-1d4"
    elif db <= 24:
        db = "0"
    elif db <= 32:
        db = "+1d4"
    else:
        db = "+1d6"

    result = (
        f"STR:{stats['STR']} CON:{stats['CON']} POW:{stats['POW']} "
        f"DEX:{stats['DEX']} APP:{stats['APP']} SIZ:{stats['SIZ']} "
        f"INT:{stats['INT']} EDU:{stats['EDU']}\n"
        f"[HP:{hp} MP:{mp} SAN:{san} IDE:{ide} LUK:{luk} KNO:{kno} DB:{db}]"
    )
    await ctx.send(result)
