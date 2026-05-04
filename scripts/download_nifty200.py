import requests
import pandas as pd
import os
from datetime import datetime
import io

def download_nifty200():
    """
    Download Nifty 200 index constituents list.
    URL: https://nsearchives.nseindia.com/content/indices/ind_nifty200list.csv
    """
    url = "https://nsearchives.nseindia.com/content/indices/ind_nifty200list.csv"

    # Define a clear, fixed filename to avoid any server-side filename issues
    output_filename = "ind_nifty200list.csv"
    output_path = os.path.join('data', 'reference', output_filename)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/csv,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    try:
        print(f"📥 Downloading Nifty 200 list from: {url}")
        # Use stream=True for more control and to inspect headers if needed
        response = requests.get(url, headers=headers, timeout=60, stream=True)

        if response.status_code == 200:
            # Check if the content is CSV (basic check)
            content_type = response.headers.get('content-type', '')
            print(f"   Content-Type: {content_type}")

            # Read the content as text. Use response.text to handle decoding automatically.
            # If you want to force a specific encoding like 'utf-8-sig' for BOM, you can use:
            # content = response.content
            # df = pd.read_csv(io.BytesIO(content), encoding='utf-8')
            df = pd.read_csv(io.StringIO(response.text))
            # Alternatively, a more direct method:
            # df = pd.read_csv(url, headers=headers)

            if df.empty:
                print("⚠️ Downloaded file is empty.")
                return None

            print(f"✅ Downloaded Nifty 200 list: {len(df)} rows")
            print(f"   Columns: {list(df.columns)}")

            # Create reference directory if it doesn't exist
            os.makedirs('data/reference', exist_ok=True)
            df.to_csv(output_path, index=False)
            print(f"   File saved as: {output_path}")

            # Display first few symbols for confirmation
            symbol_col = next((col for col in df.columns if col.lower() == 'symbol'), None)
            if symbol_col:
                print(f"   Sample symbols: {df[symbol_col].head(5).tolist()}")
            else:
                print("   Warning: Could not find a 'Symbol' column in the downloaded file.")

            return df
        else:
            # HTTP error handling
            print(f"❌ HTTP {response.status_code}: Could not download Nifty 200 list.")
            print("   The NSE server might be unreachable or the file is temporarily unavailable.")
            print("   Please check the URL in a browser or try again later.")
            return None

    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        print(f"❌ Network error while downloading: {e}")
        print("   Check your internet connection or the server's availability.")
        return None
    except pd.errors.EmptyDataError:
        print("❌ Downloaded file is empty or not a valid CSV.")
        return None
    except Exception as e:
        # Catch-all for any other unexpected errors
        print(f"❌ An unexpected error occurred: {e}")
        print("   This might be due to a malformed response from the server.")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    download_nifty200()
