import datetime
import re

import feedparser

BLOG_START_COMMENT = '<!-- START_SECTION:blog -->'
BLOG_END_COMMENT = '<!-- END_SECTION:blog -->'

BRAIN_START_COMMENT = '<!-- START_SECTION:brain -->'
BRAIN_END_COMMENT = '<!-- END_SECTION:brain -->'

DOUBAN_START_COMMENT = '<!-- START_SECTION:douban -->'
DOUBAN_END_COMMENT = '<!-- END_SECTION:douban -->'

DOUBAN_RATING = {
    '<p>推荐: 很差</p>': '🌟☆☆☆☆ 很差',
    '<p>推荐: 较差</p>': '🌟🌟☆☆☆ 较差',
    '<p>推荐: 还行</p>': '🌟🌟🌟☆☆ 还行',
    '<p>推荐: 推荐</p>': '🌟🌟🌟🌟☆ 推荐',
    '<p>推荐: 力荐</p>': '🌟🌟🌟🌟🌟 力荐'
}


def generate_blog(rss_link, limit, readme) -> str:
    """Generate blog"""
    entries = feedparser.parse(rss_link)["entries"]
    arr = [
        {
            # "title": (entry["title"][0:20] + "...") if(len(entry["title"]) > 22) else entry["title"],
            "title": entry["title"],
            "url": entry["link"],
            "published": format_time(entry["published"]),
        }
        for entry in entries[:limit]
    ]

    content = "\n".join(
        ["<li> <a href='{url}' target='_blank'>{title}</a> - {published} </li>".format(**item) for item in arr]
    )

    return generate_new_readme(BLOG_START_COMMENT, BLOG_END_COMMENT, content, readme)

def generate_brain(rss_link, limit, readme) -> str:
    """Generate brain"""
    entries = feedparser.parse(rss_link)["entries"]
    arr = [
        {
            # "title": (entry["title"][0:20] + "...") if(len(entry["title"]) > 22) else entry["title"],
            "title": entry["title"],
            "url": entry["link"],
            "published": format_time(entry["published"]),
        }
        for entry in entries[:limit]
    ]

    content = "\n".join(
        ["<li> <a href='{url}' target='_blank'>{title}</a> - {published} </li>".format(**item) for item in arr]
    )

    return generate_new_readme(BRAIN_START_COMMENT, BRAIN_END_COMMENT, content, readme)

def generate_douban(username, limit, readme) -> str:
    """Generate douban"""
    entries = feedparser.parse("https://www.douban.com/feed/people/" + username + "/interests")["entries"]
    arr = [
        {
            "title": item["title"],
            "url": item["link"].split("#")[0],
            "published": format_time(item["published"]),
            "rating_star": generate_rating_star(item["description"])
        }
        for item in entries[:limit]
    ]

    content = "\n".join(
        ["<li> <a href='{url}' target='_blank'>{title}</a> {rating_star}- {published}</li>".format(**item) for item in arr]
    )

    return generate_new_readme(DOUBAN_START_COMMENT, DOUBAN_END_COMMENT, content, readme)


def generate_new_readme(start_comment: str, end_comment: str, content: str, readme: str) -> str:
    """Generate a new Readme.md"""
    pattern = f"{start_comment}[\\s\\S]+{end_comment}"
    repl = f"{start_comment}\n{content}\n{end_comment}"
    if re.search(pattern, readme) is None:
        print(f"can not find section in your readme, please check it, it should be {start_comment} and {end_comment}")

    return re.sub(pattern, repl, readme)

def format_time(timestamp) -> datetime:
    # 定义输入时间字符串可能的格式列表
    input_formats = [
        "%a, %d %b %Y %H:%M:%S %Z",      # 格式1
        "%a, %d %b %Y %H:%M:%S %z",      # 格式2
        "%a, %d %b %Y %H:%M:%S GMT",     # 格式3
        "%a, %d %b %Y %H:%M:%S %z%Z",    # 格式4
        # 在这里添加更多格式...
    ]

    # 尝试使用不同格式解析时间字符串
    for input_format in input_formats:
        try:
            date_obj = datetime.datetime.strptime(timestamp, input_format)
            # 转换为所需的输出格式
            formatted_date = date_obj.strftime('%Y-%m-%d %I:%M:%S %p')
            return formatted_date
        except ValueError:
            continue

    # 如果无法解析任何格式，返回空字符串或其他适当的值
    return ""

def generate_rating_star(desc) -> str:
    pattern = re.compile(r'<p>推荐: [\S\S]+</p>')
    matches = re.findall(pattern, desc)
    print(matches)
    if len(matches) > 0:
        return DOUBAN_RATING[matches[0]]
    return ''
