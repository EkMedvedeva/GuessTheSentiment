from deployment import deployment_helper
from deployment.deployment_registry import DeploymentRegistry


logger = deployment_helper.logger
registry = DeploymentRegistry(0)


@registry.base_update
def deploy_v0_0():
    logger.info('Blank base update')


@registry.minor_update
def deploy_v0_1():
    logger.info('Blank minor update')

