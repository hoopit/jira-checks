from __future__ import annotations, absolute_import

import json
import os
from typing import Dict, Tuple, Optional

from GithubClient import GithubClient
from config import Config
from jira import JiraClient, TransitionEvent


def enable_debug_logging():
    import logging
    # http.client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def _get_status_properties(transition_event: TransitionEvent) -> Optional[Tuple[str, str]]:
    new_status = transition_event.to_status.replace(" ", "_").capitalize()
    state = os.getenv(f"STATUS_{new_status}_STATE")
    desc = os.getenv(f"STATUS_{new_status}_DESC")
    if not state or not desc:
        return None
    return state, desc


def _get_transition_properties(transition_event: TransitionEvent) -> Tuple[str, str]:
    properties = JiraClient().get_transition_properties(transition_event.transitionId, transition_event.workflowName)
    state = next(x['value'] for x in properties if x['key'] == 'githubCheckState')
    description = next(x['value'] for x in properties if x['key'] == 'githubCheckDescription')
    return state, description


def _get_properties(transition_event: TransitionEvent):
    return _get_status_properties(transition_event) or _get_transition_properties(transition_event)


def handle_transition(event: dict, context) -> Dict:
    """
    Jira transition webhook handler
    :param event: AWS Lambda proxy event
    :param context: AWS context
    :return: Http response
    """
    enable_debug_logging()
    print(f"event: {json.dumps(event)}")
    body: Dict = json.loads(event['body'])
    print(f"body: {json.dumps(body)}")
    transition_event = TransitionEvent(data=body)
    properties = _get_transition_properties(transition_event)
    payload = {
        'context': Config.check_name,
        'target_url': f'{Config.jira_cloud_url}/browse/{transition_event.issue_key}',
        'state': properties[0],
        'description': properties[1]
    }
    print(f"payload: {json.dumps(payload)}")
    if payload:
        pull_requests = JiraClient().get_pull_requests(transition_event.issue_id)
        for pull_request in pull_requests['detail'][0]['pullRequests']:
            number = pull_request['id'].replace('#', '')
            url = pull_request['source']['url']
            (owner, repo, branch) = url.replace('https://github.com/', '').split('/', 2)
            r = GithubClient().get_pull_request(owner=owner, repo=repo, number=number)
            r = GithubClient().post(r['statuses_url'], payload=payload)
            print(f"github response: {json.dumps(r.json())}")
    else:
        print("No handler for event: Ignoring...")
    return {"statusCode": 200}
