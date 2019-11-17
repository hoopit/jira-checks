import json
from typing import Dict, Tuple

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


def _get_status_properties(workflow_name: str, status_name: str) -> Tuple[str, str]:
    workflow = JiraClient().get_workflow(workflow_name)
    statuses = workflow['values'][0]['statuses']
    target_status = next(x for x in statuses if x['name'] == status_name)
    properties = target_status['properties']
    state = next(x['value'] for x in properties if x['key'] == 'githubCheckState')
    description = next(x['value'] for x in properties if x['key'] == 'githubCheckDescription')
    return state, description


def _get_transition_properties(transition_id: int, workflow_name: str) -> Tuple[str, str]:
    properties = JiraClient().get_transition_properties(transition_id, workflow_name)
    state = next(x['value'] for x in properties if x['key'] == 'githubCheckState')
    description = next(x['value'] for x in properties if x['key'] == 'githubCheckDescription')
    return state, description


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
    properties = _get_transition_properties(transition_event.transitionId, transition_event.workflowName)
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
