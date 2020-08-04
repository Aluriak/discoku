# dokubot
A discord bot to announce new pages in a doku wiki.


## Setup & running
When running dokubot, it expects a single parameter : the (path to) configuration file.

    python -m discoku config.ini

The `config.ini` should looks like :

    [general]
    name = DiscokuBot
    [trigger]
    # push a discord message on new pages
    on_new_page = true
    # push a discord message on page modifications
    on_modification = false
    # messages sent on discord
    message = Page {page} was {verb} by {author} with message: *{summary}*              (link: {link})
    message_no_sum = Page {page} was {verb} by {author} without any explanation  (boooooh !)             (link: {link})
    [discord]
    api_token = HEREISSOMEVERYSECRETTOKEN
    channel = General
    # The discord channel id in which pushing the messages.
    #  If not given, will wait for a message in order to find the id.
    channel_id = 999999999999999999
    # seconds between two discord-side waits
    idle_time = 5
    [dokuwiki]
    url = https://wiki.example.net
    login = ADokuWikiLoginAbleToRTC
    password = AVERYSECRETPASSWORD
    # seconds between two dokuwiki checks
    idle_time = 11
    # dokuwiki vocabulary ({verb} in discord message)
    C = created
    D = deleted
    E = edited

Should be enough.
