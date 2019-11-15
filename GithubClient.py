import requests
from requests import Response
from requests.auth import HTTPBasicAuth

from config import Config


class GithubClient:
    """
    Github REST client
    """

    auth = HTTPBasicAuth(Config.github_user, Config.github_api_key)

    def __init__(self) -> None:
        super().__init__()

    def update_status(self, repo, sha, payload) -> Response:
        return requests.post(rf"{Config.github_url}/repos/{repo}/statuses/{sha}",
                             auth=self.auth,
                             json=payload)

    def get_pull_request(self, owner, repo, number):
        return requests.get(f'{Config.github_url}/repos/{owner}/{repo}/pulls/{number}',
                            auth=self.auth).json()

    def post(self, url, payload):
        return requests.post(url,
                             auth=self.auth,
                             json=payload)
