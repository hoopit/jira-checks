# jira-checks
Github checks integration for Jira status

AWS Lambda implementation that handles webhooks from Jira and updates status checks on Github for related PRs.

# Installation

## Webhook configuration
1. Update configuration in config.py.
2. Deploy using serverless.

## Jira configuration
#### Create webhook 
Add webhook https://\<host>.atlassian.net/plugins/servlet/webhooks, point it to the deployed function.
- Events: None
- Exclude body: No

#### Update workflow
For each transition that should update the github status
1. Add required transition properties:
    - githubCheckState: pending, success, failure, error (refer to github docs)
    - githubCheckDescription: \<state description>

2. Add post function:
    - Add call to the webhook configured above. 



