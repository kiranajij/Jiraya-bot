import discord
from discord.ext import commands
import json
from NHentai import NHentai
import asyncio
from .token import TOKEN


def make_embed(cont:dict):
    embed = discord.Embed(
        colour=discord.Colour.green(),
        title=cont['title'],
        url=f"https://nhentai.net/g/{cont['id']}"
    )
    embed.set_thumbnail(url=cont['images'][0])
    embed.set_image(url=cont['images'][0])
    embed.add_field(name="ID", value=cont['id'], inline=True)
    embed.add_field(name="Pages", value=cont['pages'][0], inline=True)
    embed.add_field(name="Artists", value=", ".join(cont['artists']))
    embed.add_field(name="Tags", value=", ".join(cont['tags']))
    embed.add_field(name="Languages", value=", ".join(cont['languages']))
    return embed

nh = NHentai()
def get_prefix(bot, msg):
    with open("prefixes.json", 'r') as fp:
        prefixes = json.load(fp)
        gid      = msg.guild.id

        this_prefix = prefixes.get(str(gid), ">")
        return this_prefix

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

@bot.command()
@commands.is_owner()
async def setprefix(ctx, pref):
    gid = str(ctx.guild.id)
    me = ctx.guild.me
    with open("prefixes.json", 'r') as f:
        prefixes    = json.load(f)

    with open("prefixes.json", "w") as f:
        prefixes[gid] = pref
        json.dump(prefixes, f, indent=2)

    await me.edit(nick=f"({pref}) {me.name}", reason="Amartya bollo korte")


@bot.command()
async def bigbrain(ctx):

    role   = ctx.guild.get_role(772415348133462046)
    print(role)
    print(role.members)
    for member in role.members:
        print(member)
        embed = discord.Embed(title="Big Brain Award",
            description="BIG BRAIN AWARD GOES TO")
        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        embed.set_image(url=member.avatar_url)
        embed.colour = discord.Colour.gold()
        
        await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send(f"{round(bot.latency*1000)}ms")

@bot.command()
async def random(ctx):
    if not ctx.channel.is_nsfw():
        await ctx.send("Channel is not NSFW", delete_after=5)
        return
    await ctx.trigger_typing()
    rnd = nh.get_random()
    await ctx.send(rnd['images'][0])

@bot.command()
async def get(ctx, id: int):
    if not ctx.channel.is_nsfw():
        await ctx.send("Channel is not NSFW", delete_after=5)
        return

    await ctx.trigger_typing()
    cont = nh._get_doujin(id=str(id))
    if cont is None:
        await ctx.send("Not found!")
        return
    await ctx.send(embed=make_embed(cont))

@bot.command()
async def getfull(ctx, id: int):
    cont = nh._get_doujin(id=str(id))
    if cont is None:
        await ctx.send("Not found!")
        return
    await ctx.author.send(embed=make_embed(cont))
    for img in cont['images']:
        await ctx.author.send(img)

@bot.command()
async def getpage(ctx, id:int, page: int):
    if not ctx.channel.is_nsfw():
        await ctx.send("Channel is not NSFW", delete_after=5)
        return
    cont = nh._get_doujin(id=str(id))
    if cont is None:
        await ctx.send("Not found!")
        return
    await ctx.send(cont['images'][page-1])

@bot.command()
async def search(ctx, query: str):
    if not ctx.channel.is_nsfw():
        await ctx.send("Channel is not NSFW", delete_after=5)
        return

    await ctx.trigger_typing()
    conts = nh.search(query=query, sort="popular", page="1")

    msg = ""
    for i, cont in enumerate(conts['doujins']):
        if i==10: break
        msg += f"{i+1}. **{cont['title']}**\n\n"
    msg += f"{ctx.author.mention} type the number to get, send 'x' to cancel"
    await ctx.send(msg, delete_after=30)

    def check(msg):
        return msg.author == ctx.author and (msg.content.isdigit() or msg.content=='x')

    try:
        msg = await bot.wait_for('message', check=check, timeout=30)
        if msg == 'x': return
        n = int(msg.content)-1
        item = nh._get_doujin(id=conts['doujins'][n]['id'])
        await ctx.send(embed=make_embed(item))

    except asyncio.TimeoutError:
        await ctx.send("No response", delete_after=5)
    except IndexError:
        pass

bot.run(TOKEN)



