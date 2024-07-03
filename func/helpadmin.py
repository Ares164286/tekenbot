command_admin_descriptions = {
    "履歴を保存": "指定されたチャンネルのメッセージ履歴をデータベースに保存します。",
    # 他の管理者用コマンドの説明をここに追加
}

async def send_admin_help(ctx):
    help_message = "以下は利用可能な管理者用コマンドとその説明です:\n\n"
    for command, description in command_admin_descriptions.items():
        help_message += f"/{command} - {description}\n"
    await ctx.send(f"```\n{help_message}\n```")
