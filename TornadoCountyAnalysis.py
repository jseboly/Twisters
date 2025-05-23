# This script uses GIS analysis to create an Excel spreadsheet listing tornado counts, track lengths, and track areas
# by county and state, using the latest data available from the Storm Prediction Center's database.

import os, requests

# Globals
working_folder = "C:/Dev/TornadoCountyAnalysis"  #Set the folder to save output to
tornado_file_url = "https://www.spc.noaa.gov/wcm/data/1950-2024_all_tornadoes.csv"  #URL to download the tornado CSV file from

def download_file(url, workspace):

    # Send request
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for failed requests
    except:
        raise ValueError("Invalid URL. Please check URL and try again.") from None
    
    # Save file
    filename = "tornado_data.csv"
    try:
        local_path = os.path.join(workspace, filename)
        with open(local_path, "wb") as file:
            file.write(response.content)
        print("File saved as " + local_path)
    except FileNotFoundError:
        raise ValueError("Invalid file path. Please check whether the specified working folder exists.") from None

def main():
    # download file from SPC site
    download_file(tornado_file_url, working_folder)

main()