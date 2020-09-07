import os
import subprocess
import asyncio
import discord
from discord.ext import commands

from helpers import create_mute_role, create_new_data

TOKEN = os.getenv('SPARTA_TOKEN')

PREFIX = "s!"
bot = commands.Bot(command_prefix=PREFIX,
                   description="I am Sparta Bot, a bot for the Official Sparta Gaming Discord server.",
                   help_command=None)
THEME_COLOR = discord.Colour.blue()


async def update_presence():
    while True:
        server_count = len(bot.guilds)
        activity = discord.Activity(
            type=discord.ActivityType.watching, name=f"{server_count} servers || {PREFIX}help")
        await bot.change_presence(activity=activity)
        await asyncio.sleep(10)


misc_embed = discord.Embed(title="Misc. Help", color=THEME_COLOR)
misc_embed.add_field(
    name=f"`{PREFIX}help <category>`", value="Displays command help")
misc_embed.add_field(name=f"`{PREFIX}hello`", value="Say hello to the bot")
misc_embed.add_field(name=f"`{PREFIX}info`",
                     value="Displays the bot's information")
misc_embed.add_field(name=f"`{PREFIX}clear <count>`", value="Deletes messages")
misc_embed.add_field(name=f"`{PREFIX}nuke`",
                     value="Deletes all messages in a channel")
misc_embed.add_field(
    name=f"`{PREFIX}invite`", value="Get the link to invite Sparta Bot to your server")
misc_embed.add_field(
    name=f"`{PREFIX}github`", value="Get the link to the GitHub Repository")


server_settings_embed = discord.Embed(
    title="Server Settings Commands Help", color=THEME_COLOR)
server_settings_embed.add_field(
    name=f"`{PREFIX}welcomemessage <message>`", value="Change the default Welcome Message. Use `[mention]` to mention the user, and mention any channel to show it in the message.")


mod_embed = discord.Embed(title="Moderator Help", color=THEME_COLOR)
mod_embed.add_field(name=f"`{PREFIX}warn <user> <reason>`",
                    value="Warn a user for doing something")
mod_embed.add_field(name=f"`{PREFIX}clearwarn <user>`",
                    value="Clear a user's warns")
mod_embed.add_field(name=f"`{PREFIX}warncount <user>`",
                    value="Displays how many times a user has been warned")
mod_embed.add_field(name=f"`{PREFIX}mute <user>`", value="Mutes a user")
mod_embed.add_field(name=f"`{PREFIX}unmute <user>`", value="Unmutes a user")
mod_embed.add_field(
    name=f"`{PREFIX}tempmute <user> <time in seconds>`", value="Temporarily mutes a user")
mod_embed.add_field(name=f"`{PREFIX}ban <user> <reason>`",
                    value="Bans a user from the server")
mod_embed.add_field(name=f"`{PREFIX}unban <username with #number> <reason>`",
                    value="Unbans a user from the server")
mod_embed.add_field(name=f"`{PREFIX}kick <user> <reason>`",
                    value="Kicks a user from the server")
mod_embed.add_field(name=f"`{PREFIX}lockchannel <channel>`",
                    value="Locks a channel so only Administrators can use it")
mod_embed.add_field(name=f"`{PREFIX}unlockchannel <channel>`",
                    value="Unlocks a channel so every server member can use it")


auto_embed = discord.Embed(title="Auto Moderator Help", color=THEME_COLOR)
auto_embed.add_field(name=f"`{PREFIX}activateautomod`",
                     value="Turns on Automod in your server")
auto_embed.add_field(name=f"`{PREFIX}stopautomod`",
                     value="Turns off Automod in your server")
auto_embed.add_field(name=f"`{PREFIX}whitelistuser <user>`",
                     value="Make a user immune to Auto Mod (Administrators are already immune)")
auto_embed.add_field(name=f"`{PREFIX}whitelisturl <url>`",
                     value="Allow a specific url to bypass the Auto Mod")
auto_embed.add_field(name=f"`{PREFIX}whitelistchannel <channel>`",
                     value="Allow a specific channel to bypass the Auto Mod")
