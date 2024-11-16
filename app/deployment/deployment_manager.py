import os
import shutil
import zipfile
import json
import time
from datetime import datetime, timezone

from deployment import deployment_scripts, deployment_helper


class DeploymentManager:
    
    def __init__(self):
        self.current_time = int(time.time())
        self.backup()
        self.version_history_load()
        self.overwrite()
        self.execute_scripts()
    
    def backup(self):
        print('Backing up...')
        if not os.path.exists(deployment_helper.CURRENT_PATH):
            print('There is nothing to back up')
            return
        
        zip_name = f'deployment_{self.current_time}.zip'
        zip_path = deployment_helper.path_join(deployment_helper.BACKUP_PATH, zip_name)
        print(f'Creating a zip file located at "{zip_path}"...')
        
        deployment_helper.create_folder_for_file(zip_path)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in deployment_helper.list_files(deployment_helper.CURRENT_PATH):
                file_path = deployment_helper.path_join(deployment_helper.CURRENT_PATH, file.relative_path)
                zip_file.write(file_path, file.relative_path)

        print('Backup created')
    
    def version_history_load(self):
        print('Loading the version history...')
        try:
            with open(deployment_helper.VERSION_HISTORY_PATH, 'r') as file:
                text = file.read()
            self.version_history = json.loads(text)
            current_version_name = self.version_history[-1]['next_version']
            self.current_version = self.string_to_version(current_version_name)
        except Exception as error:
            self.current_version = None
            self.version_history = None

        if self.current_version is None:
            print('No version history found')
        else:
            print(f'The current version is {current_version_name}')
    
    def overwrite(self):
        print('Overwriting source to current...')
        
        folders = ('app', 'website', 'reviews')
        for folder in folders:
            source_path = deployment_helper.path_join(deployment_helper.SOURCE_PATH, folder)
            current_path = deployment_helper.path_join(deployment_helper.CURRENT_PATH, folder)
            source_files = set(deployment_helper.list_files(source_path))
            current_files = set(deployment_helper.list_files(current_path))

            all_files = source_files | current_files
            
            for file in all_files:
                if file.relative_path.startswith('deployment'):
                    continue
                if '__pycache__' in file.relative_path:
                    continue
                
                source_file_path = deployment_helper.path_join(source_path, file.relative_path)
                current_file_path = deployment_helper.path_join(current_path, file.relative_path)
                
                if file in source_files:
                    deployment_helper.create_folder_for_file(current_file_path)
                    shutil.copy2(source_file_path, current_file_path)
                else:
                    os.remove(current_file_path)

        print('Overwritten')

    def version_to_string(self, version):
        if version is None:
            return ''
        major, minor = version
        return f'v{major}.{minor}'

    def string_to_version(self, text):
        major, minor = text[1:].split('.')
        return (int(major), int(minor))

    def execute_scripts(self):
        if self.version_history is None:
            self.version_history = []
        
        current_time_str = str(datetime.fromtimestamp(self.current_time, tz=timezone.utc))
        
        for script in deployment_scripts.scripts_get(self.current_version):
            previous_version_name = self.version_to_string(script.previous_version)
            next_version_name = self.version_to_string(script.next_version)
            print(f'Executing the deployment script {previous_version_name} → {next_version_name}...')
            deployment_helper.log_clear()
            script.function()
            output = deployment_helper.log_get()
            print(f'Execution done, output:\n{output}')
            
            deployment_log = {
                'previous_version': previous_version_name,
                'next_version': next_version_name,
                'time': current_time_str,
                'output': output
            }
            self.version_history.append(deployment_log)
        
        deployment_helper.create_folder_for_file(deployment_helper.VERSION_HISTORY_PATH)
        with open(deployment_helper.VERSION_HISTORY_PATH, 'w') as file:
            text = json.dumps(self.version_history, indent=4)
            file.write(text)


def run():
    deployment_manager = DeploymentManager()

