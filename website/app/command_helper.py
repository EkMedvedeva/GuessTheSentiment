from dataclasses import dataclass
import subprocess


@dataclass
class CommandResult:
    command
    output
    error


def command_run(command, timeout=5, cwd=None):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    output, error = process.communicate(timeout=timeout)
    result = CommandResult(
        command = command,
        output = output.decode('utf-8', errors='ignore'),
        error = error.decode('utf-8', errors='ignore')
    )
    return result