auto_embed.add_field(name=f"`{PREFIX}automodstatus`",
                     value="Displays the status of AutoMod in your server")


programming_embed = discord.Embed(
    title="Programming Commands Help", color=THEME_COLOR)
programming_embed.add_field(
    name=f"`{PREFIX}eval <code in codeblocks>`", value="Allows you to run Python3 code in Discord.")


all_help_embeds = [misc_embed, server_settings_embed, mod_embed, auto_embed, programming_embed]
warn_count = {}
server_data = {}
current_help_msg = None
current_help_user = None
help_index = 0
help_control_emojis = ["⬅️", "➡️"]


@bot.event
async def on_ready():
    bot.loop.create_task(update_presence())
    print("Bot is ready...")


@bot.event
async def on_member_join(member):
    global server_data

    guild = member.guild
    channels = guild.channels
    rules_channel = None
    self_roles_channel = None

    if str(guild.id) not in server_data:
        server_data[str(guild.id)] = create_new_data()
    data = server_data[str(guild.id)]

    print(f"{member} has joined {guild} server...")

    # Channel Links
    for channel in channels:
        if str(channel).find("rules") != -1:
            rules_channel = channel
            print("rules channel found")
        if str(channel).find("self-roles") != -1:
            self_roles_channel = channel
            print("self-roles channel found")

    # Welcome Message
    if data["welcome_msg"] is None:
        server_wlcm_msg = f"Welcome, {member.mention}, to the Official **{guild.name}** Server"
    else:
        server_wlcm_msg = data["welcome_msg"]
        server_wlcm_msg = server_wlcm_msg.replace(
            "[mention]", f"{member.mention}")
        if rules_channel:
            server_wlcm_msg = server_wlcm_msg.replace(
                "[rules]", f"{rules_channel.mention}")
        if self_roles_channel:
            server_wlcm_msg = server_wlcm_msg.replace(
                "[self-roles]", f"{self_roles_channel.mention}")

    for channel in channels:
        if str(channel).find("welcome") != -1:
            await channel.send(server_wlcm_msg)
            break


@bot.event
async def on_member_remove(member):
    guild = member.guild
    channels = guild.channels
    print(f"{member} has left the server...")

    # Leave Message
    for channel in channels:
        if str(channel).find("bye") != -1 or str(channel).find("leave") != -1:
            msg = f"Goodbye, **{str(member)}**, thank you for staying at **{guild.name}** Server\n"
            await channel.send(msg)
            break


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    global help_index

    if reaction.message.id == current_help_msg and user.id != 731763013417435247:
        if user.id == current_help_user:
            channel: discord.TextChannel = reaction.message.channel

            if reaction.emoji == help_control_emojis[0]:
                help_index -= 1

            if reaction.emoji == help_control_emojis[1]:
                help_index += 1

            if help_index < 0:
                help_index = len(all_help_embeds) - 1
            elif help_index >= len(all_help_embeds):
                help_index = 0

            message: discord.Message = await channel.fetch_message(current_help_msg)
            await message.edit(embed=all_help_embeds[help_index])
            await message.remove_reaction(reaction.emoji, user)


# LABEL: Misc Commands
@bot.command(name="help")
async def _help(ctx):
    msg: discord.Message = await ctx.send("Here is the command help:", embed=all_help_embeds[help_index])

    for emoji in help_control_emojis:
        await msg.add_reaction(emoji)

    global current_help_msg, current_help_user
    current_help_msg = msg.id
    current_help_user = ctx.author.id


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hi, I am Sparta Bot!")


@bot.command(name="info")
async def info(ctx):
    embed = discord.Embed(title="Bot Information", color=THEME_COLOR)
    ping = round(bot.latency * 1000)
    guild_count = len(bot.guilds)
    members = []
    unique_member_count = 0

    for guild in bot.guilds:
        for member in guild.members:
            if not member in members:
                unique_member_count += 1
            members.append(member)

    embed.add_field(name="Ping", value=f"{ping}ms")
    embed.add_field(name="Servers", value=guild_count)
    embed.add_field(name="Users", value=len(members))
    embed.add_field(name="Unique Users", value=unique_member_count)

    await ctx.send(content=None, embed=embed)


