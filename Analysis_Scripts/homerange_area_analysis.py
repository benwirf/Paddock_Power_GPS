'''This script calculates area as a percentage of total paddock area for each home range percentile polygon
THIS APPROACH USES DIRECT API GEOMETRIC TRANSFORMATIONS AND OPERATIONS'''

from datetime import date
import calendar
import os
import csv


project = QgsProject.instance()

months_dict = dict((month, index) for index, month in enumerate(calendar.month_name) if month)

homerange_source_folder = r'C:/Users/qw2/Desktop/Paddock_Power_GPS/home_range_geopackage_files/BIG_MUDGEE'

period_1_months = ['June', 'July', 'August', 'September', 'October', 'November', 'December']
period_2_months = ['January', 'February', 'March', 'April', 'May']

def get_file_date(file_name):
    '''
    Returns the correct date (year & month) associated with each homerange geopackage
    To allow for processing in the logical order by date.
    '''
    month = file_name.split('.')[0].split('_')[1]
    if month in period_1_months:
        actual_year = str(int(folder_year) - 1)
    elif month in period_2_months:
        actual_year = folder_year
    mnth_digit = months_dict[month]
    yr_and_mnth = f'{actual_year}{str(mnth_digit).zfill(2)}'
    dt = date(int(actual_year), mnth_digit, 1)
    return dt
    

def transformed_geom(g):
    new_geom = QgsGeometry.fromWkt(g.asWkt())
    src_crs = QgsCoordinateReferenceSystem('EPSG:4326')
    dest_crs = QgsCoordinateReferenceSystem('EPSG:9473')
    x_form = QgsCoordinateTransform(src_crs, dest_crs, project)
    new_geom.transform(x_form)
    return new_geom
    

def calculate_homerange_area_percentage(paddock_lyr, home_range_lyr):
    homerange_areas = {}
    
    pdk_feat = next(paddock_lyr.getFeatures())
    pdk_geom_9473 = transformed_geom(pdk_feat.geometry())
    total_pdk_area = pdk_geom_9473.area()# m2
    
    hr_50_color = '#F8766D'
    hr_75_color = '#00BA38'
    hr_95_color = '#619CFF'
        
    hr_50_ids = [ft.id() for ft in home_range_lyr.getFeatures() if ft['colour'] == hr_50_color]
    hr_50_lyr = home_range_lyr.materialize(QgsFeatureRequest(hr_50_ids))
    hr_50_geoms_9473 = [transformed_geom(ft.geometry()) for ft in hr_50_lyr.getFeatures()]
    hr_50_geoms_clipped_to_pdk = [g.intersection(pdk_geom_9473) for g in hr_50_geoms_9473]
    hr_50_pdk_area = sum([g.area() for g in hr_50_geoms_clipped_to_pdk])# m2
    hr_50_pcnt_of_pdk = (hr_50_pdk_area/total_pdk_area)*100
    homerange_areas['50%_homerange']=round(hr_50_pcnt_of_pdk, 2)
    ################
    
    hr_75_ids = [ft.id() for ft in home_range_lyr.getFeatures() if ft['colour'] == hr_75_color]
    hr_75_lyr = home_range_lyr.materialize(QgsFeatureRequest(hr_75_ids))
    hr_75_geoms_9473 = [transformed_geom(ft.geometry()) for ft in hr_75_lyr.getFeatures()]
    hr_75_geoms_clipped_to_pdk = [g.intersection(pdk_geom_9473) for g in hr_75_geoms_9473]
    hr_75_pdk_area = sum([g.area() for g in hr_75_geoms_clipped_to_pdk])# m2
    hr_75_pcnt_of_pdk = (hr_75_pdk_area/total_pdk_area)*100
    homerange_areas['75%_homerange']=round(hr_75_pcnt_of_pdk, 2)
    #########################
    
    hr_95_ids = [ft.id() for ft in home_range_lyr.getFeatures() if ft['colour'] == hr_95_color]
    hr_95_lyr = home_range_lyr.materialize(QgsFeatureRequest(hr_95_ids))
    hr_95_geoms_9473 = [transformed_geom(ft.geometry()) for ft in hr_95_lyr.getFeatures()]
    hr_95_geoms_clipped_to_pdk = [g.intersection(pdk_geom_9473) for g in hr_95_geoms_9473]
    hr_95_pdk_area = sum([g.area() for g in hr_95_geoms_clipped_to_pdk])# m2
    hr_95_pcnt_of_pdk = (hr_95_pdk_area/total_pdk_area)*100
    homerange_areas['95%_homerange']=round(hr_95_pcnt_of_pdk, 2)
    
    return homerange_areas

#############################################################################################################

output_csv = r'C:/Users/qw2/Desktop/Paddock_Power_GPS/home_range_geopackage_files/BIG_MUDGEE/Big_Mudgee_homerange_areas.csv'
results_tbl = open(output_csv, mode='w', newline='')
writer = csv.writer(results_tbl)
writer.writerow(['Paddock',
                'Year',
                'Month',
                '50 Homerange % of pdk',
                '75 Homerange % of pdk',
                '95 Homerange % of pdk'])

for file in os.scandir(homerange_source_folder):
    # Folder names end in '_gpkg'
    if file.name.split('_')[1] == 'gpkg':
        paddock = file.name.split('_')[0][:-4]
        folder_year = file.name.split('_')[0][-4:]
        subfolder = os.path.join(homerange_source_folder, file.name)
        file_dict = {}
        for file in os.scandir(subfolder):
            # These are actual geopackages
            if file.name.split('.')[1] == 'gpkg':
                f_name = file.name
                dt = get_file_date(f_name)
                file_dict[f_name]=dt
        sorted_gpkgs = sorted(file_dict.items(), key=lambda x:x[1])
        for i in sorted_gpkgs:
            # i is a tuple containing gpkg file name & its associated datetime
            file_name = i[0]
            paddock_and_month = file_name.split('.')[0]
            file_date = str(i[1])
            yr = file_date.split('-')[0]
            mnth = file_date.split('-')[1]
            yr_and_month = f'{yr}{mnth}'
            homerange_path = os.path.join(subfolder, file_name)
            homerange_lyr = QgsVectorLayer(f'{homerange_path}|layername=homerange', f'{paddock_and_month}_{yr}', 'ogr')
            paddock_lyr = QgsVectorLayer(f'{homerange_path}|layername=paddock', f'{paddock_and_month}_{yr}', 'ogr')
            homerange_areas = calculate_homerange_area_percentage(paddock_lyr, homerange_lyr)
            writer.writerow([paddock,
                            yr,
                            mnth,
                            homerange_areas['50%_homerange'],
                            homerange_areas['75%_homerange'],
                            homerange_areas['95%_homerange']])


results_tbl.close()
print('Done')