# main.py

import os
from smolagents import CodeAgent, DuckDuckGoSearchTool, tool
from mistral_model import MistralModel

# You can set this in your environment or hardcode (not recommended)
MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]

# Initialize the wrapped model
llm = MistralModel(api_key=MISTRAL_API_KEY, model="mistral-large-latest")

@tool
def install_deps(package_name: str = "mistralai") -> bool:
    """
    Installs the specified package using Replit's package manager.
    Args:
        package_name (str): The name of the package to install.
    Returns:
        bool: True if installation was successful
    """
    return os.system(f"upm add {package_name}") == 0

@tool
def create_folder(folder_path: str) -> bool:
    """
    Creates a new folder at the specified path.
    Args:
        folder_path (str): Path where the folder should be created
    Returns:
        bool: True if folder was created successfully
    """
    try:
        os.makedirs(folder_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating folder: {e}")
        return False

@tool
def list_folder_contents(folder_path: str = ".") -> str:
    """
    Lists contents of the specified folder.
    Args:
        folder_path (str): Path to list contents from
    Returns:
        str: String containing directory contents
    """
    try:
        contents = os.listdir(folder_path)
        return "\n".join(contents)
    except Exception as e:
        return f"Error listing folder: {e}"

@tool
def rename_folder(old_path: str, new_path: str) -> bool:
    """
    Renames/moves a folder from old path to new path.
    Args:
        old_path (str): Current folder path
        new_path (str): New folder path
    Returns:
        bool: True if folder was renamed successfully
    """
    try:
        os.rename(old_path, new_path)
        return True
    except Exception as e:
        print(f"Error renaming folder: {e}")
        return False

@tool
def create_file(file_path: str, content: str = "") -> bool:
    """
    Creates a new file with specified content.
    Args:
        file_path (str): Path where the file should be created
        content (str): Content to write to the file
    Returns:
        bool: True if file was created successfully
    """
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error creating file: {e}")
        return False

@tool
def read_file(file_path: str) -> str:
    """
    Reads content from a file.
    Args:
        file_path (str): Path to the file to read
    Returns:
        str: Content of the file
    """
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

@tool
def modify_file(file_path: str, content: str) -> bool:
    """
    Modifies an existing file with new content.
    Args:
        file_path (str): Path to the file to modify
        content (str): New content for the file
    Returns:
        bool: True if file was modified successfully
    """
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error modifying file: {e}")
        return False


@tool
def execute_shell(command: str) -> str:
    """
    Executes a shell command with timeout and output analysis.
    Args:
        command (str): The shell command to execute
    Returns:
        str: Command output with analysis if timeout occurred
    """
    import subprocess
    import threading
    import time

    result = {"output": "", "timeout": False}
    
    def run_command():
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            result["output"] = (stdout + stderr).decode()
        except Exception as e:
            result["output"] = f"Error executing command: {e}"

    thread = threading.Thread(target=run_command)
    thread.start()
    thread.join(timeout=10)  # Wait for 10 seconds
    
    if thread.is_alive():
        result["timeout"] = True
        result["output"] += "\n[Command took longer than 10 seconds. Analysis of partial output:]"
        # Add basic analysis of the output
        lines = result["output"].split("\n")
        result["output"] += f"\n- Output length: {len(result['output'])} characters"
        result["output"] += f"\n- Number of lines: {len(lines)}"
        if "error" in result["output"].lower():
            result["output"] += "\n- Contains error messages"
        
    return result["output"]

# Create the agent with customized system prompt
system_prompt = """You are a coding assistant that creates separate files for applications and features.
When a user requests to create an application, game, or feature, always create new dedicated files instead of implementing directly in main.py.
Use appropriate file naming conventions and organize code logically.
For example:
- For a snake game, create snake_game.py
- For a web app, create app.py and related files
- For utilities, create utils.py
Only use the search tool for research and documentation purposes."""

agent = CodeAgent(
    tools=[
        DuckDuckGoSearchTool(),
        install_deps,
        create_folder,
        list_folder_contents,
        rename_folder,
        create_file,
        read_file,
        modify_file,
        execute_shell
    ],
    model=llm,
    add_base_tools=True
)
while True:
# Run the agent
    response = agent.run(input("You: "))

    if response == "bye":
        print("Bye!")
        exit(1)
    
    print("Agent response:")
    print(response)
    
