#!/usr/bin/env bash

set -eu

cd /usr/local/apache2/htdocs/
if [ ! -e "channels" ] && [ ! -L "channels" ]; then
    ln -s /volumes/channels channels
fi
# if [ ! -e "thumbs" ]; then
#     ln -s /volumes/thumbs thumbs
# fi

python3 -B /usr/src/app/index_generator.py
python3 -B /usr/src/app/scheduler.py &
httpd -D FOREGROUND
