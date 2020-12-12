from boto3 import client
from os import getenv

codeguru_reviewer = client('codeguru-reviewer')
sns = client('sns')
TEAM_EMAIL = getenv('TEAM_EMAIL')
CODEGURU_SNS_TOPIC = getenv('CODEGURU_SNS_TOPIC')


def lambda_handler(event, context):
    """
    Function to send email of recommendations to engineering team/recruiter
    :param event:
    :param context:
    :return:
    """
    code_review_arn = event['CodeReviewArn']
    response = codeguru_reviewer.list_recommendations(
        MaxResults=50,
        CodeReviewArn=code_review_arn
    )
    recommendation_summaries = response['RecommendationSummaries']
    num_of_reviews = event['Metrics']['FindingsCount']
    repo_name = event['RepositoryName']
    pr_id = event['PullRequestId']
    html_body = generate_html_reviews_email(event, recommendation_summaries)
    email_subject = 'Hey team, Amazon CodeGuru Reviewer found {num_of_reviews} in the {repo_name} PR: {pr_id}'.format(
        num_of_reviews=num_of_reviews,
        repo_name=repo_name,
        pr_id=pr_id
    )
    sns.publish(
        TopicArn=CODEGURU_SNS_TOPIC,
        Message=html_body,
        Subject=email_subject
    )


def generate_html_reviews_email(event, recommendations):
    """
    Function to generate an HTML body with table showing
    CodeGuru Reviewer recommendation summaries
    :param event:
    :param recommendations:
    :return:
    """
    pull_request_id = event['PullRequestId']
    lines_scanned = event['Metrics']['MeteredLinesOfCodeCount']
    recommendations_found = event['Metrics']['FindingsCount']
    recommendations_html_table_contents = [
        f"""
          <tr>
            <td>{recommendation['FilePath']}</td>
            <td>{recommendation['StartLine']}</td>
            <td>{recommendation['EndLine']}</td>
            <td>{recommendation['Description']}</td>
          </tr>
        """
        for recommendation in recommendations
    ]
    recommendations_html_table = '\n'.join(recommendations_html_table_contents)
    html_body = f"""
    <!DOCTYPE html>
    <html>
      <head>
      </head>
      <body>
        <p>Hi team,</p>
        <p>Amazon CodeGuru Reviewer has completed the review of {pull_request_id}, 
            scanning {lines_scanned} and found {recommendations_found} of recommendations.</p>
        <p>See Table below for the recommendations, and review the BUSINESS LOGIC in the pull request</p>
        <table style="width:100%">
          <tr>
            <th>File Path</th>
            <th>Start Line</th>
            <th>End Line</th>
            <th>Description/Recommendation</th>
          </tr>
          {recommendations_html_table}
        </table>
      </body>
    </html>
    """
    return html_body
