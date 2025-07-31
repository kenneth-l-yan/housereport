import os
import requests
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def download_images(image_urls: list):
    """
    Downloads images from a list of URLs into a directory named 'images'.
    Uses a robust requests session with retries and browser-like headers.

    Args:
        image_urls (list): A list of strings, where each string is an image URL.
    """
    # Define the directory where images will be saved
    download_dir = "./images"

    # Create the directory if it doesn't exist
    if not os.path.exists(download_dir):
        try:
            os.makedirs(download_dir)
            print(f"Created directory: {download_dir}")
        except OSError as e:
            print(f"Error creating directory {download_dir}: {e}")
            return

    print(f"Starting image download to {download_dir}...")

    # Configure session with retries and browser-like headers
    session = requests.Session()

    # Define retry strategy:
    # total=10: 1 initial attempt + 9 retries
    # backoff_factor=2: Delays of 1s, 2s, 4s, 8s, 16s, 32s, 64s, 128s, 256s between retries
    # status_forcelist: HTTP status codes that should trigger a retry
    retry_strategy = Retry(
        total=10,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET"], # Only retry HEAD and GET requests
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Add browser-like headers to the session
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
        "Accept": "image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    })

    for i, url in enumerate(image_urls):
        print(f"\n--- Processing URL {i+1}/{len(image_urls)}: {url} ---")
        filename = f"image_{i+1}.jpg" # Default filename in case parsing fails or no extension
        response = None # Initialize response to None for finally block

        try:
            # Parse the URL to get the filename from the path
            parsed_url = urlparse(url)
            path_segments = parsed_url.path.split('/')
            potential_filename = path_segments[-1]

            # Use the potential filename if it's not empty, otherwise use the default
            if potential_filename:
                filename = potential_filename

            print(f"Attempting to determine filename for {url}...")

            # If the filename doesn't have an extension, try to infer or add a default
            if '.' not in filename:
                print("Filename has no extension, attempting to infer from Content-Type...")
                try:
                    # For HEAD requests, use a slightly shorter timeout but still benefit from retries
                    response_head = session.head(url, allow_redirects=True, timeout=15) # Increased HEAD timeout
                    response_head.raise_for_status()
                    content_type = response_head.headers.get('Content-Type')
                    if content_type and 'image' in content_type:
                        if 'jpeg' in content_type or 'jpg' in content_type:
                            filename += '.jpg'
                        elif 'png' in content_type:
                            filename += '.png'
                        elif 'gif' in content_type:
                            filename += '.gif'
                        print(f"Inferred extension from Content-Type: {content_type}. New filename: {filename}")
                    else:
                        filename += '.jpg'
                        print(f"Could not infer extension from Content-Type ({content_type}), defaulting to .jpg. New filename: {filename}")
                except requests.exceptions.RequestException as head_err:
                    print(f"Warning: Could not get HEAD response for {url} to infer content type: {head_err}. Defaulting to .jpg.")
                    filename += '.jpg'
                except Exception as head_gen_err:
                    print(f"Warning: An unexpected error occurred during HEAD request for {url}: {head_gen_err}. Defaulting to .jpg.")
                    filename += '.jpg'
            else:
                print(f"Filename already has an extension: {filename}")

            # Construct the full path for saving the image
            filepath = os.path.join(download_dir, filename)

            print(f"Attempting to download {url} to {filepath}...")

            # Send a GET request to the URL to download the image
            # stream=True allows us to download large files in chunks
            # Set a very generous timeout for the actual download
            response = session.get(url, stream=True, timeout=180) # Increased GET timeout significantly (3 minutes)
            response.raise_for_status()

            # Write the image content to a file in binary write mode
            print(f"Writing content to file: {filepath}...")
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Successfully downloaded: {filename}")

        except requests.exceptions.HTTPError as errh:
            print(f"Error: HTTP Error for {url}: {errh} (Status Code: {errh.response.status_code})")
        except requests.exceptions.ConnectionError as errc:
            print(f"Error: Connection Error for {url}: {errc}. Check your internet connection or URL validity.")
        except requests.exceptions.Timeout as errt:
            print(f"Error: Timeout Error for {url}: {errt}. The server took too long to respond after multiple retries.")
        except requests.exceptions.RequestException as err:
            print(f"Error: An unexpected requests error occurred for {url}: {err}")
        except Exception as e:
            print(f"Error: An unexpected general error occurred while processing {url}: {e}")
        finally:
            if response:
                response.close()
            print(f"--- Finished processing URL {i+1}/{len(image_urls)} ---")

    print("\nImage download process completed.")
    session.close() # Close the session when done

images = ['https://images.homes.com/listings/102/8991424934-851149991/67-davinci-dr-monmouth-junction-nj-primaryphoto.jpg', 'https://imagescdn.homes.com/i2/kdjtq8dNTRtF0JgyMwW2HH4PAiad49TAXAJT_5GS1Rs/117/67-davinci-dr-monmouth-junction-nj-thumb.jpg?p=1', 'https://imagescdn.homes.com/i2/7SFlAYo5rDO1FgdeZ1ed9VPs0aNv9epJsxECS0MWKmM/117/67-davinci-dr-monmouth-junction-nj-floorplan-3.svg?p=1', 'https://images.homes.com/listings/214/1002424934-851149991/67-davinci-dr-monmouth-junction-nj-buildingphoto-4.jpg', 'https://images.homes.com/listings/214/3002424934-851149991/67-davinci-dr-monmouth-junction-nj-buildingphoto-5.jpg', 'https://images.homes.com/listings/214/5002424934-851149991/67-davinci-dr-monmouth-junction-nj-buildingphoto-6.jpg', 'https://images.homes.com/listings/214/6002424934-851149991/67-davinci-dr-monmouth-junction-nj-buildingphoto-7.jpg']

download_images(images)