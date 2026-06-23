FROM httpd:2.4

# アプリのルートURLを引数として受け取る
ARG APP_ROOT_URL="http://localhost:80/"
ENV APP_ROOT_URL=$APP_ROOT_URL

# crontabの設定を引数として受け取る（デフォルトは毎日6:00, 18:00）
ARG CRONTAB_SETTING_TEXT="0 6,18 * * *"
ENV CRONTAB_SETTING_TEXT=$CRONTAB_SETTING_TEXT

# Install python and pip
RUN apt-get update
RUN apt-get install python3 python3-pip vim python3-setuptools -y -qq --no-install-recommends

# copy applications
COPY app/ /usr/src/app/

# install Python modules needed by the Python app
# 参考情報 https://zenn.dev/eng_ryosan/articles/a635346a3123d3
RUN pip install --no-cache-dir  --break-system-packages -r /usr/src/app/requirements.txt

# copy files required for the app to run
COPY htdocs /usr/local/apache2/htdocs

# tell the port number the container should expose
EXPOSE 80

CMD ["/usr/src/app/startup.sh"]
