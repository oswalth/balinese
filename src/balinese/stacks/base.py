import aws_cdk.aws_ec2 as ec2
from aws_cdk.aws_ecr import Repository
from aws_cdk.core import Stack


class BaseStack(Stack):
    def _create_security_group(
            self,
            security_group_name: str,
            *,
            security_group_id: str = "SecurityGroup",
            allow_all_outbound: bool = True,
    ) -> ec2.ISecurityGroup:
        return ec2.SecurityGroup(
            self,
            security_group_id,
            vpc=self.vpc,
            security_group_name=security_group_name,
            allow_all_outbound=allow_all_outbound,
        )

    def _get_vpc_subnets(
            self,
            *,
            private: bool,
            vpc_subnets: ec2.SubnetSelection = None,
    ) -> ec2.SubnetSelection:
        return (
            vpc_subnets
            if vpc_subnets is not None
            else ec2.SubnetSelection(
                subnets=self.vpc.private_subnets if private else self.vpc.public_subnets
            )
        )

    def _create_ecr_repository(
        self,
        *,
        repository_name: str,
        repository_id: str = "ECRRepository",
        image_scan_on_push: bool = True,
    ) -> Repository:
        if (ecr_repo := Repository.from_repository_name(
            self,
            id=repository_id,
            repository_name=repository_name
        )) is None:
            ecr_repo = Repository(
                self,
                repository_id,
                repository_name=repository_name,
                image_scan_on_push=image_scan_on_push,
            )
        return ecr_repo
