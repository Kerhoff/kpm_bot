import requests
import os


OPEN_STORIES_QUERY= os.environ['OPEN_STORIES_QUERY']
RESOLVED_STORIES_QUERY= os.environ['RESOLVED_STORIES_QUERY']
JIRA_URL: str = os.environ['JIRA_URL']
JIRA_LOGIN: str = os.environ['JIRA_LOGIN']
JIRA_PASSWORD: str = os.environ['JIRA_PASSWORD']

auth_data: tuple = (JIRA_LOGIN, JIRA_PASSWORD)


def _request(endpoint, query):
    headers = {"User-Agent":
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
               }
    response = requests.get(JIRA_URL + endpoint,
                            params=query,
                            auth=auth_data,
                            headers=headers)
    response.raise_for_status()
    return response.json()


def get_open_stories():
    query = {'jql': f'{OPEN_STORIES_QUERY}', 'startAt': 0, 'maxResults': 100}
    data = _request("/search", query)
    return data['issues']

def get_resolved_stories():
    query = {'jql': f'{RESOLVED_STORIES_QUERY}', 'startAt': 0, 'maxResults': 100}
    data = _request("/search", query)
    return data['issues']

