from aws_cdk.core import Stack, Construct
from aws_cdk.aws_elasticloadbalancingv2 import ApplicationLoadBalancer
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_ecs_patterns as ecs_patterns
from aws_cdk.aws_ecr import Repository
from aws_cdk.aws_iam import User, Group


ABYSSINIAN = "abyssinian"


class AbyssinianStack(Stack):
    def __init__(
        self,
        scope: Construct,
        **kwargs,
    ) -> None:
        super().__init__(scope, ABYSSINIAN, **kwargs)

        self._create_primary_infra()

    def _create_primary_infra(self):
        stack_id = self.to_string()

        # Create VPC
        self.vpc = ec2.Vpc(
            self,
            "VPC",
            cidr="10.120.0.0/16",
        )

        # Create security group for RDS and ALB
        self.sg_backend = self._create_security_group(
            f"{stack_id}-backend",
            security_group_id="BackendSecurityGroup",
        )

        # Create ECR repository for Uprise
        self.ecr_repo = Repository(
            self,
            "ECRRepository",
            repository_name=stack_id,
            image_scan_on_push=True,
        )

        iam_group = Group(self, "SystemGroup", group_name=stack_id)
        iam_user = self.iam_user = User(self, "SystemUser", user_name=f"{stack_id}-user")
        iam_group.add_user(iam_user)

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
            cpu=256,
            memory_limit_mib=512,
            security_groups=[self.sg_backend],
            task_subnets=self._get_vpc_subnets(
                private=True, vpc_subnets=None
            ),
            cluster=self.ecs_cluster,
            desired_count=2,
            enable_ecs_managed_tags=True,
            load_balancer=fargate_service_load_balancer,
            propagate_tags=ecs.PropagatedTagSource.TASK_DEFINITION,
            service_name=f"{stack_id}-backend-a",
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=9050
            ),
        )
        self.ecs_service.target_group.configure_health_check(path="/ping")
