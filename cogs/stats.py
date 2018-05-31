from discord.ext import commands
import discord

import pydest

from cogs.utils.message_manager import MessageManager
from cogs.utils import constants, helpers
from cogs.embed_builders import pvp_stats_embed
from cogs.models.pvp_stats import PvPStats


class Stats:

    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def stats(self, ctx):
        """Display various Destiny 2 stats"""
        if ctx.invoked_subcommand is None:
            cmd = self.bot.get_command('help')
            await ctx.invoke(cmd, 'stats')


    @stats.command()
    async def pvp(self, ctx, username=None, platform=None):
        """Display PvP stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats pvp` - Display your PvP stats (preferred platform)
        \$`stats pvp Asal#1502 bnet` - Display Asal's PvP stats on Battle.net
        \$`stats pvp @user` - Display a registered user's PvP stats (preferred platform)
        \$`stats pvp @user bnet` - Display a registered user's PvP stats on Battle.net
        """
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        pvp_stats_json = (await self.get_stats(platform_id, membership_id, [5]))['allPvP']['allTime']
        if not pvp_stats_json:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        pvp_stats = PvPStats(pvp_stats_json)
        await manager.send_embed(pvp_stats_embed(pvp_stats, "Crucible Stats", display_name, platform_id))
        await manager.clean_messages()


    @stats.command()
    async def pve(self, ctx, username=None, platform=None):
        """Display PvE stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats pve` - Display your PvE stats (preferred platform)
        \$`stats pve Asal#1502 bnet` - Display Asal's PvE stats on Battle.net
        \$`stats pve @user` - Display a registered user's PvE stats (preferred platform)
        \$`stats pve @user bnet` - Display a registered user's PvE stats on Battle.net
        """
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        pve_stats = await self.get_stats(platform_id, membership_id, [7,4,16,18])
        if not pve_stats:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        time_played = pve_stats['allPvE']['allTime']['totalActivityDurationSeconds']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0
        best_weapon = pve_stats['allPvE']['allTime']['weaponBestType']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0
        num_heroic_events = pve_stats['allPvE']['allTime']['heroicPublicEventsCompleted']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0
        num_events = pve_stats['allPvE']['allTime']['publicEventsCompleted']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0
        num_raids = pve_stats['raid']['allTime']['activitiesCleared']['basic']['displayValue'] if len(pve_stats['raid']) else 0
        raid_time = pve_stats['raid']['allTime']['totalActivityDurationSeconds']['basic']['displayValue'] if len(pve_stats['raid']) else 0
        num_nightfall = pve_stats['nightfall']['allTime']['activitiesCleared']['basic']['displayValue'] if len(pve_stats['nightfall']) else 0
        num_strikes = pve_stats['allStrikes']['allTime']['activitiesCleared']['basic']['displayValue'] if len(pve_stats['allStrikes']) else 0
        fastest_nightfall = pve_stats['nightfall']['allTime']['fastestCompletionMs']['basic']['displayValue'] if len(pve_stats['nightfall']) else 0
        kills = pve_stats['allPvE']['allTime']['kills']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0
        assists = pve_stats['allPvE']['allTime']['assists']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0
        deaths = pve_stats['allPvE']['allTime']['deaths']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0

        e = discord.Embed(colour=constants.BLUE)
        e.set_author(name="{} | PvE Stats".format(display_name), icon_url=constants.PLATFORM_URLS.get(platform_id))
        e.add_field(name='Kills', value=kills, inline=True)
        e.add_field(name='Assists', value=assists, inline=True)
        e.add_field(name='Deaths', value=deaths, inline=True)
        e.add_field(name='Strikes', value=num_strikes, inline=True)
        e.add_field(name='Nightfalls', value=num_nightfall, inline=True)
        e.add_field(name='Fastest Nightfall', value=fastest_nightfall, inline=True)
        e.add_field(name='Public Events', value=num_events, inline=True)
        e.add_field(name='Heroic Public Events', value=num_heroic_events, inline=True)
        e.add_field(name='Favorite Weapon', value=best_weapon, inline=True)
        e.add_field(name='Total Raid Time', value=raid_time, inline=True)
        e.add_field(name='Raids', value=num_raids, inline=True)
        e.add_field(name='Time Played', value=time_played, inline=True)

        await manager.send_embed(e)
        await manager.clean_messages()


    @stats.command()
    async def trials(self, ctx, username=None, platform=None):
        """Display Trials stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats trials` - Display your Trials stats (preferred platform)
        \$`stats trials Asal#1502 bnet` - Display Asal's Trials stats on Battle.net
        \$`stats trials @user` - Display a registered user's Trials stats (preferred platform)
        \$`stats trials @user bnet` - Display a registered user's Trials stats on Battle.net
        """
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        trials_stats_json = (await self.get_stats(platform_id, membership_id, [39]))['trialsofthenine'].get('allTime')
        if not trials_stats_json:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        trials_stats = PvPStats(trials_stats_json)
        await manager.send_embed(pvp_stats_embed(trials_stats, "Trials of the Nine Stats", display_name, platform_id))
        await manager.clean_messages()


    @stats.command()
    async def ib(self, ctx, username=None, platform=None):
        """Display Iron Banner stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats ib` - Display your Iron Banner stats (preferred platform)
        \$`stats ib Asal#1502 bnet` - Display Asal's Iron Banner stats on Battle.net
        \$`stats ib @user` - Display a registered user's Iron Banner stats (preferred platform)
        \$`stats ib @user bnet` - Display a registered user's Iron Banner stats on Battle.net
        """
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        ib_stats_json = (await self.get_stats(platform_id, membership_id, [19]))['ironBanner'].get('allTime')
        if not ib_stats_json:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        ib_stats = PvPStats(ib_stats_json)
        await manager.send_embed(pvp_stats_embed(ib_stats, "Iron Banner Stats", display_name, platform_id))
        await manager.clean_messages()


    @stats.command()
    async def rumble(self, ctx, username=None, platform=None):
        """Display Rumble stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats rumble` - Display your Rumble stats (preferred platform)
        \$`stats rumble Asal#1502 bnet` - Display Asal's Rumble stats on Battle.net
        \$`stats rumble @user` - Display a registered user's Rumble stats (preferred platform)
        \$`stats rumble @user bnet` - Display a registered user's Rumble stats on Battle.net
        """
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        rumble_stats_json = (await self.get_stats(platform_id, membership_id, [48]))['rumble'].get('allTime')
        if not rumble_stats_json:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        rumble_stats = PvPStats(rumble_stats_json)
        await manager.send_embed(pvp_stats_embed(rumble_stats, "Rumble Stats", display_name, platform_id))
        await manager.clean_messages()


    @stats.command()
    async def doubles(self, ctx, username=None, platform=None):
        """Display Doubles stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats doubles` - Display your Doubles stats (preferred platform)
        \$`stats doubles Asal#1502 bnet` - Display Asal's Doubles stats on Battle.net
        \$`stats doubles @user` - Display a registered user's Doubles stats (preferred platform)
        \$`stats doubles @user bnet` - Display a registered user's Doubles stats on Battle.net
        """
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        doubles_stats_json = (await self.get_stats(platform_id, membership_id, [49]))['allDoubles'].get('allTime')
        if not doubles_stats_json:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        doubles_stats = PvPStats(doubles_stats_json)
        await manager.send_embed(pvp_stats_embed(doubles_stats, "Doubles Stats", display_name, platform_id))
        await manager.clean_messages()


    @stats.command()
    async def mayhem(self, ctx, username=None, platform=None):
        """Display Mayhem stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats mayhem` - Display your Mayhem stats (preferred platform)
        \$`stats mayhem Asal#1502 bnet` - Display Asal's Mayhem stats on Battle.net
        \$`stats mayhem @user` - Display a registered user's Mayhem stats (preferred platform)
        \$`stats mayhem @user bnet` - Display a registered user's Mayhem stats on Battle.net
        """
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        mayhem_stats_json = (await self.get_stats(platform_id, membership_id, [25]))['allMayhem'].get('allTime')
        if not mayhem_stats_json:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        mayhem_stats = PvPStats(mayhem_stats_json)
        await manager.send_embed(pvp_stats_embed(mayhem_stats, "Mayhem Stats", display_name, platform_id))
        await manager.clean_messages()


    async def get_stats(self, platform_id, membership_id, modes):
        try:
            res = await self.bot.destiny.api.get_historical_stats(platform_id, membership_id, groups=['general'], modes=modes)
        except:
            return
        if res['ErrorCode'] == 1:
            return res['Response']
