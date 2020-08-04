import os
import datetime
import argparse
import configparser
import discord
try:
    from dokuwikixmlrpc import DokuWikiClient, DokuWikiXMLRPCError
except ImportError:
    print('Python package dokuwikixmlrpc not installed.')
    print('You may want to run something like `pip3 install dokuwikixmlrpc --user -U`')
    exit(1)


TYPE_TO_VERB = {
    'C': 'créée',
    'E': 'modifiée',
    'D': 'supprimée'
}


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def get_config_from_cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('configfile', type=str, help='ini file containing all important info')
    filename = parser.parse_args().configfile
    config = configparser.ConfigParser()
    config.read(os.path.expanduser(filename))
    return config


class Discoku(discord.Client):
    def __init__(self, discord_channel:str, discord_channel_id:str, discord_idle:int, dokuconfig, discord_message:str, discord_message_no_summary:str):
        self.discord_channel = discord_channel
        self.discord_channel_id = discord_channel_id or None
        self.channel_object = None
        self.discord_idle = int(discord_idle)
        self.dokuwiki_idle = int(dokuconfig['idle_time'])
        self.next_dokuwiki_check_at = self.next_dokuwiki_check()
        self.dokuconfig = dokuconfig
        self.last_dokuwiki_check = now()
        self.discord_message, self.discord_message_no_summary = discord_message, discord_message_no_summary
        super().__init__()

    def next_discord_check(self) -> datetime.datetime:
        return now()+datetime.timedelta(seconds=self.discord_idle)
    def next_dokuwiki_check(self) -> datetime.datetime:
        return now()+datetime.timedelta(seconds=self.dokuwiki_idle)

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))
        # try to get the correct channel object
        self.channel_object = self.get_channel(int(self.discord_channel_id)) if self.discord_channel_id else None
        while True:
            await discord.utils.sleep_until(self.next_discord_check())
            # print('CHANNEL:', self.channel_object)
            if self.channel_object:
                for msg in self.dokuwiki_news():
                    await self.channel_object.send(msg)

    async def on_message(self, message):
        # wait to get the reference to the channel object
        # that's needed to be done manually once, to get the
        if self.channel_object is None and self.discord_channel == str(message.channel):
            print('Channel ID found:', message.channel.id)
            print('You should consider adding it in your config file.')
            self.channel_object = self.get_channel(message.channel.id)


    def dokuwiki_news(self):
        """Yield messages giving human readable info about remote dokuwiki informations"""
        if self.next_dokuwiki_check_at > now():  # do nothing
            return
        client = DokuWikiClient(self.dokuconfig['url'], self.dokuconfig['login'], self.dokuconfig['password'])
        try:
            changes = client.recent_changes(int(self.last_dokuwiki_check.timestamp()))
        except DokuWikiXMLRPCError as err:
            if err.message != 'There are no changes in the specified timeframe':
                raise
            else:
                changes = []  # no changes
        # if not changes:
            # print('No change')
        for change in changes:
            # print(change)
            versions = client.page_versions(change['name'])
            last = versions[0]
            # print('\t', versions)
            verb = self.dokuconfig[last['type']]
            page_url = self.dokuconfig['url'].rstrip('/') + '/' + change['name']
            message = self.discord_message if last['sum'] else self.discord_message_no_summary
            yield message.format(page=change['name'], verb=verb, author=change['author'], summary=discord.utils.escape_markdown(last['sum'])[:50], link=page_url)
        self.last_dokuwiki_check = now()
        self.next_dokuwiki_check_at = self.next_dokuwiki_check()


if __name__ == '__main__':
    config = get_config_from_cli()
    client = Discoku(config['discord']['channel'], config['discord'].get('channel_id', None), config['discord']['idle_time'], config['dokuwiki'], config['trigger']['message'], config['trigger']['message_no_sum'])
    client.run(config['discord']['api_token'])
