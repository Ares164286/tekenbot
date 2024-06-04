import func.call as call
import func.fusion as fusion
import func.hantei as hantei
import func.jobs as jobs
import func.stats_6e as stats_6e
import func.stats_7e as stats_7e
import funcslash.activity_report as activity_report
import funcslash.wakeup as Wakeup
import funcslash.yubaba as yubaba

commands_dict = {
    "時間割": call.send_timetable,
    "伝助": call.send_densuke,
    "でんじょ": call.send_densuke,
    "でんすけ": call.send_densuke,
    "lms": call.send_lms,
    "べんてん": call.send_benten,
    "勉天": call.send_benten,
    "ココフォリア": call.send_cocofolia,
    "ここふぉりあ": call.send_cocofolia,
    "cocofolia": call.send_cocofolia,
    "COCOFOLIA": call.send_cocofolia,
    "職業基本": jobs.send_base_skills,
    "職業2010": jobs.send_2010_skills,
    "職業ランダム": jobs.send_random_base_skill,
    "職業2010ランダム": jobs.send_random_2010_skill,
    "フュージョン": fusion.try_fusion_command,
    "起きろ": wakeup.Wakeup,
    "判定": hantei.hantei,
    "能力値": stats_6e.send_stats,
    "能力値7": stats_7e.send_stats_7e,
    "活動報告": activity_report.report,
    "湯婆婆": yubaba.yubaba,
    "help": send_help,
    "へるぷ": send_help,
    "ヘルプ": send_help,
}

command_descriptions = {
    "時間割": "時間割の画像を送信します。",
    "伝助": "伝助のリンクを送信します。",
    "lms": "明星LMSのリンクを送信します。",
    "べんてん": "勉天のリンクを送信します。",
    "勉天": "勉天のリンクを送信します。",
    "ココフォリア": "COCOFOLIAのリンクを送信します。",
    "職業基本": "基本的な職業データを表示します。",
    "職業2010": "2010年の職業データを表示します。",
    "職業ランダム": "基本的な職業データからランダムに1つ表示します。",
    "職業2010ランダム": "2010年の職業データからランダムに1つ表示します。",
    "フュージョン": "サーバー内のランダムな2名の表示名を合体させます。",
    "起きろ": "指定したユーザーに10回のメンションを飛ばします。",
    "判定": "任意の文章に対して◎◯△✕で返答します。",
    "能力値": "クトゥルフ6版の能力値を生成します。",
    "能力値7": "クトゥルフ7版の能力値を生成します。",
    "活動報告": "活動報告のフォーマットを表示します。",
    "湯婆婆": "指定したユーザーの名前を変更します。",
}

async def send_help(ctx):
    help_message = "以下は利用可能なコマンドとその説明です:\n\n"
    for command, description in command_descriptions.items():
        help_message += f"/{command} - {description}\n"
    await ctx.send(f"```\n{help_message}\n```")

