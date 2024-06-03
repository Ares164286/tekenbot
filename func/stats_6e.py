import random

def roll_dice(sides, times):
    return sum(random.randint(1, sides) for _ in range(times))

def calculate_db(str_val, siz_val):
    total = str_val + siz_val
    if total <= 12:
        return "-1d6"
    elif total <= 16:
        return "-1d4"
    elif total <= 24:
        return "0"
    elif total <= 32:
        return "+1d4"
    elif total <= 40:
        return "+1d6"
    else:
        return "+2d6"

def generate_stats():
    stats = {
        "STR": roll_dice(6, 3),
        "CON": roll_dice(6, 3),
        "POW": roll_dice(6, 3),
        "DEX": roll_dice(6, 3),
        "APP": roll_dice(6, 3),
        "SIZ": roll_dice(6, 2) + 6,
        "INT": roll_dice(6, 2) + 6,
        "EDU": roll_dice(6, 3) + 3
    }

    stats["HP"] = (stats["CON"] + stats["SIZ"]) // 2
    stats["MP"] = stats["POW"]
    stats["SAN"] = stats["POW"] * 5
    stats["IDE"] = stats["INT"] * 5
    stats["LUK"] = stats["POW"] * 5
    stats["KNO"] = stats["EDU"] * 5
    stats["DB"] = calculate_db(stats["STR"], stats["SIZ"])

    return stats

async def send_stats(ctx, times=1):
    result_messages = []
    for _ in range(times):
        stats = generate_stats()
        stats_message = f"STR:{stats['STR']} CON:{stats['CON']} POW:{stats['POW']} DEX:{stats['DEX']} APP:{stats['APP']} SIZ:{stats['SIZ']} INT:{stats['INT']} EDU:{stats['EDU']}\n"
        details_message = f"[HP:{stats['HP']} MP:{stats['MP']} SAN:{stats['SAN']} IDE:{stats['IDE']} LUK:{stats['LUK']} KNO:{stats['KNO']} DB:{stats['DB']}]"
        result_messages.append(stats_message + details_message)

    await ctx.send("\n\n".join(result_messages))
