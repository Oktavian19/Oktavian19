import datetime
import os
import re
import requests
from dateutil import relativedelta

USER_NAME = os.environ.get("USER_NAME", "Oktavian19")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "")

# GitHub join date: October 13, 2020
JOIN_DATE = datetime.datetime(2020, 10, 13)

def format_plural(unit):
    return "s" if unit != 1 else ""

def get_uptime_string():
    diff = relativedelta.relativedelta(datetime.datetime.today(), JOIN_DATE)
    return "{} {}, {} {}, {} {}{}".format(
        diff.years, "year" + format_plural(diff.years),
        diff.months, "month" + format_plural(diff.months),
        diff.days, "day" + format_plural(diff.days),
        " 🚀" if (diff.months == 0 and diff.days == 0) else ""
    )

def fetch_github_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    if ACCESS_TOKEN:
        headers["authorization"] = f"token {ACCESS_TOKEN}"

    stats = {
        "repos": 19,
        "contrib": 20,
        "stars": 3,
        "commits": 380,
        "followers": 22,
        "loc": 45210,
        "loc_add": 52180,
        "loc_del": 6970
    }

    try:
        u_resp = requests.get(f"https://api.github.com/users/{USER_NAME}", headers=headers, timeout=10)
        if u_resp.status_code == 200:
            u_data = u_resp.json()
            stats["repos"] = u_data.get("public_repos", stats["repos"])
            stats["followers"] = u_data.get("followers", stats["followers"])

        r_resp = requests.get(f"https://api.github.com/users/{USER_NAME}/repos?per_page=100", headers=headers, timeout=10)
        if r_resp.status_code == 200:
            repos = r_resp.json()
            total_stars = sum(r.get("stargazers_count", 0) for r in repos)
            stats["stars"] = total_stars
    except Exception as e:
        print(f"[Notice] Using cached metrics: {e}")

    if ACCESS_TOKEN:
        try:
            today_str = datetime.datetime.utcnow().isoformat() + "Z"
            start_str = JOIN_DATE.isoformat() + "Z"
            query = """
            query($login: String!, $from: DateTime!, $to: DateTime!) {
                user(login: $login) {
                    contributionsCollection(from: $from, to: $to) {
                        contributionCalendar {
                            totalContributions
                        }
                    }
                }
            }
            """
            g_resp = requests.post(
                "https://api.github.com/graphql",
                json={"query": query, "variables": {"login": USER_NAME, "from": start_str, "to": today_str}},
                headers=headers,
                timeout=10
            )
            if g_resp.status_code == 200:
                data = g_resp.json()
                contribs = data.get("data", {}).get("user", {}).get("contributionsCollection", {}).get("contributionCalendar", {}).get("totalContributions")
                if contribs is not None:
                    stats["commits"] = contribs
        except Exception as e:
            print(f"[Notice] GraphQL query fallback: {e}")

    return stats

def update_element(svg_text, element_id, new_val):
    pattern = re.compile(r'(<tspan[^>]*id=["\']' + element_id + r'["\'][^>]*>)(.*?)(</tspan>)')
    return pattern.sub(r'\g<1>' + str(new_val) + r'\g<3>', svg_text)

def justify_and_replace(svg_text, element_id, new_text, length=0):
    if isinstance(new_text, int):
        formatted_val = f"{new_text:,}"
    else:
        formatted_val = str(new_text)

    svg_text = update_element(svg_text, element_id, formatted_val)

    if length > 0:
        just_len = max(0, length - len(formatted_val))
        if just_len <= 2:
            dot_map = {0: '', 1: ' ', 2: '. '}
            dot_string = dot_map[just_len]
        else:
            dot_string = ' ' + ('.' * just_len) + ' '
        svg_text = update_element(svg_text, f"{element_id}_dots", dot_string)

    return svg_text

def update_svg(filepath, uptime_str, stats):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Ensure single space before pipe in repos line
    content = content.replace("}  |", "} |")

    content = justify_and_replace(content, "age_data", uptime_str, 32)
    content = justify_and_replace(content, "commit_data", stats["commits"], 22)
    content = justify_and_replace(content, "star_data", stats["stars"], 14)
    content = justify_and_replace(content, "repo_data", stats["repos"], 6)
    content = justify_and_replace(content, "contrib_data", stats["contrib"])
    content = justify_and_replace(content, "follower_data", stats["followers"], 8)
    content = justify_and_replace(content, "loc_data", stats["loc"], 8)
    content = justify_and_replace(content, "loc_add", stats["loc_add"])
    content = justify_and_replace(content, "loc_del", stats["loc_del"], 7)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    uptime_str = get_uptime_string()
    stats = fetch_github_data()

    print(f"Updating profile SVGs for {USER_NAME}...")
    print(f"Uptime: {uptime_str}")
    print(f"Stats: {stats}")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    for fname in ["dark_mode.svg", "light_mode.svg"]:
        fpath = os.path.join(base_dir, fname)
        if os.path.exists(fpath):
            update_svg(fpath, uptime_str, stats)
            print(f"Successfully updated {fname}")

if __name__ == "__main__":
    main()
