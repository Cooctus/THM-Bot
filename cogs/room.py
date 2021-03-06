from discord.ext import commands
import discord, random, time, asyncio, aiohttp, json
import ast

from libs.embedmaker import officialEmbed

# Channel ID.
channelJson = open("config/channels.json", "r").read()
channelID = json.loads(channelJson)["announcements"]

# Role IDs.
rolesF = json.loads(open("config/roles.json", "r").read())
adminID = rolesF["admin"]

# Role managment function.
def hasRole(member, id):
        for role in member.roles:
                if id == role.id:
                        return True
        return False

# Sending announcement function.
async def send(channel, json_data):
    # Set up embed.
    img = json_data[0]["image"]
    title = json_data[0]["title"]
    code = "http://tryhackme.com/room/" + json_data[0]["code"]
    description = json_data[0]["description"]

    embed = officialEmbed(title, description)
    embed.set_image(url=img)

    # Send messages.
    await channel.send("A new room is available!  |  Check it out: "+code, embed=embed)

    # Updates local file.
    with open("config/room.json", "w") as file:
        json.dump(json_data, file)

class Room(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Learn how to use OpenVPN to connect to the network.")
    async def vpn(self, ctx):
        response = officialEmbed()
        response.set_thumbnail(url="https://tryhackme.com/room/openvpn")
        response.add_field(name="Learn how to use OpenVPN to connect to our network!", value="https://tryhackme.com/room/openvpn")
        await ctx.send(embed=response)

    @commands.command(description="Manually announce the last room.", hidden=True)
    async def room(self, ctx):
        if not hasRole(ctx.author, adminID):
            botMsg = await ctx.send("You do not have the permission to do that.")
            
            time.sleep(5)

            await botMsg.delete()
            await ctx.message.delete()
            return
        
        # Gets channel.
        channel = self.bot.get_channel(channelID)

        # Getting the API's JSON.
        async with aiohttp.ClientSession() as session:
            async with session.get("http://tryhackme.com/api/newrooms") as new_data:
                text = await new_data.read()
                json_data = json.loads(text) 
        
        await send(channel, json_data)

    async def new_room(self):
        # Setup the channel to send the announcements into.
        channelJson = open("config/channels.json", "r").read()
        channelID = json.loads(channelJson)["announcements"]
        channel = self.bot.get_channel(channelID)
        
        while True:
          
            # Reading the json and loading it.
            roomJson = open("config/room.json", "r").read()
            stored_data = json.loads(roomJson)

            # Getting infos from the API.
            async with aiohttp.ClientSession() as session:
                async with session.get("http://tryhackme.com/api/newrooms") as new_data:

                    text = await new_data.read()
                    json_data = json.loads(text)

                    # Getting the titles from both JSONs.
                    # Try-except to avoid wrongly [...] (making the bot more stable thx to this)
                    try:
                        titleJsonData = json_data[0]["title"]
                        titleStoredData = stored_data[0]["title"]
                    except:
                        copyfile("config/room_default.json", "config/room.json")
                        
                        roomJson = open("config/room.json", "r").read()

                        titleJsonData = json_data[0]["title"]
                        titleStoredData = stored_data[0]["title"]


                    # Check for new data.
                    if titleJsonData != titleStoredData:
                        await send(channel, json_data)
                            
            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.new_room()


def setup(bot):
    bot.add_cog(Room(bot))



