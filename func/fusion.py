import discord
import random
import asyncio

async def fusion(ctx):
    members = [member for member in ctx.guild.members if not member.bot and member.display_name]
    if len(members) < 2:
        await ctx.send("サーバーに有効なメンバーが2人以上いません。")
        return

    member1, member2 = random.sample(members, 2)
    name1 = member1.display_name
    name2 = member2.display_name

    half1 = name1[:len(name1)//2]
    half2 = name2[len(name2)//2:]

    new_name = half1 + half2

    try:
        await change_nickname_with_retry(ctx, new_name)
        await ctx.send(f"{name1}&{name2}\n「「フュー...ジョン」」\n「「はっ！！！」」\n{ctx.author.name}が「{new_name}」になりました")
    except discord.Forbidden:
        await ctx.send("表示名を変更する権限がありません。")
    except discord.HTTPException as e:
        await ctx.send(f"表示名の変更中にHTTPエラーが発生しました: {e.status} - {e.text}")
    except Exception as e:
        await ctx.send(f"表示名の変更中に予期しないエラーが発生しました: {e}")

async def change_nickname_with_retry(ctx, new_name, retries=5):
    for i in range(retries):
        try:
            await ctx.author.edit(nick=new_name)
            return
        except discord.HTTPException as e:
            if e.status == 429:  # 429 Too Many Requests
                retry_after = int(e.headers.get("Retry-After", 5))
                await ctx.send(f"レート制限に達しました。{retry_after}秒後に再試行します。")
                await asyncio.sleep(retry_after)
            else:
                raise
    raise discord.HTTPException("リトライ回数が上限に達しました。表示名の変更に失敗しました。")

async def try_fusion_command(ctx):
    try:
        await fusion(ctx)
    except Exception as e:
        await ctx.send(f"コマンド実行中にエラーが発生しました: {e}")
