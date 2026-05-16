from router import route


def lambda_handler(event, context):
    return route(event)
