from typing import Any

from aws_cdk.aws_iam import Group, User
from aws_cdk.core import Stack, Construct
import aws_cdk.aws_ec2 as ec2


class SharedStack(Stack):
    def __init__(
        self, scope: Construct, **kwargs: Any
    ) -> None:
        super().__init__(scope, "shared", **kwargs)

        stack_id = self.to_string()

        self.vpc = ec2.Vpc(
            self,
            "VPC",
            cidr="10.120.0.0/16",
        )

        # Create Service user for IaC
        iam_group = Group(self, "SystemGroup", group_name=stack_id)
        iam_user = self.iam_user = User(self, "SystemUser", user_name=f"{stack_id}-user")
        iam_group.add_user(iam_user)
