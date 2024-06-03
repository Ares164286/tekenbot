import func.call as call
import func.fusion as fusion
import func.hantei as hantei
import func.jobs as jobs
import func.stats_6e as stats_6e
import func.stats_7e as stats_7e

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
    "判定": hantei.hantei,
    "能力値": stats_6e.send_stats,  # 能力値コマンドを追加
    "能力値7": stats_7e.send_stats_7e  # 能力値7コマンドを追加
}

# 能力値コマンドを更新
async def handle_stats_command(ctx, *, args=None):
    times = 1  # デフォルトは1回
    if args:
        try:
            times = int(args)
        except ValueError:
            times = 1  # 無効な引数の場合はデフォルトの1回
    await stats_6e.send_stats(ctx, times)

commands_dict["能力値"] = handle_stats_command

# 能力値7コマンドを更新
async def handle_stats_7e_command(ctx, *, args=None):
    times = 1  # デフォルトは1回
    if args:
        try:
            times = int(args)
        except ValueError:
            times = 1  # 無効な引数の場合はデフォルトの1回
    await stats_7e.send_stats_7e(ctx, times)

commands_dict["能力値7"] = handle_stats_7e_command
