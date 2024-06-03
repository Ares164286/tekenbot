import random

def roll_dice(sides, times):
    return sum(random.randint(1, sides) for _ in range(times))

def calculate_db(str_val, siz_val):
    total = str_val + siz_val
    if total <= 64:
        return "-2"
    elif total <= 84:
        return "-1"
    elif total <= 124:
        return "0"
    elif total <= 164:
        return "+1d4"
    elif total <= 204:
        return "+1d6"
    else:
        return "+2d6"

def generate_stats_7e():
    stats = {
        "STR": roll_dice(6, 3) * 5,
        "CON": roll_dice(6, 3) * 5,
        "POW": roll_dice(6, 3) * 5,
        "DEX": roll_dice(6, 3) * 5,
        "APP": roll_dice(6, 3) * 5,
        "SIZ": (roll_dice(6, 2) + 6) * 5,
        "INT": (roll_dice(6, 2) + 6) * 5,
        "EDU": (roll_dice(6, 3) + 3) * 5
    }

    stats["HP"] = (stats["CON"] + stats["SIZ"]) // 10
    stats["MP"] = stats["POW"] // 5
    stats["SAN"] = stats["POW"]
    stats["IDE"] = stats["INT"]
    stats["LUK"] = roll_dice(6, 3) * 5  # 7版ではLUKもランダムに決定
    stats["KNO"] = stats["EDU"]
    stats["DB"] = calculate_db(stats["STR"], stats["SIZ"])

    return stats

async def send_stats_7e(ctx, times=1):
    result_messages = []
    for _ in range(times):
        stats = generate_stats_7e()
        stats_message = f"STR:{stats['STR']} CON:{stats['CON']} POW:{stats['POW']} DEX:{stats['DEX']} APP:{stats['APP']} SIZ:{stats['SIZ']} INT:{stats['INT']} EDU:{stats['EDU']}\n"
        details_message = f"[HP:{stats['HP']} MP:{stats['MP']} SAN:{stats['SAN']} IDE:{stats['IDE']} LUK:{stats['LUK']} KNO:{stats['KNO']} DB:{stats['DB']}]"
        result_messages.append(stats_message + details_message)

    await ctx.send("\n\n".join(result_messages))
