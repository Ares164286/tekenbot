import discord
import random

def roll_dice(sides, rolls):
    return [random.randint(1, sides) for _ in range(rolls)]

async def send_stats(ctx, *args):
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
            "STR": sum(roll_dice(6, 3)),
            "CON": sum(roll_dice(6, 3)),
            "POW": sum(roll_dice(6, 3)),
            "DEX": sum(roll_dice(6, 3)),
            "APP": sum(roll_dice(6, 3)),
            "SIZ": sum(roll_dice(6, 2)) + 6,
            "INT": sum(roll_dice(6, 2)) + 6,
            "EDU": sum(roll_dice(6, 3))
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
        results.append(result)
    await ctx.send("\n\n".join(results))
