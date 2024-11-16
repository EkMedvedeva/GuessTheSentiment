import importlib
import re

from deployment import deployment_helper


REGISTRY_TABLE = {}


# Load all scripts inside the /scripts folder and add the registry to the table
for file in deployment_helper.list_files('app/deployment/scripts'):
    re_match = re.match(r'(v\d+).py', file.name)
    if re_match is None:
        continue
    script_name = re_match.group(1)
    script_module = importlib.import_module(f'deployment.scripts.{script_name}')
    
    registry = script_module.registry
    REGISTRY_TABLE[registry.major_version] = registry


def scripts_get(current_version):
    latest_major_version = max(REGISTRY_TABLE)
    registry = REGISTRY_TABLE[latest_major_version]
    yield from registry.scripts_get(current_version)

