from dataclasses import dataclass
from typing import Callable


@dataclass
class DeploymentScript:
    previous_version: tuple[int, int]
    next_version: tuple[int, int]
    function: Callable[[], None]


DEPLOYMENT_SCRIPTS = []
BASE_VERSION = (0, 0)


def deployment_decorator(function, major):
    # Get the previous version
    if len(DEPLOYMENT_SCRIPTS) == 0:
        previous_version = BASE_VERSION
    else:
        previous_version = DEPLOYMENT_SCRIPTS[-1].next_version
    # Get the next version
    if major:
        next_version = (previous_version[0] + 1, 0)
    else:
        next_version = (previous_version[0], previous_version[1] + 1)
    # Register the received function as a deployment function
    # with the correct version numbers
    deployment_script = DeploymentScript(
        previous_version=previous_version,
        next_version=next_version,
        function=function
    )
    DEPLOYMENT_SCRIPTS.append(deployment_script)
    return function

def major_update(function):
    return deployment_decorator(function, True)

def minor_update(function):
    return deployment_decorator(function, False)

def scripts_get(current_version):
    if current_version is None:
        current_version = BASE_VERSION
    for deployment_script in DEPLOYMENT_SCRIPTS:
        if deployment_script.next_version > current_version:
            yield deployment_script


# ------------------------------------------------------------
# Start of the deployment scripts


@minor_update
def deploy_v0_1():
    return 'Blank update'

