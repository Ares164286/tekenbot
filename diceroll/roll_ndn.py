import random
import re
from .zenkaku_hankaku import zenkaku_to_hankaku

async def roll_ndn(match):
    try:
        command = match.group(0)

        # 正規表現で命令部分を抽出
        dice_expression = match.group(1)
        extra_text = match.group(2).strip() if match.group(2) else ""

        # ダイスロールと四則演算を評価
        total, details = eval_dice_expression(dice_expression)

        return f"{command}の結果: {details} -> 合計: {total}"
    except Exception as e:
        return f"エラーが発生しました: {e}"

def eval_dice_expression(expression):
    tokens = re.split(r'(\d+[dD]\d+|\+|\-|\*|/|\d+)', expression)
    tokens = [token.strip() for token in tokens if token.strip()]
    total = 0
    current_op = '+'
    details = []

    def roll_dice(dice_notation):
        num, die = map(int, re.split(r'[dD]', dice_notation))
        rolls = [random.randint(1, die) for _ in range(num)]
        return sum(rolls), rolls

    for token in tokens:
        if re.match(r'\d+[dD]\d+', token):
            subtotal, rolls = roll_dice(token)
            details.append(f"[{', '.join(map(str, rolls))}]")
        elif token in '+-*/':
            current_op = token
            details.append(token)
            continue
        else:
            subtotal = int(token)
            details.append(f"[{subtotal}]")

        if current_op == '+':
            total += subtotal
        elif current_op == '-':
            total -= subtotal
        elif current_op == '*':
            total *= subtotal
        elif current_op == '/':
            total /= subtotal

    return total, ' '.join(details)
