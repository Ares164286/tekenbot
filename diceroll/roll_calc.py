import re
from .zenkaku_hankaku import zenkaku_to_hankaku

async def roll_calc(command):
    try:
        # 全角文字を半角文字に変換
        command = command.translate(zenkaku_to_hankaku()).strip()

        # 正規表現で命令部分を抽出
        match = re.match(r"^\s*[Cc]\(([\d+\-*/().\s]+)\)\s*(.*)?$", command)
        if match:
            expression = match.group(1)
            extra_text = match.group(2).strip() if match.group(2) else ""

            # 式の評価
            result = eval(expression)

            return f"{command}の結果: {result}"
        else:
            return None
    except Exception as e:
        return f"エラーが発生しました: {e}"
