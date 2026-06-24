#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pathlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from wsgiref.handlers import format_date_time
import glob
from dataclasses import dataclass
from jinja2 import Template, Environment, FileSystemLoader
from typing import Any
from email.utils import formatdate
import hashlib
import urllib

"""
Envs:
  PCS_APP_ROOT_URL      -- アプリのルートURL(例: http://hogehoge.local:80/)
  PCS_HTDOCS_ROOT_DIR   -- apacheのhtdocsルートディレクトリ(例: /usr/local/apache2/htdocs/)
  PCS_TEMPLATES_DIR     -- index.htmlとPodcast feedデータのテンプレート(例: /usr/src/app/templates/)
  PCS_AUDIO_ROOT_DIR    -- オーディオファイルのルートディレクトリ
"""

@dataclass
class FeedInfo:
    channel_name: str
    feed_file_fullpath: str = ""

    def hash(self) -> str:
        return hashlib.md5(self.channel_name.encode()).hexdigest()

    def url(self) -> str:
        return urllib.parse.urljoin(FileIO.channel_dir_url, os.path.join(urllib.parse.quote(FileIO.channel_dir_name), urllib.parse.quote(self.channel_name), urllib.parse.quote(FileIO.podcast_feed_filename)))

class FileIO:
    app_root_url: str = os.environ.get("PCS_APP_ROOT_URL","http://localhost:8080/")
    htdocs_dir_path = os.environ.get("PCS_HTDOCS_ROOT_DIR","/usr/local/apache2/htdocs/")
    templates_dir_path = os.environ.get("PCS_TEMPLATES_DIR","/usr/src/app/templates/")
    music_files_dir_path = os.environ.get("PCS_AUDIO_ROOT_DIR", os.path.join(htdocs_dir_path, "channels"))
    podcast_feed_filename :str = "podcast_feed.rss"
    feeds_dir_name = "feeds"
    channel_dir_name = "channels"
    thumbnail_dir_name = "thumbs"
    index_html_template_filename = "index-template.html.j2"
    feed_template_filename = "feed-template.xml.j2"

    index_html_file_path = os.path.join(htdocs_dir_path, "index.html")
    output_xml_dir_path = os.path.join(htdocs_dir_path, feeds_dir_name)
    feeds_dir_url = os.path.join(app_root_url, feeds_dir_name)
    channel_dir_url = os.path.join(app_root_url, channel_dir_name)
    thumbnail_dir_path = os.path.join(htdocs_dir_path, thumbnail_dir_name)
    default_thumbnail_url = os.path.join(app_root_url, thumbnail_dir_name, "music.png")

    timezone= os.environ.get("PCS_TIMEZONE","Asia/Tokyo")
    timezone_info = ZoneInfo(timezone)

    @staticmethod
    def get_channel_rss_list() -> list[FeedInfo]:
        # ファイルのフルパスの一覧を生成
        feed_file_fullpaths: list[str] = []
        feed_file_fullpaths.extend(glob.glob(os.path.join(FileIO.music_files_dir_path, "**", FileIO.podcast_feed_filename), recursive=True))

        rss_info_list: list[FeedInfo] = []
        for fullpath in feed_file_fullpaths:
            rss_info = FeedInfo(feed_file_fullpath=fullpath, channel_name=pathlib.Path(fullpath).parent.name)
            print(f"rss_info feed_file_fullpath[{rss_info.feed_file_fullpath}], channel_name[{rss_info.channel_name}]")
            rss_info_list.append(rss_info)

        return sorted(rss_info_list, key=lambda e: e.channel_name)

    @staticmethod
    def get_index_html_template() -> Template:
        #テンプレート読み込み
        env = Environment(loader=FileSystemLoader(FileIO.templates_dir_path, encoding="utf8"), autoescape=True)
        return env.get_template(FileIO.index_html_template_filename)

    @staticmethod
    def output_index_html(filename :str, html_text: str):
        html_file_path = os.path.join(FileIO.htdocs_dir_path, filename)

        with open(html_file_path, "w") as f:
            f.write(html_text)

class TemplateRenderer:
    @staticmethod
    def render_index_html(filename :str, feed_info_list: list[FeedInfo]):
        feeds: list[dict[str, str]] = []
        for feed_info in feed_info_list:
            feeds.append({
              "path": feed_info.url(),
              "title": feed_info.channel_name
            })

        rendering_params = { "last_update_date": datetime.now(FileIO.timezone_info), "feeds": feeds }

        html = FileIO.get_index_html_template().render(rendering_params)
        FileIO.output_index_html(filename, html)

class FeedGenerator:
    @staticmethod
    def generate():
        FeedGenerator.generate_index()  #podcast_feed.rssのindexを作る(ファイル名はindex.html)

    @staticmethod
    def generate_index():
        channel_rss_list = FileIO.get_channel_rss_list()

        TemplateRenderer.render_index_html("index.html", channel_rss_list)

if __name__ == "__main__":
    FeedGenerator.generate()
