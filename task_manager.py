import os
import logging

from interfaces import trello
from interfaces import jira

JIRA_LINK = os.environ['JIRA_LINK']
TRELLO_INBOX = os.environ['INBOX_ID']

DATA: dict = {}
UNKNOWN_CARDS: list = []
NEW_STORIES: list = []


def load_data() -> bool:
    global DATA
    if DATA:
        return True
    else:
        cards: list = trello.get_cards_on_board()
        open_stories: list = jira.get_open_stories()
        resolved_stories: list = jira.get_resolved_stories()
        if cards and open_stories and resolved_stories:
            DATA = {'cards': cards, 'open_stories': open_stories, 'resolved_stories': resolved_stories}
            return True
        else:
            return False


def update_data() -> bool:
    global DATA
    cards: list = trello.get_cards_on_board()
    open_stories: list = jira.get_open_stories()
    resolved_stories: list = jira.get_resolved_stories()
    if cards and open_stories and resolved_stories:
        DATA = {'cards': cards, 'open_stories': open_stories, 'resolved_stories': resolved_stories}
        return True
    else:
        return False


def get_resolved_cards() -> dict:
    global DATA

    cards: list = DATA['cards']
    resolved_stories: list = DATA['resolved_stories']

    resolved_stories_keys: set = set([story['key'] for story in resolved_stories])
    resolved_cards = [card for card in cards if card['desc'].split('/')[-1].split(')')[0] in resolved_stories_keys]

    names_of_resolved_cards: str = ""
    for card in resolved_cards:
        names_of_resolved_cards += f"\r\n<a href=\"{card['shortUrl']}\">{card['name']}</a>"

    message: str = f"<strong>Resolved in JIRA</strong>\r\nNum: <strong>{len(resolved_cards)}</strong>\r\nNames:{names_of_resolved_cards}"

    return {'message': message}


def get_unknown_or_closed_cards() -> dict:
    global DATA
    global UNKNOWN_CARDS

    cards: list = DATA['cards']
    open_stories: list = DATA['open_stories']
    resolved_stories: list = DATA['resolved_stories']

    open_stories_keys: set = set([story['key'] for story in open_stories])
    cards_not_in_open_stories: list = [card for card in cards if
                                       card['desc'].split('/')[-1].split(')')[0] not in open_stories_keys]

    resolved_stories_keys: set = set([story['key'] for story in resolved_stories])
    UNKNOWN_CARDS = [card for card in cards_not_in_open_stories if
                 card['desc'].split('/')[-1].split(')')[0] not in resolved_stories_keys]

    unknown_card_names: str = ""
    for card in UNKNOWN_CARDS:
        unknown_card_names += f"\r\n<a href=\"{card['shortUrl']}\">{card['name']}</a>"

    message: str = f"<strong>Unknown or Closed Cards</strong>\r\nNum: <strong>{len(UNKNOWN_CARDS)}</strong>\r\nNames:{unknown_card_names}"

    return {'message': message}


def get_open_stories_without_card() -> dict:
    global DATA
    global NEW_STORIES

    cards = DATA['cards']
    open_stories = DATA['open_stories']

    cards_set: set = set([card['desc'].split('/')[-1].split(')')[0] for card in cards])
    NEW_STORIES = [story for story in open_stories if story['key'] not in cards_set]

    story_summaries: str = ""
    for story in NEW_STORIES:
        story_summaries += f"\r\n<a href=\"{JIRA_LINK}/{story['key']}\">{story['fields']['summary']}</a>"

    message: str = f"<strong>Stories without Card</strong>\r\nNum: <strong>{len(NEW_STORIES)}</strong>\r\nSummaries:{story_summaries}"
    return {'message': message}


def create_new_stories_cards_on_board(new_stories=None) -> dict:
    success = 0
    fail = 0

    if new_stories is None:
        new_stories = NEW_STORIES

    for story in new_stories:
        name = story['fields']['summary']
        key = story['key']
        description = f'[{key}]({JIRA_LINK}/{key})'

        create_card_result: str = trello.create_card(name, description, list_id=TRELLO_INBOX)
        if create_card_result:
            success += 1
        else:
            fail += 1
    message = f"Creating result:\r\nSuccess - {success}\r\nFail - {fail}"
    return {'message': message}


def delete_unknown_cards(unknown_cards=None) -> dict:
    success: int = 0
    fail: int = 0

    if unknown_cards is None:
        unknown_cards = UNKNOWN_CARDS

    for card in unknown_cards:
        delete_card_result: str = trello.delete_card(card['id'])
        if delete_card_result:
            success += 1
        else:
            fail += 1

    message: str = f"Delete result:\r\nSuccess - {success}\r\nFail - {fail}"
    return {'message': message}
