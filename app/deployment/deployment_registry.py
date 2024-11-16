from dataclasses import dataclass
from typing import Callable


@dataclass
class DeploymentScript:
    previous_version: tuple[int, int]
    next_version: tuple[int, int]
    function: Callable[[], None]


class DeploymentRegistry:
    
    def __init__(self, major_version):
        self.major_version = major_version
        self.scripts = []
    
    def script_register(self, function, previous_version, next_version):
        # Register the received function as a deployment function
        # with the correct version numbers
        deployment_script = DeploymentScript(
            previous_version=previous_version,
            next_version=next_version,
            function=function
        )
        self.scripts.append(deployment_script)
        return function
    
    def base_update(self, function):
        # There is no previous version
        previous_version = None
        # The next version is the base
        next_version = (self.major_version, 0)
        return self.script_register(function, previous_version, next_version)
    
    def minor_update(self, function):
        # Get the previous version
        previous_version = self.scripts[-1].next_version
        # The next version is just a minor update
        next_version = (previous_version[0], previous_version[1] + 1)
        return self.script_register(function, previous_version, next_version)
    
    def scripts_get(self, current_version):
        for deployment_script in self.scripts:
            if current_version is None or deployment_script.next_version > current_version:
                yield deployment_script

