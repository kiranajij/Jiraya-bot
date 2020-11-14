# discord specific imports
import discord
from discord.ext import commands
from discord.ext.commands import Context

# other imports
import logging, asyncio
from NHentai import NHentai

# custom impors
from custom_embeds import ErrorEmbed, SuccessEmbed, WarningEmbed


# The code begins here
logging.basicConfig(level=logging.ERROR,format="[%(levelname)s)]\t%(message)s")

nh = NHentai()

# The cog responsible for the NHentai Integration

class Hentai(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_before_invoke(self, ctx: Context):
        """
        As the scrapping takes time, we trigger a `typing` indicator whenever
        any command in invoked.
        """
        await ctx.channel.trigger_typing()
    
    async def cog_command_error(self, ctx: Context, error: Exception):
        
        """
        This function is responsible for Error Handling. Everytime a commands raises
        an Error, this function gets invoked and sends the Error message to the Channel
        the command was given.
        """

        logging.error(f"{type(error)}:{error}")            # Log the error in the console
        
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=ErrorEmbed("Channel is not NSFW"))
            return

        await ctx.send(embed=ErrorEmbed(str(error)), delete_after=10)
    

    def cog_check(self, ctx: Context) -> bool:
        """
        Check if the channel is NSFW. The entire cog requires the channel to be NSFW
        """

        return ctx.channel.is_nsfw()

    @commands.command()
    async def get(self, ctx: Context, id: int) -> None:

        """
        get returns the NHentai manga that was requested.
        id: The id of the hentai manga.
        """

        cont = nh._get_doujin(id=str(id))       # get the doujin 
        if cont is None:
            await ctx.send(
                embed=ErrorEmbed("Not found!"),
                delete_after=10
            )
            return

        await ctx.send(embed=self.make_embed(cont))

    @commands.command()
    async def getfull(self, ctx: Context, id: int):
        """

        Sends you the entire manga as an image page by page.
        Be careful using this.

        """
        cont = nh._get_doujin(id=str(id))       # get the doujin
        if cont is None:
            await ctx.send(
                embed=ErrorEmbed("Not found!"),
                delete_after=10
            )
            return
            
        await ctx.author.send(embed=make_embed(cont))
        for img in cont['images']:
            await ctx.author.send(img)

    @commands.command()
    async def getpage(self, ctx: Context, id:int, page: int):
        """
        Returns the image on the given page number.
        Syntax:  ${prefix} getpage <id> <page>
        """
        cont = nh._get_doujin(id=str(id))
        if cont is None:
            await ctx.send(
                ErrorEmbed("Not found!"),
                delete_after=10
            )

            return
        await ctx.send(cont['images'][page-1])

    @commands.command()
    async def random(self, ctx: Context) -> None:

        """
        Get a random hentai from NHentai.
        """

        rnd = nh.get_random()                       # query a random manga
        await ctx.send(embed=self.make_embed(rnd))  # send it to the channel
    
    @commands.command()
    async def search(self, ctx: Context, query: str):

        conts = nh.search(query=query, sort="popular", page="1")

        msg = ""
        for i, cont in enumerate(conts['doujins']):
            if i==10: break
            msg += f"{i+1}. [{cont['title']}](https://nhentai.net/g/{cont['id']}/)\n\n"
        msg += f"{ctx.author.mention} type the number to get, send 'x' to cancel"
        

        embed=discord.Embed(
                title="Here you go",
                description=msg,
                colour=discord.Colour.dark_theme()
        )
        embed.set_footer(text=f"Requested by || {ctx.author.display_name}",
                    icon_url=ctx.author.avatar_url,
        )
        botmsg = await ctx.send(
            embed=embed,
            delete_after=30
        )

        def check(msg):
            return msg.author == ctx.author and (msg.content.isdigit() or msg.content=='x')

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30)
            await botmsg.delete()
            await msg.delete()

            if msg.content == 'x': return

            n = int(msg.content)-1
            item = nh._get_doujin(id=conts['doujins'][n]['id'])
            await ctx.send(embed=self.make_embed(item))

        except asyncio.TimeoutError:
            await ctx.send(embed=WarningEmbed("No Response!"), delete_after=5)

    @staticmethod
    def make_embed(cont:dict) -> discord.Embed:
        """
        This class method takes a NHentai manga element and turns it into a 
        discord Embed and returns it

        """

        embed = discord.Embed(
            colour=discord.Colour.green(),
            title=cont['title'],
            url=f"https://nhentai.net/g/{cont['id']}"
        )

        embed.set_thumbnail(url=cont['images'][0])
        embed.set_image(url=cont['images'][0])
        embed.add_field(name="ID", value=cont['id'], inline=True)
        embed.add_field(name="Pages", value=cont['pages'][0], inline=False)
        embed.add_field(name="Artists", value=", ".join(cont['artists']), inline=False)
        embed.add_field(name="Tags", value=", ".join(cont['tags']), inline=False)
        embed.add_field(name="Languages", value=", ".join(cont['languages']), inline=False)
        return embed


def setup(bot):
    bot.add_cog(Hentai(bot))