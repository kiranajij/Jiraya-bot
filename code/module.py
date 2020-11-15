# discord specific imports
import discord
from discord import Colour
from discord.ext import commands
from discord.ext.commands import Context

# other imports
import logging, asyncio, random
import hentai
from hentai import Hentai, Format, Utils
from typing import List

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

        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                embed=ErrorEmbed(str(error)[str(error).find('[')+1::])
            )
        else:
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
            raise ValueError("[Doujin doesn't exist! Try another one.")

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
            raise ValueError("[Page number must start from 1")

        try:
            hnt = Hentai(id)

        except Exception:
            raise ValueError("[No such Douji found!")

        else:
            # TODO: Update this messy looking shit to something good looking using itertools

            LIMIT = 10
            i = 1
            for page in hnt.pages[from_page-1::]:
                i += 1
                await ctx.author.send(page.url)
                if i > LIMIT:
                    await ctx.author.send("Enter `n` for next 10 pages!")
                    try:
                        await self.bot.wait_for('message',
                                           timeout=60,
                                           check=lambda msg: msg.content=='n')
                        i = 1
                        continue
                    except asyncio.TimeoutError:
                        await ctx.author.send("Timeout!")
                        return


    @commands.command()
    async def getpage(self, ctx: Context, id: int, page: int):
        """
        Returns the image on the given page number.
        Syntax:  ${prefix} getpage <id> <page>
        """

        # This block checks if the asked hentai is a valid hentai
        if page < 1:
            raise ValueError("[Page number must be > 1.")
        try:
            hnt = Hentai(id)
        except:
            raise ValueError(f"page: {page}[Doujin not found!")
        else:
            # If the ID is a valid hentai then do these

            embed = self.make_page_embed(ctx, hnt, page)

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
    async def search(self, ctx: Context, *, query: str):
        """
        TODO: Make this function work
        :param ctx:
        :param query:
        :return:
        """
        result = Utils.search_by_query(query)
        embed  = self.process_search_result(result)
        msg = await ctx.send(embed=embed)

        def check(msg: discord.Message) -> bool:
            """
            Check if the function is
            :param msg:
            :return:
                        """
            if msg.author != ctx.author: return False
            content = msg.content
            try:
                n = int(content)
                if n < 1 or n > 10: return False

            except Exception:
                return content == 'x' or False
            else:
                return True

        try:
            response = await self.bot.wait_for('message',
                                               check=check,
                                               timeout=30)
        except asyncio.TimeoutError:
            await ctx.send(embed=WarningEmbed("OOPS! timeout"),
                           delete_after=10
            )
        else:
            await msg.delete()
            content = response.content
            if content == 'x':
                await msg.delete()
                await response.delete()
                return
            n = int(content)
            await response.delete()
            await ctx.send(
                embed=self.make_embed(result[n-1])
            )



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
            colour=NHentaiCommands.get_random_color(),
            title=hnt.title(Format.Pretty),
            url=f"https://nhentai.net/g/{hnt.id}"
        )

        embed.set_thumbnail(
            url=hnt.thumbnail
        )
        embed.set_image(url=hnt.cover)

        description = \
            f"`id`      :    {hnt.id}\n" + \
            f"`pages`   :    {hnt.num_pages}\n" + \
            f"`tags`    :    {convert(hnt.tag)}\n"

        if hnt.artist: description += f"artist   :   {convert(hnt.artist)}"

        embed.description = description
        return embed

    @staticmethod
    def make_page_embed(ctx: Context, hnt: Hentai, page: int):

        """
        This function converts a `getpage` query to a suitable Embed.
        :raises: ValueError if the page number provided is invalid
        :param ctx: context
        :param hnt: the hentai
        :param page: the desired page number
        :return: an Embed or Raises an Error
        """

        if page < 1 or page > hnt.num_pages:
            raise ValueError(f"[Invalid page **{page}**")

        embed = discord.Embed(
            title=hnt.title(Format.Pretty) + f" || page {page}",
            url=NHentaiCommands.hentai_url(hnt)+f"{page}",
            colour=NHentaiCommands.get_random_color()
        )
        embed.set_image(url=hnt.pages[page - 1].url)
        embed.set_footer(
            text=f"requested by || {ctx.author.name}({ctx.author.display_name})",
            icon_url=ctx.author.avatar_url
        )

        return embed

    @staticmethod
    def get_random_color() -> Colour:

        """
        TODO: Add more colors that look good
        :return:
        """

        colors = [
            Colour.blurple(), Colour.dark_blue(), Colour.dark_orange(),
            Colour.dark_magenta(), Colour.teal(), Colour.magenta(),
            Colour.dark_gold(), Colour.blurple()
        ]

        return random.choice(colors)

    @staticmethod
    def process_search_result(result: List[Hentai]):
        description = ""
        for i, hentai in enumerate(result):
            if i > 9: break
            description = description + f"{i+1}. {NHentaiCommands.get_url_hidden(hentai)}"+\
                f"  ({hentai.id})"+\
                f" | Pages **{hentai.num_pages}**"+\
                f"| ❤ **{hentai.num_favorites}**\n\n"

        return discord.Embed(description=description)

    @staticmethod
    def get_url_hidden(hentai: Hentai):
        return f"[{hentai.title(Format.Pretty)}]({NHentaiCommands.hentai_url(hentai)})"


class Helper:
    @staticmethod
    def check(ctx: Context, message: discord.Message) -> bool:
        """
        Check if the function is
        :param msg:
        :return:
                    """
        if msg.author != ctx.author: return False
        content = msg.content
        try:
            n = int(content)
            if n < 1 or n > 10: return False

        except Exception:
            return content == 'x' or False
        else:
            return True


def setup(bot):
    bot.add_cog(NHentaiCommands(bot))
