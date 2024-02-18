#!/bin/sh
#
# Description:
#
set -eux

# Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google.list \
    && sudo apt-get update \
    && sudo apt-get install -y -qq google-chrome-stable

google-chrome -h
google-chrome --version
# Install ChromeDriver from Chrome for Testing
# https://googlechromelabs.github.io/chrome-for-testing/
CHROME_VERSION="$(google-chrome --version | awk -F '[ .]' '{print $3"."$4"."$5"."$6}')"
echo "CHROME_VERSION: $CHROME_VERSION"
echo 'start wget'
curl -s https://googlechromelabs.github.io/chrome-for-testing/\#stable
sleep 1
echo 'start grep'
grep --version
# なぜか gh-actions の grep では -E オプションの +? だと最短一致にならなかった。。。
curl -s https://googlechromelabs.github.io/chrome-for-testing/\#stable | grep -oP 'id=stable.+?Version: <code>.+?</'
sleep 1
curl -s https://googlechromelabs.github.io/chrome-for-testing/\#stable | grep -oP 'id=stable.+?Version: <code>.+?</' | grep -Po '\d+\.\d+\.\d+\.\d+'

STABLE_DRIVER_VERSION="$(curl -s https://googlechromelabs.github.io/chrome-for-testing/\#stable | grep -oP 'id=stable.+?Version: <code>.+?</' | grep -Po '\d+\.\d+\.\d+\.\d+')"
echo "STABLE_DRIVER_VERSION: $STABLE_DRIVER_VERSION"
wget -qO /tmp/chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/$STABLE_DRIVER_VERSION/linux64/chromedriver-linux64.zip
echo 'unzip chromedriver'
unzip -q /tmp/chromedriver-linux64.zip -d /opt
echo 'move chromedriver'
chmod 755 /opt/chromedriver-linux64/chromedriver \
    && mv /opt/chromedriver-linux64/chromedriver ./config # Supposed in book_manager folder
