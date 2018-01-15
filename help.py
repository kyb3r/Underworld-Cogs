import discord
from discord.ext import commands
import requests
import json
import os
from .utils.dataIO import dataIO, fileIO
from cogs.utils import checks
import asyncio
import random
from random import choice as rand_choice
import string
import datetime

creditIcon = "https://imgur.com/D2T2Mpl"
credits = "Bot by Blessedville"
BOTCOMMANDER_ROLES =  ["ADMIN", "Clan Leaders", "Co Leaders"];

rules_text = """**Here are some UnderWorld Family Discord server rules.**\n
• Be respectful of other members. Do not talk them down in any way.
• Respect others' opinions. If you disagree, please do so in a constructive manner.
• Do not spam, and avoid ever using @everyone or @here without permission from Clan Leaders or Co Leaders.
• Be careful with sarcasm: sarcasm with no tone doesn't work via text.
• If you are transferring from one UnderWorld Family clan to another, please contact your destination clan's clan leader first, and wait for the all clear from that clan leader.
• A good rule is to talk to people as if you were talking to them face to face.\n
**Violation of these roles will lead to punishment including temporary guest role reduced access, temporary kick from server, or permanent kick from server, depending on the severity and/or frequency of the offense**"""

commands_text =  """Here are some of theunderworld Family Bot commands, you can use them in the #bot-spam channel.\n
**!clashProfile** - to view your Clash Royale stats.
**!chests** - to view your upcoming chests you will receive.
**!offers** - view your upcoming shop offers.
**!tourney** - to instantly recieve an open tournament that is available to join.
**!topmembers** - shows the top ranked players in our family.
**!payday** - receive your 300 credits every 30 minutes.
**!heist** - Play a heist with a crew in #heist channel.
**!slot** - Play the slot machine.
**!buy** - Take a look at what you can purchase with your credits.
**!balance** - To check your current bank balance.
**!profile** - view your server profile.
**!deck** - make and save your deck.
**!uwrl** - to see status of all UnderWorld Family clans.
**!rep @user** - give reputation points to users.
**!remindme** - Use this command to make the bot remind you of something in the future.
**!trivia** - start a trivia of your choice. Bot will ask you questions, you will get points of answering them.
**!queue** -  Listen to songs, type with command with the song name inside a voice channel. (!skip, !pause, !resume, !playlist).\n
**You can type !help here to see the full commands list**"""

info_text = """You will find several channels on our Discord Server\n
**#global-chat**: to discuss about the game.
**#tourneys**: Dozens of tournaments posted everyday.
**#news**: important info about family.
**#deck-recommendation**: decks discussion.
**#off-topic**: you can chat about anything unrelated to clash royale here.
**#bots-spam**: play bot commands, You can mute the channels you don't need in DISCORD settings.
**#friends-forever**: Post your Clash friend invite link or add others.
"""
cw_info = """We organize a **clanwar** every weekend, which aims to determine **which clan is the strongest**.

The **idea** is simple: A private tournament that anyone may join **within UnderWorld and the alliance. **
Score is calculated in a way that allows every participant to contribute to help their clan win.  We sum the earned tournament trophies of the members of each clan to calculate a clan score, clan with highest clan score is declared the **winner**!

There are 2 factors to win: convince more players to participate within your clan and earn more tournament trophies. Both are **equally important**. We publish tourneys and passwords at same time, so we give equal chances to each clan and player.

**All clans** will be closed/full to avoid any leaks, nobody will be allowed to join.

**3 golden Rules for clanwars:** We respect the Opponent (no BMing if you win), we play to have fun (no obligation to participate), and don't join if you think you cannot play.
"""

esports_info = """The UW eSports Team is recruiting all active and aspiring players!

With the goal of encouraging competitive play in the family, there is a monthly ranked season system on the eSports Team Server where players compete to play on UW eSports A Team and B team to represent the family in various International events. Our strongest players will compete side by side with the very best in leagues such as CCTS, CPL, and even RPL!

While we have a clan called UW eSports!, the team operates separately from the clan, and sends members from any family clan to events.

But please remember that this is a more professional setting than the rest of the family and poor behaviour will not be tolerated.

https://discord.me/underworldcr
"""

coc_bs = """We also play **Clash of Clans** and **Brawl Stars**, we would like to invite to you join them if you play either of these supercell games.

• Clash of Clans - **LeGeND Raiders! (#JQJRGVJU)** - https://discord.me/underworldcr
• Brawl Stars - **UnderBrawlers! (#LLPR9PP)** - https://discord.me/underworldcr

You can send a request to join with the message "from UNDERWORLD". Join the discord server when you are accepted.
"""

social_info = """Stay Social! Come and follow us on these platforms to stay up to date on the latest news and announcements.

https://twitter.com/underworldcr

Visit our website to see live clan statistics:
https://sites.google.com/view/underworldcr/home
"""

