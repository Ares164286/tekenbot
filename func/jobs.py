import discord
import random

async def send_long_message(ctx, content):
    # メッセージを1500文字以下のチャンクに分割
    chunks = [content[i:i+1500] for i in range(0, len(content), 1500)]
    for chunk in chunks:
        await ctx.send(f'```\n{chunk}\n```')

async def send_base_skills(ctx):
    with open('CoC6thjobs/base.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        await send_long_message(ctx, content)

async def send_2010_skills(ctx):
    with open('CoC6thjobs/2010.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        await send_long_message(ctx, content)

async def send_random_base_skill(ctx):
    with open('CoC6thjobs/base.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        # 空行で区切られた部分を職業データとして扱う
        skills = content.strip().split('\n\n')
        random_skill = random.choice(skills).strip()
        await ctx.send(f'```\n{random_skill}\n```')

async def send_random_2010_skill(ctx):
    with open('CoC6thjobs/2010.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        # 空行で区切られた部分を職業データとして扱う
        skills = content.strip().split('\n\n')
        random_skill = random.choice(skills).strip()
        await ctx.send(f'```\n{random_skill}\n```')
