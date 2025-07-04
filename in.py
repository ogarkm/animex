import re
import sys
import requests
from bs4 import BeautifulSoup

# --- Helper Functions (Adapted for Local Script) ---
# Note: We've replaced web server errors with printing an error and exiting the script.

def get_anime_title(jikan_id: str) -> str:
    """Fetches the anime title from Jikan API."""
    print(f"[*] Fetching title for Jikan ID: {jikan_id}...")
    url = f"https://api.jikan.moe/v4/anime/{jikan_id}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"Error: Jikan API returned status {resp.status_code}. ID {jikan_id} might be incorrect.")
            sys.exit(1)
        data = resp.json().get("data", {})
        title = data.get("title_english") or data.get("title")
        if not title:
            print("Error: Could not find a title in the Jikan API response.")
            sys.exit(1)
        print(f"[*] Found title: {title}")
        return title
    except requests.exceptions.RequestException as e:
        print(f"Error: A network error occurred while contacting Jikan API: {e}")
        sys.exit(1)

def slugify_title_for_9anime(title: str) -> str:
    """Converts a title to a URL-friendly slug."""
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    slug = s.strip("-")
    print(f"[*] Generated slug: {slug}")
    return slug

def find_9anime_iframe_src(nineanime_url: str) -> str:
    """Finds the GogoAnime iframe source from a 9anime page."""
    print(f"[*] Scraping 9anime page: {nineanime_url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(nineanime_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"Error: 9Anime page not found (status {resp.status_code}). The anime/episode may not exist there.")
            print(f"URL tried: {nineanime_url}")
            sys.exit(1)

        soup = BeautifulSoup(resp.text, "html.parser")
        embed_div = soup.find("div", id="embed_holder")
        if not embed_div:
            print("Error: Could not find the video player container on the 9anime page.")
            sys.exit(1)

        iframe_tag = embed_div.find("iframe", src=True)
        if iframe_tag:
            src = iframe_tag["src"]
            print(f"[*] Found iframe source: {src}")
            return src

        script_tag = embed_div.find("script")
        if script_tag and script_tag.string:
            match = re.search(r"<iframe[^>]*\s+src=[\"']([^\"']+)[\"']", script_tag.string)
            if match:
                src = match.group(1)
                print(f"[*] Extracted iframe source from script: {src}")
                return src

        print("Error: Could not find or extract the iframe source from the 9anime page.")
        sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Error: A network error occurred while contacting 9anime: {e}")
        sys.exit(1)


def generate_iframe_src(jikan_id: str, episode: int, dub: bool = False) -> str:
    """Generates the GogoAnime iframe source URL."""
    title = get_anime_title(jikan_id)
    base_slug = slugify_title_for_9anime(title)
    slug_suffix = f"-dub-episode-{episode}" if dub else f"-episode-{episode}"
    nineanime_slug = f"{base_slug}{slug_suffix}"
    nineanime_url = f"https://9anime.org.lv/{nineanime_slug}/"
    return find_9anime_iframe_src(nineanime_url)

def generate_download_link(jikan_id: str, episode: int, dub: bool = False) -> str:
    """Generates the GogoAnime iframe source URL."""
    title = get_anime_title(jikan_id)
    base_slug = slugify_title_for_9anime(title)
    slug_suffix = f"-dub-episode-{episode}" if dub else f"-episode-{episode}"
    nineanime_slug = f"{base_slug}{slug_suffix}"
    return f"https://9anime.org.lv/{nineanime_slug}/"

def resolve_redirect_url(url: str) -> str:
    """Follows redirects to find the final direct download URL."""
    print("[*] Resolving download redirect... (this may take a moment)")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.head(url, headers=headers, allow_redirects=True, timeout=15)
        resp.raise_for_status()
        final_url = resp.url
        print("[*] Redirect resolved.")
        return final_url
    except requests.exceptions.Timeout:
        print("Error: Request timed out while resolving download redirect.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to resolve download redirect: {e}")
        sys.exit(1)

def extract_nonce_from_html(html: str) -> str:
    """Extracts the nonce value from the HTML or JavaScript."""
    # Try to find nonce in JS variable assignment (e.g., var nonce = '...';)
    match = re.search(r"nonce\s*[:=]\s*['\"]([a-fA-F0-9]{10,})['\"]", html)
    if match:
        nonce = match.group(1)
        print(f"[*] Extracted nonce from HTML: {nonce}")
        return nonce
    # Try to find nonce in data attributes or elsewhere if needed
    print("Error: Could not find nonce in the HTML.")
    sys.exit(1)

def get_nonce_from_9anime(jikan_id: str, episode: int, dub: bool = False) -> str:
    """Fetches the episode page and extracts the nonce value."""
    title = get_anime_title(jikan_id)
    base_slug = slugify_title_for_9anime(title)
    slug_suffix = f"-dub-episode-{episode}" if dub else f"-episode-{episode}"
    nineanime_slug = f"{base_slug}{slug_suffix}"
    nineanime_url = f"https://9anime.org.lv/{nineanime_slug}/"
    print(f"[*] Fetching episode page for nonce: {nineanime_url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(nineanime_url, headers=headers, timeout=10)
        resp.raise_for_status()
        print("[*] Successfully fetched nonce.")
        print("[*] Nonce: " + extract_nonce_from_html(resp.text))
        return extract_nonce_from_html(resp.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch episode page for nonce: {e}")
        sys.exit(1)

def get_download_link(jikan_id: str, episode: int, dub: bool, quality: str) -> str:
    """Fetches the final, direct download link using the AJAX endpoint."""
    nonce = get_nonce_from_9anime(jikan_id, episode, dub)
    ep = episode
    mal_id = jikan_id

    print(f"[*] Fetching download links via AJAX for MAL ID {mal_id}, episode {ep}...")

    params = {
        "action": "fetch_download_links",
        "mal_id": mal_id,
        "ep": ep,
        "nonce": nonce
    }
    try:
        resp = requests.get(
            "https://9anime.org.lv/wp-admin/admin-ajax.php",
            params=params,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        print("[*] Successfully fetched download links via AJAX.")
    except Exception as e:
        print(f"Error: Failed to fetch download links via AJAX: {e}")
        sys.exit(1)

    if data.get("data", {}).get("status") == 200 or data.get("status") == 200:
        html_content = data.get("data", {}).get("result") or data.get("result")
        soup = BeautifulSoup(html_content, "html.parser")
        section_text = "Dub" if dub else "Sub"
        # Find all divs and match the heading by text (not just direct children)
        section_heading = None
        for div in soup.find_all("div"):
            if div.get_text(strip=True) == section_text:
                section_heading = div
                break
        if not section_heading:
            print(f"Error: '{section_text}' download section not found.")
            sys.exit(1)
        # The next sibling div contains the links
        links_container = section_heading.find_next_sibling("div")
        if not links_container:
            print(f"Error: Could not find link container for '{section_text}' section.")
            sys.exit(1)
        quality_link_tag = None
        for a in links_container.find_all("a"):
            if a.get_text(strip=True).lower() == quality.lower():
                quality_link_tag = a
                break
        if not quality_link_tag or not quality_link_tag.has_attr('href'):
            available_links = [a.get_text(strip=True) for a in links_container.find_all('a')]
            error_msg = f"Error: Download link for quality '{quality}' not found in '{section_text}' section."
            if available_links:
                error_msg += f"\nAvailable qualities for this section: {', '.join(available_links)}"
            else:
                error_msg += "\nNo download qualities were found in this section."
            print(error_msg)
            sys.exit(1)
        initial_url = quality_link_tag['href']
        print(f"[*] Found initial download link: {initial_url}")
        final_url = resolve_redirect_url(initial_url)
        return final_url
    elif data.get("data", {}).get("status") == 500 or data.get("status") == 500:
        print("No Download Links Available yet.")
        sys.exit(1)
    else:
        print("Unexpected error occurred. Please try again later.")
        sys.exit(1)

def main():
    """Main function to run the script and get user input."""
    print("--- Anime Downloader Script ---")
    print("This script will find a direct download link for an anime episode.")
    print("You will need the Jikan (MyAnimeList) ID for the anime.\n")

    # Get Jikan ID
    jikan_id = input("Enter the Jikan/MAL ID (e.g., 52991 for Frieren): ").strip()
    if not jikan_id.isdigit():
        print("Error: ID must be a number.")
        sys.exit(1)
    try:
        print(f"[*] Anime Selected: {get_anime_title(jikan_id)}")
        v = input("Press Enter to continue...")
    except Exception as e:	
        print(f"Error: Failed to fetch anime title: {e}")
        sys.exit(1)

    # Get Episode Number
    while True:
        episode_str = input("Enter the episode number: ").strip()
        if episode_str.isdigit():
            episode = int(episode_str)
            break
        else:
            print("Invalid input. Please enter a whole number for the episode.")

    # Get Dubbed preference
    while True:
        dub_str = input("Do you want the Dubbed version? (yes/no): ").strip().lower()
        if dub_str in ['yes', 'y']:
            dub = True
            break
        elif dub_str in ['no', 'n']:
            dub = False
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")
    
    # Get Quality preference
    allowed_qualities = ['360p', '720p', '1080p']
    while True:
        quality = input(f"Enter desired quality ({'/'.join(allowed_qualities)}): ").strip().lower()
        if quality in allowed_qualities:
            break
        else:
            print(f"Invalid input. Please choose one of: {', '.join(allowed_qualities)}")
    
    print("\n" + "="*30)
    print("Starting process...")

    try:
        final_download_link = get_download_link(
            jikan_id=jikan_id,
            episode=episode,
            dub=dub,
            quality=quality
        )
        print("="*30 + "\n")
        print("✅ SUCCESS! ✅")
        print("Final Direct Download Link:")
        print(final_download_link)
        print("\nCopy and paste the link above into your browser or download manager.")

    except SystemExit:
        # This catches our sys.exit() calls from the helper functions
        print("\n❌ Process failed. Please check the error message above. ❌")
    except Exception as e:
        # Catch any other unexpected errors
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()