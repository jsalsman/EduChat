import requests
from bs4 import BeautifulSoup
import urllib.parse

# Define the tools schema
tools = [
    {
      "name": "web_search",
      "description": "Search the web using DuckDuckGo",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string"
          },
          "num_results": {
            "type": "integer"
          }
        },
        "required": [
          "query"
        ]
      }
    },
    {
      "name": "read_webpage",
      "description": "Read and extract text content from a webpage",
      "parameters": {
        "type": "object",
        "properties": {
          "url": {
            "type": "string"
          }
        },
        "required": [
          "url"
        ]
      }
    }
]

def search_duckduckgo(query: str, num_results: int = 5) -> list:
  """Search DuckDuckGo and return results with clean, decoded URLs."""
  encoded_query = urllib.parse.quote(query)
  url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
  headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  }

  response = requests.get(url, headers=headers)
  soup = BeautifulSoup(response.text, 'html.parser')

  results = []
  for result in soup.find_all('div', class_='result')[:num_results]:
    title_elem = result.find('a', class_='result__a')
    link = title_elem.get('href') if title_elem else None
    title = title_elem.text if title_elem else None
    snippet = result.find('a', class_='result__snippet')
    description = snippet.text if snippet else None

    if title and link:
      # Decode the DuckDuckGo redirect URL
      if 'duckduckgo.com/l/?uddg=' in link:
        # Extract the encoded URL and decode it
        canonical_url = urllib.parse.unquote(link.split('uddg=')[1])
        # Remove the DuckDuckGo tracking parameter
        if '&rut=' in canonical_url:
          canonical_url = canonical_url.split('&rut=')[0]
      else:
        canonical_url = link

      results.append({
          "title": title,
          "url": canonical_url,
          "description": description
      })

  return results

def read_webpage(url: str) -> str:
  """Read and extract text content from a webpage."""
  try:
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove unwanted elements
    for element in soup(["script", "style", "nav", "header", "footer"]):
      element.decompose()

    # Get text and maintain links with their href URLs
    for a_tag in soup.find_all('a'):
      href = a_tag.get('href')
      if href:
        a_tag.replace_with(f"[ {a_tag.text} ]( {href} )")

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)

    return text[:300000]  # Truncate to avoid token limits, adjusted for larger context window
  except Exception as e:
    return f"Error reading webpage: {str(e)}"
