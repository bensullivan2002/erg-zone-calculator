from aws_cdk import (
    Stack,
    aws_s3,
    RemovalPolicy,
)
from constructs import Construct


class InfraStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        static_site_assets_bucket = aws_s3.Bucket(  # noqa: F841
            self,
            "StaticSiteAssetsBucket",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
