# Company Classification Tool

This tool automates the process of classifying companies into sub-verticals based on their descriptions using a combination of RapidAPI for fetching company details and the OpenAI API for classification. It processes a list of companies from a CSV file, enriches them with descriptions fetched from LinkedIn (via RapidAPI), and classifies each into a sub-vertical category using OpenAI's language model.

## Features

- Fetch company descriptions from LinkedIn via RapidAPI.
- Classify companies into sub-verticals using OpenAI's language model.
- Load and save company data from/to CSV files.
- Configurable through a JSON file for API keys and other settings.
- Enterprise-standard logging for monitoring and debugging.

## Setup

### Prerequisites

- Python 3.6+
- `pandas`, `requests`, `tqdm`, and `openai` libraries.
- RapidAPI and OpenAI API keys.

### Installation

1. Clone the repository or download the script to your local machine.
2. Install required Python packages:

   ```bash
   pip install pandas requests tqdm openai
   ```

3. Create a `config.json` file in the script's directory with your API keys and other configurations:

   ```json
   {
     "rapidapi_key": "<your_rapidapi_key_here>",
     "rapidapi_host": "linkedin-api8.p.rapidapi.com",
     "openai_key": "<your_openai_api_key_here>",
     "openai_base_url": "https://api.openai.com"
   }
   ```

4. Ensure the CSV file with company data is prepared and accessible to the script.

## Usage

Run the script from the command line:

```bash
python <script_name>.py
```

Replace `<script_name>` with the actual name of the script.

The script will:

- Load company data from the specified CSV file.
- Fetch descriptions for each company using LinkedIn's details via RapidAPI.
- Classify each company into a sub-vertical based on its description using OpenAI.
- Save the enriched and classified company data to a new CSV file.

## Logging

The tool logs its operations to both the console and a file named `classification.log`, located in the script's directory. The log includes information on the script's progress, any errors encountered, and the classification results for each company.

## Troubleshooting

If you encounter any issues, review the `classification.log` file for detailed error messages and troubleshooting information. Common issues may include rate limits from the APIs or misconfigurations in `config.json`.
