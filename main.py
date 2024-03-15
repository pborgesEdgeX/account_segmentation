import json
import logging

import openai
import pandas as pd
import requests
from tqdm import tqdm

# Configure logging for enterprise standards
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("classification.log"),  # Log to file
                        logging.StreamHandler()  # Log to standard output
                    ])
logger = logging.getLogger(__name__)


def load_config(config_path='config.json'):
    """
    Loads the configuration file.
    """
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {config_path}. Ensure the file exists.")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error parsing the configuration file at {config_path}. Ensure valid JSON format.")
        raise


def load_csv(file_path, skiprows):
    """
    Loads a CSV file into a pandas DataFrame, handling potential errors.
    """
    try:
        data = pd.read_csv(file_path, skiprows=skiprows)
        data.columns = ['Index', 'AccountID', 'Blank', 'Account Name', 'Account Owner',
                        'T3M $DBU Annualised (converted)', 'Account Status', 'Region Level 1', 'Region Level 2',
                        'Databricks Vertical Map', 'Industry']
        return data.drop(columns=['Index', 'Blank', 'Region Level 1']).dropna()
    except Exception as e:
        logger.error("Error loading CSV file: %s", e)
        raise


def save_csv(dataframe, file_path):
    """
    Saves a pandas DataFrame into a CSV file, handling potential errors.
    """
    try:
        dataframe.to_csv(file_path, index=False)
        logger.info("Data successfully saved to %s", file_path)
    except Exception as e:
        logger.error("Error saving DataFrame to CSV: %s", e)
        raise


def fetch_company_details(account_name, RAPIDAPI_KEY, RAPIDAPI_HOST):
    """
    Fetches company details from LinkedIn via RapidAPI.
    """
    logger.info("Fetching company details for: %s", account_name)
    url = "https://linkedin-api8.p.rapidapi.com/get-company-details"
    querystring = {"username": account_name}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()['data']
            description = data.get('description', 'No description provided.')
            logger.info("Successfully fetched data for %s", account_name)
            return data, description
        else:
            logger.error("Failed to fetch data for %s. Status code: %s", account_name, response.status_code)
            return {}, "No description provided."
    except Exception as e:
        logger.error("Exception when fetching data for %s: %s", account_name, e)
        return {}, "No description provided."


def classify_company(description, company_name, OPENAI_API_KEY, OPENAI_BASE_URL):
    """
    Classifies a company into a sub-vertical based on its description using an LLM approach via OpenAI API.
    """
    client = openai.OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a go-to-market expert, and your job is to classify the industry of a company based on its description. Just return a list of top three classifications. Keep it very concise and brief."
                },
                {
                    "role": "user",
                    "content": "Here's the description of the company:" + description
                }
            ],
            model="databricks-mixtral-8x7b-instruct",
            max_tokens=256
        )

        # Extracting the classification from the response
        response_content = chat_completion.choices[0].message.content
        # Logging the full classification response
        logger.info(f"Full classification response for {company_name}: \n%s", response_content)

        # Extracting the first classification and full response
        full_classification_response = response_content.strip()  # Removing leading/trailing whitespace if any
        first_classification = full_classification_response.split('\n')[0].split('. ')[1]

        logger.info(f"First classification for {company_name}: %s", first_classification)

        # Return both the first classification and the full response
        return first_classification, full_classification_response
    except Exception as e:
        logger.error(f"Error during API call for {company_name}: %s", e, exc_info=True)
        return "Error in classification", "Error in classification response"


def process_and_classify_accounts(dataframe, config):
    """
    Processes and classifies accounts in the DataFrame, adding descriptions and sub-vertical classifications.
    """
    RAPIDAPI_KEY = config.get('rapidapi_key')
    RAPIDAPI_HOST = config.get('rapidapi_host')
    OPENAI_API_KEY = config.get('openai_key')
    OPENAI_BASE_URL = config.get('openai_base_url')

    logger.info("Processing and classifying accounts...")
    for index, row in tqdm(dataframe.iterrows(), total=dataframe.shape[0], desc="Classifying Accounts"):
        account_name = row['Account Name']
        company_details, description = fetch_company_details(account_name, RAPIDAPI_KEY, RAPIDAPI_HOST)

        # Determine the effective description
        effective_description = description if description not in ["No description provided.", ""] else row['Industry']
        dataframe.at[index, 'Description'] = effective_description

        # Classify and retrieve both first classification and full categories
        sub_vertical, full_categories = classify_company(effective_description, account_name, OPENAI_API_KEY,
                                                         OPENAI_BASE_URL)
        dataframe.at[index, 'Sub-Vertical'] = sub_vertical
        dataframe.at[index, 'Categories'] = full_categories

    return dataframe


def main():
    file_path = '/Users/paulo.borges/PycharmProjects/account_segmentation/.venv/input/MFG Accounts - West Industry   Vertical-2024-03-14-12-04-11.xlsx - MFG Accounts - West Industry   .csv'
    enriched_file_path = '/Users/paulo.borges/PycharmProjects/account_segmentation/.venv/output/output.csv'

    try:
        config = load_config()
        data_cleaned = load_csv(file_path, skiprows=10)
        enriched_data = process_and_classify_accounts(data_cleaned, config)
        save_csv(enriched_data, enriched_file_path)
        logger.info("Classification process completed successfully.")
    except Exception as e:
        logger.error("An error occurred during the classification process: %s", e)


if __name__ == '__main__':
    main()
