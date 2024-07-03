import func.save_messages as save_messages
import func.helpadmin as help_admin  # helpadmin.pyからインポート

commands_admin_dict = {
    "履歴を保存": save_messages.save_history_cmd,
    "管理者ヘルプ": help_admin.send_admin_help,
    # 他の管理者用コマンドをここに追加
}
