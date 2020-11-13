import discord
from discord import Colour, Embed

ERRORICON = "https://cdn1.iconfinder.com/data/icons/color-bold-style/21/08-512.png"
SUCCESSICON = "https://cdn3.iconfinder.com/data/icons/flat-actions-icons-9/792/Tick_Mark_Dark-512.png"
WARNINGICON =  "https://www.freeiconspng.com/uploads/orange-warning-icon-3.png"


class ErrorEmbed(Embed):
    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colour = Colour.red()
        # self.title = "Error!"
        self.set_author(name="Error!", icon_url=ERRORICON)
        self.description = message


class SuccessEmbed(Embed):
    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)   
        self.colour = Colour.green()
        self.description = message
        self.set_author(icon_url=SUCCESSICON,
            name="Success!")

class WarningEmbed(Embed):
    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)   
        self.colour = Colour.gold()
        self.description = message
        self.set_author(icon_url=WARNINGICON,
            name="Warning!")

