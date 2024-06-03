import random
import re
from .zenkaku_hankaku import zenkaku_to_hankaku

async def roll_choice(command):
    try:
        # 全角文字を半角文字に変換
        command = command.translate(zenkaku_to_hankaku()).strip()

        # 正規表現で命令部分を抽出
        match = re.match(r"^\s*[Cc]hoice\[\s*([^\[\]]+)\s*\]\s*(.*)?$", command, re.IGNORECASE)
        if match:
            choices_str = match.group(1)
            extra_text = match.group(2).strip() if match.group(2) else ""

            # カンマで分割してリストを作成
            choices = [choice.strip() for choice in choices_str.split(',')]

            if choices:
                selected = random.choice(choices)
                return f"{command}の結果: {selected}"
            else:
                return "選択肢が認識されませんでした。"
        else:
            return None
    except Exception as e:
        return f"エラーが発生しました: {e}"
