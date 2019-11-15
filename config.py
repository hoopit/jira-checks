import os
from enum import Enum


class CheckStatus(Enum):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILURE = 'failure'
    ERROR = 'error'


class Config:
    """
    User configuration
    """
    check_name = os.getenv('GITHUB_CHECK_NAME')

    jira_cloud_url = os.getenv('JIRA_CLOUD_URL')
    jira_user = os.getenv('JIRA_USER')
    jira_api_key = os.getenv('JIRA_API_KEY')

    github_url = os.getenv('GITHUB_URL')
    github_user = os.getenv('GITHUB_USER')
    github_api_key = os.getenv('GITHUB_API_KEY')
