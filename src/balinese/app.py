from aws_cdk.core import App, Environment

from balinese.settings import Settings
from balinese.stacks.abyssinian import AbyssinianStack
from balinese.stacks.shared import SharedStack


def create_app(*, settings: Settings = None) -> App:
    if settings is None:
        settings = Settings()

    env = get_env(settings=settings)
    app = App()

    shared_stack = SharedStack(app)

    # Create API infra stack
    abyssinian_stack = AbyssinianStack(app, vpc=shared_stack.vpc)
    abyssinian_stack.add_dependency(shared_stack)

    return app


def get_env(*, settings: Settings) -> Environment:
    return Environment(account=settings.account, region=settings.region)
