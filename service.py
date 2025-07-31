from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import os
from dotenv import load_dotenv
from gradio_client import Client
import requests
import time
from urllib.parse import urlparse
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import random
from PIL import Image


load_dotenv()

START_TASK_URL = "http://0.0.0.0:7861/tasks/start"
STATUS_URL = "http://0.0.0.0:7861/tasks/status"
GET_RESULTS_URL = "http://0.0.0.0:7861/tasks/result"

def initialize_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=os.environ["LLM_API_KEY"],
        temperature=0
    )

def start_task(prompt):
    print("Starting task...")
    response = requests.post(START_TASK_URL, json={"task": prompt})
    print("Task started.")
    
    while True:
        status = requests.get(STATUS_URL).json()
        # print("Current status:", status)
        if not status.get("running", True):
            print("Task completed.")
            break
        time.sleep(7)

    return None

def get_result():
    result = requests.get(GET_RESULTS_URL).json()
    return result

def get_clean_json(mess):
    llm = initialize_llm()

    prompt = f"""I have this messy result, and I want you to extract only the portion of key JSON info. Here's the messy result: {mess}. Please return just this clean information in the form of json, nothing else.
    
    Here's an example of the bit I want to extract. The exact values might not be the same, but the format should be like this:
    
    ```json{{"home_info": {{"zip_code": "00000", "num_of_bed": 2, "num_of_bath": 2, "square_footage": 2000, "year_built": 1940, "property_type": "Single Family", "additional_info": "This house is great!"}}}}```
    """

    raw = llm.invoke(prompt).content.strip()
    # print(raw) #debug
    clean_str = raw[7:-3].strip()
    parsed = json.loads(clean_str)
    return parsed



# Test with an address: 67 Davinci Dr Monmouth Junction, NJ 08852

def get_house_info(address: str):
    print("Retrieving house info...")
    prompt = f"""
        On Homes.com, search for "{address}" in the search box. Then, on the resulting webpage, extract all of these information from this page. For the additional info, extract the "About this home" section, along with any information that is important. Also, be sure to interact with buttons on the page if it reveals more information that was otherwise unavailable. Then, extract the Tax History information from the page.
        
        Return the result as JSON in the following format: 
        
        {{ 
            "home_info": {{
                {{"zip_code": "<value>"}}, 
                {{"num_of_bed": <value>}}, 
                {{"num_of_bath": <value>}}, 
                {{"square_footage": <value>}}, 
                {{"year_built": <value>}}, 
                {{"property_type": "<value>"}}, 
                {{"additional_info": "<value>"}},
                {{"url": "<url of the resulting webpage>}},
                {{"tax_history": [
                    {{
                    "year": 2022,
                    "tax_paid": "100",
                    "tax_assessment_total": "100,
                    "land_assessment": "300",
                    "improvement_assessment": "300"
                    }},
                    {{
                    "year": 2023,
                    "tax_paid": "100",
                    "tax_assessment_total": "100,
                    "land_assessment": "300",
                    "improvement_assessment": "300"
                    }},
                    {{
                    "year": 2024,
                    "tax_paid": "100",
                    "tax_assessment_total": "100,
                    "land_assessment": "300",
                    "improvement_assessment": "300"
                    }}
                ]}}
            }}
        }}
    """
    start_task(prompt)
    result = get_result()

    llm = initialize_llm()

    prompt = f"""I have this messy result, and I want you to extract only the portion of key JSON info. Here's the messy result: {result}. Please return just this clean information in the form of json, nothing else.
    
    Here's an example of the bit I want to extract. The exact values might not be the same, but the format should be like this:
    
    ```json{{"home_info": {{"zip_code": "00000", "num_of_bed": 2, "num_of_bath": 2, "square_footage": 2000, "year_built": 1940, "property_type": "Single Family", "additional_info": "This house is great!", "url": "<url of the resulting webpage>"}}}}```
    """

    raw = llm.invoke(prompt).content.strip()
    # print(raw) #debug
    clean_str = raw[7:-3].strip()
    parsed = json.loads(clean_str)
    print("House info retrieved successfully.")
    return parsed
    


def get_fun_things(address: str):
    llm = initialize_llm()

    print("Retrieving fun activities...")
    
    prompt = f"""
        What are some fun things to do near {address}?
        Provide a list of activities, parks, major places, nearby towns/cities, events, shopping malls, etc., that are enjoyable and accessible in the vicinity, say, a 1 hour radius. Provide it in a list format, and a short description of each activity or place. 
        """
    
    response = llm.invoke(prompt)
    print("Fun activities successfully retrieved.")
    return response.content.strip()


