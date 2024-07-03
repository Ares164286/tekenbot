import func.call as call
import func.fusion as fusion
import func.hantei as hantei
import func.jobs as jobs
import func.stats_6e as stats_6e
import func.stats_7e as stats_7e
import func.help as help_cmd
import func.flash_word as flash_word
import func.hitandblow as hitandblow

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
    "フュージョン": fusion.fusion,  # フュージョンコマンドを更新
    "判定": hantei.hantei,
    "能力値": stats_6e.send_stats,
    "能力値7": stats_7e.send_stats_7e,
    "へるぷ": help_cmd.send_help,
    "ヘルプ": help_cmd.send_help,
    "フラッシュワード": flash_word.flash_word,
    "hb": hitandblow.start_game,
    "履歴を保存": save_messages.SaveMessages.save_history_cmd,
}
