from sdv_welcome_bot import (
    INTRO_CHANNEL_ID,
    SDV_TEAM_ROLE_ID,
    UNVERIFIED_ROLE_ID,
    needs_promotion,
    repost_text,
)


def test_only_a_human_without_sdv_team_posting_in_the_intro_channel_is_promoted():
    assert needs_promotion(INTRO_CHANNEL_ID, False, {UNVERIFIED_ROLE_ID})
    assert needs_promotion(
        INTRO_CHANNEL_ID, False, set()
    )  # joined while the bot was down
    assert not needs_promotion(
        INTRO_CHANNEL_ID, False, {SDV_TEAM_ROLE_ID, UNVERIFIED_ROLE_ID}
    )
    assert not needs_promotion(INTRO_CHANNEL_ID, True, {UNVERIFIED_ROLE_ID})
    assert not needs_promotion(INTRO_CHANNEL_ID + 1, False, {UNVERIFIED_ROLE_ID})


def test_repost_fits_discords_message_cap():
    assert repost_text("<@1>", "hi") == "<@1> has joined the server!\nhi"
    assert len(repost_text("<@1>", "x" * 2000)) == 2000
