#!/usr/bin/env python3

import aws_cdk as cdk
from rag.rag_stack import RAGStack

app = cdk.App()
RAGStack(app, "RAGStack")

app.synth()
