#/bin/bash

# these patterns are excluded for diff check.
## e.g.) query parameter to invalidate cache
excluded_patterns=("style.min.css\?[0-9]*-[0-9]*" "common.js\?[0-9]*-[0-9]*")

curl -s https://odhackathon.metro.tokyo.lg.jp/ > new_file

echo "---------------------------------- Before ---------------------------------"
diff <(echo "${new}") <(echo "${old}")

for pattern in "${excluded_patterns[@]}"; do
    echo "$pattern"
    # Delete the specified pattern
    sed -i -E "s@$pattern@@g" new_file
    sed -i -E "s@$pattern@@g" odhackathon/index.txt
    # # For Mac (BSD)
    # sed -i -e "s@$pattern@@g" new_file
    # sed -i -e "s@$pattern@@g" odhackathon/index.txt
done

echo ""
echo "---------------------------------- After ---------------------------------"
# diff new_file odhackathon/index.txt

# exit code is greater than 0 when diff found.
echo $?

exit 0

# ------------------ examples ----------------------
diff <(cat odhackathon/index.txt |
    sed '@https://odhackathon.metro.tokyo.lg.jp/wp-content/themes/opendatahackathon/assets/css/style.min.css@d' |\
     sed '@https://odhackathon.metro.tokyo.lg.jp/wp-content/themes/opendatahackathon/assets/js/common.js@d') \
    <(curl https://odhackathon.metro.tokyo.lg.jp/ |\
     sed '@https://odhackathon.metro.tokyo.lg.jp/wp-content/themes/opendatahackathon/assets/css/style.min.css@d' |\
     sed '@https://odhackathon.metro.tokyo.lg.jp/wp-content/themes/opendatahackathon/assets/js/common.js@d')

diff <(cat odhackathon/index.txt |
     sed -E 's@(style.min.css)\?[0-9]*-[0-9]*@\1@g' |\
     sed -E 's@(common.js)\?[0-9]*-[0-9]*@\1@g') \
    <(curl -s https://odhackathon.metro.tokyo.lg.jp/ |\
     sed -E 's@(style.min.css)\?[0-9]*-[0-9]*@\1@g' |\
     sed -E 's@(common.js)\?[0-9]*-[0-9]*@\1@g')

echo '<link href="https://odhackathon.metro.tokyo.lg.jp/wp-content/themes/opendatahackathon/assets/css/style.min.css?20220720-1408" rel="stylesheet" media="all">' |\
 sed -E 's@(style.min.css)\?[0-9]*-[0-9]*@\1@g'

echo '<link href="https://odhackathon.metro.tokyo.lg.jp/wp-content/themes/opendatahackathon/assets/css/style.min.css?20220720-1408" rel="stylesheet" media="all">' |\
 sed '/style.min.css\?[0-9]*-[0-9]*/d'

echo '<link href="https://odhackathon.metro.tokyo.lg.jp/wp-content/themes/opendatahackathon/assets/css/style.min.css?20220720-1408" rel="stylesheet" media="all">' |\
 sed 's@style.min.css\?[0-9]*-[0-9]*@@g'
