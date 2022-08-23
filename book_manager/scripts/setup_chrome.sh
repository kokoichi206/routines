#!/bin/sh
#
# Description:
#   Setup the initial Android project.
#   You can setup ci and version setting.
#
set -eu

# Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y -qq google-chrome-stable \
    && google-chrome --version

# Install ChromeDriver
CHROME_VERSION=`google-chrome --version | awk -F '[ .]' '{print $3"."$4"."$5}'` \
    && CHROME_DRIVER_VERSION=`wget -qO- chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION` \
    && wget -qO /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
    && unzip -q /tmp/chromedriver_linux64.zip -d /opt \
    && rm /tmp/chromedriver_linux64.zip \
    && chmod 755 /opt/chromedriver \
    && mv /opt/chromedriver ./config # Supposed in book_manager folder
