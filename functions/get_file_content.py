import os

from google.genai import types

MAX_CHARS = 10000


def get_file_content(working_directory, file_path):
    abs_working_dir = os.path.abspath(working_directory)
    target_file = abs_working_dir
    if file_path:
        target_file = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_file.startswith(abs_working_dir):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    with open(target_file, "r", encoding="utf-8") as file:
        content = file.read()
        if len(content) > MAX_CHARS:
            truncated_content = content[: MAX_CHARS - 1]
            truncated_message = (
                f'\n[...File "{file_path}" truncated at 10000 characters]'
            )
            return truncated_content + truncated_message
        return content


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Get the content of a file in the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to get the file content from, relative to the working directory.",
            ),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to get the content from.",
            ),
        },
        required=["working_directory", "file_path"],
    ),
)
