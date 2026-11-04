import datetime
import os
import re
import requests
from dateutil import relativedelta

USER_NAME = os.environ.get("USER_NAME", "Oktavian19")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "")

# GitHub join date: October 13, 2020
JOIN_DATE = datetime.datetime(2020, 10, 13)

# ANSI Color codes supported by GitHub markdown ```ansi
BOLD = "\033[1m"
RESET = "\033[0m"
GRAY = "\033[90m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
GREEN = "\033[32m"
RED = "\033[31m"
WHITE = "\033[37m"

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

# ASCII Portrait lines (24 chars wide, 25 lines high)
ASCII_PORTRAIT = [
    "                        ",
    "                        ",
    "   ..                   ",
    "        `l' .           ",
    "  ,<_?})ju{.            ",
    " `[txUCJvtt-.           ",
    " :|((jXv/1(\\            ",
    "l]tf/jnxxjn|+:          ",
    ":}/UUvzuXLz]{:          ",
    " `[Xz/\\(rYf<:           ",
    "  `(ntttrr~             ",
    "   :1rnut)^             ",
    "  ;/xfnurrt'            ",
    "  !mucXvnqw.            ",
    "   JbnuJk$t .           ",
    " . _@M|o@#l .           ",
    "  ..po^?&q` .           ",
    "  . /q`l#L .            ",
    "  . i\\`'cu .            ",
    "     ,;:>_ .            ",
    "     `:^,\"              ",
    "     .!;'               ",
    "      ^;'               ",
    "      .^.               ",
    "       .                "
]

def dot(n):
    return f"{GRAY}{'.' * max(1, n)}{RESET}"

def generate_ansi_block(uptime_str, stats):
    repos = f"{stats['repos']:,}"
    contrib = f"{stats['contrib']:,}"
    stars = f"{stats['stars']:,}"
    commits = f"{stats['commits']:,}"
    followers = f"{stats['followers']:,}"
    loc = f"{stats['loc']:,}"
    loc_add = f"{stats['loc_add']:,}"
    loc_del = f"{stats['loc_del']:,}"

    # Target column for values: 27 characters (label + dots)
    # Target column for stats pipe '|': 34 characters
    d_commit = max(2, 23 - len(commits))
    d_follower = max(2, 9 - len(followers))
    d_star = max(2, 13 - len(stars))
    d_loc = max(2, 9 - len(loc))

    right_lines = [
        f"{BOLD}{WHITE}oktavian@cachyos{RESET} {GRAY}-------------------------------------------------{RESET}",
        f"{GRAY}.{RESET} {YELLOW}OS{RESET}: {dot(24)} {CYAN}CachyOS Linux, Debian 13, Android{RESET}",
        f"{GRAY}.{RESET} {YELLOW}Uptime{RESET}: {dot(20)} {CYAN}{uptime_str}{RESET}",
        f"{GRAY}.{RESET} {YELLOW}Host{RESET}: {dot(22)} {CYAN}State Polytechnic of Malang (Polinema){RESET}",
        f"{GRAY}.{RESET} {YELLOW}Kernel{RESET}: {dot(20)} {CYAN}Full-Stack & Mobile Developer{RESET}",
        f"{GRAY}.{RESET} {YELLOW}Shell{RESET}: {dot(21)} {CYAN}fish 3.7+, bash 5.2{RESET}",
        f"{GRAY}.{RESET} {YELLOW}IDE{RESET}: {dot(23)} {CYAN}VS Code, Vim{RESET}",
        f"{GRAY}.{RESET}",
        f"{GRAY}.{RESET} {YELLOW}Languages.Programming{RESET}: {dot(5)} {CYAN}Dart, PHP, Python, TypeScript, JS{RESET}",
        f"{GRAY}.{RESET} {YELLOW}Languages.Frameworks{RESET}: {dot(6)} {CYAN}Flutter, Laravel, Next.js, React{RESET}",
        f"{GRAY}.{RESET} {YELLOW}Languages.Real{RESET}: {dot(12)} {CYAN}Indonesian (Native), English{RESET}",
        f"{GRAY}.{RESET}",
        f"{GRAY}.{RESET} {YELLOW}Focus.Mobile{RESET}: {dot(14)} {CYAN}Cross-platform Flutter applications{RESET}",
        f"{GRAY}.{RESET} {YELLOW}Focus.Backend{RESET}: {dot(13)} {CYAN}Laravel APIs, Debian Server bots{RESET}",
        f"{GRAY}.{RESET}",
        f"{WHITE}- Contact{RESET} {GRAY}-------------------------------------------------------{RESET}",
        f"{GRAY}.{RESET} {YELLOW}Email.Personal{RESET}: {dot(12)} {CYAN}oktavianeka4@gmail.com{RESET}",
        f"{GRAY}.{RESET} {YELLOW}LinkedIn{RESET}: {dot(18)} {CYAN}oktavian-eka-ramadhan-834a0a205{RESET}",
        f"{GRAY}.{RESET} {YELLOW}GitHub{RESET}: {dot(20)} {CYAN}Oktavian19{RESET}",
        f"{GRAY}.{RESET}",
        f"{WHITE}- GitHub Stats{RESET} {GRAY}--------------------------------------------------{RESET}",
        f"{GRAY}.{RESET} {YELLOW}Repos{RESET}: {dot(4)} {CYAN}{repos}{RESET} {{{YELLOW}Contributed{RESET}: {CYAN}{contrib}{RESET}}}  | {YELLOW}Stars{RESET}: {dot(d_star)} {CYAN}{stars}{RESET}",
        f"{GRAY}.{RESET} {YELLOW}Commits{RESET}: {dot(d_commit)} {CYAN}{commits}{RESET} | {YELLOW}Followers{RESET}: {dot(d_follower)} {CYAN}{followers}{RESET}",
        f"{GRAY}.{RESET} {YELLOW}Lines of Code{RESET}: {dot(d_loc)} {CYAN}{loc}{RESET} ( {GREEN}{loc_add}++{RESET}, {RED}{loc_del}--{RESET} )",
        f"{GRAY}.{RESET}"
    ]

    combined = []
    for l_left, l_right in zip(ASCII_PORTRAIT, right_lines):
        combined.append(f"{l_left}   {l_right}")

    return "\n".join(combined)

def update_readme(readme_path, ansi_block):
    if not os.path.exists(readme_path):
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_section = f"<!-- START_SECTION:neofetch -->\n```ansi\n{ansi_block}\n```\n<!-- END_SECTION:neofetch -->"
    
    if "<!-- START_SECTION:neofetch -->" in content:
        pattern = re.compile(r"<!-- START_SECTION:neofetch -->.*?<!-- END_SECTION:neofetch -->", re.DOTALL)
        content = pattern.sub(new_section, content)
    else:
        # Default template if markers missing
        content = f"""<h1 align="center">Hi 👋, I'm Oktavian Eka Ramadhan</h1>

{new_section}

<p align="center">
  <a href="https://linkedin.com/in/oktavian-eka-ramadhan-834a0a205">LinkedIn</a> • 
  <a href="mailto:oktavianeka4@gmail.com">Email</a> • 
  <a href="https://github.com/Oktavian19">GitHub</a>
</p>
"""

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated README.md with ANSI terminal block")

def main():
    uptime_str = get_uptime_string()
    stats = fetch_github_data()

    print(f"Updating profile for {USER_NAME}...")
    print(f"Uptime: {uptime_str}")
    print(f"Stats: {stats}")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(base_dir, "README.md")
    
    ansi_block = generate_ansi_block(uptime_str, stats)
    update_readme(readme_path, ansi_block)

if __name__ == "__main__":
    main()
