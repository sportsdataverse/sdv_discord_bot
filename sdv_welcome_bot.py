"""SportsDataverse Discord welcome gate.

Newcomers get the `unverified` role on join. Their first post in the
introductions channel swaps it for `sdv-team`, which unlocks the rest of the
server, and their intro is reposted to #general so people can say hello.

The same Discord application's token also mints the per-person /join invites
in sportsdataverse-web (REST only), and those invites land in the same
introductions channel.
"""

import logging
import os

import discord

GUILD_ID = 798201448843837500
INTRO_CHANNEL_ID = 849715155415203890
SDV_TEAM_ROLE_ID = 821195094639247390
UNVERIFIED_ROLE_ID = 1008955473225072661
GENERAL_CHANNEL_NAME = "general"
PROMPT_TTL_SEC = 30  # the join prompt and the welcome ack delete themselves

log = logging.getLogger("sdv_welcome_bot")


def needs_promotion(
    channel_id: int, author_is_bot: bool, author_role_ids: set[int]
) -> bool:
    """A human's post in the intro channel promotes them, once."""
    return (
        channel_id == INTRO_CHANNEL_ID
        and not author_is_bot
        and SDV_TEAM_ROLE_ID not in author_role_ids
    )


def repost_text(mention: str, content: str) -> str:
    """The #general repost, kept under Discord's 2000-character message cap."""
    head = f"{mention} has joined the server!\n"
    body = (
        content
        if len(head) + len(content) <= 2000
        else content[: 2000 - len(head) - 1] + "…"
    )
    return head + body


intents = discord.Intents.default()
intents.members = True  # privileged: on_member_join
intents.message_content = True  # privileged: the intro text reposted to #general
client = discord.Client(intents=intents)


@client.event
async def on_ready() -> None:
    log.info("logged in as %s", client.user)


@client.event
async def on_member_join(member: discord.Member) -> None:
    if member.guild.id != GUILD_ID or member.bot:
        return
    await member.add_roles(
        discord.Object(UNVERIFIED_ROLE_ID), reason="newcomer: awaiting introduction"
    )
    log.info("unverified: %s (%s)", member, member.id)
    channel = member.guild.get_channel(INTRO_CHANNEL_ID)
    if isinstance(channel, discord.TextChannel):
        await channel.send(
            f"{member.mention}, welcome! To access the server, please verify yourself by sending a quick "
            "introduction while mentioning who invited you. This message will soon self-destruct.",
            delete_after=PROMPT_TTL_SEC,
        )


@client.event
async def on_message(message: discord.Message) -> None:
    if message.guild is None or message.guild.id != GUILD_ID:
        return
    author = message.author
    if not isinstance(author, discord.Member):  # webhooks, departed members
        return
    if not needs_promotion(
        message.channel.id, author.bot, {r.id for r in author.roles}
    ):
        return
    # add before remove, so a failure in between never leaves them with neither role
    await author.add_roles(
        discord.Object(SDV_TEAM_ROLE_ID), reason="posted an introduction"
    )
    await author.remove_roles(
        discord.Object(UNVERIFIED_ROLE_ID), reason="posted an introduction"
    )
    log.info("promoted: %s (%s)", author, author.id)
    await message.channel.send(
        f"Welcome, {author.mention}! You are now free to explore the SDV server! We are excited to have you here.",
        delete_after=PROMPT_TTL_SEC,
    )
    general = discord.utils.get(message.guild.text_channels, name=GENERAL_CHANNEL_NAME)
    if general is not None:
        # the intro is untrusted text: ping only its author, never @everyone or a role
        await general.send(
            repost_text(author.mention, message.content),
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False, users=[author]
            ),
        )


if __name__ == "__main__":
    client.run(os.environ["DISCORD_BOT_TOKEN"], root_logger=True)
