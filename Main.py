import random
import asyncio
import discord
from discord.ext import commands
import aiohttp

bot = commands.Bot(command_prefix='!')

# Create a custom check function that checks for the "Moderator" role
def has_moderator_role():
    def predicate(ctx):
        # Check if the user has the "Moderator" role
        role = discord.utils.get(ctx.guild.roles, name="Moderator")
        return role in ctx.author.roles
    return commands.check(predicate)

@bot.command()
@has_moderator_role()
async def ban(ctx, user: discord.Member, *, reason: str = None):
    # Ban the user and send a message to the user
    try:
        await user.ban(reason=reason)
        # If a reason was specified, include it in the message
        if reason is not None:
            await ctx.send(f'{user.mention} has been banned from the server for the following reason: {reason}')
        else:
            await ctx.send(f'{user.mention} has been banned from the server.')
    # If the user doesn't have permission to ban, raise a PermissionsError
    except discord.errors.PermissionsError:
        await ctx.send("You don't have permission to use this command.")
    # If the user doesn't have the "Moderator" role, raise a MissingRole error
    except discord.errors.MissingRole:
        await ctx.send("You must have the Moderator role to use this command.")

@bot.command()
@has_moderator_role()
async def kick(ctx, user: discord.Member, *, reason: str = None):
    # Kick the user and send a message to the user
    try:
        await user.kick(reason=reason)
        # If a reason was specified, include it in the message
        if reason is not None:
            await ctx.send(f'{user.mention} has been kicked from the server for the following reason: {reason}')
        else:
            await ctx.send(f'{user.mention} has been kicked from the server.')
    # If the user doesn't have permission to kick, raise a PermissionsError
    except discord.errors.PermissionsError:
        await ctx.send("You don't have permission to use this command.")
    # If the user doesn't have the "Moderator" role, raise a MissingRole error
    except discord.errors.MissingRole:
        await ctx.send("You must have the Moderator role to use this command.")

@bot.command()
@has_moderator_role()
async def warn(ctx, user: discord.Member, *, reason: str):
    # Check if the user has permission to use the command
    if ctx.author.permissions_in(ctx.channel).manage_messages:
        # Create an embed with the warning information
        embed = discord.Embed(title="Warning", description=reason, color=0xff0000)
        embed.set_footer(text=f"Warned by {ctx.author}")

        # Send the warning message to the user
        await user.send(embed=embed)

        # Confirm to the user that the warning was sent
        await ctx.send(f"Warning sent to {user}.")
    else:
        # If the user doesn't have permission, let them know
        await ctx.send("You do not have permission to use this command.")


@bot.command()
@has_moderator_role()
async def giveaway(ctx, *, prize: str):
    message = await ctx.send(f"{ctx.author.mention} is giving away {prize}! React with 🎉 to enter!")
    await message.add_reaction("🎉")

    def check(reaction, user):
        return user != ctx.bot.user and str(reaction.emoji) == "🎉"

    try:
        reaction, user = await bot.wait_for("reaction_add", check=check, timeout=60.0)
    except asyncio.TimeoutError:
        await message.edit(content="The giveaway has ended. Better luck next time!")
        return

    await message.edit(content=f"{user.mention} has won the giveaway for {prize}! Congratulations!")

    def check_reroll(m):
        return m.author == ctx.author and m.content.lower() == "reroll"

    try:
        await bot.wait_for("message", check=check_reroll, timeout=30.0)
    except asyncio.TimeoutError:
        return

    # Select a new winner
    all_reactions = [r async for r in message.reactions if r.emoji == "🎉"]
    if not all_reactions:
        await message.edit(content="No one entered the giveaway. Better luck next time!")
        return
    reaction = random.choice(all_reactions)
    users = await reaction.users().flatten()
    new_winner = random.choice(users)

    await message.edit(content=f"{new_winner.mention} has won the giveaway for {prize}! Congratulations!")

bot.remove_command('help')

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help",
        description="List of available commands",
        color=discord.Color.blue()
    )

    # Create a field for each category of commands
    embed.add_field(
        name="Moderation",
        value="`ban` `kick` `warn` `deleterole` `createrole` `say`\n`setpresence`",
        inline=False
    )
    embed.add_field(
        name="Fun",
        value="`meme` `rps`",
        inline=False
    )
    embed.add_field(
        name="Information",
        value="`help` `info`",
        inline=False
    )

    # Send the embedded message to the user
    await ctx.send(embed=embed)

@bot.command()
async def say(ctx, *, message: str):
    # Check if the user has permission to use the command
    if ctx.author.permissions_in(ctx.channel).manage_messages:
        await ctx.message.delete()
        await ctx.send(message)
    else:
        # If the user doesn't have permission, let them know
        await ctx.send("You do not have permission to use this command.")
        
@bot.command()
@commands.has_permissions(manage_roles=True)
async def createrole(ctx, *, role_name: str):
    # Check if the role already exists
    existing_role = discord.utils.get(ctx.guild.roles, name=role_name)
    if existing_role:
        await ctx.send(f"A role with the name '{role_name}' already exists.")
        return

    # Create the role
    new_role = await ctx.guild.create_role(name=role_name)
    await ctx.send(f"Created new role: {new_role.mention}")



@bot.command()
@commands.has_permissions(manage_roles=True)
async def deleterole(ctx, *, role_name: str):
    # Check if the role exists
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send(f"No role with the name '{role_name}' was found.")
        return

    # Delete the role
    await role.delete()
    await ctx.send(f"Deleted role: {role.name}")


@bot.command(pass_context=True)
async def meme(ctx):
    embed = discord.Embed(title="", description="")

    async with aiohttp.ClientSession() as cs:
        async with cs.get('https://www.reddit.com/r/dankmemes/new.json?sort=hot') as r:
            res = await r.json()
            embed.set_image(url=res['data']['children'] [random.randint(0, 25)]['data']['url'])
            await ctx.send(embed=embed)

@bot.command()
async def rps(ctx, choice):
    asyncio.sleep(1)
    choices=["rock", "paper", "scissors"]
    comp_choice = random.choice(choices)
    asyncio.sleep(10)
    await ctx.send(f'GGS!, you chose {choice} and i chose {comp_choice} ')
    if choice not in choices:
        await ctx.send("error: please put rock, paper or scissors")

DEFAULT_PRESENCE = "!help"

@bot.event
async def on_ready():
    # Set the default presence for the bot
    await bot.change_presence(activity=discord.Game(name=DEFAULT_PRESENCE))

# Define a command for changing the bot's presence
@bot.command()
async def setpresence(ctx, *, presence: str):
    # Update the bot's presence
    await bot.change_presence(activity=discord.Game(name=presence))

    # Confirm the change to the user
    await ctx.send(f"Successfully updated presence to: {presence}")

# Define the command and associated function
@bot.command()
async def info(ctx):
    # Retrieve the bot's version number from a global variable
    version = "0.7.2"

    # Send a message to the channel with the bot's version number
    await ctx.send(f"My version is {version}")
    await ctx.send("created on 15/12/2022")
    await ctx.send("invite link:\n https://discord.com/api/oauth2/authorize?client_id=1052269166385700956&permissions=8&scope=bot%20applications.commands")



bot.run('MTA1MjI2OTE2NjM4NTcwMDk1Ng.Ga5exd.O0hg76tBxPZ1FyPAWbcxJBppwRZ-Qzo6UKsfSQ')

