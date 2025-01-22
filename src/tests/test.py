import os
import requests
import hashlib
import sys
import zipfile
from pathlib import Path

# Configuration
server_url = "https://your-server.com"  # Base URL to the server for patches and manifest
local_version_file = "client_version.txt"  # Local version file to store current version
local_dir = "game_client"  # Directory containing the client files
manifest_url = server_url + "/manifest.json"  # URL to the server's manifest (contains patch info)

def get_local_version():
    """Get the local version of the game from a version file."""
    if os.path.exists(local_version_file):
        with open(local_version_file, "r") as file:
            return file.read().strip()
    return None

def download_file(url, destination):
    """Download a file from the server to the local destination."""
    print(f"Downloading {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Ensure the request was successful

    with open(destination, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"Downloaded to {destination}")

def download_patch(patch_url, destination):
    """Download a patch file and extract it."""
    download_file(patch_url, destination)
    print(f"Extracting patch {destination}...")
    with zipfile.ZipFile(destination, 'r') as zip_ref:
        zip_ref.extractall(local_dir)
    print(f"Patch applied successfully from {destination}.")

def verify_file_integrity(file_path, expected_hash):
    """Verify a file's integrity using SHA256 checksum."""
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    file_hash = sha256_hash.hexdigest()
    if file_hash == expected_hash:
        return True
    else:
        print(f"Integrity check failed for {file_path}. Expected: {expected_hash}, Found: {file_hash}")
        return False

def check_for_updates():
    """Check if there are updates available by comparing the local and remote version."""
    local_version = get_local_version()
    if local_version is None:
        print("Local version not found. Installing the game...")
        return True  # No version, consider it outdated

    print(f"Current local version: {local_version}")

    try:
        response = requests.get(manifest_url)
        response.raise_for_status()
        manifest = response.json()

        remote_version = manifest.get("version")
        if remote_version > local_version:
            print(f"New version available: {remote_version}")
            return True
        else:
            print("No update needed. Your client is up to date.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error checking for updates: {e}")
        return False

def download_and_apply_updates():
    """Download and apply necessary updates."""
    try:
        response = requests.get(manifest_url)
        response.raise_for_status()
        manifest = response.json()

        for patch in manifest.get("patches", []):
            patch_url = patch.get("url")
            file_name = patch.get("file_name")
            expected_hash = patch.get("sha256")

            # Download patch and apply it
            patch_file = Path(local_dir) / f"{file_name}.zip"
            download_patch(patch_url, patch_file)

            # Verify the integrity of the patched file
            patched_file_path = Path(local_dir) / file_name
            if not verify_file_integrity(patched_file_path, expected_hash):
                print(f"Failed to verify the integrity of the patch for {file_name}.")
                return False

        # Update local version file
        new_version = manifest.get("version")
        with open(local_version_file, "w") as file:
            file.write(new_version)
        print(f"Client updated to version {new_version}.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error downloading patches: {e}")
        return False

def start_game():
    """Start the game after verifying the integrity of files and updating."""
    print("Starting the game...")
    # Add your game start logic here, for example:
    # subprocess.run(["python", "game.py"])  # Replace with your actual game startup command

def main():
    """Main launcher logic."""
    if check_for_updates():
        if download_and_apply_updates():
            start_game()
        else:
            print("Update failed. Exiting.")
            sys.exit(1)
    else:
        start_game()

if __name__ == "__main__":
    main()



