import json

from boto3 import client
from os import getenv

codeguru_reviewer = client('codeguru-reviewer')
stepfunctions = client('stepfunctions')
ASSOCIATED_REPO = getenv('ASSOCIATED_REPOSITORY')
CODEGURU_REVIEWER_STATE_MACHINE_ARN = getenv('CODEGURU_REVIEWER_STATE_MACHINE_ARN')


def lambda_handler(event, context):
    """
    Function to check pending Pull Request Code Reviews
    :param event:
    :param context:
    :return:
    """
    response = codeguru_reviewer.list_code_reviews(
        ProviderTypes=['Bitbucket', 'GitHub', 'GitHubEnterpriseServer'],
        States=['Pending'],
        RepositoryNames=[ASSOCIATED_REPO],
        Type='PullRequest',
        MaxResults=50
    )
    summaries = response['CodeReviewSummaries']
    print(summaries)
    if len(summaries) > 0:
        # for each start a state machine execution
        list(map(start_codeguru_reviewer_state_machine, summaries))
    return {
        'status': 200
    }


def start_codeguru_reviewer_state_machine(summary):
    """
    Function starts a state machine for summary
    :param summary:
    :return:
    """
    code_review_name = summary['Name']
    code_review_arn = summary['CodeReviewArn']
    owner = summary['Owner']
    pull_request_id = summary['PullRequestId']
    state_machine_input = dict(
        Name=code_review_name,
        CodeReviewArn=code_review_arn,
        Owner=owner,
        PullRequestId=pull_request_id
    )
    response = stepfunctions.start_execution(
        stateMachineArn=CODEGURU_REVIEWER_STATE_MACHINE_ARN,
        name=f'codeguru-pr-{pull_request_id}-review',
        input=json.dumps(state_machine_input)
    )
    return None
