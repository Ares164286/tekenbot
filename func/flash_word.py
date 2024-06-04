import discord
import random

hiragana_list = [
    "あ", "い", "う", "え", "お",
    "か", "き", "く", "け", "こ",
    "さ", "し", "す", "せ", "そ",
    "た", "ち", "つ", "て", "と",
    "な", "に", "ぬ", "ね", "の",
    "は", "ひ", "ふ", "へ", "ほ",
    "ま", "み", "む", "め", "も",
    "や", "ゆ", "よ",
    "ら", "り", "る", "れ", "ろ",
    "わ"
]

async def flash_word(ctx, *args):
    num_times = 1  # デフォルトの出力回数
    if args:
        try:
            num_times = int(args[0])
        except ValueError:
            await ctx.send("回数は整数で指定してください。")
            return

    results = []
    for _ in range(num_times):
        character = random.choice(hiragana_list)
        number = random.randint(2, 7)
        result = f"「{character}」{number}"
        results.append(result)

    await ctx.send("\n".join(results))
