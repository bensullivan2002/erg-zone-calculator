from typing_extensions import final
from aws_cdk import (
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
    Duration,
    RemovalPolicy,
)
from constructs import Construct


class CdnConstruct(Construct):
    """CloudFront distribution and S3 bucket for static content."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        certificate: acm.Certificate,
        hosted_zone: route53.IHostedZone,
        domain_name: str = "zonecalculator.com"
    ) -> None:
        super().__init__(scope, construct_id)

        self.domain_name: str = domain_name

        # S3 bucket for static assets (reuse existing one)
        self.static_bucket = s3.Bucket(
            self, "StaticSiteAssetsBucket",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,  # CloudFront will access via OAC
        )

        # Origin Access Control for S3
        oac = cloudfront.OriginAccessControl(
            self, "OAC",
            description="OAC for static site bucket"
        )

        # CloudFront distribution
        self.distribution = cloudfront.Distribution(
            self, "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    self.static_bucket,
                    origin_access_control=oac
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
            ),
            domain_names=[domain_name],
            certificate=certificate,
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",  # SPA fallback
                    ttl=Duration.minutes(5)
                )
            ]
        )

        # Grant CloudFront access to S3 bucket
        self.static_bucket.grant_read(self.distribution.grant_principal)

        # Route53 record for main domain
        route53.ARecord(
            self, "SiteAliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(self.distribution)
            )
        )
