from aws_cdk import (
    aws_lambda as lambda_,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as integrations,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
    Duration,
)
from constructs import Construct
from pathlib import Path


class ApiConstruct(Construct):
    """API Gateway and Lambda function for the FastAPI application."""
    
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        certificate: acm.Certificate,
        hosted_zone: route53.IHostedZone,
        domain_name: str = "zonecalculator.com"
    ) -> None:
        super().__init__(scope, construct_id)
        
        self.domain_name = domain_name
        self.api_domain = f"api.{domain_name}"
        
        # Lambda function for FastAPI
        self.lambda_function = lambda_.Function(
            self, "ApiFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_handler.handler",
            code=lambda_.Code.from_asset(
                str(Path(__file__).parent.parent.parent.parent),  # Root directory
                exclude=[
                    "infra/*",
                    "*.git*",
                    "*.md",
                    "__pycache__",
                    "*.pyc",
                    ".pytest_cache",
                    "tests/*"
                ]
            ),
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "PYTHONPATH": "/var/task/src",
            }
        )
        
        # HTTP API Gateway
        self.api = apigwv2.HttpApi(
            self, "HttpApi",
            api_name="erg-zone-calculator-api",
            description="ERG Zone Calculator API",
            cors_preflight={
                "allow_origins": [f"https://{domain_name}"],
                "allow_methods": [apigwv2.CorsHttpMethod.GET, apigwv2.CorsHttpMethod.POST],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        )
        
        # Lambda integration
        lambda_integration = integrations.HttpLambdaIntegration(
            "LambdaIntegration",
            self.lambda_function
        )
        
        # Add routes
        self.api.add_routes(
            path="/{proxy+}",
            methods=[apigwv2.HttpMethod.ANY],
            integration=lambda_integration
        )
        
        # Custom domain for API
        self.domain = apigwv2.DomainName(
            self, "ApiDomain",
            domain_name=self.api_domain,
            certificate=certificate
        )
        
        # Map domain to API
        apigwv2.ApiMapping(
            self, "ApiMapping",
            api=self.api,
            domain_name=self.domain
        )
        
        # Route53 record for API subdomain
        route53.ARecord(
            self, "ApiAliasRecord",
            zone=hosted_zone,
            record_name="api",
            target=route53.RecordTarget.from_alias(
                targets.ApiGatewayv2DomainProperties(
                    self.domain.regional_domain_name,
                    self.domain.regional_hosted_zone_id
                )
            )
        )