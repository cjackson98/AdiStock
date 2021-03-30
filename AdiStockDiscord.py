import json
import discord
import datetime
import TotalStockChecker
from discord.ext import commands
from discord.ext.commands import Bot

with open('config.json', 'r') as f:
    config_data = json.load(f)

TOKEN = config_data["TOKEN"]
BOT_PREFIX = config_data["BOT_PREFIX"]

bot = commands.Bot(command_prefix=BOT_PREFIX)

start_time = datetime.datetime.now()

@bot.command(description="Takes in a provided PID from the command and uses it to get information (availability, stock numbers, splash page, images, price, etc) about that product.", brief="Gets stock information of a provided PID", aliases=['STOCK', 'Stock'])
async def stock(ctx):

    message = ctx.message.content.split()

    if len(message) <= 1: # Check if a PID is provided
        await ctx.channel.send("No PID provided.")
        return
    else: # Get PID and make adidasInfo object with it
        pid = message[1].upper()
        await ctx.channel.send('Checking information for "{}". . .'.format( pid ))


        debug = False

        item_info = TotalStockChecker.adidasInfo(pid)

        if debug == "true": # Check if requests.get worked or not for each URL and display success/failures
            stock = "Success: {} - Valid: {}".format( item_info.stock_success, item_info.stock_valid )
            avail = "Success: {} - Valid: {}".format( item_info.avail_success, item_info.avail_valid )
            info = "Success: {} - Valid: {}".format( item_info.info_success, item_info.info_valid )

            embed = discord.Embed(title="Getting information. . .")
            embed.add_field(name="Product Info:", value=info, inline=False)
            embed.add_field(name="Availability Data:", value=avail, inline=False)
            embed.add_field(name="Stock Data:", value=stock, inline=False)
            embed.add_field(name="URLs:", value=item_info.get_urls(), inline=False)

            embed.color = 0Xffffff
            await ctx.channel.send(embed=embed)

        
        if not item_info.info_valid: # If info is not valid, display error
            embed = discord.Embed(title="Error getting product info for {}\nProduct might not be loaded on Adidas site.".format(item_info.pid), color=0xff0000)
        else: # Create and populate embed (if info is valid)
            
            images = [] # Get image URLs in a readable format (from generator object)
            for x in item_info.get_images():
                images.append(x)

            embed = discord.Embed (title=item_info.get_product_url(), color=0x00ff00, url=item_info.get_product_url()) # , timestamp=datetime.datetime.utcnow()
            embed.set_thumbnail(url=images[0])
            embed.set_author(name=item_info.get_name(), url=item_info.get_product_url(), icon_url="https://cdn.frankerfacez.com/emoticon/270930/4")
            
            embed.add_field(name="Price:", value=item_info.get_price(), inline=False)
            embed.add_field(name="Splash page release?", value=item_info.get_splash_page(), inline=False)
            embed.add_field(name="Release Date:", value=item_info.get_release_date(), inline=False)
            embed.add_field(name="Total Stock:", value=item_info.get_total_stock(), inline=False)
            
            if item_info.get_availability():
                embed.add_field(name="Per Size Availability:", value=item_info.get_availability(), inline=False)
            else:
                embed.add_field(name="Per Size Availability:", value="Stock information not yet available, but product info is loaded onto Adidas site.", inline=False)
                embed.color = 0xffa500

            current_time = datetime.datetime.now()
            uptime = current_time - start_time
            minutes = int(uptime.seconds/60)
            hours = int(minutes/60)
            embed.set_footer(text="Uptime: {} days, {} hours, {} minutes, {} seconds.".format(uptime.days, hours, minutes%60, uptime.seconds%60))

        await ctx.channel.send(embed=embed)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Adidas | CJ | {}'.format(BOT_PREFIX)))
    print('Logged in as "{}"'.format(bot.user.name))
    print('ID: {}'.format(bot.user.id))
    print('Made by CJ')