@bot.command(name="invite")
async def invite(ctx):
    invite_url = "https://discord.com/oauth2/authorize?client_id=731763013417435247&permissions=8&scope=bot"
    embed = discord.Embed(
        title="Click here to invite Sparta Bot!", url=invite_url, color=THEME_COLOR)
    await ctx.send(content=None, embed=embed)


@bot.command(name="github")
async def github(ctx):
    repo_url = "https://github.com/MysteryCoder456/Sparta-Bot"
    embed = discord.Embed(
        title="Click here to go to the GitHub Repository!", url=repo_url, color=THEME_COLOR)
    await ctx.send(content=None, embed=embed)


@bot.command(name="clear")
@commands.has_guild_permissions(manage_messages=True)
async def clear(ctx, count: int = None):
    if count is None:
        await ctx.send("Insufficient arguments.")
    else:
        await ctx.channel.purge(limit=count+1)
        await ctx.send(f"Cleared the last {count} message(s)!")
        await asyncio.sleep(3)
        await ctx.channel.purge(limit=1)


@bot.command(name="nuke")
@commands.has_guild_permissions(manage_messages=True)
async def nuke(ctx):
    temp_channel = await ctx.channel.clone()
    await temp_channel.edit(position=ctx.channel.position)
    await ctx.channel.delete(reason="Nuke")
    await ctx.send("Nuked this channel!")


# LABEL: Server Settings
@bot.command(name="welcomemessage")
@commands.has_guild_permissions(administrator=True)
async def welcome_message(ctx, *, msg: str):
    global server_data
    if str(ctx.guild.id) not in server_data:
        server_data[str(ctx.guild.id)] = create_new_data()

    server_data[str(ctx.guild.id)]["welcome_msg"] = msg
    await ctx.send(f"This server's welcome message has been set to **{msg}**")


# LABEL: Moderator Commands
@bot.command(name="warn")
@commands.has_guild_permissions(administrator=True)
async def warn(ctx, user: discord.User = None, *, reason=None):
    if user is None or reason is None:
        await ctx.send("Insufficient arguments.")
    else:
        print(f"Warning user {user.name} for {reason}...")

        if str(user) not in warn_count:
            warn_count[str(user)] = 1
        else:
            warn_count[str(user)] += 1

        embed = discord.Embed(
            title=f"{user.name} has been warned", color=THEME_COLOR)
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="This user has been warned",
                        value=f"{warn_count[str(user)]} time(s)")

        await ctx.send(content=None, embed=embed)


@bot.command(name="clearwarn")
@commands.has_guild_permissions(administrator=True)
async def clearwarn(ctx, user: discord.User = None):
    global warn_count
    if user is None:
        warn_count = {}
        await ctx.send("Clearing all warns.")
    else:
        warn_count[str(user)] = 0
        await ctx.send(f"Clearing warns for {user.mention}.")


@bot.command(name="warncount")
async def warncount(ctx, user: discord.User):
    if str(user) not in warn_count:
        warn_count[str(user)] = 0

    count = warn_count[str(user)]
    await ctx.send(f"{user.mention} has been warned {count} time(s)")


@bot.command(name="mute")
@commands.has_guild_permissions(administrator=True)
async def mute(ctx, user: discord.Member = None):
    if user is None:
        await ctx.send("Insufficient arguments.")
    else:
        guild = ctx.guild
        mute_role = None

        for role in guild.roles:
            if role.name.lower() == "muted":
                mute_role = role
                break

        if mute_role in user.roles:
            await ctx.send("This user is already muted.")

        else:
            if not mute_role:
                mute_role = await create_mute_role(guild)

            await user.add_roles(mute_role)
            await ctx.send(f"User {user.mention} has been muted! They cannot speak.")


