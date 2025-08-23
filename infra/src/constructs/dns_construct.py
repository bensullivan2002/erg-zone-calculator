from aws_cdk import (
    aws_route53 as route53,
    aws_certificatemanager as acm,
)
from constructs import Construct


class DnsConstruct(Construct):
    """DNS and SSL certificate management."""
    
    def __init__(self, scope: Construct, construct_id: str, domain_name: str = "zonecalculator.com") -> None:
        super().__init__(scope, construct_id)
        
        self.domain_name = domain_name
        
        # Get existing hosted zone
        self.hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=domain_name
        )
        
        # Create SSL certificate for main domain and API subdomain
        # Must be in us-east-1 for CloudFront
        self.certificate = acm.Certificate(
            self, "Certificate",
            domain_name=domain_name,
            subject_alternative_names=[f"api.{domain_name}"],
            validation=acm.CertificateValidation.from_dns(self.hosted_zone)
        )