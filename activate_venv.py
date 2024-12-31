# import os
# import platform
# import subprocess

# def activate(venv_path):
#     current_directory = os.getcwd()
#     full_venv_path = os.path.join(current_directory, venv_path)

#     if platform.system() == "Windows":
#         activate_script = os.path.join(full_venv_path, "Scripts", "activate.bat")
#     else:
#         activate_script = os.path.join(full_venv_path, "bin", "activate")

#     subprocess.run("conda deactivate", shell=True)
#     subprocess.run(f"source {activate_script}", shell=True)



# venv_path = "aqua_venv"
# activate(venv_path)

import os
import platform
import subprocess

def activate(venv_path):
    # Get the current working directory
    current_directory = os.getcwd()
    
    # Check if a Conda environment is active, and deactivate it
    if "CONDA_DEFAULT_ENV" in os.environ:
        print("Deactivating Conda environment...")
        # subprocess.run("conda deactivate", shell=False, executable="/bin/bash")
        subprocess.call("conda deactivate", shell=True, executable='/bin/bash')
    
    # Now append the current working directory to the venv path
    full_venv_path = os.path.join(current_directory, venv_path)

    # Activate the Python virtual environment
    if platform.system() == "Linux" or platform.system() == "Darwin":
        # For Linux/Mac, use the venv activation script
        activate_script = os.path.join(venv_path, "bin", "activate")
        print(f"Activating virtual environment: {activate_script}")
        subprocess.run(f"source {activate_script}", shell=True, executable="/bin/bash")
    else:
        print(f"Unsupported platform: {platform.system()}. This code is designed for Linux or Mac.")
        return

# Example of usage
venv_path = "aqua_venv"  # This is your venv directory relative to the current working directory
activate(venv_path)
