# House Report

## Overview

`housereport` is an application that generates detailed, personalized real estate reports for a given property address. It leverages AI (Google Gemini via LangChain), web scraping, data visualization, and prompt engineering to provide buyers with comprehensive insights, including:

- Property details and tax history
- Fun things to do nearby
- Crime statistics and maps
- Demographic breakdowns
- School ratings
- Comparable sales and price estimates
- Gallery of property images
- Custom HTML report output

## Features

- **AI-powered data extraction**: Uses Gemini (via LangChain) to extract and summarize property, crime, demographic, and school info.
- **Web scraping**: Fetches images and similar house data using Selenium.
- **Data visualization**: Generates graphs for demographics and property value.
- **Custom HTML report**: Outputs a styled report.

## Project Structure

- [`app.py`](app.py): FastAPI entrypoint, orchestrates report generation.
- [`service.py`](service.py): Core logic for data extraction, scraping, and report creation.
- [`graphs.py`](graphs.py): Generates graphs for inclusion in the report.
- [`res.py`](res.py): Example data.
- [`template.html`](template.html): HTML template for the report.
- [`images/`](images/): Stores generated graphs and downloaded images.
- `.env`: Stores your API key(s).

## Setup Instructions

### 1. Clone the repository

Enter the following command to clone the contents of this repository.
```sh
git clone https://github.com/opaida-kenneth/housereport.git
```

### 2. Clone FormPilot (required browser agent)

FormPilot is a seperate tool required for the automated web browsing tasks present in this application. Clone it alongside this project.

```sh
git clone (link to formpilot GitHub)
```

Follow FormPilot’s setup instructions in its own README.

### 3. Install dependencies

Idealy, you should instantiate a Python virtual environment (through Anaconda, etc.) in Python version 3.11.

```sh
cd housereport
pip install -r requirements.txt
```

### 4. Set up your API key

In a `.env` file in the `housereport` directory, list your Gemini API key.

```
LLM_API_KEY=your_google_gemini_api_key
```

In the `FormPilot` directory's .env file, update the Gemini API key there as well.


### 5. Start the FormPilot browser agent

```sh
cd FormPilot
python api_server.py
```

### 6. Start the FastAPI server

```sh
cd housereport
uvicorn app:app --reload
```


### 7. Access the API

With the both the app.py of `housereport` and the api_server.py of `FormPilot` up and running, you may now send get requests to the /report endpoint.

One may use external tools, such as Thunderclient or PostMan, to simplify the process. If you are to use one of the aforementioned applications, be sure to select Params, not Body, and in the Key and Value boxes, enter "address" and "address_of_property", respectively.

The response will contain the HTML report.


## Example Usage

```sh
curl "http://localhost:8000/report?address=67 Davinci Dr Monmouth Junction, NJ 08852"
```


## Notes

- Notice that in app.py, there are numerous `time.sleep(65)` code segments throughout. This is because many free LLM API keys, including the one I used throughout the duration of my internship, have per-minute token usage limits. Waiting 60-65 seconds ensures that the limit is not breached. If you have a more substantial LLM API key, feel free to remove these code segments.
- **FormPilot** must be running for scraping tasks to work.
- You need a valid Google Gemini API key for AI-powered features.
- The application uses Selenium and Chrome WebDriver for scraping.
- The generated HTML report can be printed or converted to PDF.