#!/usr/bin/env python3

import argparse
import json
import requests
import sys
from pathlib import Path

def get_user_input():
    """Get URL and format preferences from user"""
    print("\n=== Web Scraper ===")
    
    # Get URL
    while True:
        url = input("\nEnter the URL to scrape: ").strip()
        if url.startswith(('http://', 'https://')):
            break
        print("Please enter a valid URL starting with http:// or https://")
    
    # Get format preference
    print("\nAvailable formats:")
    print("1. All formats (markdown, HTML, and JSON)")
    print("2. Markdown only")
    print("3. HTML only")
    print("4. JSON only")
    
    while True:
        try:
            choice = int(input("\nSelect format (1-4): "))
            if choice in [1, 2, 3, 4]:
                break
            print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a valid number")
    
    format_map = {
        1: 'all',
        2: 'markdown',
        3: 'html',
        4: 'json'
    }
    
    # Get custom filename (optional)
    custom_name = input("\nEnter custom filename (press Enter to use default): ").strip()
    
    return url, format_map[choice], custom_name if custom_name else None

def scrape_url(url, output_format='all', output_file=None):
    """
    Scrape a URL and save the output
    
    Args:
        url (str): The URL to scrape
        output_format (str): Format to save ('all', 'markdown', 'html')
        output_file (str): Output file path (optional)
    """
    # API endpoint
    api_url = 'http://localhost:3002/v1/scrape'
    headers = {'Content-Type': 'application/json'}
    data = {'url': url}
    
    try:
        print("\nScraping, please wait...")
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if not result.get('success'):
            print(f"\nError: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
        content = result['data']
        
        if not output_file:
            domain = url.split('//')[-1].split('/')[0]
            output_file = f"scraped_{domain}"
        
        output_file = str(Path(output_file).with_suffix(''))
        print("\nSaving files...")
        
        if output_format in ['all', 'markdown']:
            md_file = f"{output_file}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content.get('markdown', ''))
            print(f"✓ Markdown saved to: {md_file}")
            
        if output_format in ['all', 'html']:
            html_file = f"{output_file}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content.get('html', ''))
            print(f"✓ HTML saved to: {html_file}")
            
        if output_format in ['all', 'json']:
            json_file = f"{output_file}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"✓ Full JSON response saved to: {json_file}")
        
        print("\nDone! Files have been saved successfully.")
            
    except requests.exceptions.RequestException as e:
        print(f"\nError making request: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='Web scraping tool')
        parser.add_argument('url', help='URL to scrape')
        parser.add_argument('-f', '--format', 
                          choices=['all', 'markdown', 'html', 'json'],
                          default='all',
                          help='Output format (default: all)')
        parser.add_argument('-o', '--output',
                          help='Output file name (without extension)')
        
        args = parser.parse_args()
        url, output_format, output_file = args.url, args.format, args.output
    else:
        url, output_format, output_file = get_user_input()
    
    scrape_url(url, output_format, output_file)

if __name__ == '__main__':
    main() 