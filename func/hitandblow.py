import random

class HitAndBlowGame:
    def __init__(self):
        self.answer = self.generate_answer()
        self.attempts = 0

    def generate_answer(self):
        return ''.join(random.sample('0123456789', 4))

    def check_guess(self, guess):
        hit = sum(1 for a, b in zip(self.answer, guess) if a == b)
        blow = sum(1 for g in guess if g in self.answer) - hit
        return hit, blow

    def reset(self):
        self.answer = self.generate_answer()
        self.attempts = 0

games = {}

TARGET_CHANNEL_IDS = [1247535324440170546, 1324602681637077042]  # 指定したチャンネルIDに置き換えてください

async def start_game(ctx, *args):
    if ctx.channel.id not in TARGET_CHANNEL_IDS:
        await ctx.send("このコマンドは指定されたチャンネルでのみ使用できます。")
        return

    user_id = ctx.author.id

    if args and args[0].lower() == 'reset':
        if user_id in games:
            del games[user_id]
            await ctx.send(f"{ctx.author.name} さんのゲームをリセットしました。")
        else:
            await ctx.send(f"{ctx.author.name} さんは現在ゲームを行っていません。")
        return

    if user_id not in games:
        games[user_id] = HitAndBlowGame()
        await ctx.send(f"{ctx.author.name} さんのヒットアンドブローゲームが始まりました！4桁の数字を当ててください。")

    game = games[user_id]

    if args:
        guess = args[0]
        if len(guess) != 4 or not guess.isdigit():
            await ctx.send("4桁の数字を入力してください。")
            return

        game.attempts += 1
        hit, blow = game.check_guess(guess)
        await ctx.send(f"{ctx.author.name} さんの推測: {guess} - ヒット: {hit}, ブロー: {blow}")

        if hit == 4:
            await ctx.send(f"おめでとうございます、{ctx.author.name} さん！ {game.attempts} 回の試行で正解を当てました。ゲームをリセットします。")
            game.reset()
    else:
        await ctx.send(f"{ctx.author.name} さん、4桁の数字を推測してください。")
