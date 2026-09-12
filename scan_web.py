import asyncio
import json
import re
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

START_URL = "https://www.torm.com/news/company-announcements/default.aspx"
OUTPUT_DIR = Path("result")
OUTPUT_DIR.mkdir(exist_ok=True)
MAX_ARTICLES = 2


def clean_text(text: str) -> str:
    """Normalize whitespace in extracted strings."""
    return re.sub(r"\s+", " ", text or "").strip()


async def safe_goto(page, url: str, wait_ms: int = 3000) -> bool:
    """Safely navigate to a URL with error handling."""
    try:
        print(f"Navigating to: {url}")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(wait_ms)
        return True
    except Exception as exc:
        print(f"[WARNING] Navigation issue at {url}: {exc}")
        return False


async def get_article_links(page) -> list[dict]:
    """Level 1: Fetch listing page and extract real announcement links."""
    print("Opening listing page...")
    if not await safe_goto(page, START_URL, wait_ms=4000):
        print("[ERROR] Failed to load listing page.")
        return []

    # Handle potential cookie banners
    try:
        cookie_btn = page.locator("button:has-text('Accept'), button:has-text('Allow all')")
        if await cookie_btn.count() > 0:
            await cookie_btn.first.click()
            await page.wait_for_timeout(1000)
    except Exception:
        pass

    # Scroll page to trigger lazy loading
    for _ in range(5):
        await page.mouse.wheel(0, 1500)
        await page.wait_for_timeout(800)

    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    extracted_links = []
    seen_urls = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        text = clean_text(anchor.get_text(" ", strip=True))

        if not href or len(text) < 5:
            continue

        # Ignore anchor fragment links like #maincontent
        if "#" in href:
            href = href.split("#")[0]
            if not href:
                continue

        full_url = urljoin(START_URL, href)

        # Restrict strictly to details pages
        if "company-announcements-details" not in full_url:
            continue

        if full_url in seen_urls:
            continue

        seen_urls.add(full_url)
        extracted_links.append({"title": text, "url": full_url})

    print(f"Extracted {len(extracted_links)} unique detail page links.")
    return extracted_links[:MAX_ARTICLES]


async def extract_article_content(page, article: dict) -> dict:
    """Level 2: Open individual detail page and extract dynamic article text."""
    url = article["url"]
    print(f"Extracting content from: {url}")

    await safe_goto(page, url, wait_ms=3000)

    # Scroll down to ensure dynamic blocks trigger
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    await page.wait_for_timeout(1000)

    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Clean header, footer, script, and navigation noise
    for element in soup(["script", "style", "noscript", "svg", "nav", "header", "footer"]):
        element.decompose()

    # Identify main body container or fallback to body
    main_container = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", class_=re.compile(r"module|news|detail|content", re.I))
        or soup.body
    )

    paragraphs = []
    if main_container:
        # Include tables, paragraphs, headers, and bullet lists
        for node in main_container.find_all(["h1", "h2", "h3", "h4", "p", "li", "td"]):
            txt = clean_text(node.get_text())
            if len(txt) > 25 and txt not in paragraphs:
                paragraphs.append(txt)

    full_text = "\n\n".join(paragraphs)

    # Fallback if specific tags missed text block
    if not full_text and main_container:
        full_text = clean_text(main_container.get_text(" ", strip=True))

    # Extract Date matching common format strings
    date_match = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
        soup.get_text(),
        re.IGNORECASE,
    )
    date_str = date_match.group(0) if date_match else "N/A"

    return {
        "title": article["title"],
        "date": date_str,
        "url": url,
        "content": full_text,
    }


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Level 1: Extract real detail links
        articles = await get_article_links(page)

        # Level 2: Fetch contents
        results = []
        for idx, article in enumerate(articles, 1):
            print(f"[{idx}/{len(articles)}]")
            try:
                data = await extract_article_content(page, article)
                results.append(data)
                print(f"--> Extracted {len(data['content'])} characters.")
            except Exception as err:
                print(f"[ERROR] Failed extracting {article['url']}: {err}")

        await browser.close()

    # Save output
    json_path = OUTPUT_DIR / "torm_articles.json"
    md_path = OUTPUT_DIR / "torm_articles.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# TORM Company Announcements\n\n")
        for idx, item in enumerate(results, 1):
            f.write(f"## {idx}. {item['title']}\n")
            f.write(f"**Date:** {item['date']}  \n")
            f.write(f"**URL:** {item['url']}\n\n")
            f.write(f"{item['content']}\n\n---\n\n")

    print(f"\nSaved {len(results)} items to {OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())