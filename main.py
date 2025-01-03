import os
import discord
from discord.ext import commands
import commands as cmd  # commands.pyからインポート
import diceroll.roll_parser as roll_parser  # roll_parserをインポート

# 環境変数からDiscordボットのトークンを取得
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# 必要なIntentsを定義
intents = discord.Intents.default()
intents.members = True  # メンバー情報を取得するためのIntentを有効化
intents.message_content = True  # メッセージの内容を取得するためのIntentを有効化
intents.dm_messages = True  # DMメッセージを取得するためのIntentを有効化
intents.guilds = True

# Discordのクライアントインスタンスを作成
client = commands.Bot(command_prefix='/', intents=intents)

# 特定のチャンネルIDを指定（リスト形式）
TARGET_CHANNEL_IDS = [1324596489657516114, 1245562745269780531, 1117864819442335824, 1117859740970651798, 1247166684121268266, 1247535324440170546]  # ここに指定するチャンネルIDを入力

@client.event
async def on_ready():
    print(f'{client.user} としてログインしました。')
    print("すべての追加機能を読み込んでいます...")
    try:
        await load_extensions()  # コグのロードを開始
    except Exception as e:
        print(f"追加機能のロード中にエラーが発生しました。: {e}")
    for guild in client.guilds:
        bot_member = guild.get_member(client.user.id)
        if bot_member:
            permissions = bot_member.guild_permissions
            print(f"{guild.name}での権限: {permissions}")

    await client.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name='あれすくんを監視中'))
    
# コグのロード
async def load_extensions():
    extensions = ["func.color_tile_game", "func.past_self", "func.save_messages", 'funcslash.wakeup', 'funcslash.yubaba', 'funcslash.activity_report', "func.echo_past_message",]
    loaded_extensions = []
    for ext in extensions:
        try:
            await client.load_extension(ext)
            loaded_extensions.append(ext)
        except Exception as e:
            print(f"拡張機能のロードに失敗しました。{ext}: {type(e).__name__} - {e}")

    # ロードされたコグ一覧を表示
    if loaded_extensions:
        print("すべての追加機能が正常にロードされました。:")
        for ext in loaded_extensions:
            print(f" - {ext}")
    else:
        print("拡張機能が正常にロードされませんでした。")


@client.event
async def on_message(message):
    # ボット自身のメッセージには反応しない
    if message.author == client.user:
        return

    # @here や @everyone のメンションには反応しない
    if any(mention in message.content for mention in ["@here", "@everyone"]):
        return

    # ボットがメンションされた場合の処理
    if client.user.mentioned_in(message):
        await message.channel.send("コマンド一覧→ /ヘルプ, /へるぷ")
        return

    # DMメッセージの場合
    if isinstance(message.channel, discord.DMChannel):
        await handle_dm_message(message)
        return

    # サーバーメッセージの場合
    if message.channel.id in TARGET_CHANNEL_IDS:
        if message.content.startswith('/'):
            await client.process_commands(message)
        else:
            # ダイスロールコマンドを解析
            response = await roll_parser.parse_roll_command(message.content)
            if response:
                user_name_message = f'＞{message.author.name}'
                await message.channel.send(user_name_message)
                await message.channel.send(response)
            else:
                await client.process_commands(message)

async def handle_dm_message(message):
    # DMメッセージを処理するロジック
    response = await roll_parser.parse_roll_command(message.content)
    if response:
        user_name_message = f'＞{message.author.name}'
        await message.channel.send(user_name_message)
        await message.channel.send(response)
    else:
        await client.process_commands(message)

# コマンドの実行を関数として定義
async def execute_command(ctx, function, *args):
    if args:
        await function(ctx, *args)
    else:
        await function(ctx)

# 各コマンドを辞書から設定
for command, function in cmd.commands_dict.items():
    async def wrapper(ctx, function=function, *, args=None):
        if args:
            await execute_command(ctx, function, args)
        else:
            await execute_command(ctx, function)
    wrapper.__name__ = command  # これでコマンド名を設定
    client.command(name=command)(wrapper)

# Botの起動とエラーハンドリング
try:
    client.run(TOKEN)
except Exception as e:
    print(f'Error: {e}')
    os.system("kill 1")
