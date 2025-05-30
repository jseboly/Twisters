# TWISTERS PROJECT
This project has three main parts, each demonstrating how open source GIS python libraries can be used to analyse, map, and uncover trends in U.S. tornado data.

## Data Sources
The tornado data used for this project was obtained from NOAA's Storm Prediction Center, and can be downloaded here: <https://www.spc.noaa.gov/wcm/data/1950-2024_actual_tornadoes.csv>

This link downloads a CSV file containing a row for each reported tornado along with various attributes, including the date, time, EF Scale rating, start lat and long, and end lat and long.
For the purposes of this analysis, I assumed that the track of each tornado was a straight line from its start location to its end location. I used geopandas and shapely to construct line features from the start point to the end point for each tornado.

### Caveats
There are several caveats and assumptions associated with this data set that need to be kept in mind when interpreting the results of this analysis.
* These are tornado reports and are not an exhaustive list of all tornadoes that occurred. There is a well-documented bias that tornadoes, especially weaker ones, are more likely to be reported in areas with high population density.
* Tornadoes do not travel in perfectly straight lines, and in some cases may leave the ground and touch back down one or more times between their start and end points.
* The EF Scale is a good but imperfect rating system in that it is wholly based on the damage that a tornado leaves behind, so isn't directly correlated to the strength of a tornado. For example, if a very strong tornado passes through an area with no structures/buildings, it isn't able to meet the criteria for the higher EF ratings due to not producing observable damage.
* The tornado database is less reliable the farther back in time you go. Therefore, I have chosen to only use tornadoes from the year 2000 and later.

## PART 1 - Tornadoes By County
This analysis seeks to uncover which parts of the United States are more tornado-prone by mapping the tornado frequency, intensity, and coverage on a county-by-county basis. This requires summarizing tornado data by county and calculating three data points:
* Frequency - the total number of tornadoes that occurred in the county.
* Intensity - the aggregate strength of all tornadoes that occurred in the county.
* Coverage - the total length of all tornado tracks that crossed the county.
Since the size of the county is a major factor in the number of tornadoes it is impacted by, these three variables are all normalized (divided) by the area of the county before mapping.

Here are the steps I followed to obtain these results for each county:
* Intersect the tornado tracks (lines) with the counties (polygons).
* Summarize the resulting dataset on county FIPS code (the safest way to ensure a unique value for each county), finding the counts, the sum of the EF ratings, and the sum of the lengths for each county.
* Join back to the original counties on FIPS code and add these attributes to the county dataset.
* Plot the counties on a map (three different maps symbolized by these three variables).

These three maps are visible in this repository as TornadoCountMap.pdf, TornadoMagnitudeMap.pdf, and TornadoLengthMap.pdf.
Additionally, I created an interactive map containing a separate layer for each of these variables using the Folium library. The file size with all three layers included was too large to upload to GitHub, so I have included a pared down version containing only tornado counts that is in the repository as twisters.html.

Hope you enjoy and learn something from perusing this data! Please reach out to jseboly@gmail.com with any questions or comments.