def get_crime_info(zip_code):
    prompt = f""" Go to "https://crimegrade.org/crime-by-zip-code/". Search for {zip_code}. On the following page, note the url of the page. Then, extract the overall crime grade, which should be in a letter grade format. Then, under "Is {zip_code}, NJ Safe?" section, there will be a short summary. Extract that summary. Return in the following format: 

    {{ 
        "crime": {{
            "crime_score": "<letter_grade>", 
            "summary": "<short_summary>",
            "source": "crimegrade.org",
            "url": "<url_of_the_page>"
        }}
    }}
    """
    print("Retrieving crime info...")
    start_task(prompt)
    mess = get_result()

    llm = initialize_llm()

    prompt = f"""I have this messy result, and I want you to extract only the portion of key JSON info. Here's the messy result: {mess}. Please return just this clean information in the form of json, nothing else.
    
    Here's an example of the bit I want to extract. The exact values might not be the same, but the format should be like this:
    
    ```json {{"crime": {{"crime_score": "letter_grade", "summary": "short_summary", "source": "crimegrade.org", "url": <url_of_the_page>}}}}```
    """

    raw = llm.invoke(prompt).content.strip()
    clean_str = raw[7:-3].strip()
    parsed = json.loads(clean_str)
    print("Crime info successfully retrieved.")
    return parsed


def fetch_image_urls(url):
    # Configure Selenium to run headless Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Automatically download and manage ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        print("Page loading...")

        # Wait for the carousel to load (adjust timeout as needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".primary-carousel-slide-img"))
        )
        print("Carousel loaded.")

        # Extract image URLs
        images = driver.find_elements(By.CSS_SELECTOR, ".primary-carousel-slide-img")
        urls = [img.get_attribute("src") for img in images if img.get_attribute("src")]

        return urls

    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        driver.quit()


def get_demographics(zip_code):
    prompt = f"""Go to https://bestneighborhood.org/racial-distribution-by-city/. Search for {zip_code}. Then, on the following page, extract the racial distribution information (which should be in a table format with "Self-Identified Race" in one column and the "Monmouth Junction, NJ Population" in the other column with percentages). Once you got that information, scroll down further to get the Diversity Score (which is a number). Return in the following format:
    {{
        "demographics": {{
            "racial_distribution": {{
                "white": <x>,
                "black": <x>,
                "asian": <x>,
                "hispanic": <x>,
                "native_american": <x>,
                "other": <x>,
                ...

            }},
            "diversity_score": <x>,
            "source": "bestneighborhood.org"
        }}
    }}
    """
    print("Retrieving demographics...")
    start_task(prompt)
    mess = get_result()

    llm = initialize_llm()

    prompt = f"""I have this messy result, and I want you to extract only the portion of key JSON info. Here's the messy result: {mess}. Please return just this clean information in the form of json, nothing else.
    
    Here's an example of the bit I want to extract. The exact values might not be the same, but the format should be like this:
    
    ```json{{"demographics": {{"racial_distribution": {{"white": <x>, "black": <x>, "asian": <x>, "hispanic": <x>,...}},"diversity_score": <x>, "source": "bestneighborhood.org"}}}}```
    """

    raw = llm.invoke(prompt).content.strip()
    # print(raw) #debug
    clean_str = raw[7:-3].strip()
    parsed = json.loads(clean_str)
    print("Demographics info successfully retrieved.")
    return parsed


def get_school_info(address: str):
    print("Rerieving school ratings...")
    prompt = f"""
        On https://schoolsparrow.com/, under the SCHOOL SEARCH, search for the state that {address} is in (note, be sure to type the full name if the state, e.g. if NY, type New York). On the next page, in the search box, type the city that {address} is in. Once the city has been typed, a list of schools should automatically appear in the table below. For each school entry, note the School Name, its School Level, and the SchoolSparrow 2020-21 Rating. Return the result as JSON in the following format: 
        
        {{ 
            "schools_information": [
                {{
                    "school_name": "<value>",
                    "school_level": "<value>",
                    "rating": "<value>"
                }},
                ...
            ]
        }}
    """
    llm = initialize_llm()
    start_task(prompt)
    mess = get_result()
    prompt = f"""I have this messy result, and I want you to extract only the portion of key JSON info. Here's the messy result: {mess}. Please return just this clean information in the form of json, nothing else.
    
    Here's an example of the bit I want to extract. The exact values might not be the same, but the format should be like this:
    
    ```json {{"schools_information": [{{"school_name": "<value>", "school_level": "<value>", "rating": "<value>"}},...]}}```
    """
    raw = llm.invoke(prompt).content.strip()
    clean_str = raw[7:-3].strip()
    parsed = json.loads(clean_str)
    return parsed


