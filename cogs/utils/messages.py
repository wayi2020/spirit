import asyncio

import discord

from cogs.utils import constants


def delete_all(message):
    """Helper function used to delete messages"""
    return True;


async def clear_messages(bot, messages):
    """Delete messages after a delay"""
    await asyncio.sleep(constants.SPAM_DELAY)
    for message in messages:
        if not message.channel.is_private:
            await bot.delete_message(message)


class MessageManager:

    def __init__(self, bot, user, channel, message):
        self.bot = bot
        self.user = user
        self.channel = channel
        self.messages = [message]

    async def say_and_wait(self, content, mention=True):
        """Send a message and wait for user's response"""
        msg = await self.bot.send_message(self.channel, "{}: {}".format(self.user.mention, content))
        self.messages.append(msg)
        res = await self.bot.wait_for_message(author=self.user, channel=self.channel)

        # If the user responds with a command, we'll need to stop executing and clean up
        if res.content.startswith('!'):
            await self.clear()
            return False
        else:
            self.messages.append(res)
            return res

    async def say(self, content, embed=False, delete=True, mention=True):
        """Send a single message"""
        msg = None
        if embed:
            msg = await self.bot.send_message(self.channel, embed=content)
        else:
            msg = await self.bot.send_message(self.channel, "{}: {}".format(self.user.mention, content))
        if delete:
            self.messages.append(msg)

    async def clear(self):
        """Delete all messages"""
        await clear_messages(self.bot, self.messages)