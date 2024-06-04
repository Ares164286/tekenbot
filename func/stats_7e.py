import discord
import random

def roll_dice(sides, rolls):
    return [random.randint(1, sides) for _ in range(rolls)]

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
            "STR": sum(roll_dice(6, 3)) * 5,
            "CON": sum(roll_dice(6, 3)) * 5,
            "POW": sum(roll_dice(6, 3)) * 5,
            "DEX": sum(roll_dice(6, 3)) * 5,
            "APP": sum(roll_dice(6, 3)) * 5,
            "SIZ": (sum(roll_dice(6, 2)) + 6) * 5,
            "INT": (sum(roll_dice(6, 2)) + 6) * 5,
            "EDU": (sum(roll_dice(6, 3)) + 3) * 5
        }
        hp = (stats["CON"] + stats["SIZ"]) // 10
        mp = stats["POW"] // 5
        san = stats["POW"]
        ide = stats["INT"]
        luk = stats["POW"]
        kno = stats["EDU"]
        db = (stats["STR"] + stats["SIZ"]) // 10

        if db <= 64:
            db = "-1d6"
        elif db <= 84:
            db = "-1d4"
        elif db <= 124:
            db = "0"
        elif db <= 164:
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
