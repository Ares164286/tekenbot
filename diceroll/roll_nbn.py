import random
import re
from .zenkaku_hankaku import zenkaku_to_hankaku

async def roll_nbn(match):
    try:
        command = match.group(0)

        # 正規表現で命令部分を抽出
        dice_expression = match.group(1)
        extra_text = match.group(2).strip() if match.group(2) else ""

        # ダイスロールを評価
        details = eval_nbn_dice_expression(dice_expression)

        return f"{command}の結果: {details}"
    except Exception as e:
        return f"エラーが発生しました: {e}"

def eval_nbn_dice_expression(expression):
    tokens = re.split(r'(\d+[bB]\d+)', expression)
    tokens = [token.strip() for token in tokens if token.strip()]
    details = []

    def roll_dice(dice_notation):
        num, die = map(int, re.split(r'[bB]', dice_notation))
        rolls = [random.randint(1, die) for _ in range(num)]
        return rolls

    for token in tokens:
        if re.match(r'\d+[bB]\d+', token):
            rolls = roll_dice(token)
            details.append(f"[{', '.join(map(str, rolls))}]")

    return ' '.join(details)