def get_price_estimate(info):
    llm = initialize_llm()

    prompt = f"""Given this information about a house, {info}, estimate the price of the house using these three pricing strategies: 

    1. Rule of Thumb Method: Estimated Price = (Sqft)(Avg. Price per Sqft in Area).
    2. Comparable sales method: Estimated Price = Price of Similar Property ± Adjustments for Differences.

    Some key factors you can consider for adjustments include: 
    Location
Homes in desirable areas or regions typically have higher prices per square foot. However, location goes well beyond zip codes and neighborhoods. A few location factors that increase or decrease values include: 

Proximity to schools and location within good districts. 
Distance from major roads or disruptive infrastructure like railroad lines and airports.
The value and condition of homes that surround the property. 
Nearby amenities like dog parks, playgrounds, grocery stores, and entertainment. 
A home may be in a desirable zip code but fall just out of range for a good school district. Two homes might be exactly the same, but one is next to a loud interstate. Location can have a big impact on price per square foot values.

Condition
Homes in better condition tend to have higher prices. This is because there is less work for buyers to do once they move in. One survey found 70% of buyers want a turnkey house that doesn’t require a lot of extra repairs. 

Condition doesn’t just relate to essential repairs, it can also relate to aging design elements. Old, dirty carpet that needs to be replaced or a kitchen that hasn’t been renovated since the 1980s can bring down perceived values.

If you are unsure why a house sold for a low price per square foot rate, look at the photos. The property may be worn or need essential repairs that caused the price to drop. 

Age
Older homes may have a lower price per square foot than newer homes. However, this usually is a reflection of the condition of the property. An older home may need essential replacements – like updated insulation, infrastructure repairs, or a new roof – or code upgrades like updated electrical wiring. A recent home will be built up to modern codes and have all new elements. 

However, there isn’t a direct correlation between age and price per square foot value. Some historic homes may sell for more because of their unique designs. Well-maintained old homes may pull in high sales prices, especially in desirable neighborhoods.

Poorly built new construction properties may sell for less if they have several known issues. Multiple factors contribute to the median price of a house and age is just one of them.

Lot Size
It’s important to look beyond the physical structure for sale to understand its price per square foot. Larger lot sizes may result in a higher price per square foot values for the home. This is because some buyers want large yards for their kids and pets to play in or simply value privacy.

Extra land is seen as a value-add to a house, making bigger lots more desirable. If two extremely similar houses have different price per square foot values, look at the lot size and location. 

Property Amenities
Look beyond the square footage of a home and consider the amenities that comprise the structure. Homes with additional amenities like pools, garages, or finished basements tend to have higher price per square foot values. This is because buyers are willing to pay more for these assets.

For example, a closed garage is often considered safer and more convenient for buyers than an open carport. Even though both amenities take up the same amount of space, the garage might increase the home’s price per square foot.

Market Trends
Market trends are incredibly fickle and can impact your price-per-square-foot calculations. This is why it is so important to look at small sales windows that are less than 30 days out and datasets within specific zip codes and neighborhoods.

Macroeconomic trends like changes in interest rates or buyer perceptions can change the median price of your home – even if you do nothing to it. 
    """

    response = llm.invoke(prompt)
    print("Price estimate successfully calculated.")
    return response.content.strip()


