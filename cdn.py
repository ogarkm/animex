import js2py
import re
import requests
import sys

# Make sure this function replaces your old resolve_redirect_url
def resolve_redirect_url(url: str) -> str:
    """
    Resolves the Kwik player page by fetching its content, de-obfuscating
    the JavaScript packer, and extracting the final video source URL.
    """
    try:
        headers = {"Referer": "https://9anime.org.lv/"}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        html_content = resp.text

        # Step 1: Find the packed JavaScript code using regex.
        # This looks for the specific "eval(function(p,a,c,k,e,d)..." pattern.
        packed_match = re.search(r"eval\(function\(p,a,c,k,e,d\)(.+?)\)\)", html_content, re.DOTALL)
        if not packed_match:
            print("Could not find the packed JS code on the Kwik page.")
            sys.exit(1)

        packed_js = "eval" + packed_match.group(0)

        # Step 2: Use a JS runtime to execute the packed code.
        # This will unpack it into readable JavaScript containing the video source.
        unpacked_js = js2py.eval_js(packed_js)

        # Step 3: Search the unpacked JavaScript for the final source URL.
        # It's usually in a "source: '...'" or "sources:[{src: '...'}]" format.
        source_match = re.search(r'source:\s*["\'](https?://[^"\']+)', unpacked_js)
        if not source_match:
            print("Could not find the video source URL in the unpacked JavaScript.")

        # The captured group is our final, direct download link.
        final_url = source_match.group(1)
        
        # Sometimes the filename needs to be appended
        if "file=" not in final_url:
             title_match = re.search(r'<h1 class="title">\s*(.+?)\s*</h1>', html_content)
             if title_match:
                 filename = title_match.group(1).strip()
                 final_url += f"?file={filename}"

        return final_url

    except requests.exceptions.RequestException as e:
        print(f"Network error while fetching the Kwik page: {e}")
    except Exception as e:
        # Catch any other errors during the process
        print(f"An error occurred while resolving the redirect URL: {e}")



print(resolve_redirect_url(input("Enter the Kwik player URL: ")))