import discord
import random
import asyncio

async def fusion(ctx, *args):
    if len(args) == 2:
        # 引数で名前が指定された場合
        name1, name2 = args
        new_name = create_fusion_name(name1, name2)
        await change_nickname(ctx, new_name)
        await ctx.send(f"{name1}&{name2}\n「「フュー...ジョン」」\n「「はっ！！！」」\n{ctx.author.name}が「{new_name}」になりました")
    else:
        # 引数が指定されていない場合
        await random_fusion(ctx)

def create_fusion_name(name1, name2):
    half1 = name1[:len(name1)//2]
    half2 = name2[len(name2)//2:]
    return half1 + half2

async def change_nickname(ctx, new_name):
    try:
        await ctx.author.edit(nick=new_name)
    except discord.Forbidden:
        await ctx.send("表示名を変更する権限がありません。")
    except discord.HTTPException as e:
        await ctx.send(f"表示名の変更中にHTTPエラーが発生しました: {e.status} - {e.text}")
    except Exception as e:
        await ctx.send(f"表示名の変更中に予期しないエラーが発生しました: {e}")

async def random_fusion(ctx):
    members = [member for member in ctx.guild.members if not member.bot and member.display_name]
    if len(members) < 2:
        await ctx.send("サーバーに有効なメンバーが2人以上いません。")
        return

    member1, member2 = random.sample(members, 2)
    name1 = member1.display_name
    name2 = member2.display_name

    new_name = create_fusion_name(name1, name2)

    await change_nickname(ctx, new_name)
    await ctx.send(f"{name1}&{name2}\n「「フュー...ジョン」」\n「「はっ！！！」」\n{ctx.author.name}が「{new_name}」になりました")

async def try_fusion_command(ctx, *, args=None):
    if args:
        names = args.split()
        if len(names) == 2:
            await fusion(ctx, names[0], names[1])
            return
    await fusion(ctx)
