import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb=boto3.resource('dynamodb')
TABLE_NAME = 'CC-A2-TEAM'
table=dynamodb.Table(TABLE_NAME)

def handler(event, context):
    
    ls=[]
    Event=event['queryStringParameters']
    i=0
    while(i<len(Event)):
        ls.append(Event['tag{}'.format(i+1)])
        i=i+1
    
    queryString=""
    for k in ls:
        if(not queryString):
            queryString="attribute_exists({})".format(k)
        else:
            queryString=queryString+" AND attribute_exists({})". format(k)

    response = table.scan(
        ProjectionExpression='#u',
        ExpressionAttributeNames = {'#u': 'url'},
        FilterExpression=queryString
        )
    
    output=""
    for j in response['Items']:
        output=output+j['url']

    return {
        'statusCode': 200,
        'body': json.dumps(output)
    }