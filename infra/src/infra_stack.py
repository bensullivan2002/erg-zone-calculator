from aws_cdk import Stack
from constructs import Construct

from constructs.dns_construct import DnsConstruct
from constructs.api_construct import ApiConstruct
from constructs.cdn_construct import CdnConstruct


class InfraStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        domain_name = "zonecalculator.com"

        # DNS and SSL certificates
        dns = DnsConstruct(self, "Dns", domain_name=domain_name)

        # API Gateway and Lambda
        api = ApiConstruct(
            self,
            "Api",
            certificate=dns.certificate,
            hosted_zone=dns.hosted_zone,
            domain_name=domain_name,
        )

        # CloudFront and S3
        cdn = CdnConstruct(
            self,
            "Cdn",
            certificate=dns.certificate,
            hosted_zone=dns.hosted_zone,
            domain_name=domain_name,
        )

        # Store references for potential outputs
        self.api_url = api.api.url
        self.distribution_domain = cdn.distribution.distribution_domain_name
        self.static_bucket = cdn.static_bucket