@bot.command(name="unmute")
@commands.has_guild_permissions(administrator=True)
async def unmute(ctx, user: discord.Member = None):
    if user is None:
        await ctx.send("Insufficient arguments.")
    else:
        guild = ctx.guild
        mute_role = None

        for role in guild.roles:
            if role.name.lower() == "muted":
                mute_role = role
                break

        if mute_role in user.roles:
            if not mute_role:
                mute_role = await create_mute_role(guild)

            await user.remove_roles(mute_role)
            await ctx.send(f"User {user.mention} has been unmuted! They can now speak.")

        else:
            await ctx.send("This user was never muted.")


@bot.command(name="tempmute")
@commands.has_guild_permissions(administrator=True)
async def tempmute(ctx, user: discord.Member = None, time: int = None):
    if user is None or time is None:
        await ctx.send("Insufficient arguments.")
    else:
        guild = ctx.guild
        mute_role = None

        for role in guild.roles:
            if role.name.lower() == "muted":
                mute_role = role
                break

        if not mute_role:
            mute_role = await create_mute_role(guild)

        await user.add_roles(mute_role)
        await ctx.send(f"User {user.mention} has been muted for {time} seconds!")
        await asyncio.sleep(time)
        await user.remove_roles(mute_role)
        await ctx.send(f"User {user.mention} has been unmuted after {time} seconds of TempMute! They can now speak.")


@bot.command(name="ban")
@commands.has_guild_permissions(ban_members=True)
async def ban(ctx, user: discord.User = None, *, reason=None):
    if user is None:
        await ctx.send("Insufficient arguments.")
    else:
        await ctx.guild.ban(user, reason=reason)
        if reason:
            await ctx.send(f"User **{user}** has been banned for reason: **{reason}**.")
        else:
            await ctx.send(f"User **{user}** has been banned.")
        await user.send(f"You have been **banned** from **{ctx.guild}** server due to the following reason:\n**{reason}**")


@bot.command(name="unban")
@commands.has_guild_permissions(ban_members=True)
async def unban(ctx, username: str = None, *, reason=None):
    if username is None:
        await ctx.send("Insufficient arguments.")
    else:
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = username.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)

        try:
            if reason:
                await ctx.send(f"User **{username}** has been unbanned for reason: **{reason}**.")
            else:
                await ctx.send(f"User **{username}** has been unbanned.")
            await user.send(f"You have been **unbanned** from **{ctx.guild}** server due to the following reason:\n**{reason}**")
        except NameError:
            await ctx.send(f"{username} is has not been banned in this server.")


@bot.command(name="kick")
@commands.has_guild_permissions(kick_members=True)
async def kick(ctx, user: discord.User = None, *, reason=None):
    if user is None:
        await ctx.send("Insufficient arguments.")
    else:
        await ctx.guild.kick(user, reason=reason)
        if reason:
            await ctx.send(f"User **{user}** has been kicked for reason: **{reason}**.")
        else:
            await ctx.send(f"User **{user}** has been kicked.")
        await user.send(f"You have been **kicked** from **{ctx.guild}** server due to the following reason:\n**{reason}**")


@bot.command(name="lockchannel")
@commands.has_guild_permissions(administrator=True)
async def lockchannel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel

    for role in ctx.guild.roles:
        if role.permissions.administrator:
            await channel.set_permissions(role, send_messages=True, read_messages=True)
        elif role.name == "@everyone":
            await channel.set_permissions(role, send_messages=False)

    await ctx.send(f"🔒The channel {channel.mention} has been locked")


@bot.command(name="unlockchannel")
@commands.has_guild_permissions(administrator=True)
async def unlockchannel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel

    await channel.set_permissions(ctx.guild.roles[0], send_messages=True)

    await ctx.send(f"🔓The channel {channel.mention} has been unlocked")


# LABEL: AutoMod Commands
@bot.command(name="activateautomod")
@commands.has_guild_permissions(administrator=True)
async def activateautomod(ctx):
    global server_data
    if str(ctx.guild.id) not in server_data:
        server_data[str(ctx.guild.id)] = create_new_data()

    server_data[str(ctx.guild.id)]["active"] = True
    await ctx.send("Automod is now active in your server...")


