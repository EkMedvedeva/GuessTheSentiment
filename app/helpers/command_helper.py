from dataclasses import dataclass, asdict
import subprocess


@dataclass
class CommandResult:
    command: list[str]
    output: str
    error: str

    asdict = asdict


def command_run(command, timeout=5, cwd=None):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    output, error = process.communicate(timeout=timeout)
    result = CommandResult(
        command = command,
        output = output.decode('utf-8', errors='ignore'),
        error = error.decode('utf-8', errors='ignore')
    )
    return result

