from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_apigateway as apigateway,
)

from cdklabs.generative_ai_cdk_constructs import (
    bedrock
)

from constructs import Construct

class RAGStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        kb = bedrock.KnowledgeBase(self, 'DocKnowledgeBase', 
            embeddings_model= bedrock.BedrockFoundationModel.TITAN_EMBED_TEXT_V1,                  
        )

        documentBucket = s3.Bucket(self, 'DocumentBucket')

        deployment = s3deploy.BucketDeployment(self, "DeployDocuments",
            sources=[s3deploy.Source.asset("docs")],
            destination_bucket=documentBucket
        )

        bedrock.S3DataSource(self, 'KBS3DataSource',
            bucket= deployment.deployed_bucket,
            knowledge_base=kb,
            data_source_name='documents',
            chunking_strategy= bedrock.ChunkingStrategy.FIXED_SIZE,
            max_tokens=500,
            overlap_percentage=20   
        )

        kbQueryLambdaFunction = _lambda.Function(
            self, 'KBQueryFunction',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('lambda'),
            handler='app.handler',
            environment={
                'KB_ID': kb.knowledge_base_id,
                'KB_MODEL_ARN': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0',
            },
            timeout=Duration.seconds(15)
        )

        kbArn = f'arn:aws:bedrock:{Stack.of(self).region}:{Stack.of(self).account}:knowledge-base/{kb.knowledge_base_id}'

        policy_statement = iam.PolicyStatement(
            actions=[
                "bedrock:Retrieve",
                "bedrock:RetrieveAndGenerate",
                "bedrock:InvokeModel"
            ],
            resources=[
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                kbArn
            ]
        )

        kbQueryLambdaFunction.add_to_role_policy(policy_statement)

        api = apigateway.LambdaRestApi(
            self, 'KBQueryApiGW',
            handler=kbQueryLambdaFunction,
            proxy=False
        )

        kb_query = api.root.add_resource('query')
        kb_query.add_method('POST')

        CfnOutput(
            self, 'ApiEndpoint',
            value=api.url,
            description='The endpoint of the KB Query API'
        )