import argparse
import os
import time
import datetime
import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from config import PENDING_FILE, SCOPES, ENDPOINT_PUBLISH, ENDPOINT_METADATA, DAILY_LIMIT, WAIT_BETWEEN_REQUESTS

def get_authorized_session(key_path):
    """Creates an authorized session for the Google Indexing API."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            key_path, scopes=SCOPES)
        return AuthorizedSession(credentials)
    except Exception as e:
        print(f"Authentication error (check your JSON file): {e}")
        exit(1)

def get_urls_from_sitemap(sitemap_url, only_today=False):
    """Extracts URLs from the sitemap. Supports nested sitemap indexes."""
    urls = []
    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        # XML Namespace definition (Sitemap standard)
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # If this is a sitemap index, iterate through child sitemaps
        for sitemap in root.findall('ns:sitemap', namespaces):
            loc = sitemap.find('ns:loc', namespaces)
            if loc is not None:
                urls.extend(get_urls_from_sitemap(loc.text, only_today))
                
        # If this is a standard urlset, collect URLs
        today_str = datetime.date.today().isoformat()
        for url in root.findall('ns:url', namespaces):
            loc = url.find('ns:loc', namespaces)
            lastmod = url.find('ns:lastmod', namespaces)
            
            if loc is not None:
                if only_today:
                    # Check if lastmod exists and starts with today's date (e.g., 2026-05-11)
                    if lastmod is not None and lastmod.text and lastmod.text.startswith(today_str):
                        urls.append(loc.text)
                else:
                    urls.append(loc.text)
    except Exception as e:
        print(f"Error reading sitemap ({sitemap_url}): {e}")
        
    return urls

def load_pending_urls():
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return None

def save_pending_urls(urls):
    with open(PENDING_FILE, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(f"{url}\n")

def remove_url_from_file(url_to_remove):
    urls = load_pending_urls()
    if urls and url_to_remove in urls:
        urls.remove(url_to_remove)
        save_pending_urls(urls)

def publish_url(session, url):
    """Submits the URL to Google for indexing."""
    body = {
        "url": url,
        "type": "URL_UPDATED"
    }
    return session.post(ENDPOINT_PUBLISH, json=body)

def check_status(session, url):
    """Checks the indexing notification status of the URL."""
    return session.get(f"{ENDPOINT_METADATA}?url={url}")

def main():
    parser = argparse.ArgumentParser(description="Google Indexing API Automation")
    parser.add_argument('--mode', choices=['bulk', 'default', 'status'], required=True, help="Operation mode")
    parser.add_argument('--sitemap', help="Sitemap URL (required for bulk and default modes)")
    parser.add_argument('--url', help="URL to check (required for status mode)")
    parser.add_argument('--key', default='service_account.json', help="Google Service Account JSON file path")
    
    args = parser.parse_args()
    session = get_authorized_session(args.key)

    # 1. BULK MODE
    if args.mode == 'bulk':
        if not args.sitemap:
            print("Error: --sitemap parameter is required in bulk mode.")
            return

        pending_urls = load_pending_urls()
        
        if pending_urls is None:
            print("No saved file found. Scanning sitemap...")
            pending_urls = get_urls_from_sitemap(args.sitemap, only_today=False)
            # Make the list unique to prevent duplicates
            pending_urls = list(set(pending_urls)) 
            save_pending_urls(pending_urls)
            print(f"Total {len(pending_urls)} URLs found and saved to {PENDING_FILE}.")
        else:
            print(f"Saved file found. Continuing to process remaining {len(pending_urls)} URLs...")

        if not pending_urls:
            print("No URLs found to process.")
            return

        count = 0
        for url in pending_urls[:]:
            if count >= DAILY_LIMIT:
                print(f"\n[!] Daily maximum limit of {DAILY_LIMIT} requests reached. Stopping process.")
                print(f"Remaining URLs are waiting in {PENDING_FILE} to be processed tomorrow.")
                break
            
            print(f"[{count+1}/{DAILY_LIMIT}] Sending request: {url}")
            response = publish_url(session, url)
            
            if response.status_code in (200, 204):
                print(" -> Success.")
                remove_url_from_file(url)
                count += 1
            else:
                print(f" -> Error ({response.status_code}): {response.text}")
            
            time.sleep(WAIT_BETWEEN_REQUESTS)
            
        if len(load_pending_urls()) == 0:
            print("\nAll URLs processed successfully and file cleared!")

    # 2. DEFAULT MODE
    elif args.mode == 'default':
        if not args.sitemap:
            print("Error: --sitemap parameter is required in default mode.")
            return
            
        print("Scanning sitemap and searching for today's content...")
        today_urls = get_urls_from_sitemap(args.sitemap, only_today=True)
        today_urls = list(set(today_urls))
        
        if not today_urls:
            print("No new or updated content found for today.")
            return
            
        print(f"Found {len(today_urls)} URLs for today. Sending requests...")
        for i, url in enumerate(today_urls):
            print(f"[{i+1}/{len(today_urls)}] Sending: {url}")
            response = publish_url(session, url)
            if response.status_code in (200, 204):
                print(" -> Success.")
            else:
                print(f" -> Error ({response.status_code}): {response.text}")
            time.sleep(3) # Respect API limits

    # 3. STATUS MODE
    elif args.mode == 'status':
        if not args.url:
            print("Error: --url parameter is required in status mode.")
            return
            
        print(f"Checking status: {args.url}")
        response = check_status(session, args.url)
        
        if response.status_code == 200:
            data = response.json()
            print("\n--- Index Status ---")
            print(f"Last Notification Time: {data.get('urlNotificationMetadata', {}).get('latestUpdate', {}).get('notifyTime', 'Unknown')}")
            print(f"Notification Type: {data.get('urlNotificationMetadata', {}).get('latestUpdate', {}).get('type', 'Unknown')}")
        elif response.status_code == 404:
            print("No previous notification made via Indexing API for this URL.")
        else:
            print(f"Error ({response.status_code}): {response.text}")

if __name__ == "__main__":
    main()
