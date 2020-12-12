from boto3 import client

codeguru_reviewer = client('codeguru-reviewer')


def lambda_handler(event, context):
    """
    Function to check status of CodeGuru Reviewer Review
    :param event:
    :param context:
    :return:
    """
    print(event)
    code_review_arn = event['CodeReviewArn']
    response = codeguru_reviewer.describe_code_review(
        CodeReviewArn=code_review_arn
    )
    code_review = response['CodeReview']
    code_review.pop('CreatedTimeStamp', None)
    code_review.pop('LastUpdatedTimeStamp', None)
    return response['CodeReview']
