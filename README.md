# Google Indexing API Automation

Python script configured to automatically submit URLs to Google Search Console via the Indexing API.

## Features

- **Bulk Mode**: Process all URLs from sitemap
- **Default Mode**: Process only today's updated content
- **Status Mode**: Check indexing status of a specific URL
- Daily 200 request limit
- Rate limiting: 60 requests per minute (automatic wait)
- Pending URL persistence and resumable processing

## Installation

### 1. Install Required Packages

```bash
pip install -r requirements.txt
```

### 2. Create Google Service Account

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Indexing API"
4. Create a Service Account
5. Download the JSON key file and place it in the project as `service_account.json`

### 3. Add Service Account to Search Console

Open [Google Search Console](https://search.google.com/search-console):
1. Select your property
2. Settings → Owners
3. Add your Service Account email address

## Usage

### Bulk Mode - Process All URLs

```bash
python main.py --mode bulk --sitemap https://yoursite.com/sitemap.xml
```

On first run, reads all URLs from sitemap and saves them to `pending_urls.txt`. On subsequent runs, uses the pending file.

### Default Mode - Process Today's Updates

```bash
python main.py --mode default --sitemap https://yoursite.com/sitemap.xml
```

Processes only URLs updated today by checking the `lastmod` date.

### Status Mode - Check URL Status

```bash
python main.py --mode status --url https://yoursite.com/page
```

Shows the Google indexing status of a specific URL.

### Custom Service Account File

```bash
python main.py --mode bulk --sitemap https://yoursite.com/sitemap.xml --key /path/to/key.json
```

## Limitations

- Daily 200 request limit
- 60 requests per minute (1 second wait between requests)
- Supports nested/hierarchical sitemaps

## File Structure

```
pending_urls.txt          # URLs waiting to be processed
service_account.json      # Google Service Account (in gitignore)
main.py                   # Main script
requirements.txt          # Python dependencies
config.py                 # Configuration settings
```

## Troubleshooting

- **Authentication error**: Check `service_account.json` file and path
- **Sitemap error**: Verify sitemap URL is correct
- **Rate limit**: Script automatically handles rate limiting with delays

## License

MIT
