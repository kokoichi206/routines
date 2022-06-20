#!/bin/bash
# 
# Description
#   Download the yesterday's lines of codes
#   from the artifacts.
#   Output file name is `last_result`
#
# Usage:
#   bash action_checker/num_codes.sh
#
set -euo pipefail

# Constants for GitHub api
MY_NAME="kokoichi206"
REPO_NAME="routines"
REPO_TOKEN=$1

# artifacts store the weekly commit activity, so it should reset once a week
## https://docs.github.com/ja/rest/metrics/statistics#get-the-weekly-commit-activity
if [[ $(date +'%u') == 1 ]]; then
    echo "Today is Monday!"
    echo "Reset the weekly result"
    echo 0 > last_result
    exit 0
fi

# Download the latest artifact.
# your TOKEN must have public_repo access to download an artifact
## https://github.com/actions/upload-artifact/issues/51#issuecomment-622960634
curl -s \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$MY_NAME/$REPO_NAME/actions/artifacts" |\
    jq '.artifacts[0].archive_download_url' |\
    xargs -I@ curl -s \
        -L \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Authorization: token ${REPO_TOKEN}"\
        -o last_result.zip \
        "@"

unzip last_result.zip
