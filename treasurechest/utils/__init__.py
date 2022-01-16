import time
import os
import re


def get_date_from_timestamp(timestamp, dt_format='%Y-%m-%d %H:%M:%S'):
    date = time.strftime(dt_format, time.localtime(timestamp))
    return date


def mkdir_from_date(post):
    year = post.date[0:4]
    month = post.date[5:7]
    file_dir = os.path.join(post.config.blog_dir, f"content/posts/{year}/{month}/")
    os.makedirs(file_dir, exist_ok=True)
    return file_dir


def make_header(title: str, date: str, author: str, categories: str, featured_image: str = '', tags: str = ''):
    header = '\n'.join([
        "---",
        f"title: {title}",
        f"date: {date}",
        f"author: {author}",
        f"featured_image: '{featured_image}'",
        f"categories: {categories}",
        f"tags: {tags}",
        "---",
    ])
    return header


def make_file_name(prefix: str, number: int, title: str):
    file_name = f"{prefix}-{number}-{'-'.join(title.lower().split()[:5])}"
    file_name = re.sub('[^a-z0-9\\-]+', '', file_name) + ".md"
    return file_name
