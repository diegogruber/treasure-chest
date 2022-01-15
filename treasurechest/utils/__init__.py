import time
import os


def get_date_from_timestamp(timestamp, dt_format='%Y-%m-%d %H:%M:%S'):
    date = time.strftime(dt_format, time.localtime(timestamp))
    return date


def mkdir_from_date(post):
    year = post.date[0:4]
    month = post.date[5:7]
    file_dir = os.path.join(post.config.blog_dir, f"content/posts/{year}/{month}/")
    os.makedirs(file_dir, exist_ok=True)
    return file_dir
