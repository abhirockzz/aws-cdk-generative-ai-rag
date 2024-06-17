import boto3
import json
import os

def handler(event, context):

    input = event.get('body')
    print("Question:", input)

    client = boto3.client('bedrock-agent-runtime')

    knowledgeBaseId = os.getenv("KB_ID")
    modelArn = os.getenv("KB_MODEL_ARN")

    resp = client.retrieve_and_generate(
        input={
            'text': input
        },
        retrieveAndGenerateConfiguration={
            'knowledgeBaseConfiguration': {
                'modelArn': modelArn,
                'knowledgeBaseId': knowledgeBaseId,
            },
            'type': 'KNOWLEDGE_BASE'
        }
    )
    
    kbTextResponse = resp['output']['text']
    print("KB response:", kbTextResponse)

    response = {
        'statusCode': 200,
        'body': json.dumps({
            "question": event.get('body'),
            "response": kbTextResponse,
        }),
    }

    return response