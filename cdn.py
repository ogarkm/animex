import re
import sys
import requests
import js2py

def find_and_unpack_video_script(html_content: str) -> str:
    """
    Finds the 'eval(function(p,a,c,k,e,d)...)' packed script, unpacks it,
    and returns the readable JavaScript.
    """
    # This regex is specifically designed to find the P.A.C.K.E.R. script
    # It's more precise than a generic 'eval' search.
    packer_match = re.search(r"eval\(function\(p,a,c,k,e,d\)(.+?)\)\)", html_content, re.DOTALL)
    
    if not packer_match:
        print("\n❌ Error: Could not find the P.A.C.K.E.R. 'eval(function...)' script.")
        print("   This is the main script that holds the video link.")
        print("   The website's protection method may have changed.")
        sys.exit(1)

    # Reconstruct the full JavaScript string to be executed
    packed_js = "eval" + packer_match.group(0)
    print("[*] Found the correct P.A.C.K.E.R. script. De-obfuscating...")

    try:
        # Use js2py to execute the packer, which returns the unpacked, readable JS
        unpacked_js = js2py.eval_js(packed_js)
        return unpacked_js
    except Exception as e:
        print(f"\n❌ Error: The 'js2py' library failed to unpack the script: {e}")
        sys.exit(1)


def find_source_in_unpacked_js(unpacked_js: str) -> str:
    """
    Searches the readable JavaScript for the video source URL.
    """
    # This regex looks for: source: 'https://...' or sources:[{src:'https://...'}]
    source_match = re.search(r'source:\s*["\'](https?://[^"\']+)', unpacked_js)
    
    if source_match:
        print("[*] Successfully extracted the direct source URL!")
        return source_match.group(1)
    else:
        print("\n❌ Error: Could not find the 'source:' URL in the unpacked script.")
        print("   This means the final link is in a different variable.")
        print("   Below is the full unpacked script for manual inspection:\n")
        print("="*50)
        print(unpacked_js)
        print("="*50)
        sys.exit(1)

def main():
    """A simple main function to test the resolver."""
    print("--- Kwik Video Link Extractor ---")
    print("This script targets the correct 'packer' obfuscation layer.\n")
    
    kwik_url = input("Enter the full Kwik URL to test: ").strip()

    if not kwik_url:
        print("No URL entered. Exiting.")
        return

    print("\n" + "="*30)
    print(f"[*] Fetching Kwik page: {kwik_url}")

    try:
        # Fetch the HTML content of the page
        headers = {"Referer": "https://9anime.org.lv/"}
        resp = requests.get(kwik_url, headers=headers, timeout=15)
        resp.raise_for_status()
        html_content = resp.text
        
        # Step 1: Unpack the correct script
        unpacked_javascript = find_and_unpack_video_script(html_content)
        
        # Step 2: Find the source link within the result
        final_download_link = find_source_in_unpacked_js(unpacked_javascript)
        
        print("="*30 + "\n")
        print("✅ SUCCESS! ✅")
        print("Final Direct Download Link:")
        print(final_download_link)
        
    except SystemExit:
        print("\nProcess stopped due to a critical error.")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network Error: Failed to fetch the Kwik page: {e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()