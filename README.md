# sdv_discord_bot

The SportsDataverse Discord welcome gate:

1. Anyone who joins gets the `unverified` role, and a prompt in the introductions channel.
2. Their first post in the introductions channel swaps `unverified` for `sdv-team`. That
   unlocks the private channels, and their intro is reposted to #general.

The same Discord application's token also mints the per-person invites for
[sportsdataverse.org/join](https://sportsdataverse.org/join) (`DISCORD_BOT_TOKEN` in the
sportsdataverse-web Vercel project). Those invites land in the introductions channel too.

The ids (server, introductions channel, both roles) are constants at the top of
`sdv_welcome_bot.py`.

## One-time Discord setup

In the [Developer Portal](https://discord.com/developers/applications), open the application,
then go to **Bot**:

- **Public Bot**: off.
- **Privileged Gateway Intents**: turn on **Server Members** (for joins) and **Message
  Content** (for the #general repost). Presence stays off.

Add the application to the server with this URL:

```
https://discord.com/oauth2/authorize?client_id=<APPLICATION_ID>&scope=bot&permissions=268438529
```

`268438529` grants View Channels, Send Messages, Manage Roles, and Create Invite. Create
Invite is used by the website.

Then, in **Server Settings → Roles**, drag the application's role **above `sdv-team` and
`unverified`**. Discord refuses role changes on roles that sit higher than the bot's own
role; the log shows `403 Forbidden (error code: 50013)`.

## Run it (droplet)

```sh
uv sync --no-dev
install -d -m 700 /etc/sdv-discord-bot
install -m 600 /dev/null /etc/sdv-discord-bot/sdv-discord-bot.env
$EDITOR /etc/sdv-discord-bot/sdv-discord-bot.env     # DISCORD_BOT_TOKEN=...
cp deploy/sdv-discord-bot.service /etc/systemd/system/
systemctl daemon-reload && systemctl enable --now sdv-discord-bot
journalctl -u sdv-discord-bot -f                     # "logged in as ...", then one line per join/promotion
```

## Tests

```sh
uv run pytest
```
