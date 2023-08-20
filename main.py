import base64
import os
import sys
from github import Github, GithubException
import re
from datetime import datetime
import pytz

import social

REPOSITORY = os.getenv('INPUT_REPOSITORY')
GH_TOKEN = os.getenv('INPUT_GH_TOKEN')

COMMIT_MESSAGE = os.getenv("INPUT_COMMIT_MESSAGE")

BLOG_RSS_LINK = os.getenv('INPUT_BLOG_RSS_LINK')
BLOG_LIMIT = int(os.getenv('INPUT_BLOG_LIMIT'))

BRAIN_RSS_LINK = os.getenv('INPUT_BRAIN_RSS_LINK')
BRAIN_LIMIT = int(os.getenv('INPUT_BRAIN_LIMIT'))

DOUBAN_NAME = os.getenv('INPUT_DOUBAN_NAME')
DOUBAN_LIMIT = int(os.getenv('INPUT_DOUBAN_LIMIT'))

def decode_readme(data: str) -> str:
    """Decode the contents of old readme"""
    decoded_bytes = base64.b64decode(data)
    return str(decoded_bytes, 'utf-8')

# 获取当前上海时区时间
def get_shanghai_time():
    shanghai_tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(shanghai_tz)

# 根据规则转换时间
def convert_time(current_time):
    hour = current_time.hour
    if hour == 0:
        hour12 = 12
        am_pm = 'AM'
    elif hour < 12:
        hour12 = hour
        am_pm = 'AM'
    elif hour == 12:
        hour12 = 12
        am_pm = 'PM'
    else:
        hour12 = hour - 12
        am_pm = 'PM'

    minute = current_time.minute
    if minute >= 0 and minute <= 15:
        time_str = f":clock{hour12}"
    elif minute > 15 and minute <= 30:
        time_str = f":clock{hour12}30"
    elif minute > 30 and minute <= 45:
        time_str = f":clock{hour12}30"
    elif minute > 45 and minute <= 60:
        time_str = f":clock{hour12 + 1}"
    else:
        time_str = f":clock{hour12}30"

    return time_str

# 读取并更新文件内容
def update_file_content(file_path, new_time_str):
    with open(file_path, 'r') as file:
        content = file.read()

    updated_content = re.sub(r':clock\d{1,4} `(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})`', new_time_str, content)

    with open(file_path, 'w') as file:
        file.write(updated_content)


if __name__ == "__main__":
    gh = Github(GH_TOKEN)
    try:
        repo = gh.get_repo(REPOSITORY)
    except GithubException:
        print(
            "Authentication Error. Try saving a GitHub Token in your Repo Secrets or Use the GitHub Actions Token, "
            "which is automatically used by the action.")
        sys.exit(1)
    contents = repo.get_readme()

    old_readme = decode_readme(contents.content)
    new_readme = old_readme

    if BLOG_RSS_LINK is not None and BLOG_LIMIT > 0:
        print("BLOG_RSS_LINK:" + BLOG_RSS_LINK)
        print("BLOG_LIMIT:" + str(BLOG_LIMIT))
        new_readme = social.generate_blog(BLOG_RSS_LINK, BLOG_LIMIT, new_readme)
        
    if BRAIN_RSS_LINK is not None and BRAIN_LIMIT > 0:
        print("BRAIN_RSS_LINK:" + BRAIN_RSS_LINK)
        print("BRAIN_LIMIT:" + str(BRAIN_LIMIT))
        new_readme = social.generate_brain(BRAIN_RSS_LINK, BRAIN_LIMIT, new_readme)
        
    if DOUBAN_NAME is not None and DOUBAN_LIMIT > 0:
        print("DOUBAN_NAME:" + DOUBAN_NAME)
        print("DOUBAN_LIMIT:" + str(DOUBAN_LIMIT))
        new_readme = social.generate_douban(DOUBAN_NAME, DOUBAN_LIMIT, new_readme)

    if new_readme == old_readme:
        print("nothing changed")
    else:
        print("readme change, start update ...")
        #repo.update_file(path=contents.path, message=COMMIT_MESSAGE,
        #                 content=new_readme, sha=contents.sha)
        
        # 获取当前上海时区时间
        current_shanghai_time = get_shanghai_time()
        # 转换当前时间为指定格式
        new_time_str = convert_time(current_shanghai_time) + f" `{current_shanghai_time.strftime('%Y-%m-%d %H:%M:%S')}`"
        print(new_time_str)
        updated_content = re.sub(r':clock\d{1,4} `(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})`', new_time_str, new_readme)
        repo.update_file(path=contents.path, message=COMMIT_MESSAGE,
                         content=updated_content, sha=contents.sha)
        
        print(" ✅ Your readme update completed!")
