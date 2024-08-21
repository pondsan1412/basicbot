import discord
import discord.ext.commands as commands
from datetime import datetime,timedelta,timezone
import asyncio
#select intents
def intents():
    intents = discord.Intents.default()
    intents.members = True # when member have action in guild
    intents.presences =False #dont need to see member presense
    intents.message_content=True #this field is require before we need to track message for scan bad words
    return intents

#build bot class in super simple way
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents() #this parameter require intents
)

#write bot event for when bot is online because we need to know
@bot.event
async def on_ready():
    print(bot.user.name)

    #say hello world to specific ch in guild to make sure if bot is worked
    #better then !ping
    ch_ = discord.utils.get(
        bot.get_all_channels(),
        name="「👾🛠」𝓓𝓮𝓫𝓾𝓰𝓰𝓲𝓷𝓰"
    )
    #everytime bot is online
    await ch_.send('hello world!')

#detect when member leaves guild
@bot.event
async def on_member_remove(member:discord.Member):
    ch_ = discord.utils.get(
        member.guild.text_channels,
        name="「👾🛠」𝓓𝓮𝓫𝓾𝓰𝓰𝓲𝓷𝓰"
    )
    if ch_:
        await ch_.send(f"good bye :( {member.mention}")


#detect when member joins your server
@bot.event
async def on_member_join(member:discord.Member):

    #this line bot make dm to member who just joined recently
    await member.send(f"welcome bro!! {member.mention}")

    # Automatically add "Member" role if it exists
    role = discord.utils.get(
        member.guild.roles,
        name="Member"
    )
    if role:
        await member.add_roles(role)

#if they dont have role name "Member " in your server
@bot.event
async def on_member_update(before:discord.Member,after:discord.Member):
    if before.roles != after.roles:
        if not any(role.name =="Member" for role in after.roles):
            role = discord.utils.get(
                after.guild.roles,
                name="Member"
            )
            if role:
                await after.add_roles(role)

#I prefer global it
#need to make object
BAD_WORDS = {
    "idiots", "fuck","pussy","dick"
}


muted_members = {} #dict to keep track of muted members


#detecting bad words
#using message event
@bot.event
async def on_message(message:discord.Message):
    if message.author ==bot.user: return #to avoid read itself bot will spam message

    if any(word in message.content.lower() for word in BAD_WORDS):
        await message.channel.send(f"{message.author.mention}, please stop swearing!!!")
        await message.delete(delay=5) #5 second and then message will be deleted
    #check if the mesasge author is in the muted members dict
    if message.author.id in muted_members:
        await message.delete()
        return
    
    await bot.process_commands(message)

# command to mute a member
@bot.command()
async def mute(
    ctx:commands.Context,
    member:discord.Member,
    minutes: int
):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(
            f"you do not have permission {member.mention}"
        )
        return #if not return then code will be continue :skull:
    
    mute_role =discord.utils.get(
        ctx.guild.roles,
        name="Muted"
    )
    if mute_role is None:
        await ctx.send("Mute role not found.")
        return
    
    #add role to member
    await member.add_roles(mute_role)
    await ctx.send(f"{member.mention} has been muted for {minutes}!")

    #cal unmute time
    unmute_time = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    muted_members[member.id] = unmute_time

    #start a backgound task
    await asyncio.create_task(unmute_member_after(member, minutes))

async def unmute_member_after(member:discord.Member, minutes: int):
    await asyncio.sleep(minutes * 60)
    mute_role =discord.utils.get(
        member.guild.roles,
        name='Muted'
    )
    if mute_role:
        await member.remove_roles(mute_role)
        await bot.get_channel(member.guild.system_channel.id).send(f"{member.mention} has been unmuted!!!!")
        muted_members.pop(member.id, None)

import json
with open('config.json', 'r') as f:
    config = json.load(f)
TOKEN = config['TOKEN']

bot.run(TOKEN)