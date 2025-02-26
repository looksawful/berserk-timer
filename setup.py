import os
import subprocess
import sys
import platform


def check_and_create_venv():
    """Check if virtual environment exists, and create it if not."""
    venv_path = os.path.join(os.getcwd(), 'venv')

    if not os.path.exists(venv_path):
        print("Virtual environment not found. Creating one...")
        if platform.system() == 'Windows':
            subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        else:
            subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")


def activate_venv():
    """Activate the virtual environment based on the operating system."""
    if platform.system() == 'Windows':
        activate_script = os.path.join(
            os.getcwd(), 'venv', 'Scripts', 'activate.bat')
    else:
        activate_script = os.path.join(os.getcwd(), 'venv', 'bin', 'activate')

    subprocess.call([activate_script])


def install_requirements():
    """Install dependencies from requirements.txt."""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip",
                          "install", "-r", "requirements.txt"])
    print("Dependencies installed.")


def check_commit():
    """Automatically commit any uncommitted changes."""
    print("Checking for uncommitted changes...")
    result = subprocess.run(["git", "status", "--porcelain"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stdout:
        print("Uncommitted changes found. Committing changes automatically.")
        subprocess.check_call(["git", "add", "."])
        subprocess.check_call(
            ["git", "commit", "-m", "Auto commit before running setup"])
        subprocess.check_call(["git", "push"])
        print("Changes committed and pushed.")
    else:
        print("No uncommitted changes found.")


def main():
    check_commit()
    check_and_create_venv()
    activate_venv()
    install_requirements()


if __name__ == "__main__":
    main()
