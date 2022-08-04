from typing import Any

from aws_cdk.core import Construct
from aws_cdk.aws_elasticloadbalancingv2 import ApplicationLoadBalancer
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_ecs_patterns as ecs_patterns

from balinese.stacks.base import BaseStack


class WebStack(BaseStack):
    def __init__(
        self,
        scope: Construct,
        *,
        vpc: ec2.Vpc,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, "web", **kwargs)

        self.vpc = vpc

        self._create_primary_infra()
        self._create_secondary_infra()

    def _create_primary_infra(self):
        stack_id = self.to_string()

        # Create security group for RDS and ALB
        self.sg_backend = self._create_security_group(
            f"{stack_id}-web",
            security_group_id="WebSecurityGroup",
        )

        # Create ECR repository
        self.ecr_repo = self._create_ecr_repository(repository_name=stack_id)

    def _create_secondary_infra(self):
        stack_id = self.to_string()

        self.ecs_cluster = ecs.Cluster(
            self,
            "ECSCluster",
            vpc=self.vpc,
            cluster_name=stack_id,
            container_insights=True,
        )

        image = ecs.ContainerImage.from_ecr_repository(self.ecr_repo, tag="latest")

        fargate_service_load_balancer = ApplicationLoadBalancer(
            self,
            "ECSFargateServiceLoadBalancer",
            load_balancer_name=f"{stack_id}-lb",
            idle_timeout=None,
            vpc=self.vpc,
            internet_facing=True,
            vpc_subnets=self._get_vpc_subnets(
                private=False, vpc_subnets=None
            ),
        )

        self.ecs_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "ECSFargateService",
            cpu=512,
            memory_limit_mib=1024,
            security_groups=[self.sg_backend],
            task_subnets=self._get_vpc_subnets(
                private=True, vpc_subnets=None
            ),
            cluster=self.ecs_cluster,
            desired_count=1,
            enable_ecs_managed_tags=True,
            load_balancer=fargate_service_load_balancer,
            propagate_tags=ecs.PropagatedTagSource.TASK_DEFINITION,
            service_name=f"{stack_id}-web-a",
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=8050
            ),
        )
        self.ecs_service.target_group.configure_health_check(path="/")
