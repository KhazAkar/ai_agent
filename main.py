import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_file_content import get_file_content, schema_get_file_content
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.run_python_file import run_python_file, schema_run_python_file
from functions.write_file import schema_write_file, write_file

# Load environment variables
status = load_dotenv()
if not status:
    print("No .env found")
    raise SystemExit(1)

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Register available tools
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)

# System prompt for the agent
system_prompt = """
You are a helpful AI coding agent. When a user asks a question or makes a request, make a function call plan. Use the following tools to inspect the project:

 - get_files_info: list files and directories
 - get_file_content: read file contents
 - write_file: modify files
 - run_python_file: execute Python scripts

After executing the required functions, provide a concise answer. Prepend your answer with `Final response:` on a new line. All output should be plain text, suitable for a terminal.

All paths you provide should be relative to the working directory. When calling `run_python_file`, the `working_directory` argument should be the base directory for the Python script, and `file_path` should be relative to *that* `working_directory`. For example, to run the calculator, you would call:
run_python_file(working_directory='calculator', file_path='main.py', args=['"1 + 1"'])
"""

# Mapping of function names to actual callables
function_mapping = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def call_function(function_call_part, verbose=False):
    """
    Execute a function call based on the provided `function_call_part`.
    Returns a `types.Content` object with the tool response.
    """
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f"- Calling function: {function_call_part.name}")

    if function_call_part.name not in function_mapping:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )

    function_result = function_mapping[function_call_part.name](
        **function_call_part.args
    )

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": function_result},
            )
        ],
    )


def main(args: argparse.Namespace):
    """
    Main loop that drives the Gemini model with iterative function calls.
    """
    # Start with the user prompt
    messages = [types.Content(role="user", parts=[types.Part(text=args.prompt)])]
    max_iterations = 20

    for _ in range(max_iterations):
        try:
            # Send the full conversation history to the model
            gen_content_response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=[available_functions],
                ),
            )
        except Exception as e:
            print(f"Error during generate_content: {e}")
            break

        # Assuming only one candidate for simplicity, as is common with Gemini models.
        # If multiple candidates are expected to be processed, this logic needs adjustment.
        if not gen_content_response.candidates:
            print("Model returned no candidates.")
            break

        candidate = gen_content_response.candidates[0]
        messages.append(candidate.content)  # Add the model's Content object to history

        function_calls_this_iteration = False
        final_text_parts = []

        # Process each part of the candidate's content
        for part in candidate.content.parts:
            if part.function_call:
                function_calls_this_iteration = True
                tool_response = call_function(part.function_call, args.verbose)
                if not tool_response:
                    raise ValueError("Function call result is empty")
                messages.append(tool_response)
                if args.verbose:
                    print(f"-> {tool_response.parts[0].function_response.response}")
            elif part.text:
                final_text_parts.append(part.text)

        # Determine if the model is finished
        if not function_calls_this_iteration and final_text_parts:
            # Model finished: no function calls and provided a text response
            final_response_text = "\n".join(final_text_parts).strip()
            print(final_response_text)
            print(
                f"Prompt tokens: {gen_content_response.usage_metadata.prompt_token_count}"
            )
            print(
                f"Response tokens: {gen_content_response.usage_metadata.candidates_token_count}"
            )
            break
        elif function_calls_this_iteration:
            # Model made function calls, continue loop to let it react to tool output
            continue
        # If no function calls and no text (e.g., model is just thinking or empty response),
        # continue the loop until max_iterations or a final text response.
    else:
        print("Maximum iterations reached without a final response.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--verbose", action="store_true")
    parsed_args = parser.parse_args()
    main(parsed_args)
