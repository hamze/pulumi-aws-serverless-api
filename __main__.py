import json
import pulumi
import pulumi_aws as aws

# ====== Config ======
region = aws.config.region

# ====== DynamoDB ======
table = aws.dynamodb.Table(
    "contactMessages",
    attributes=[aws.dynamodb.TableAttributeArgs(name="id", type="S")],
    hash_key="id",
    billing_mode="PAY_PER_REQUEST",
)

# ====== IAM for Lambda ======
lambda_role = aws.iam.Role(
    "contactLambdaRole",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }),
)

aws.iam.RolePolicyAttachment(
    "lambdaBasicLogs",
    role=lambda_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
)

aws.iam.RolePolicy(
    "lambdaDynamoAccess",
    role=lambda_role.id,
    policy=table.arn.apply(
        lambda arn: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "dynamodb:PutItem",
                            "dynamodb:Scan",
                            "dynamodb:GetItem",
                            "dynamodb:Query"
                        ],
                        "Resource": [arn, f"{arn}/index/*"],
                    }
                ],
            }
        )
    ),
)

# ====== Lambda functions ======
post_fn = aws.lambda_.Function(
    "postContactFn",
    role=lambda_role.arn,
    runtime="python3.11",
    handler="handler.handler",
    environment=aws.lambda_.FunctionEnvironmentArgs(variables={"TABLE_NAME": table.name}),
    code=pulumi.AssetArchive({
        ".": pulumi.FileArchive("functions/post_contact"),
    }),
)

list_fn = aws.lambda_.Function(
    "listContactsFn",
    role=lambda_role.arn,
    runtime="python3.11",
    handler="handler.handler",
    environment=aws.lambda_.FunctionEnvironmentArgs(variables={"TABLE_NAME": table.name}),
    code=pulumi.AssetArchive({
        ".": pulumi.FileArchive("functions/list_contacts"),
    }),
)

# ====== HTTP API (API Gateway v2) ======
api = aws.apigatewayv2.Api(
    "contactApi",
    protocol_type="HTTP",
    cors_configuration=aws.apigatewayv2.ApiCorsConfigurationArgs(
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    ),
)

# Integrations
post_integration = aws.apigatewayv2.Integration(
    "postIntegration",
    api_id=api.id,
    integration_type="AWS_PROXY",
    integration_uri=post_fn.arn,
    integration_method="POST",
    payload_format_version="2.0",
)

list_integration = aws.apigatewayv2.Integration(
    "listIntegration",
    api_id=api.id,
    integration_type="AWS_PROXY",
    integration_uri=list_fn.arn,
    integration_method="POST",
    payload_format_version="2.0",
)

# Routes (JWT disabled for testing → use "NONE")
post_route = aws.apigatewayv2.Route(
    "postRoute",
    api_id=api.id,
    route_key="POST /contact",
    target=pulumi.Output.concat("integrations/", post_integration.id),
    authorization_type="NONE",
)

list_route = aws.apigatewayv2.Route(
    "listRoute",
    api_id=api.id,
    route_key="GET /contacts",
    target=pulumi.Output.concat("integrations/", list_integration.id),
    authorization_type="NONE",
)

# Stage ($default with auto-deploy)
stage = aws.apigatewayv2.Stage(
    "defaultStage",
    api_id=api.id,
    name="$default",
    auto_deploy=True,
)

# Allow API Gateway to invoke Lambdas
for name, fn in {"postInvoke": post_fn, "listInvoke": list_fn}.items():
    aws.lambda_.Permission(
        name,
        action="lambda:InvokeFunction",
        function=fn.name,
        principal="apigateway.amazonaws.com",
        source_arn=pulumi.Output.concat(api.execution_arn, "/*/*"),
    )

# ====== Stack outputs ======
pulumi.export("apiEndpoint", api.api_endpoint)
pulumi.export("dynamoTableName", table.name)