def download_map_image(url, output_filename="crime_map.webp"):
    """
    Navigates to a given URL, extracts the map image URL from the HTML,
    downloads the image to a local file, and returns the image URL.

    Args:
        url (str): The URL of the webpage to navigate to.
        output_filename (str): The name of the file to save the image as.
        
    Returns:
        tuple: (image_url: str, success: bool)
               image_url - the URL of the downloaded image (or None if failed)
               success - True if download succeeded, False otherwise
    """
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    service = Service()
    driver = None
    
    try:
        # Initialize WebDriver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print(f"Navigating to {url}...")
        driver.get(url)
        time.sleep(7)

        # Extract image URL
        image_url = None
        try:
            map_image_element = driver.find_element(By.ID, "per-capita-map")
            image_url = map_image_element.get_attribute("src")
            print(f"Found image URL: {image_url}")
        except Exception as e:
            print(f"Could not find image element: {e}")
            return None, False

        # Download image
        if image_url:
            try:
                response = requests.get(image_url, stream=True, timeout=10)
                response.raise_for_status()
                
                with open(output_filename, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"Image successfully saved as {output_filename}")
                return image_url
                
            except Exception as e:
                print(f"Failed to download image: {e}")
                return image_url
                
        return None, False
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, False
        
    finally:
        if driver:
            driver.quit()
            print("WebDriver closed.")


def get_similar_houses(url):
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Anti-detection settings
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print("Loading page with VISIBLE browser - watch what happens")
        driver.get(url)
        time.sleep(5)  # Let page load
        
        # Enhanced human-like scrolling
        scroll_actions = [
            (300, 0.8, 1.5),   # Initial small scroll
            (800, 0.5, 1.2),    # Medium scroll
            (1200, 0.3, 0.8),   # Large scroll
            (600, 0.8, 1.5),    
            (600, 0.8, 1.5),
            (1000, 0.8, 1.5), 
            (1200, 0.8, 1.5), 
            (800, 0.8, 1.5),
            (600, 0.8, 1.5), 
            (1200, 0.8, 1.5), 
            (800, 0.8, 1.5),
            (600, 0.8, 1.5),
            (800, 0.8, 1.5)
        ]
        
        for scroll_px, min_delay, max_delay in scroll_actions:
            driver.execute_script(f"window.scrollBy(0, {scroll_px});")
            time.sleep(3)
            print(f"Scrolled {scroll_px}px, waiting {min_delay}-{max_delay}s")

        print("Scrolling complete, waiting for lazy loading...")
        time.sleep(3)  # Wait for loading 

        # Find the section by its ID
        similar_homes_container = driver.find_element(
            By.CSS_SELECTOR, 
            "#similar-sold-section-server-side .embla__container"
        )
        
        print("Found correct container, saving REAL content...")
        with open("real_similar_homes.html", "w", encoding='utf-8') as f:
            f.write(similar_homes_container.get_attribute('outerHTML'))

        mess = similar_homes_container.get_attribute('outerHTML')
        
        print("SUCCESS! Check real_similar_homes.html")

        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        driver.save_screenshot("error.png")
        print("Saved screenshot as error.png")
    finally:
        driver.quit()



