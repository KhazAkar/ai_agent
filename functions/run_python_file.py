import os
import subprocess

from google.genai import types


def run_python_file(working_directory, file_path, args=[]):
    abs_working_dir = os.path.abspath(working_directory)
    target_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not target_file_path.startswith(abs_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(target_file_path):
        return f'Error: File "{file_path}" not found.'
    if not target_file_path.endswith(".py"):
        return f'Error: File "{file_path}" is not a Python file.'

    try:
        result = subprocess.run(
            ["python", target_file_path] + args,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )

        stdout = result.stdout.strip() if result.stdout else ""
        stderr = result.stderr.strip() if result.stderr else ""
        if result.returncode != 0:
            return f"Process exited with code {result.returncode}\n{stdout}{stderr}"
        elif not stdout and not stderr:
            return "No output produced."
        else:
            return f"{stdout}{stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Process timed out"


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run Python files in the specified directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The working directory of the Python file to run.",
            ),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path of the Python file to run, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="The optional arguments to pass to the Python file. Tests don't require args.",
            ),
        },
        required=["working_directory", "file_path"],
    ),
)
