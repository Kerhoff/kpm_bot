import requests
import os


TRELLO_URL = os.environ['TRELLO_URL']
TRELLO_BOARD = os.environ['BOARD']
TRELLO_API_KEY = os.environ['TRELLO_API_KEY']
TRELLO_API_TOKEN = os.environ['TRELLO_API_TOKEN']

authData: dict = {'key': TRELLO_API_KEY, 'token': TRELLO_API_TOKEN}


def _get_request(endpoint, params=None):
    if params is None:
        params = authData
    else:
        params.update(authData)
    
    headers = {"Accept": "application/json"}
    
    response = requests.get(TRELLO_URL + endpoint, params=params, headers=headers)
    return response.json()


def _post_request(endpoint, data=None):
    if data is None:
        data = authData
    else:
        data.update(authData)
    
    response = requests.post(TRELLO_URL + endpoint, data=data)
    return response


def _delete_request(endpoint):
    return requests.delete(TRELLO_URL + endpoint, params=authData)        


def get_user_info() -> dict:
    return _get_request("/members/me/")


def get_boards() -> list:
    return _get_request("/members/me/boards", {'fields': ['name', 'url']})


def get_lists(board_id) -> list:
    return _get_request(f"/boards/{board_id}/lists")


def get_cards_on_board() -> list:
    boards: list = get_boards()
    board_id: str = ''.join([board['id'] for board in boards if board['name'] == TRELLO_BOARD])
    return _get_request(f"/boards/{board_id}/cards")


def create_card(name, description, list_id) -> str:
    return _post_request(f"/cards", {'name': name, 'desc': description, 'idList': list_id})


def delete_card(card_id) -> str:
    return _delete_request(f"/cards/{card_id}")
