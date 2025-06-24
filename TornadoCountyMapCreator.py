# This script uses GIS analysis to create a map showing all tornadoes affecting a given county since 2000,
# using the latest data available from the Storm Prediction Center's database.

import os, requests, pandas, geopandas, zipfile, contextily # type: ignore
from shapely.geometry import Point, LineString
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patheffects as pe
from adjustText import adjust_text # type: ignore

# Globals
working_folder = "C:\Dev\TornadoCountyMap"  #Set the folder to save output to
PROJECT_SR = "esri:102100"  #Web Mercator for working with OSM/basemaps
tornado_file_url = "https://www.spc.noaa.gov/wcm/data/1950-2024_actual_tornadoes.csv"  #URL to download the tornado CSV file from
county_file_url = "https://www.weather.gov/source/gis/Shapefiles/County/c_18mr25.zip"  #URL to download the county shapefile from

 # Specify the county for which analysis will be performed here
CHOSEN_STATE_NAME = 'TN' 
CHOSEN_COUNTY_NAME = 'Shelby'

# This function downloads a file from a specified URL to a specified folder with a specified file name.
def download_file_from_url(url, workspace, filename):

    # Send request
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for failed requests
    except:
        raise ValueError("Invalid URL. Please check URL and try again.") from None
    
    # Save file    
    try:
        local_path = os.path.join(workspace, filename)
        with open(local_path, "wb") as file:
            file.write(response.content)
        print("File saved as " + local_path)
    except FileNotFoundError:
        raise ValueError("Invalid file path. Please check whether the specified working folder exists.") from None

    return local_path

# This function takes a CSV with latitude and longitude columns and converts it to a geopandas geodataframe
def get_lines_from_csv(tornado_file_path, keep_columns, start_x_field, start_y_field, end_x_field, end_y_field, sr_wkid):
    df = pandas.read_csv(tornado_file_path)
    df = df[(df['yr'] > 1999) & (df['elat'] != 0) & (df['elon'] != 0)] # filter to tornadoes since 2000 that have an end lat and long listed
    needed_fields = {start_x_field, start_y_field, end_x_field, end_y_field} | set(keep_columns)
    if needed_fields.issubset(df.columns):
        df['start_point'] = [Point(xy) for xy in zip(df[start_x_field], df[start_y_field])]
        df['end_point'] = [Point(xy) for xy in zip(df[end_x_field], df[end_y_field])]
        df['geometry'] = df.apply(lambda row: LineString([row['start_point'], row['end_point']]), axis='columns')
        keep_columns.append('geometry')
        gdf = geopandas.GeoDataFrame(df[keep_columns], geometry='geometry')
        gdf.set_crs(epsg=sr_wkid, inplace=True)
    else:
        raise ValueError("One or more of the expected latitude/longitude columns were missing from the .csv. Please check the column names.")
    return gdf

# This function takes a ZIP file containing all the shapefile components and unzips it to the same folder as the ZIP folder. 
def zip_to_shp(in_zip):
    out_folder = os.path.dirname(in_zip)
    with zipfile.ZipFile(in_zip, 'r') as zip_ref:
        file_name_list = zip_ref.namelist()
        zip_ref.extractall(out_folder)
    shp_found = False
    for file_name in file_name_list:       
        if ".shp" in file_name:
            out_path = file_name
            shp_found = True
    if not shp_found:
        raise TypeError("No shapefile was found in the zipped file " + in_zip)
    print("Shapefile extracted to " + out_path)
    os.remove(in_zip)
    return out_path

def create_static_map(tornadoes, county, map_title, out_file_name):
    out_path = os.path.join(working_folder, out_file_name)
    fig, ax = plt.subplots()
    county.plot(ax=ax, color='none', edgecolor='black')
    tornadoes.plot(ax=ax, edgecolor='black')   
    texts = []
    for idx, row in tornadoes.iterrows():
        x, y = row.geometry.centroid.xy
        tornado_label_string = str(row["mo"]) + "/" + str(row['dy']) + "/" + str(row["yr"]) + '\nRating:' + str(row['mag'])
        try:
            text = ax.annotate(tornado_label_string, xy=(x[0], y[0]), xytext=(x[0] - 20000, y[0] + 3000),
                arrowprops=dict(arrowstyle="->", color="gray"), fontsize=10, color="red")
            text.set_path_effects([pe.Stroke(linewidth=3, foreground="white"), pe.Normal()])
            texts.append(text)
        except:
            print("Unable to create label for this row.")
    adjust_text(texts)
    plt.axis('off')
    plt.title(map_title)
    contextily.add_basemap(ax, source=contextily.providers.CartoDB.Voyager)

    plt.show();
    #pdf.savefig(fig)
    #plt.close(fig)
    return out_path

def main():
    # download file from SPC site
    #csv_file_name = "tornado_data.csv"
    #tornado_file_path = download_file_from_url(tornado_file_url, working_folder, csv_file_name)
    tornado_file_path = 'C:\\Dev\\TornadoCountyMap\\tornado_data.csv'

    # convert csv file into geodataframe
    START_X_FIELD = "slon"
    START_Y_FIELD = "slat"
    END_X_FIELD = "elon"
    END_Y_FIELD = "elat"
    TORNADO_KEEP_COLUMNS = ['yr','mo','dy','time','slon','slat','elon','elat','mag','wid']
    TORNADO_CSV_SR = 4269
    tornado_lines = get_lines_from_csv(
        tornado_file_path, TORNADO_KEEP_COLUMNS, START_X_FIELD, START_Y_FIELD, END_X_FIELD, END_Y_FIELD, TORNADO_CSV_SR
        )
    tornado_lines = tornado_lines.to_crs(PROJECT_SR)

    # download counties shapefile
    #county_file_name = "counties.zip"
    #county_zip_path = download_file_from_url(county_file_url, working_folder, county_file_name)
    #county_shp_path = zip_to_shp(county_zip_path)
    county_shp_path = 'C:\\Dev\\TornadoCountyMap\\c_18mr25.shp'
    county_polygons = geopandas.read_file(county_shp_path)
    COUNTY_KEEP_COLUMNS = ['STATE', 'COUNTYNAME', 'FIPS', 'geometry']
    county_polygons = county_polygons[COUNTY_KEEP_COLUMNS]
    county_polygons = county_polygons[(county_polygons['STATE'] == CHOSEN_STATE_NAME) & (county_polygons['COUNTYNAME'] == CHOSEN_COUNTY_NAME)]
    county_polygons = county_polygons.to_crs(PROJECT_SR)  #reproject to working spatial reference

    # clip tornadoes to the county
    clipped_tornadoes = tornado_lines.overlay(county_polygons, how='intersection')

    # create static map
    tornado_count_map_path = create_static_map(
        clipped_tornadoes,
        county_polygons,
        map_title = 'Tornadoes in ' + CHOSEN_COUNTY_NAME + " County, " + CHOSEN_STATE_NAME + ", 2000-present",
        out_file_name = 'TornadoCountMap.pdf'
        )

main()
