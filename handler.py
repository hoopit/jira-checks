import json
from typing import Dict

from GithubClient import GithubClient
from config import Config
from jira import JiraClient, TransitionEvent


def enable_debug_logging():
    import logging
    import http.client
    http.client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def handle_transition(event, context) -> Dict:
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
    properties = JiraClient().get_transition_properties(transition_event.transitionId, transition_event.workflowName)
    payload = {
        'context': Config.check_name,
        'target_url': f'{Config.jira_cloud_url}/browse/{transition_event.issue_key}',
        'state': next((x['value'] for x in properties if x['key'] == 'githubCheckState'), None),
        'description': next((x['value'] for x in properties if x['key'] == 'githubCheckDescription'), None)
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
