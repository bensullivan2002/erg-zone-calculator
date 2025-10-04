import aws_cdk.aws_s3 as s3
from uuid import uuid4
from aws_cdk import core as cdk

def create_cdfn_bucket(scope: cdk.Construct, id: str):
    bucket_uuid = uuid4()
    cdfn_bucket_id = f"{id}-{bucket_uuid}"
    cdfn_bucket_props = s3.BucketProps(
        access_control = s3.BucketAccessControl.PRIVATE,
        auto_delete_objects = True,
        cors = [
            s3.CorsRule(
                allowed_methods = [s3.HttpMethods.GET],
                allowed_origins = ["*"],
                allowed_headers = ["*"],
                exposed_headers = []
            )
        ],
        encryption = s3.BucketEncryption.S3_MANAGED,
        enforce_ssl = True,
        minimum_tls_version = 1.2,
        versioned = True,
        removal_policy = s3.RemovalPolicy.DESTROY,
        website_index_document = "index.html",
        website_error_document = "error.html"
    )

    return s3.Bucket(scope, cdfn_bucket_id, cdfn_bucket_props)
