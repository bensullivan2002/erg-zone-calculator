#!/usr/bin/env python3
import aws_cdk as cdk
from infra.infra_stack import InfraStack
from infra.src.origin_S3_bucket import create_cdfn_bucket


app = cdk.App()
InfraStack(
    app,
    "InfraStack",
    env=cdk.Environment(account="971422671361", region="eu-west-2"),
    cdfn_origin_s3_bucket = create_cdfn_bucket(app, "cdfn-bucket")
)

app.synth()
