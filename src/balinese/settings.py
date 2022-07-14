from pydantic import BaseSettings, Field

from balinese.constants import DEFAULT_CDK_ACCOUNT, DEFAULT_CDK_REGION


class Settings(BaseSettings):
    # Common settings
    account: str = Field(DEFAULT_CDK_ACCOUNT, env="CDK_ACCOUNT")
    region: str = Field(DEFAULT_CDK_REGION, env="AWS_DEFAULT_REGION")
