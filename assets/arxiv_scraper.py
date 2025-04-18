import requests
from bs4 import BeautifulSoup
import re
import webbrowser

# Define your keywords of interest
KEYWORDS = ["exoplanet"]

# URL of the arXiv astro-ph recent submissions
URL = "https://arxiv.org/list/astro-ph/recent?skip=0&show=2000"

def fetch_papers(url):
    import requests
    from bs4 import BeautifulSoup

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to fetch page, status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    dt_tags = soup.find_all("dt")
    dd_tags = soup.find_all("dd")

    #print(f"✅ Found {len(dt_tags)} <dt> tags and {len(dd_tags)} <dd> tags")   # Print step for debugging

    papers = []

    for i, (dt, dd) in enumerate(zip(dt_tags, dd_tags), start=1):
        #print(f"\n🔍 Processing entry #{i}")   # Print step for debugging

        abs_link_tag = dt.find("a", href=True)
        #if not abs_link_tag:
        #    print("⚠️ Missing abstract link <a href=...>")
        #    continue           # Print step for debugging
        full_link = "https://arxiv.org" + abs_link_tag["href"]

        # Try to extract title div
        title_div = dd.find("div", class_=lambda x: x and "list-title" in x)
        #if not title_div:
        #    print("⚠️ Missing <div class='list-title'> in <dd>")
        #    continue           # Print step for debugging

        title = title_div.text.replace("Title:", "").strip()
        #print(f"✅ Found title: {title}")  # Print step for debugging

        papers.append((title, full_link))

    return papers

def filter_papers(papers, keywords):
    return [
        (title, link)
        for title, link in papers
        if any(kw.lower() in title.lower() for kw in keywords)
    ]

def fetch_abstract(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    abstract = soup.find("blockquote", class_="abstract mathjax")
    if abstract:
        return abstract.get_text(strip=True).replace("Abstract: ", "")
    return "Abstract not found."

def main():
    print("🔭 Fetching latest arXiv astro-ph papers...")
    papers = fetch_papers(URL)
    
    print(f"\nTotal papers found: {len(papers)}")
    #for title, link in papers:
    #    print(f"- {title}")    # Print step for debugging
    
    filtered = filter_papers(papers, KEYWORDS)

    if not filtered:
        print("No papers matched your keywords this week.")
        return

    print("\n📄 Matching Papers:")
    for i, (title, link) in enumerate(filtered):
        print(f"{i+1}.{title}\n")

    # Ask the user for which papers to show abstracts
    choices = input(
        "\nEnter the numbers of the papers you'd like to study (comma-separated): "
    )
    indices = [int(i.strip()) - 1 for i in choices.split(",") if i.strip().isdigit()]

    print("\n📝 Abstracts:")
    for idx in indices:
        if 0 <= idx < len(filtered):
            title, link = filtered[idx]
            abstract = fetch_abstract(link)
            print(f"\n▶ {title}\n{link}\n{abstract}")
            
            open_browser = input("🌐 Open this paper in your browser? (y/n): ").strip().lower()
            if open_browser == "y":
                webbrowser.open(link)
        else:
            print(f"Invalid index: {idx+1}")

if __name__ == "__main__":
    main()
