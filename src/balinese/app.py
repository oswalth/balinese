from aws_cdk.core import App, Environment

from balinese.settings import Settings


def create_app(*, settings: Settings = None) -> App:
    if settings is None:
        settings = Settings()

    env = get_env(settings=settings)
    app = App()



    return app


def get_env(*, settings: Settings) -> Environment:
    return Environment(account=settings.account, region=settings.region)
