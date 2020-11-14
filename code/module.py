# discord specific imports
import discord
from discord import Colour
from discord.ext import commands
from discord.ext.commands import Context

# other imports
import logging, asyncio, random
import hentai
from hentai import Hentai, Format, Utils

# custom imports
from custom_embeds import ErrorEmbed, SuccessEmbed, WarningEmbed

# The code begins here
logging.basicConfig(level=logging.INFO, format="[%(levelname)s]\t%(message)s")


# The cog responsible for the NHentai Integration

class NHentaiCommands(commands.Cog):

    """
    This is cog that contains all the NHentai related commands
    """

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

        logging.error(f"{type(error).__name__}:{error}")  # Log the error in the console

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

        try:
            hnt = Hentai(id)

        except Exception:
            await ctx.send(
                embed=ErrorEmbed("Doujin doesn't exist!"),
                delete_after=10
            )
        else:
            embed = self.make_embed(hnt)
            await ctx.send(embed=embed)

    @commands.command()
    async def getfull(self, ctx: Context, id: int, from_page: int = 1):
        """

        Sends you the entire manga as an image page by page.
        Be careful using this.

        """

        if from_page < 1:
            raise ValueError("Page number must start from 1")

        try:
            hnt = Hentai(id)

        except Exception:
            await ctx.send(
                embed=ErrorEmbed("No such Doujin!"),
                delete_after=10
            )
        else:
            LIMIT = 10
            i = 1
            for page in hnt.pages[from_page-1::]:
                i += 1
                await ctx.author.send(page.url)
                if i > LIMIT:
                    await ctx.author.send("Enter `n` for next 10 pages!")
                    try:
                        await self.bot.wait_for('message',
                                           timeout=600,
                                           check=lambda msg: msg.content=='n')
                        i = 1
                        continue
                    except asyncio.TimeoutError:
                        await ctx.author.send("Timeout!")


    @commands.command()
    async def getpage(self, ctx: Context, id: int, page: int):
        """
        Returns the image on the given page number.
        Syntax:  ${prefix} getpage <id> <page>
        """

        try:
            hnt = Hentai(id)
        except:
            await ctx.send(
                embed=ErrorEmbed("Not found!"),
                delete_after=10
            )
        else:

            embed=discord.Embed(
                title=hnt.title(Format.Pretty)+f" || page {page}",
                url=self.hentai_url(hnt),
                colour=self.get_random_color()
            )
            embed.set_image(url=hnt.pages[page-1].url)
            embed.set_footer(
                text=f"requested by || {ctx.author.name}({ctx.author.display_name})",
                icon_url=ctx.author.avatar_url
            )

            await ctx.send(
                embed=embed
            )

    @commands.command()
    async def random(self, ctx: Context) -> None:

        """
        Get a random hentai from NHentai.
        """

        hnt = Utils.get_random_hentai()
        embed = self.make_embed(hnt)
        await ctx.send(embed=embed)

    @commands.command()
    async def search(self, ctx: Context, query: str):
        pass

    @staticmethod
    def hentai_url(hnt: Hentai) -> str:
        return f"https://nhentai.net/g/{hnt.id}/"

    @staticmethod
    def make_embed(hnt: Hentai) -> discord.Embed:
        """
        This class method takes a NHentai manga element and turns it into a 
        discord Embed and returns it

        """

        def convert(tag: list) -> str:
            lst = list(map(lambda x: x.name, tag))
            return ", ".join(lst)

        embed = discord.Embed(
            colour=discord.Colour.red(),
            title=hnt.title(Format.Pretty),
            url=f"https://nhentai.net/g/{hnt.id}"
        )

        embed.set_thumbnail(
            url=hnt.thumbnail
        )
        embed.set_image(url=hnt.cover)

        embed.description = \
            f"`id`      :    {hnt.id}\n" + \
            f"`pages`   :    {hnt.num_pages}\n" + \
            f"`tags`    :    {convert(hnt.tag)}\n" + \
            f"`artist`  :    {convert(hnt.artist)}"

        return embed

    @staticmethod
    def get_random_color() -> Colour:
        colors = [
            Colour.blurple(), Colour.dark_blue(), Colour.dark_orange(),
            Colour.dark_magenta(), Colour.teal()
        ]

        return random.choice(colors)

def setup(bot):
    bot.add_cog(NHentaiCommands(bot))
