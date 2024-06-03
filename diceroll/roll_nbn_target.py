import random
import re
from .zenkaku_hankaku import zenkaku_to_hankaku

async def roll_nbn_target(match):
    try:
        command = match.group(0)

        # 正規表現で命令部分を抽出
        dice_expression = match.group(1)
        operator = match.group(2)
        target_value = int(match.group(3))
        extra_text = match.group(4).strip() if match.group(4) else ""

        # ダイスロールを評価
        rolls = eval_nbn_target_dice_expression(dice_expression)
        success = eval(f"{len([r for r in rolls if r >= target_value])} {operator} {target_value}")

        result = "成功" if success else "失敗"
        return f"{command}の結果: {rolls} -> {len([r for r in rolls if r >= target_value])} -> {result}"
    except Exception as e:
        return f"エラーが発生しました: {e}"

def eval_nbn_target_dice_expression(expression):
    tokens = re.split(r'(\d+[bB]\d+)', expression)
    tokens = [token.strip() for token in tokens if token.strip()]
    rolls = []

    def roll_dice(dice_notation):
        num, die = map(int, re.split(r'[bB]', dice_notation))
        return [random.randint(1, die) for _ in range(num)]

    for token in tokens:
        if re.match(r'\d+[bB]\d+', token):
            rolls.extend(roll_dice(token))

    return rolls