def create_html_report(property_map):
    llm = initialize_llm()
    prompt = f"""You are a highly skilled real estate agent tasked with writing a compelling and personable report about a house. Your goal is to highlight its best features and make it appealing to potential buyers, mirroring the persuasive and engaging tone, along with the styling of the webpage, of the provided HTML template.

    You will be given a Python dictionary containing detailed information about the house, and an HTML template that shows the desired structure and style of the report: {property_map}.

    Your task is to:

    Extract and utilize all relevant information from the provided Python dictionary to populate the report.

    Adopt a persuasive and personable tone, similar to the example content within the HTML template. Imagine you are speaking directly to a potential buyer.

    Write a report with that infomration in the style of a template.

    Maintain the overall structure and flow of the provided HTML template.

    The images the first two pictures in the [house_images] will be used as the first two images in the report, and the rest will be used in the gallery section.

    For the graphs for demographics and property value, you will use "images/demographic_graph.png" and "images/house_value_graph.png" respectively.

    Return just the html, with the complete code.

    Here is an example template with another address. Complete disregard and erase any mention of the other address (since it's an example) and replace it with new information about our new address: 

    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>Your New Home at 25 Keswick Rd</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;500;600&family=Dancing+Script:wght@700&display=swap" rel="stylesheet">
    <style>
        body {{
        background-color: #fdfaf4;
        font-family: 'Inter', sans-serif;
        margin: 3em auto;
        max-width: 800px;
        padding: 2.5em 3em;
        line-height: 1.8;
        font-size: 1.15rem;
        color: #3b3b3b;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}

        h1 {{
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        color: #2c3e50;
        margin-bottom: 0.3em;
        }}

        h2 {{
        font-size: 1.6rem;
        margin-top: 2em;
        color: #1a5276;
        }}

        .signature {{
        font-family: 'Dancing Script', cursive;
        font-size: 1.6rem;
        color: #7e4a1c;
        margin-top: 2em;
        }}

        .image-block {{
        text-align: center;
        margin: 1.5em 0;
        page-break-inside: avoid;
        }}

        .image-block img {{
        max-width: 100%;
        height: auto;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        display: block;
        margin: 0 auto;
        }}

        .quote {{
        margin: 2em 0;
        padding-left: 1em;
        border-left: 4px solid #d4b483;
        font-style: italic;
        color: #555;
        }}

        ul {{
        padding-left: 1.2em;
        margin-top: 1em;
        }}

        ul li {{
        margin-bottom: 0.6em;
        }}

        .metric-list {{
        list-style: none;
        padding-left: 0;
        margin: 1.5em 0;
        }}

        .metric-list li {{
        margin-bottom: 0.5em;
        font-weight: 500;
        }}

        table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 1em;
        }}

        th, td {{
        border: 1px solid #ddd;
        padding: 0.6em;
        text-align: center;
        }}

        th {{
        background-color: #1a5276;
        color: white;
        }}

        .footer {{
        margin-top: 4em;
        font-size: 0.95rem;
        color: #888;
        border-top: 1px solid #ddd;
        padding-top: 1em;
        text-align: center;
        }}

        .subtle-note {{
        font-style: italic;
        font-size: 0.95rem;
        margin-top: 1em;
        color: #666;
        }}

        .highlight {{
        color: #c0392b;
        font-weight: bold;
        }}

        .gallery {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 1em;
        margin-top: 1em;
        page-break-inside: avoid;
        }}

        .gallery img {{
        width: 100%;
        height: auto;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        display: block;
        page-break-inside: avoid;
        break-inside: avoid;
        }}

        @media print {{
        body {{
            background: white !important;
            color: black !important;
            box-shadow: none !important;
            max-width: 100%;
            margin: 0;
            padding: 1in;
            font-size: 12pt;
        }}
        .gallery, .gallery img {{
            page-break-inside: avoid;
            break-inside: avoid;
        }}

        .image-block img {{
            page-break-inside: avoid;
            break-inside: avoid;
        }}

        .footer {{
            font-size: 10pt;
            color: #444;
        }}

        @page {{
            size: Letter;
            margin: 1in;
        }}

        a {{
            color: black;
            text-decoration: none;
        }}

        h1, h2 {{
            color: black !important;
            page-break-after: avoid;
        }}
        }}
    </style>
    </head>
    <body>

    <h1>Welcome Home to 25 Keswick Road</h1>
    <p>Dear Mr. YZ,</p>

    <p>Let me take you on a little journey—not just through a house, but through what could soon become your next chapter. Nestled in the heart of East Windsor, this Colonial-style home has been lovingly maintained since 2001 and is ready to welcome you in.</p>



    <div class="image-block">
        <img src="images/1.avif" alt="Front porch">
    </div>
    <div class="image-block">
        <img src="images/2.jpg" alt="Backyard trees">
    </div>

    <p>Step through the front door and you’re immediately greeted by original hardwood floors that tell their own quiet story. East-facing windows bathe the space in morning light, while a cozy fireplace beckons for winter evenings. With <strong>3 bedrooms</strong>, <strong>2.5 bathrooms</strong>, and <strong>1,758 square feet</strong>, this home strikes a rare balance between charm and practicality.</p>

    <div class="quote">"The current owners tell me their favorite spot is the window seat in the primary bedroom — perfect for curling up with a book while watching the seasons change in your private backyard oasis."</div>

        <h2>Pricing Estimates</h2>
    <p>Now, let us calculate a rough price estimate for the house using a few methods. What I want you to know is that the following calculations are meant for you as a baseline to compare against the listing price, not as end all be all price.</p>

    <h3>1. Rule of Thumb Method</h3>
    <ul class="metric-list">
    <li>Square Footage: <strong>1,758 sqft</strong></li>
    <li>Average Price per Sqft: <strong>$243</strong> (East Windsor average price per sqft)</li>
    <li>Estimated Value: <span class="highlight">$427,194</span></li>
    </ul>

    <p class="subtle-note">This number is a conservative baseline for the property's value calculated by multiplying the average price per square foot for the zip code by the square footage of the property.</p>

    <h3>2. Comparable Sales Method</h3>
    <p>We compared 25 Keswick Rd against two recently sold properties in the area:</p>

    <table>
    <thead>
        <tr>
        <th>Feature</th>
        <th>25 Keswick</th>
        <th>201 Morrison Ave</th>
        <th>947 Old York Rd</th>
        </tr>
    </thead>
    <tbody>
        <tr><td><strong>Address</strong></td><td>25 Keswick Rd</td><td>201 Morrison Ave</td><td>947 Old York Rd</td></tr>
        <tr><td><strong>Beds/Baths</strong></td><td>3/2.5</td><td>7/4</td><td>3/2</td></tr>
        <tr><td><strong>Square Footage</strong></td><td>1,758</td><td>3,500</td><td>1,400</td></tr>
        <tr><td><strong>Sale Price</strong></td><td>-</td><td>$799,900</td><td>$530,000</td></tr>
        <tr><td><strong>Price/Sqft</strong></td><td>-</td><td>$228</td><td>$378</td></tr>
    </tbody>
    </table>

    <h3>Adjustments Analysis</h3>
    <ul class="metric-list">
    <li><strong>201 Morrison Ave:</strong>
        <ul>
        <li>Oversized at 3,500 sqft ($228/sqft)</li>
        <li>Adjusted estimate: <span class="highlight">$400,824</span> (lower bound)</li>
        </ul>
    </li>
    <li><strong>947 Old York Rd:</strong>
        <ul>
        <li>Undersized at 1,400 sqft ($378/sqft)</li>
        <li>Added $15,000 for extra half-bath</li>
        <li>Adjusted estimate: <span class="highlight">$679,524</span> (upper bound)</li>
        </ul>
    </li>
    </ul>

    <p>Balancing both comparables gives us:</p>
    <p style="font-size: 1.3rem; text-align: center;">
    <span class="highlight">$540,174</span>
    </p>

    <h3>Important Considerations</h3>
    <ul>
    <li><strong>Market Status:</strong> Optimism and demand in a market at any given time flucates depending on the housing market/economy. The calculations above are more baseline and conservative.</li>
    <li><strong>Unique Features:</strong> Asbestos shingle roof may require future attention</li>
    <li><strong>Zoning:</strong> R2 zoning offers flexibility for future use</li>
    <li><strong>Local Expertise:</strong> These estimates would be refined with hyperlocal sales data</li>
    </ul>

    <p class="subtle-note">Note: For the most accurate valuation, we recommend a professional appraisal which considers all unique characteristics of the property.</p>

    <h2>Home Stands Out</h2>
    <ul>
        <li>No HOA — you can personalize the home as you wish</li>
        <li>Expansive deck ideal for summer BBQs and quiet mornings</li>
        <li>Warm-toned hardwood floors with a gorgeous natural patina</li>
        <li>Chef’s kitchen perfect for weekend breakfasts and holiday dinners</li>
        <li>Sunlit spaces that feel warm and open</li>
    </ul>

    <div class="gallery">
        <img src="images/3.avif" alt="Kitchen">
        <img src="images/4.avif" alt="Living Room">
        <img src="images/5.avif" alt="Dining Room">
        <img src="images/6.avif" alt="Primary Bedroom">
        <img src="images/7.avif" alt="Deck View">
    </div>

    <div class="quote">"We raised our children here and it's been the perfect place to watch them grow. The neighborhood kids still play together after school, just like when we first moved in. We'll miss the sound of laughter echoing through these rooms." — <em>Current Homeowners</em></div>

    <h2>Safe, Smart, and Family-Friendly</h2>
    <p style="font-size: 1.3rem; font-weight: 600; color: #049e44; margin-top: -0.3em; margin-bottom: 0.8em;">
        Crime Grade: A
    </p>
    <p>You’re not just buying a house — you’re joining a neighborhood. The eastern part of East Windsor is known for its peace and safety, with odds of being a crime victim just <strong>1 in 88</strong>. It’s the kind of place where neighbors wave and kids ride bikes until sunset.</p>

    <p>The A grade indicates that the rate of crime is much lower than that of the average US zip. 08520 ranks in the 91st percentile for safety, meaning it is safer than 91% of zip codes.</p>


    <div class="image-block">
        <img src="images/crime_map_08540.webp" alt="Crime map">
    </div>

    <p>And for families? You're covered. This home is zoned for some of Mercer County’s top schools:</p>
    <ul class="metric-list">
        <li>📘 Reuther Elementary — <span class="highlight">9/10</span></li>
        <li>📘 Perry L. Drew Elementary — <span class="highlight">8/10</span></li>
        <li>📘 Melvin H. Kreps Middle School — <span class="highlight">8/10</span></li>
        <li>📘 High School South — <span class="highlight">7/10</span></li>
    </ul>

    <p>Did you know that a great school district and low crime rates are top factors for home value growth? Not only is this house a great investment for your kids, but for yourselves as well--take it from me.</p>

    <h2>A Proven Investment</h2>
    <p>Homes like this don’t just hold value—they grow it. Over the past decade, 25 Keswick has seen a <strong>36% increase</strong> in assessed value:</p>

    <table>
        <thead>
        <tr>
            <th>Year</th>
            <th>Tax Paid</th>
            <th>Assessment</th>
        </tr>
        </thead>
        <tbody>
        <tr><td>2024</td><td>$11,623</td><td>$340,000</td></tr>
        <tr><td>2023</td><td>$11,623</td><td>$330,000</td></tr>
        <tr><td>2022</td><td>$11,322</td><td>$320,000</td></tr>
        <tr><td>2021</td><td>$11,240</td><td>$310,000</td></tr>
        <tr><td>2020</td><td>$11,253</td><td>$290,000</td></tr>
        </tbody>
    </table>

    <div class="image-block">
        <img src="images/money_graph.png" alt="Property value graph">
    </div>

    <h2>Weekends You'll Look Forward To</h2>
    <p>Living here means being minutes from the very best of Central Jersey:</p>
    <ul>
        <li><strong>Nature & Parks:</strong> Mercer County Park (15 min), D&R Canal Trail (10–20 min), Thompson Park Zoo (20 min)</li>
        <li><strong>Arts & Culture:</strong> Grounds for Sculpture (20 min), Princeton Art Museum (25 min), Old Barracks Museum (30 min)</li>
        <li><strong>Shopping:</strong> Quaker Bridge Mall (20 min), Princeton boutiques (25 min)</li>
        <li><strong>Food & Wine:</strong> Old Hights Brewing Co. (10 min), Working Dog Winery (20 min)</li>
        <li><strong>Nearby Towns:</strong> Princeton (25 min), New Brunswick (30 min), Lambertville (45 min)</li>
    </ul>

    <p class="subtle-note">And yes—when you're done with your day out, you get to return to your private, peaceful sanctuary at 25 Keswick Rd.</p>

    <h2>A Community That Reflects the World</h2>
    <p>One of the things I personally admire about this area is just how beautifully diverse it is. With a <strong>diversity score of 97</strong>, East Windsor brings together families from all walks of life. It’s the kind of neighborhood where every culture is welcomed—and celebrated.</p>

    <p>Here’s a glimpse into the neighborhood’s vibrant blend:</p>
    <ul class="metric-list">
        <li>Asian — <strong>47.8%</strong></li>
        <li>White — <strong>33.0%</strong></li>
        <li>Black — <strong>8.0%</strong></li>
        <li>Hispanic — <strong>7.1%</strong></li>
    </ul>

    <div class="image-block">
        <img src="images/demographic_graph.png" alt="Demographics">
    </div>

    <p>If you're looking to raise your family in a community that reflects the rich diversity of the world, you'll feel right at home here.</p>

    <h2>Estimated Market Value</h2>

    <p>Based on current market data and comparable properties, here's how we estimate the value of 25 Keswick Road:</p>

    <div class="quote">"In today's market, pricing a home is both an art and a science. We consider multiple valuation methods to arrive at a fair market range."</div>

    <h2>Let’s Make It Yours</h2>
    <p>Homes like this don’t stay on the market long. Between its timeless style, modern updates, and unbeatable location, it’s already drawing attention from savvy buyers.</p>

    <p><strong>Don’t wait:</strong> Let’s schedule your private tour today. I’d love nothing more than to walk you through and answer any questions.</p>

    <p class="signature">Warmly,<br>Celine Dion<br>Opaida Realtors</p>

    <p class="subtle-note">P.S. Ask about recent upgrades like the new roof and energy-efficient windows — they’re not yet reflected in the price.</p>

    <div class="footer">
        Generated July 21, 2025 • Contact: 555‑123‑4567
    </div>

    </body>
    </html>.
    """

    response = llm.invoke(prompt).content.strip()
    return response

