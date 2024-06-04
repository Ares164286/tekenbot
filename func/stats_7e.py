import discord
import random

async def send_stats_7e(ctx, *args):
    num = 1  # デフォルトの生成回数
    if args:
        try:
            num = int(args[0])
        except ValueError:
            await ctx.send("回数は整数で指定してください。")
            return

    results = []
    for _ in range(num):
        stats = {
            "STR": random.randint(15, 90) // 5 * 5,
            "CON": random.randint(15, 90) // 5 * 5,
            "POW": random.randint(15, 90) // 5 * 5,
            "DEX": random.randint(15, 90) // 5 * 5,
            "APP": random.randint(15, 90) // 5 * 5,
            "SIZ": (random.randint(40, 90) // 5 * 5) + 30,
            "INT": (random.randint(40, 90) // 5 * 5) + 30,
            "EDU": (random.randint(50, 99) // 5 * 5) + 30
        }
        hp = (stats["CON"] + stats["SIZ"]) // 10
        mp = stats["POW"] // 5
        san = stats["POW"]
        ide = stats["INT"]
        luk = stats["POW"]
        kno = stats["EDU"]
        db = (stats["STR"] + stats["SIZ"]) // 10

        if db <= 8:
            db = "-1d6"
        elif db <= 12:
            db = "-1d4"
        elif db <= 16:
            db = "0"
        elif db <= 24:
            db = "+1d4"
        else:
            db = "+1d6"

        result = (
            f"STR:{stats['STR']} CON:{stats['CON']} POW:{stats['POW']} "
            f"DEX:{stats['DEX']} APP:{stats['APP']} SIZ:{stats['SIZ']} "
            f"INT:{stats['INT']} EDU:{stats['EDU']}\n"
            f"[HP:{hp} MP:{mp} SAN:{san} IDE:{ide} LUK:{luk} KNO:{kno} DB:{db}]"
        )
        results.append(result)
    await ctx.send("\n\n".join(results))
