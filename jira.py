import json
from typing import Dict, List

import requests
from requests.auth import HTTPBasicAuth

from config import Config


class JiraRelatedCommit:
    """
    Represents a commit recognized by Jira, i.e. what you see when viewing the repository through Jira.
    """

    def __init__(self, commit, sha) -> None:
        self.repo = commit
        self.sha = sha


class ChangeLogEvent:
    """
    Represents a Jira changelog event.
    Part of the 'issue updated' webhook data.
    """

    def __init__(self, item) -> None:
        self.field = item['field']
        self.fieldId = item['fieldId']
        self.fromId = item['from']
        self.toId = item['to']


class IssueUpdatedEvent:
    """
    Represents a jira update webhook event
    """

    def __init__(self, data) -> None:
        self.issue_id = data['issue']['id']
        self.issue_key = data['issue']['key']
        self.change_log = None
        self.fromStatus = None
        self.toStatus = None
        self._process_changelog(data['changelog']['items'])

    def _process_changelog(self, changelog):
        for item in changelog:
            if item['fieldId'] == "status":
                self.fromStatus = item['from']
                self.toStatus = item['to']


class TransitionEvent:

    def __init__(self, data) -> None:
        super().__init__()
        transition = data['transition']
        self.workflowId = transition['workflowId']
        self.workflowName = transition['workflowName']
        self.transitionId = transition['transitionId']
        self.issue_id = data['issue']['id']
        self.issue_key = data['issue']['key']


class JiraClient:
    """
    Jira REST client
    """
    auth = HTTPBasicAuth(Config.jira_user, Config.jira_api_key)

    def __init__(self) -> None:
        super().__init__()

    def get_transition_properties(self, transition_id, workflow_name) -> List[Dict]:
        r = requests.get(
            f'{Config.jira_cloud_url}/rest/api/3/workflow/transitions/{transition_id}/properties?workflowName={workflow_name}',
            auth=self.auth,
        )
        print(json.dumps(r.json()))
        return r.json()

    def get_commits(self, issue_id):
        r = requests.get(
            f'{Config.jira_cloud_url}/rest/dev-status/1.0/issue/detail?issueId={issue_id}&applicationType=GitHub&dataType=pullrequest',
            auth=self.auth
        )
        print(json.dumps(r.json()))
        commits = []
        for branch in r.json()['detail'][0]['branches']:
            commits.append(JiraRelatedCommit(branch['repository']['name'], branch['lastCommit']['id']))
        return commits

    def get_pull_requests(self, issue_id):
        r = requests.get(
            f'{Config.jira_cloud_url}/rest/dev-status/1.0/issue/detail?issueId={issue_id}&applicationType=GitHub&dataType=pullrequest',
            auth=self.auth
        )
        print(json.dumps(r.json()))
        return r.json()