coaching_info = """If you are looking to climb in your trophies and get better at the game, we have coaches at UnderWorld that can help you get to the top! Come join the coaching channel and start a session with a dedicated coach now at  https://discord.me/underworldcr
"""

class underworld:

    def __init__(self, bot):
        self.bot = bot
        self.clash = dataIO.load_json('cogs/tags.json')
        self.c = dataIO.load_json('cogs/clans.json')
        self.auth = dataIO.load_json('cogs/auth.json')
        self.welcome = dataIO.load_json('data/underworld/welcome.json')
        self.bank = dataIO.load_json('data/economy/bank.json')

    async def updateClash(self):
        self.clash = dataIO.load_json('cogs/tags.json')

    def save_data(self):
        """Saves the json"""
        dataIO.save_json('cogs/clans.json', self.c)

    async def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
       return ''.join(random.choice(chars) for _ in range(size))

    def clanArray(self):
        return self.c.keys()

    def numClans(self):
        return len(self.c.keys())

    def getAuth(self):
        return {"auth" : self.auth['token']}

    async def _add_roles(self, member, role_names):
        """Add roles"""
        server = member.server
        roles = [discord.utils.get(server.roles, name=role_name) for role_name in role_names]
        try:
            await self.bot.add_roles(member, *roles)
        except discord.Forbidden:
            raise
        except discord.HTTPException:
            raise

    async def _remove_roles(self, member, role_names):
        """Remove roles"""
        server = member.server
        roles = [discord.utils.get(server.roles, name=role_name) for role_name in role_names]
        try:
            await self.bot.remove_roles(member, *roles)
            await asyncio.sleep(3)
        except:
            pass

    @commands.group(pass_context=True)
    @checks.mod_or_permissions(administrator=True)
    async def clans(self, ctx):
        """Base command for managing clash royale clans. [p]help clans for details"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @clans.command(pass_context=True, name="register")
    @checks.mod_or_permissions(administrator=True)
    async def clans_register(self, ctx, clankey, ctag, role: discord.Role, nickname):
        """Register a clan for tracking"""
        toregister = {
            'tag': ctag,
            'role': role.name,
            'role_id': role.id,
            'name': nickname,   # Not good, will fix later
            'nickname' : nickname,
            'waiting': [],
            'personalbest': 0,
            'bonustitle': "",
            'discord': None
            }

        clankey = clankey.lower()

        self.c[clankey] = toregister
        self.save_data()
        await self.bot.say("Success")

    @clans.command(pass_context=True, name="delete")
    @checks.mod_or_permissions(administrator=True)
    async def clans_delete(self, ctx, clankey):
        """Remove a clan from tracking"""
        clankey = clankey.lower()
        if self.c.pop(clankey, None):
            self.save_data()
            await self.bot.say("Success")
            return
        await self.bot.say("Failed")

    @clans.command(pass_context=True, name="pb")
    @checks.mod_or_permissions(administrator=True)
    async def clans_pb(self, ctx, clankey, pb: int):
        """Set a Personal Best requirement for a clan"""
        clankey = clankey.lower()
        try:
            self.c[clankey]['personalbest'] = pb
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+", ".join(key for key in self.c.keys()))
            return

        self.save_data()
        await self.bot.say("Success")

    @clans.command(pass_context=True, name="bonus")
    @checks.mod_or_permissions(administrator=True)
    async def clans_bonus(self, ctx, clankey, *bonus):
        """Add bonus information to title of clan (i.e. Age: 21+)"""
        clankey = clankey.lower()
        try:
            self.c[clankey]['bonustitle'] = " ".join(bonus)
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+",".join(key for key in self.c.keys()))
            return

        self.save_data()
        await self.bot.say("Success")

    @clans.command(pass_context=True, name="discord")
    @checks.mod_or_permissions(administrator=True)
    async def clans_discord(self, ctx, clankey, discordinv):
        """Add discord invite link"""
        clankey = clankey.lower()
        try:
            self.c[clankey]['discord'] = discordinv
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+",".join(key for key in self.c.keys()))
            return

        self.save_data()
        await self.bot.say("Success")

    async def _is_commander(self, member):
        server = member.server
        botcommander_roles = [discord.utils.get(server.roles, name=r) for r in BOTCOMMANDER_ROLES]
        botcommander_roles = set(botcommander_roles)
        author_roles = set(member.roles)
        if len(author_roles.intersection(botcommander_roles)):
            return True
        else:
            return False

    async def _is_member(self, member):
        server = member.server
        botcommander_roles = [discord.utils.get(server.roles, name=r) for r in ["Member", "Elders", "Clan Leaders", "Co Leaders", "ADMIN"]]
        botcommander_roles = set(botcommander_roles)
        author_roles = set(member.roles)
        if len(author_roles.intersection(botcommander_roles)):
            return True
        else:
            return False

    @commands.command(pass_context=True)
    async def uwrl(self, ctx, member: discord.Member = None):
        """ Show UnderWorld clans, can also show clans based on a member's trophies"""

        if member is None:
            trophies = 9999
            maxtrophies = 9999
            maxmembers = 51
        else:
            try:
                await self.updateClash()
                await self.bot.type()
                profiletag = self.clash[member.id]['tag']
                profiledata = requests.get('http://api.cr-api.com/player/{}?exclude=games,currentDeck,cards,battles,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
                trophies = profiledata['trophies']
                maxtrophies = profiledata['stats']['maxTrophies']
                maxmembers = 50
                await self.bot.say("Hello {}, these are all the clans you are allowed to join, based on your statistics. \nYour Trophies: {}\nYour Personal Best: {}".format(member.mention, str(trophies), str(maxtrophies)))
            except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
                await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
                return
            except requests.exceptions.RequestException as e:
                await self.bot.say(e)
                return
            except:
                await self.bot.say("You must assosiate a tag with this member first using ``!save clash #tag @member``")
                return

        try:
            await self.bot.type()
            clans = requests.get('http://api.cr-api.com/clan/'+','.join(self.c[clan]["tag"] for clan in self.c)+'?exclude=members', headers=self.getAuth(), timeout=10).json()
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
                await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
                return
        except requests.exceptions.RequestException as e:
                await self.bot.say(e)
                return

        clans = sorted(clans, key=lambda clanned: clanned['requiredScore'], reverse=True)

        embed=discord.Embed(color=0xFAA61A)
        embed.set_author(name="UnderWorld Family Clans", url="http://cr-api.com/clan/family/uwrl/clans", icon_url="https://imgur.com/Ix5767j")
        embed.set_footer(text=credits, icon_url=creditIcon)

        foundClan = False
        totalMembers = 0
        totalWaiting = 0
        for x in range(0, len(clans)):
            numWaiting = 0
            personalbest = 0
            bonustitle = None

            for clankey in self.clanArray():
                if self.c[clankey]['tag'] == clans[x]['tag']:
                    numWaiting = len(self.c[clankey]['waiting'])
                    personalbest = self.c[clankey]['personalbest']
                    bonustitle = self.c[clankey]['bonustitle']
                    emoji = self.c[clankey]['emoji']
                    totalWaiting += numWaiting
                    break

            if numWaiting > 0:
                title = "["+str(numWaiting)+" Waiting] "
            else:
                title = ""

            totalMembers += clans[x]['memberCount']
            if clans[x]['memberCount'] < 50:
                showMembers = str(clans[x]['memberCount']) + "/50"
            else:
                showMembers = "**FULL**   "

            if str(clans[x]['type']) != 'invite only':
                title += "["+str(clans[x]['type']).capitalize()+"] "

            title += clans[x]['name'] + " (#" + clans[x]['tag'] + ") "

            if personalbest > 0:
                title += "PB: "+str(personalbest)+"+  "
                clans[x]['maxtrophies'] = personalbest

            if bonustitle is not None:
                title += bonustitle

            desc = emoji + " " + showMembers + "     :trophy: " + str(clans[x]['requiredScore']) + "+     :medal: " +str(clans[x]['score'])

            if (member is None) or ((clans[x]['requiredScore'] <= trophies) and (maxtrophies > personalbest) and (trophies - clans[x]['requiredScore'] < 1500) and (clans[x]['type'] != 'closed')):
                foundClan = True
                embed.add_field(name=title, value=desc, inline=False)

        if foundClan is False:
            embed.add_field(name="uh oh!", value="There are no clans available for you at the moment, please type !underworld to see all clans.", inline=False)

        embed.description = "Our Family is made up of " + str(self.numClans()) + " clans with a total of " + str(totalMembers) + " members. We have " + str((self.numClans()*50)-totalMembers) + " spots left and " + str(totalWaiting) + " members in waiting lists."
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    async def approve(self, ctx, member: discord.Member, clankey):
        """Send instructions to people joining a clan"""
        server = ctx.message.server
        author = ctx.message.author
        underworldServer = ["396607086533804042"]

        if server.id not in underworldServer:
            await self.bot.say("This command can only be executed in the UnderWorld Family Server")
            return

        allowed = await self._is_commander(author)

        if not allowed:
            await self.bot.say("You dont have enough permissions to approve a recruit. Type !contact to ask for help.")
            return

        clankey = clankey.lower()

        try:
            clan_tag = self.c[clankey]['tag']
            clan_name = self.c[clankey]['name']
            clan_role = self.c[clankey]['role']
            clan_pb = self.c[clankey]['personalbest']
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+", ".join(key for key in self.c.keys()))
            return

        leftClan = False
        try:
            await self.updateClash()
            await self.bot.type()
            profiletag = self.clash[member.id]['tag']
            profiledata = requests.get('http://api.cr-api.com/player/{}?exclude=games,currentDeck,cards,battles,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
            clandata = requests.get('http://api.cr-api.com/clan/{}'.format(clan_tag), headers=self.getAuth(), timeout=10).json()
            ign = profiledata['name']
            if profiledata['clan'] is None:
                leftClan = True
                clantag = ""
                clanname = ""
            else:
                clantag = profiledata['clan']['tag']
                clanname = profiledata['clan']['name']
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return
        except:
            await self.bot.say("You must assosiate a tag with this member first using ``!save clash #tag @member``")
            return

        membership = True
        for clankeys in self.clanArray():
            if self.c[clankeys]['tag'] == clantag:
                membership = False
                savekey = clankeys
                break

        if membership:

            trophies = profiledata['trophies']
            maxtrophies = profiledata['stats']['maxTrophies']

            if (clandata['memberCount'] == 50):
                await self.bot.say("Approval failed, the clan is Full.")
                return

            if ((trophies < clandata['requiredScore']) and (trophies < clan_pb)):
                await self.bot.say("Approval failed, you don't meet the trophy requirements.")
                return

            if (clandata['type'] == "closed"):
                await self.bot.say("Approval failed, the clan is currently closed.")
                return

            if not leftClan:
                await self.bot.say("Approval failed, You have not yet left your current clan.")
                return

            if len(self.c[clankey]['waiting']) > 0:
                if member.id in self.c[clankey]['waiting']:
                    if member.id != self.c[clankey]['waiting'][0]:
                        await self.bot.say("Approval failed, you are not first in queue for the waiting list on this server.")
                        return
                    else:
                        self.c[clankey]['waiting'].pop(0)
                        dataIO.save_json('cogs/clans.json', self.c)

                        role = discord.utils.get(server.roles, name="Waiting")
                        try:
                            await self.bot.remove_roles(member, role)
                        except discord.Forbidden:
                            raise
                        except discord.HTTPException:
                            raise
                else:
                    await self.bot.say("Approval failed, there is a waiting queue for this clan. Please first join the waiting list.")
                    return

            recruitCode = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

            await self.bot.send_message(member,
                "Congratulations, You have been approved to join **"+ clan_name + " (#" + clan_tag + ")**. Please follow the instructions below on how to join: \n\n" +
                "Your Recruit Code is: ``" + recruitCode + "`` \n\n"+
                "All you have to do is search the clan name in Clash Royale, request to join and enter your recruit code in the request message.\n\n" +
                "That's it! Now wait for your clan leadership to accept you. \n\n" +
                "If you do not see a 'request to join' button, make sure you leave your current clan and check the trophy requirements. \n\n" +
                "**IMPORTANT**: Once your clan leadership has accepted your request, let a staff member in discord know that you have been accepted. They will then unlock all the member channels for you."
                )
            await self.bot.say(member.mention + " has been approved for **" + clan_name + "**. Please check your DM for instructions on how to join.")

            roleName = discord.utils.get(server.roles, name=clan_role)
            await self.bot.send_message(discord.Object(id='396607086533804042'), roleName.mention + " \nName: " + ign + "\n" + "Recruit Code: ``" + recruitCode + "``")
        else:
            await self.bot.say("Approval failed, You are already a part of a clan in the family.")

    @commands.command(pass_context=True, no_pm=True)
    async def newmember(self, ctx, member: discord.Member):
        """Setup nickname, roles and invite links for a new member"""

        server = ctx.message.server
        author = ctx.message.author
        underworldServer = ["396607086533804042"]

        if server.id not in underworldServer:
            await self.bot.say("This command can only be executed in the UnderWorld Family Server")
            return

        isMember = await self._is_member(member)
        if isMember:
            await self.bot.say("Error, " + member.mention + " is not a new member.")
            return

        try:
            await self.updateClash()
            await self.bot.type()
            profiletag = self.clash[member.id]['tag']
            profiledata = requests.get('http://api.cr-api.com/player/{}?exclude=games,currentDeck,cards,battles,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
            if profiledata['clan'] is None:
                clantag = ""
                clanname = ""
            else:
                clantag = profiledata['clan']['tag']
                clanname = profiledata['clan']['name']

            ign = profiledata['name']
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return
        except:
            await self.bot.say("You must assosiate a tag with this member first using ``!save clash #tag @member``")
            return

        allowed = False
        if member is None:
            allowed = True
        elif member.id == author.id:
            allowed = True
        else:
            allowed = await self._is_commander(author)

        if not allowed:
            await self.bot.say("You dont have enough permissions to use this command on others.")
            return

        membership = False
        for clankey in self.clanArray():
            if self.c[clankey]['tag'] == clantag:
                membership = True
                savekey = clankey
                break

        if membership:

            if member.id in self.c[savekey]['waiting']:
                self.c[savekey]['waiting'].remove(member.id)
                dataIO.save_json('cogs/clans.json', self.c)

            mymessage = ""
            if ign is None:
                await self.bot.say("Cannot find IGN.")
            else:
                try:
                    newclanname = self.c[savekey]['nickname']
                    newname = ign + " | " + newclanname
                    await self.bot.change_nickname(member, newname)
                except discord.HTTPException:
                    await self.bot.say(
                        "I don’t have permission to change nick for this user.")
                else:
                    mymessage += "Nickname changed to ** {} **\n".format(newname)


            role_names = [self.c[savekey]['role'], 'Member']
            try:
                await self._add_roles(member, role_names)
                mymessage += "**" + self.c[savekey]['role'] + " ** and **Member** roles added."
            except discord.Forbidden:
                await self.bot.say(
                    "{} does not have permission to edit {}’s roles.".format(
                        author.display_name, member.display_name))
            except discord.HTTPException:
                await self.bot.say("failed to add {}.").format(', '.join(role_names))

            await self.bot.say(mymessage)

            welcomeMsg = rand_choice(self.welcome["GREETING"])
            await self.bot.send_message(discord.Object(id='396607086533804042'), welcomeMsg.format(member, server))

            await self._remove_roles(member, ['Guest'])

            if self.c[savekey]['discord'] is not None:
                joinLink = "https://discord.gg/" + str(self.c[savekey]['discord'])
                await self.bot.send_message(member,
                    "Hi There! Congratulations on getting accepted into our family. We have unlocked all the member channels for you in UnderWorld Discord Server. Now you have to carefuly read this message and follow the steps mentioned below: \n\n"+
                    "Please click on the link below to join your clan Discord server. \n\n"+
                    clanname + ": " + joinLink + "\n\n" +
                    "Please do not leave our main or clan servers while you are in the clan. Thank you."
                    )
            else:
                await self.bot.send_message(member,
                    "Hi There! Congratulations on getting accepted into our family. We have unlocked all the member channels for you in UnderWorld Discord Server. \n\n"+
                    "Please do not leave our Discord server while you are in the clan. Thank you."
                    )

            roleName = discord.utils.get(server.roles, name=role_names[0])
            await self.bot.send_message(discord.Object(id='396607086533804042'), '**' + ctx.message.author.name + '** recruited ' + '** ' + ign + ' (#'+ profiletag + ')** to ' + roleName.mention)

            await asyncio.sleep(300)
            await self.bot.send_message(member,rules_text)

            await asyncio.sleep(300)
            await self.bot.send_message(member,commands_text)

            await asyncio.sleep(300)
            await self.bot.send_message(member,info_text)

            await asyncio.sleep(300)
            await self.bot.send_message(member,cw_info)

            await asyncio.sleep(300)
            await self.bot.send_message(member,coaching_info)

            await asyncio.sleep(300)
            await self.bot.send_message(member,coc_bs)

            await asyncio.sleep(300)
            await self.bot.send_message(member,esports_info)

            await asyncio.sleep(300)
            await self.bot.send_message(member,social_info)
        else:
            await self.bot.say("You must be accepted into a clan before I can give you clan roles.")

    @commands.command(pass_context=True, no_pm=True)
    async def waiting(self, ctx, member: discord.Member, clankey):
        """Add people to the waiting list for a clan"""
        server = ctx.message.server
        author = ctx.message.author
        underworldServer = ["396607086533804042"]

        if server.id not in underworldServer:
            await self.bot.say("This command can only be executed in the UnderWorld Family Server")
            return

        allowed = await self._is_commander(author)

        if not allowed:
            await self.bot.say("You dont have enough permissions to add someone to the waiting list. Type !contact to ask for help.")
            return

        clankey = clankey.lower()

        try:
            clan_tag = self.c[clankey]['tag']
            clan_name = self.c[clankey]['name']
            clan_role = self.c[clankey]['role']
            clan_pb = self.c[clankey]['personalbest']
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+", ".join(key for key in self.c.keys()))
            return

        try:
            await self.updateClash()
            await self.bot.type()
            profiletag = self.clash[member.id]['tag']
            profiledata = requests.get('http://api.cr-api.com/player/{}?exclude=games,currentDeck,cards,battles,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
            clandata = requests.get('http://api.cr-api.com/clan/{}'.format(clan_tag), headers=self.getAuth(), timeout=10).json()
            ign = profiledata['name']
            if profiledata['clan'] is None:
                clantag = ""
                clanname = ""
            else:
                clantag = profiledata['clan']['tag']
                clanname = profiledata['clan']['name']
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return
        except:
            await self.bot.say("You must assosiate a tag with this member first using ``!save clash #tag @member``")
            return

        membership = True
        for clanKey in self.clanArray():
            if self.c[clanKey]['tag'] == clantag:
                membership = False # False
                savekey = clanKey
                break

        if membership:

            trophies = profiledata['trophies']
            maxtrophies = profiledata['stats']['maxTrophies']

            if ((trophies < clandata['requiredScore']) and (trophies < clan_pb)):
                await self.bot.say("Cannot add you to the waiting list, you don't meet the trophy requirements.")
                return

            if member.id not in self.c[clankey]['waiting']:
                self.c[clankey]['waiting'].append(member.id)
                dataIO.save_json('cogs/clans.json', self.c)
            else:
                await self.bot.say("You are already in a waiting list for this clan.")
                return

            role = discord.utils.get(server.roles, name="Waiting")
            try:
                await self.bot.add_roles(member, role)
            except discord.Forbidden:
                raise
            except discord.HTTPException:
                raise
            await self.bot.say(member.mention + " You have been added to the waiting list for **"+ clan_name + "**. We will mention you when a spot is available.")
        else:
            await self.bot.say("Cannot add you to the waiting list, You are already a part of a clan in the family.")

    @commands.command(pass_context=True, no_pm=True)
    async def remove(self, ctx, member: discord.Member, clankey):
        """Delete people from the waiting list for a clan"""
        server = ctx.message.server
        author = ctx.message.author
        underworldServer = ["396607086533804042"]

        if server.id not in underworldServer:
            await self.bot.say("This command can only be executed in the UnderWorld Family Server")
            return

        allowed = await self._is_commander(author)

        if not allowed:
            await self.bot.say("You dont have enough permissions to delete someone to the waiting list. Type !contact to ask for help.")
            return

        clankey = clankey.lower()

        try:
            clan_tag = self.c[clankey]['tag']
            clan_name = self.c[clankey]['name']
            clan_role = self.c[clankey]['role']
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+", ".join(key for key in self.c.keys()))
            return

        try:
            self.c[clankey]['waiting'].remove(member.id)
            dataIO.save_json('cogs/clans.json', self.c)

            role = discord.utils.get(server.roles, name="Waiting")
            try:
                await self.bot.remove_roles(member, role)
            except discord.Forbidden:
                raise
            except discord.HTTPException:
                raise
            await self.bot.say(member.mention + " has been removed from the waiting list for **"+ clan_name + "**.")
        except ValueError:
            await self.bot.say("Recruit not found in the waiting list.")

    @commands.command(pass_context=True, no_pm=True, aliases=["waitlist","wait"])
    async def waitinglist(self, ctx):
        """Show status of the waiting list."""

        message = ""
        counterClans = 0
        counterPlayers = 0

        server = ctx.message.server
        author = ctx.message.author
        underworldServer = ["396607086533804042"]

        if server.id not in underworldServer:
            await self.bot.say("This command can only be executed in the UnderWorld Family Server")
            return

        await self.bot.type()

        embed=discord.Embed(title="", description="", color=0x0080ff)

        for indexC, clan in enumerate(self.c):
            if self.c[clan]["waiting"]:
                counterClans += 1
                message = ""
                for index, userID in enumerate(self.c[clan]["waiting"]):
                    user = discord.utils.get(ctx.message.server.members, id = userID)
                    try:
                        message += str(index+1) + ". " + user.name + "\n"
                        counterPlayers += 1
                    except AttributeError:
                        self.c[clan]['waiting'].remove(userID)
                        dataIO.save_json('cogs/clans.json', self.c)
                        message += str(index+1) + ". " + "*user not found*" + "\n"
                embed.add_field(name=self.c[clan]["name"], value=message, inline=False)

        if not message:
            await self.bot.say("The waiting list is empty")
        else:
            embed.description = "We have " + str(counterPlayers) + " people waiting for " + str(counterClans) + " clans."
            embed.set_author(name="UnderWorld Family Waiting List", icon_url="https://imgur.com/Ix5767j")
            embed.set_footer(text=credits, icon_url=creditIcon)
            await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def changenick(self, ctx, member: discord.Member = None):
        """ Change nickname of a user of their IGN + Clan"""

        server = ctx.message.server

        if member is None:
            member = ctx.message.author

        try:
            await self.updateClash()
            await self.bot.type()
            profiletag = self.clash[member.id]['tag']
            profiledata = requests.get('http://api.cr-api.com/player/{}?exclude=games,currentDeck,cards,battles,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
            clantag = profiledata['clan']['tag']
            clanname = profiledata['clan']['name']
            ign = profiledata['name']
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return
        except:
            await self.bot.say("You must assosiate a tag with this member first using ``!save clash #tag @member``")
            return

        membership = False
        for clankey in self.clanArray():
            if self.c[clankey]['tag'] == clantag:
                membership = True
                savekey = clankey
                break

        if membership:

            mymessage = ""
            if ign is None:
                await self.bot.say("Cannot find IGN.")
            else:
                try:
                    newclanname = self.c[savekey]['nickname']
                    newname = ign + " | " + newclanname
                    await self.bot.change_nickname(member, newname)
                except discord.HTTPException:
                    await self.bot.say("I don’t have permission to change nick for this user.")
                else:
                     await self.bot.say("Nickname changed to ** {} **\n".format(newname))
        else:
            await self.bot.say("You are not even in any of our clans, what are you doing here?")

    @commands.command(pass_context=True, no_pm=True)
    async def audit(self, ctx, clankey):
        """ Check to see if your clan members are setup properly in discord."""
        server = ctx.message.server
        author = ctx.message.author
        underworldServer = ["396607086533804042"]

        if server.id not in underworldServer:
            await self.bot.say("This command can only be executed in the UnderWorld Family Server")
            return

        clankey = clankey.lower()

        try:
            clan_tag = self.c[clankey]['tag']
            clan_role = self.c[clankey]['role']
            clan_name = self.c[clankey]['name']
            clan_role_id = self.c[clankey]['role_id']
        except KeyError:
            await self.bot.say("Please use a valid clanname : "+", ".join(key for key in self.c.keys()))
            return

        allowed = await self._is_commander(author)

        if not allowed:
            await self.bot.say("You dont have enough permissions to use Audit. Type !contact to ask for help.")
            return

        await self.bot.type()

        try:
            clandata = requests.get('http://api.cr-api.com/clan/{}'.format(clan_tag), headers=self.getAuth(), timeout=10).json()
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return

        await self.updateClash()

        cr_members_name = []
        cr_members_tag = []
        cr_members_trophy = []
        for x in range(0, len(clandata['members'])):
            cr_members_name.append(clandata['members'][x]['name'])
            cr_members_tag.append(clandata['members'][x]['tag'])
            cr_members_trophy.append(clandata['members'][x]['trophies'])

        role = discord.utils.get(server.roles, id=clan_role_id)
        d_members = [m for m in server.members if role in m.roles]
        d_members = sorted(d_members, key=lambda x: x.display_name.lower())

        cr_members_with_no_player_tag = []
        cr_members_with_less_trophies = []
        d_members_with_no_player_tag = []
        d_members_not_in_clan = []
        d_members_without_role = []

        for d_member in d_members:
            try:
                player_tag = self.clash[d_member.id]['tag']

                if player_tag not in cr_members_tag:
                    d_members_not_in_clan.append(d_member.display_name)
            except KeyError:
                d_members_with_no_player_tag.append(d_member.display_name)
                continue

        for index, player_tag in enumerate(cr_members_tag):
            try:
                dc_member = None
                for key in self.clash:
                    if self.clash[key]['tag'] == player_tag:
                        dc_member = server.get_member(key)
                        break
                    else:
                        continue

                if role not in dc_member.roles:
                    d_members_without_role.append(dc_member.display_name)
            except AttributeError:
                cr_members_with_no_player_tag.append(cr_members_name[index])
                continue

        clanReq = clandata['requiredScore']
        for index, player_trophy in enumerate(cr_members_trophy):
            if player_trophy < clanReq:
                cr_members_with_less_trophies.append(cr_members_name[index])

        cr_clanSettings = []
        cr_clanSettings.append(clandata['badge']['id'] == 16000002)
        cr_clanSettings.append(clandata['location']['name'] == "International")
        cr_clanSettings.append("UnderWorld Family🔥8 Clans🔥sites.google.com/view/underworldcr/home🔥Daily Tourneys🔥Weekly Clanwar🔥discord.me/underworldcr🔥" in clandata['description'])
        cr_clanSettings.append(clandata['type'] != "closed")

        message = ""

        if False in cr_clanSettings:
            message += "\n\n:warning: Problems in clan settings for **" + clan_name + "**:```"

            if cr_clanSettings[0] is False: message += "\n• Clan Badge is incorrect."
            if cr_clanSettings[1] is False: message += "\n• Clan Location is incorrect."
            if cr_clanSettings[2] is False: message += "\n• Clan description is incorrect."
            if cr_clanSettings[3] is False: message += "\n• Clan is closed."

            message += "```"

        if cr_members_with_no_player_tag:
            message += "\n\n:warning: **("+str(len(cr_members_with_no_player_tag))+")** Players in **" + clan_name + "**, but have **NOT** joined discord: ```• "
            message += "\n• ".join(cr_members_with_no_player_tag)
            message += "```"

        if d_members_with_no_player_tag:
            message += "\n\n:warning: **("+str(len(d_members_with_no_player_tag))+")** Players with **" + clan_name + "** role, but have **NO** tags saved: ```• "
            message += "\n• ".join(d_members_with_no_player_tag)
            message += "```"

        if d_members_not_in_clan:
            message += "\n\n:warning: **("+str(len(d_members_not_in_clan))+")** Players with **" + clan_name + "** role, but have **NOT** joined the clan: ```• "
            message += "\n• ".join(d_members_not_in_clan)
            message += "```"

        if d_members_without_role:
            message += "\n\n:warning: **("+str(len(d_members_without_role))+")** Players in **" + clan_name + "**, but **DO NOT** have the clan role: ```• "
            message += "\n• ".join(d_members_without_role)
            message += "```"

        if cr_members_with_less_trophies:
            message += "\n\n:warning: **("+str(len(cr_members_with_less_trophies))+")** Players in **" + clan_name + "**, but **DO NOT** meet the trophy requirements: ```• "
            message += "\n• ".join(cr_members_with_less_trophies)
            message += "```"

        if message == "":
            message += "Congratulations, your clan has no problems found so far. Kudos!"

        await self.bot.say(message)

    @commands.command()
    async def topmembers(self, number=10):
        """Show Top UnderWorld Family Members"""

        if number > 100:
            await self.bot.say("Sorry! the number must be below 50.")
            return

        await self.bot.say("**UnderWorld Family Top Players**")
        await self.bot.type()

        allplayers = requests.get('http://cr-api.com/clan/family/uwrl/members/datatable', timeout=15).json()
        players = dict(allplayers)
        players['data'] = sorted(allplayers['data'], key=lambda x: x["family_rank_score"])

        message = "```py\n"
        for x in range(0, number):
            message += str(x + 1).zfill(2) + ".  [" + str(players['data'][x]['score']) + "]  " + players['data'][x]['name'] + " (" + players['data'][x]['clan_name'] + ") " + "\n"
            if (x+1) % 40 == 0:
                message += "```"
                await self.bot.say(message)
                message = "```py\n"

        message += "```"

        await self.bot.say(message)

    @commands.command(pass_context=True, no_pm=True)
    async def guest(self, ctx, member: discord.Member):
        """Toggle waiting Role for members"""
        server = ctx.message.server
        author = ctx.message.author

        allowed = await self._is_commander(author)

        if not allowed:
            await self.bot.say("You dont have enough permissions to assign guest role. Type !contact to ask for help.")
            return

        role = discord.utils.get(server.roles, name="Guest")
        try:
            await self.bot.add_roles(member, role)
        except discord.Forbidden:
            raise
        except discord.HTTPException:
            raise
        await self.bot.say("{} Role Added to {}".format(role.name, member.display_name))

    @commands.command(pass_context=True, no_pm=True)
    async def inactive(self, ctx, member: discord.Member):
        """Use this command after kicking people from clan"""

        server = ctx.message.server
        author = ctx.message.author
        underworldServer = ["396607086533804042"]

        if server.id not in underworldServer:
            await self.bot.say("This command can only be executed in the UnderWorld Family Server")
            return

        allowed = await self._is_commander(author)

        if not allowed:
            await self.bot.say("You dont have enough permissions to delete someone to the waiting list. Type !contact to ask for help.")
            return

        try:
            await self.updateClash()
            await self.bot.type()
            profiletag = self.clash[member.id]['tag']
            profiledata = requests.get('http://api.cr-api.com/player/{}?exclude=games,currentDeck,cards,battles,achievements'.format(profiletag), headers=self.getAuth(), timeout=10).json()
            ign = profiledata['name']
            if profiledata['clan'] is None:
                clantag = ""
                clanname = ""
            else:
                clantag = profiledata['clan']['tag']
                clanname = profiledata['clan']['name']
        except (requests.exceptions.Timeout, json.decoder.JSONDecodeError):
            await self.bot.say("Error: cannot reach Clash Royale Servers. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            await self.bot.say(e)
            return
        except:
            await self.bot.say("You must assosiate a tag with this member first using ``!save clash #tag @member``")
            return

        membership = True
        for clankey in self.clanArray():
            if self.c[clankey]['tag'] == clantag:
                membership = False # False
                savekey = clankey
                break

        if membership:
            rolesToRemove = ["Member"]
            for x in range(0,self.numClans()):
                rolesToRemove.append(self.c[clankey]['role'])

            await self._remove_roles(member, rolesToRemove)

            await self.bot.send_message(member, "Hey there, I am sorry to inform you that we have removed you from the clan. We hope to see you back again soon when you are able to follow the clan requirements.")

            await self.bot.say("Member and clan roles removed.")
        else:
            await self.bot.say("Error, This user is still in a clan in the family.")

    @commands.command()
    async def gmt(self):
        """Get the currect GMT time"""
        await self.bot.say(datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M GMT"))


def check_folders():
    if not os.path.exists("data/underworld"):
        print("Creating data/underworld folder...")
        os.makedirs("data/undeworld")

def check_files():
    f = "cogs/tags.json"
    if not fileIO(f, "check"):
        print("Creating empty tags.json...")
        dataIO.save_json(f, {})

    f = "cogs/clans.json"
    if not fileIO(f, "check"):
        print("Creating empty clans.json...")
        dataIO.save_json(f, {})

    f = "cogs/auth.json"
    if not fileIO(f, "check"):
        print("Creating empty auth.json...")
        dataIO.save_json(f, {})

def check_clans():
    c = dataIO.load_json('cogs/clans.json')
    for clankey in c.keys():
        if 'waiting' not in c[clankey]:
            c[clankey]['waiting'] = []
        if 'bonustitle' not in c[clankey]:
            c[clankey]['bonustitle'] = ""
        if 'personalbest' not in c[clankey]:
            c[clankey]['personalbest'] = 0
    dataIO.save_json('cogs/clans.json', c)

def check_auth():
    c = dataIO.load_json('cogs/auth.json')
    if 'token' not in c:
        c['token'] = ""
    dataIO.save_json('cogs/auth.json', c)

def setup(bot):
    check_folders()
    check_files()
    check_clans()
    check_auth()
    bot.add_cog(underworld(bot))
