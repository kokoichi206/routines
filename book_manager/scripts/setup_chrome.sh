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

# Install ChromeDriver from Chrome for Testing
# https://googlechromelabs.github.io/chrome-for-testing/
CHROME_VERSION=`google-chrome --version | awk -F '[ .]' '{print $3"."$4"."$5}'`
echo "CHROME_VERSION: $CHROME_VERSION"
echo 'start wget'
wget -qO /tmp/chromedriver_linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip
echo 'unzip chromedriver'
unzip -q /tmp/chromedriver_linux64.zip -d /opt \
    && rm /tmp/chromedriver-linux64.zip \
echo 'move chromedriver'
chmod 755 /opt/chromedriver-linux64/chromedriver \
    && mv /opt/chromedriver-linux64/chromedriver ./config # Supposed in book_manager folder
