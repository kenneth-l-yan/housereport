from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from service import get_house_info, get_fun_things, get_crime_info, fetch_image_urls, get_demographics, download_map_image, get_school_info, get_similar_houses, create_html_report
import time
from fastapi.middleware.cors import CORSMiddleware
from graphs import create_graphs
import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive Agg
import matplotlib.pyplot as plt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/report")
def get_report(address: str):
    house_info = get_house_info(address) 

    zip_code = house_info["home_info"]["zip_code"]
    homes_url = house_info["home_info"]["url"]
    money_data = house_info["home_info"]["tax_history"]

    time.sleep(65)

    fun_things = get_fun_things(address) 

    time.sleep(65)

    crime_info = get_crime_info(zip_code) 
    crime_url = crime_info["crime"]["url"]

    house_images = fetch_image_urls(homes_url)
    print(house_images)

    time.sleep(65)

    demographics = get_demographics(zip_code)
    demographic_data = demographics["demographics"]["racial_distribution"]
    crime_map = download_map_image(crime_url)

    time.sleep(65)

    school_info = get_school_info(address)
    create_graphs(money_data, demographic_data)

    time.sleep(65)

    similar_houses = get_similar_houses(homes_url)


    property_map = {
        "address": address,
        "house_info": house_info,
        "fun_things": fun_things,
        "crime_info": crime_info,
        "house_images": house_images,
        "demographics": demographics,
        "crime_map": crime_map,
        "school": school_info,
        "similar_houses": similar_houses,
    }

    print(property_map) # Debugging output

    html_report = create_html_report(property_map)

    return {"output": html_report}