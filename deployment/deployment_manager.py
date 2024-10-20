import os
import shutil
import zipfile
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
import deployment_scripts


SOURCE_PATH = ''
CURRENT_PATH = '../current'
BACKUP_PATH = '../backups'

VERSION_HISTORY_PATH = 'deployment/version_history.json'


@dataclass(frozen=True)
class RelativeFile:
    name: str
    relative_path: str


class DeploymentManager:
    
    def __init__(self):
        self.current_time = int(time.time())
        self.backup()
        self.version_history_load()
        self.overwrite()
        self.execute_scripts()

    def path_join(self, *paths):
        path = os.path.join(*paths)
        normalized_path = os.path.normpath(path)
        return normalized_path

    def list_files(self, folder_path):
        # Relative paths are relative to 'folder_path'
        for root_path, folder_names, file_names in os.walk(folder_path):
            root_relative_path = os.path.relpath(root_path, folder_path)
            for file_name in file_names:
                file_relative_path = self.path_join(root_relative_path, file_name)
                file = RelativeFile(name=file_name, relative_path=file_relative_path)
                yield file

    def create_folder_for_file(self, file_path):
        folder_path = os.path.dirname(file_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    
    def backup(self):
        print('Backing up...')
        if not os.path.exists(CURRENT_PATH):
            print('There is nothing to back up')
            return
        
        zip_name = f'deployment_{self.current_time}.zip'
        zip_path = self.path_join(BACKUP_PATH, zip_name)
        print(f'Creating a zip file located at "{zip_path}"...')
        
        self.create_folder_for_file(zip_path)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in self.list_files(CURRENT_PATH):
                file_path = self.path_join(CURRENT_PATH, file.relative_path)
                zip_file.write(file_path, file.relative_path)

        print('Backup created')
    
    def version_history_load(self):
        print('Loading the version history...')
        try:
            version_history_path = self.path_join(CURRENT_PATH, VERSION_HISTORY_PATH)
            with open(version_history_path, 'r') as file:
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
        untouched_files = {os.path.normpath('website/app/server.py')}
        folders = ('website', 'reviews')
        for folder in folders:
            source_path = self.path_join(SOURCE_PATH, folder)
            current_path = self.path_join(CURRENT_PATH, folder)
            source_files = set(self.list_files(source_path))
            current_files = set(self.list_files(current_path))

            all_files = source_files | current_files
            
            for file in all_files:
                source_file_path = self.path_join(source_path, file.relative_path)
                current_file_path = self.path_join(current_path, file.relative_path)
                
                if source_file_path in untouched_files and file in current_files:
                    continue
                
                if file in source_files:
                    self.create_folder_for_file(current_file_path)
                    shutil.copy2(source_file_path, current_file_path)
                else:
                    os.remove(current_file_path)

        print('Overwritten')

    def version_to_string(self, version):
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
            output = script.function()
            print(f'Execution done, output:\n{output}')
            
            deployment_log = {
                'previous_version': previous_version_name,
                'next_version': next_version_name,
                'time': current_time_str,
                'output': output
            }
            self.version_history.append(deployment_log)
        
        version_history_path = self.path_join(CURRENT_PATH, VERSION_HISTORY_PATH)
        self.create_folder_for_file(version_history_path)
        with open(version_history_path, 'w') as file:
            text = json.dumps(self.version_history, indent=4)
            file.write(text)


deployment_manager = DeploymentManager()

