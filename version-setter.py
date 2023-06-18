import json
import os
import sys
import requests
import semver
import logging
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Define global request parameters
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[403, 429, 500, 502, 503, 504], # 403 is needed for GitHub
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

# Read in environment variables needed
BRANCH_NAME = str(os.environ["GITHUB_REF"]).split('/')[-1]
ORG_NAME = str(os.environ["GITHUB_REPOSITORY"]).split('/')[0]
REPO_NAME = str(os.environ["GITHUB_REPOSITORY"]).split('/')[1]
WORKSPACE = os.getcwd()
gh_access_token = os.environ["GITHUB_TOKEN"]

# Read script params passed in when called
script_dir = os.path.dirname(os.path.abspath(__file__))
version_file_path = os.path.join(script_dir, 'version.txt')
version_file = "version.txt"

# Declare global vars
base_gh_api_url = f"https://api.github.com/repos/{ORG_NAME}/{REPO_NAME}/releases/latest"
final_version_number = ""

try:
    with open(version_file_path) as version_file:
        ver_number = version_file.read().strip().split('=')[1].strip()      
        ver_number = str(semver.VersionInfo.parse(ver_number).finalize_version())       
except Exception as e:
    logging.critical(f"Unable to parse the version.txt file to find a proper semver: {e}")
    sys.exit(1)

def find_latest_release():
    logging.info("Checking GitHub for latest release.")
    resp = http.get(url=base_gh_api_url, headers={"Accept": "application/vnd.github.groot-preview+json", "authorization": f"token {gh_access_token}"})
    if resp.status_code == 404:
        return "1.0.0"
    if resp.status_code == 200:
        resp_data = json.loads(resp.text)
        return resp_data['tag_name']
    logging.critical("Unable to check GitHub API for release number.")
    sys.exit(1)

def release_version_reconciler(base_gh_release_version, compared_ver_number):
    logging.info("Reconciling application release number.")
    if semver.compare(base_gh_release_version, compared_ver_number) >= 0:
        ver = semver.VersionInfo.parse(base_gh_release_version)
        return str(ver.bump_patch().finalize_version())
    return compared_ver_number

def write_version_to_workspace(final_version_number):
    if BRANCH_NAME == "dev":
        final_version_number = f"{final_version_number}-dev"
    logging.info(f"Release number: {final_version_number} generated! Writing to workspace.")
    with open(f"{WORKSPACE}/final_version.txt", "w") as text_file:
        text_file.write(final_version_number)
    sys.exit()

def default_release_version_setter(gh_release_version, ver_number, log_message):
    logging.info(log_message)
    if gh_release_version:
        final_version_number = release_version_reconciler(gh_release_version, ver_number)
    else:
        final_version_number = ver_number
    write_version_to_workspace(final_version_number)

logging.info(f'Attempting to get release data from GitHub for branch: {BRANCH_NAME}')
gh_release_version = find_latest_release()

default_release_version_setter(gh_release_version, ver_number, "Running release comparison now.")

