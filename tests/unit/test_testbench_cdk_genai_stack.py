import aws_cdk as core
import aws_cdk.assertions as assertions

from testbench_cdk_genai.testbench_cdk_genai_stack import TestbenchCdkGenaiStack

# example tests. To run these tests, uncomment this file along with the example
# resource in testbench_cdk_genai/testbench_cdk_genai_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TestbenchCdkGenaiStack(app, "testbench-cdk-genai")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
