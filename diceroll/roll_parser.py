import re
from .roll_ndn import roll_ndn
from .roll_target import roll_target
from .roll_nbn import roll_nbn
from .roll_nbn_target import roll_nbn_target
from .roll_calc import roll_calc
from .roll_choice import roll_choice
from .zenkaku_hankaku import zenkaku_to_hankaku

async def parse_roll_command(command):
    try:
        # 全角文字を半角文字に変換
        command = command.translate(zenkaku_to_hankaku()).strip()

        # 正規表現パターンを定義
        repeat_pattern = re.compile(r"^\s*x(\d+)\s+(.+)$", re.IGNORECASE)
        patterns = [
            (re.compile(r"^\s*[Cc]hoice\[\s*([^\[\]]+)\s*\]\s*(.*)?$", re.IGNORECASE), roll_choice),  # choice
            (re.compile(r"^\s*[Cc]\([\d+\-*/().\s]+\)\s*(.*)?$", re.IGNORECASE), roll_calc),  # 計算式
            (re.compile(r"^\s*(\d+[bB]\d+)\s*([>=<]+)\s*(\d+)\s*(.*)?$", re.IGNORECASE), roll_nbn_target),  # Bダイスロール+目標値判定
            (re.compile(r"^\s*(\d+[bB]\d+)\s*(.*)?$", re.IGNORECASE), roll_nbn),  # Bダイスロール
            (re.compile(r"^\s*([\d+dD\s+*/-]+)\s*([=<>]+)\s*(\d+)\s*(.*)?$", re.IGNORECASE), roll_target),  # ダイスロール+四則演算+目標値判定
            (re.compile(r"^\s*([\d+dD\s+*/-]+)(\s+.*)?$", re.IGNORECASE), roll_ndn),  # ダイスロール+四則演算
        ]

        match = repeat_pattern.match(command)
        if match:
            return await repeat_command(match)

        for pattern, func in patterns:
            match = pattern.match(command)
            if match:
                print(f"マッチしたパターン: {pattern.pattern}")  # デバッグログ
                return await func(match)

        return None
    except Exception as e:
        return f"エラーが発生しました: {e}"

async def repeat_command(match):
    try:
        count = int(match.group(1))
        sub_command = match.group(2)

        results = []
        for _ in range(count):
            result = await parse_roll_command(sub_command)
            results.append(result)

        return '\n'.join(results)
    except Exception as e:
        return f"エラーが発生しました: {e}"
