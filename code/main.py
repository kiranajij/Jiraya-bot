import discord
from discord.ext import commands
import json
from discord_token import AUTH_TOKEN

import logging


def get_prefix(bot, msg):
    with open("prefixes.json", 'r') as fp:
        prefixes = json.load(fp)
        gid = msg.guild.id

        this_prefix = prefixes.get(str(gid), ">")
        return this_prefix


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    logging.info(f"Logged In as {bot.user.name} (ONLINE)")


@bot.command(enabled=False)
@commands.is_owner()
async def setprefix(ctx, pref):
    gid = str(ctx.guild.id)
    me = ctx.guild.me
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)

    with open("prefixes.json", "w") as f:
        prefixes[gid] = pref
        json.dump(prefixes, f, indent=2)

    await me.edit(nick=f"({pref}) {me.name}", reason="Amartya bollo korte")


@bot.command()
async def bigbrain(ctx) -> None:
    role = ctx.guild.get_role(772415348133462046)
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
    await ctx.send(f"{round(bot.latency * 1000)}ms")


@bot.command()
async def reload(ctx):
    try:
        bot.unload_extension("module")
        bot.load_extension("module")
    except Exception:
        bot.load_extension("module")
    else:
        await ctx.send("done", delete_after=10)


bot.load_extension("module")

bot.run(AUTH_TOKEN)
