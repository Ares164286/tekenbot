import discord

async def send_timetable(ctx, *args):
    with open('picture/class_time.png', 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)

async def send_densuke(ctx, *args):
    embed = discord.Embed(title="伝助", url="https://www.densuke.biz", description="伝助のリンクはこちらです")
    await ctx.send(embed=embed)

async def send_lms(ctx, *args):
    embed = discord.Embed(title="明星LMS", url="https://manaba.meisei-u.ac.jp/ct/login", description="明星LMSのリンクはこちらです")
    await ctx.send(embed=embed)

async def send_benten(ctx, *args):
    embed = discord.Embed(title="勉天", url="https://benten.meisei-u.ac.jp/uprx/", description="勉天のリンクはこちらです")
    await ctx.send(embed=embed)

async def send_cocofolia(ctx, *args):
    embed = discord.Embed(title="COCOFOLIA", url="https://ccfolia.com/", description="COCOFOLIAのリンクはこちらです")
    await ctx.send(embed=embed)

async def send_print(ctx, *args):
    embed = discord.Embed(title="印刷", url="http://webprt.stu.meisei-u.ac.jp/rgate/webupload/ja", description="大学内で資料を印刷するためのリンクはこちらです")
    await ctx.send(embed=embed)
