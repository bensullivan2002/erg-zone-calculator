#!/usr/bin/env python3
from aws_cdk import App, Stack, RemovalPolicy
from aws_cdk import aws_s3 as s3
from uuid import uuid4
from constructs import Construct


class CdfnStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        uuid = str(uuid4())
        bucket_id = f"CdfnBucket-{uuid}"
        s3.Bucket(
            self,
            bucket_id,
            access_control=s3.BucketAccessControl.PRIVATE,
            auto_delete_objects=True,
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET],
                    allowed_origins=["*"],
                    allowed_headers=["*"],
                    exposed_headers=[],
                )
            ],
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            minimum_tls_version=1.2,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            website_index_document="index.html",
            website_error_document="error.html",
        )


app = App()
CdfnStack(app, "CdfnStack")

app.synth()