@bot.command(name="stopautomod")
@commands.has_guild_permissions(administrator=True)
async def stopautomod(ctx):
    global server_data
    if str(ctx.guild.id) not in server_data:
        server_data[str(ctx.guild.id)] = create_new_data()

    server_data[str(ctx.guild.id)]["active"] = False
    await ctx.send("Automod is now inactive in your server...")


@bot.command(name="whitelistuser")
@commands.has_guild_permissions(administrator=True)
async def whitelistuser(ctx, user: discord.User = None):
    if user is None:
        ctx.send("Insufficient Arguments")
    else:
        global server_data
        if str(ctx.guild.id) not in server_data:
            server_data[str(ctx.guild.id)] = create_new_data()

        server_data[str(ctx.guild.id)]["users"].append(str(user.id))
        await ctx.send(f"Added {user.mention} to AutoMod user whitelist.")


@bot.command(name="whitelisturl")
@commands.has_guild_permissions(administrator=True)
async def whitelisturl(ctx, url: str = None):
    if url is None:
        ctx.send("Insufficient Arguments")
    else:
        global server_data
        if str(ctx.guild.id) not in server_data:
            server_data[str(ctx.guild.id)] = create_new_data()

        server_data[str(ctx.guild.id)]["urls"].append(url)
        await ctx.send(f"Added `{url}` to AutoMod URL whitelist.")


@bot.command(name="whitelistchannel")
@commands.has_guild_permissions(administrator=True)
async def whitelistchannel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        ctx.send("Insufficient Arguments")
    else:
        global server_data
        if str(ctx.guild.id) not in server_data:
            server_data[str(ctx.guild.id)] = create_new_data()

        server_data[str(ctx.guild.id)]["channels"].append(
            str(channel.id))
        await ctx.send(f"Added {channel.mention} to AutoMod Channel whitelist.")


@bot.command(name="automodstatus")
async def automodstatus(ctx):
    status = server_data[str(ctx.guild.id)]["active"]
    await ctx.send(f"AutoMod Active: **{status}**")


# LABEL: Programming Commands
@bot.command(name="eval")
async def eval_code(ctx, *, code):
    is_owner = await bot.is_owner(ctx.author)
    if is_owner:
        # Some formatting before executing code
        print(code)
        code = code.strip("```")
        code = code.strip("py")
        code = code.strip("python")
        print(code)

        code_file = open("run.py", "w")
        code_file.write(code)
        code_file.close()

        cmd = subprocess.run(["python3", "run.py"], capture_output=True)
        output = cmd.stdout.decode()  # bytes => str

        os.remove("run.py")

        if len(output) == 0:
            output = "```There was an error in your code...```"
        else:
            output = f"```{output}```"

        output_embed = discord.Embed(title="Code Output", color=THEME_COLOR)
        output_embed.add_field(name=f"Code run by {ctx.author}:", value=output)

        await ctx.send(embed=output_embed)
    else:
        await ctx.send("You are not authorized to run this command.")


@bot.event
async def on_message(message: discord.Message):
    global server_data
    author: discord.Member = message.author
    channel: discord.TextChannel = message.channel
    guild: discord.Guild = message.guild
    # print(str(author), ": ", message.content)

    await bot.process_commands(message)

    if str(guild.id) not in server_data:
        server_data[str(guild.id)] = create_new_data()

    whitelist = server_data[str(guild.id)]

    if whitelist["active"] and str(author.id) not in whitelist["users"]:
        if not str(channel.id) in whitelist["channels"]:
            perms = author.permissions_in(channel)
            if not perms.administrator:
                if "http://" in message.content or "https://" in message.content:
                    if len(whitelist["urls"]) > 0:
                        for url in whitelist["urls"]:
                            if not url in message.content:
                                await channel.purge(limit=1)
                                await channel.send(f"{author.mention}, you are not allowed to send links in this channel.")
                    else:
                        await channel.purge(limit=1)
                        await channel.send(f"{author.mention}, you are not allowed to send links in this channel.")

                elif len(message.attachments) > 0:
                    await channel.purge(limit=1)
                    await channel.send(f"{author.mention}, you are not allowed to send attachments in this channel.")


bot.run(TOKEN)
