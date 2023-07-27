'''This script calculates breakdown (percentage) of land type for each home range percentile polygon
THIS APPROACH USES DIRECT API GEOMETRIC TRANSFORMATIONS AND OPERATIONS'''

from datetime import date
import calendar
import os
import csv


project = QgsProject.instance()

months_dict = dict((month, index) for index, month in enumerate(calendar.month_name) if month)

homerange_source_folder = r'C:/Users/qw2/Desktop/Paddock_Power_GPS/home_range_geopackage_files/GRASSY'

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
    

def calculate_homerange_land_type_percentage(paddock_lyr, home_range_lyr, land_type_lyr):
    homerange_land_types = {}
    
    hr_50_color = '#F8766D'
    hr_75_color = '#00BA38'
    hr_95_color = '#619CFF'
    
    clip_params = {'INPUT':home_range_lyr,
                    'OVERLAY':paddock_lyr,
                    'OUTPUT':'TEMPORARY_OUTPUT'}
    
    home_range_lyr_clipped_to_pdk = processing.run("native:clip", clip_params)['OUTPUT']
    
    pdk_land_type_names = [ft['LT_NAME'] for ft in land_type_lyr.getFeatures()]
    
    ###################################################################
    hr_50_ids = [ft.id() for ft in home_range_lyr_clipped_to_pdk.getFeatures() if ft['colour'] == hr_50_color]
    hr_50_lyr = home_range_lyr_clipped_to_pdk.materialize(QgsFeatureRequest(hr_50_ids))
    dissolve_50_params = {'INPUT':hr_50_lyr,
                        'FIELD':[],
                        'OUTPUT':'TEMPORARY_OUTPUT'}
    hr_50_lyr_dissolved = processing.run("native:dissolve", dissolve_50_params)['OUTPUT']
    hr_50_geom = [transformed_geom(ft.geometry()) for ft in hr_50_lyr_dissolved.getFeatures()][0]
    if not hr_50_geom:
        print("Danger")
    hr_50_total = hr_50_geom.area()
    hr_50_land_types = {}
    hr_50_pcnts = []
    for lt_name in pdk_land_type_names:
        lt_feats = [ft for ft in land_type_lyr.getFeatures() if ft['LT_NAME'] == lt_name]
        lt_pdk_total = sum([ft.geometry().area() for ft in lt_feats])###***********************
        lt_pdk_total_km2 = round(lt_pdk_total/1000000, 7)
        lt_geoms = [ft.geometry().intersection(hr_50_geom) for ft in lt_feats]
        lt_area = sum([g.area() for g in lt_geoms])
        lt_area_km2 = round(lt_area/1000000, 7)
        pcnt_of_lt_used = (lt_area/lt_pdk_total)*100###**************************
        lt_pcnt = (lt_area/hr_50_total)*100
        hr_50_pcnts.append(lt_pcnt)
        hr_50_land_types[lt_name] = (lt_pdk_total_km2, lt_area_km2, round(pcnt_of_lt_used, 5), round(lt_pcnt, 5))# Tuple containing area & pcnt
        hr_50_land_types['HR Check Sum'] = round(sum(hr_50_pcnts), 2)
    homerange_land_types['50%_homerange'] = hr_50_land_types
    ###################################################################
    hr_75_ids = [ft.id() for ft in home_range_lyr_clipped_to_pdk.getFeatures() if ft['colour'] == hr_75_color]
    hr_75_lyr = home_range_lyr_clipped_to_pdk.materialize(QgsFeatureRequest(hr_75_ids))
    dissolve_75_params = {'INPUT':hr_75_lyr,
                        'FIELD':[],
                        'OUTPUT':'TEMPORARY_OUTPUT'}
    hr_75_lyr_dissolved = processing.run("native:dissolve", dissolve_75_params)['OUTPUT']
    hr_75_geom = [transformed_geom(ft.geometry()) for ft in hr_75_lyr_dissolved.getFeatures()][0]
    if not hr_75_geom:
        print("Danger")
    hr_75_total = hr_75_geom.area()
    hr_75_land_types = {}
    hr_75_pcnts = []
    for lt_name in pdk_land_type_names:
        lt_feats = [ft for ft in land_type_lyr.getFeatures() if ft['LT_NAME'] == lt_name]
        lt_pdk_total = sum([ft.geometry().area() for ft in lt_feats])###***********************
        lt_pdk_total_km2 = round(lt_pdk_total/1000000, 7)
        lt_geoms = [ft.geometry().intersection(hr_75_geom) for ft in lt_feats]
        lt_area = sum([g.area() for g in lt_geoms])
        lt_area_km2 = round(lt_area/1000000, 7)
        pcnt_of_lt_used = (lt_area/lt_pdk_total)*100###**************************
        lt_pcnt = (lt_area/hr_75_total)*100
        hr_75_pcnts.append(lt_pcnt)
        hr_75_land_types[lt_name] = (lt_pdk_total_km2, lt_area_km2, round(pcnt_of_lt_used, 5), round(lt_pcnt, 5))# Tuple containing area & pcnt
        hr_75_land_types['HR Check Sum'] = round(sum(hr_75_pcnts), 2)
    homerange_land_types['75%_homerange'] = hr_75_land_types
    ###################################################################
    hr_95_ids = [ft.id() for ft in home_range_lyr_clipped_to_pdk.getFeatures() if ft['colour'] == hr_95_color]
    hr_95_lyr = home_range_lyr_clipped_to_pdk.materialize(QgsFeatureRequest(hr_95_ids))
    dissolve_95_params = {'INPUT':hr_95_lyr,
                        'FIELD':[],
                        'OUTPUT':'TEMPORARY_OUTPUT'}
    hr_95_lyr_dissolved = processing.run("native:dissolve", dissolve_95_params)['OUTPUT']
    hr_95_geom = [transformed_geom(ft.geometry()) for ft in hr_95_lyr_dissolved.getFeatures()][0]
    if not hr_95_geom:
        print("Danger")
    hr_95_total = hr_95_geom.area()
    hr_95_land_types = {}
    hr_95_pcnts = []
    for lt_name in pdk_land_type_names:
        lt_feats = [ft for ft in land_type_lyr.getFeatures() if ft['LT_NAME'] == lt_name]
        lt_pdk_total = sum([ft.geometry().area() for ft in lt_feats])###***********************
        lt_pdk_total_km2 = round(lt_pdk_total/1000000, 7)
        lt_geoms = [ft.geometry().intersection(hr_95_geom) for ft in lt_feats]
        lt_area = sum([g.area() for g in lt_geoms])
        lt_area_km2 = round(lt_area/1000000, 7)
        pcnt_of_lt_used = (lt_area/lt_pdk_total)*100###**************************
        lt_pcnt = (lt_area/hr_95_total)*100
        hr_95_pcnts.append(lt_pcnt)
        hr_95_land_types[lt_name] = (lt_pdk_total_km2, lt_area_km2, round(pcnt_of_lt_used, 5), round(lt_pcnt, 5))# Tuple containing area & pcnt
        hr_95_land_types['HR Check Sum'] = round(sum(hr_95_pcnts), 2)
    homerange_land_types['95%_homerange'] = hr_95_land_types
    '''#########################
    hr_50_ids = [ft.id() for ft in home_range_lyr.getFeatures() if ft['colour'] == hr_50_color]
    hr_50_lyr = home_range_lyr.materialize(QgsFeatureRequest(hr_50_ids))
    hr_50_geoms_9473 = [transformed_geom(ft.geometry()) for ft in hr_50_lyr.getFeatures()]
    hr_50_geom = QgsGeometry.collectGeometry(hr_50_geoms_9473)
    hr_50_land_type_feats = [ft for ft in land_type_lyr.getFeatures() if ft.geometry().intersects(hr_50_geom)]
    hr_50_land_type_geoms = [ft.geometry().intersection(hr_50_geom) for ft in hr_50_land_type_feats]
    total_area = sum([g.area() for g in hr_50_land_type_geoms])
    hr_50_land_types = {}
    hr_50_pcnts = []
    for lt_name in pdk_land_type_names:
        lt_feats = [ft for ft in land_type_lyr.getFeatures() if ft['LT_NAME'] == lt_name]
        lt_geoms = [ft.geometry().intersection(hr_50_geom) for ft in lt_feats]
        lt_area = sum([g.area() for g in lt_geoms])
        lt_pcnt = (lt_area/total_area)*100
        hr_50_pcnts.append(lt_pcnt)
        hr_50_land_types[lt_name] = round(lt_pcnt, 2)
        hr_50_land_types['Check Sum'] = round(sum(hr_50_pcnts), 2)
    homerange_land_types['50%_homerange'] = hr_50_land_types
    #########################

    hr_75_ids = [ft.id() for ft in home_range_lyr.getFeatures() if ft['colour'] == hr_75_color]
    hr_75_lyr = home_range_lyr.materialize(QgsFeatureRequest(hr_75_ids))
    hr_75_geoms_9473 = [transformed_geom(ft.geometry()) for ft in hr_75_lyr.getFeatures()]
    hr_75_geom = QgsGeometry.collectGeometry(hr_75_geoms_9473)
    hr_75_land_type_feats = [ft for ft in land_type_lyr.getFeatures() if ft.geometry().intersects(hr_75_geom)]
    hr_75_land_type_geoms = [ft.geometry().intersection(hr_75_geom) for ft in hr_75_land_type_feats]
    total_area = sum([g.area() for g in hr_75_land_type_geoms])
    hr_75_land_types = {}
    hr_75_pcnts = []
    for lt_name in pdk_land_type_names:
        lt_feats = [ft for ft in land_type_lyr.getFeatures() if ft['LT_NAME'] == lt_name]
        lt_geoms = [ft.geometry().intersection(hr_75_geom) for ft in lt_feats]
        lt_area = sum([g.area() for g in lt_geoms])
        lt_pcnt = (lt_area/total_area)*100
        hr_75_pcnts.append(lt_pcnt)
        hr_75_land_types[lt_name] = round(lt_pcnt, 2)
        hr_75_land_types['Check Sum'] = round(sum(hr_75_pcnts), 2)
    homerange_land_types['75%_homerange'] = hr_75_land_types
    #########################
    hr_95_ids = [ft.id() for ft in home_range_lyr.getFeatures() if ft['colour'] == hr_95_color]
    hr_95_lyr = home_range_lyr.materialize(QgsFeatureRequest(hr_95_ids))
    hr_95_geoms_9473 = [transformed_geom(ft.geometry()) for ft in hr_95_lyr.getFeatures()]
    hr_95_geom = QgsGeometry.collectGeometry(hr_95_geoms_9473)
    hr_95_land_type_feats = [ft for ft in land_type_lyr.getFeatures() if ft.geometry().intersects(hr_95_geom)]
    hr_95_land_type_geoms = [ft.geometry().intersection(hr_95_geom) for ft in hr_95_land_type_feats]
    total_area = sum([g.area() for g in hr_95_land_type_geoms])
    hr_95_land_types = {}
    hr_95_pcnts = []
    for lt_name in pdk_land_type_names:
        lt_feats = [ft for ft in land_type_lyr.getFeatures() if ft['LT_NAME'] == lt_name]
        lt_geoms = [ft.geometry().intersection(hr_95_geom) for ft in lt_feats]
        lt_area = sum([g.area() for g in lt_geoms])
        lt_pcnt = (lt_area/total_area)*100
        hr_95_pcnts.append(lt_pcnt)
        hr_95_land_types[lt_name] = round(lt_pcnt, 2)
        hr_95_land_types['Check Sum'] = round(sum(hr_95_pcnts), 2)
    homerange_land_types['95%_homerange'] = hr_95_land_types
    ##################################################'''
    
    return homerange_land_types

#############################################################################################################
land_type_src = r'C:/Users/qw2/Desktop/Paddock_Power_GPS/Land_Types/Dissolved_by_land_type/grassy_land_types.gpkg'
land_type_lyr = QgsVectorLayer(land_type_src, 'land_types', 'ogr')
output_csv = r'C:/Users/qw2/Desktop/Paddock_Power_GPS/home_range_geopackage_files/GRASSY/Grassy_homerange_land_types.csv'
results_tbl = open(output_csv, mode='w', newline='')
writer = csv.writer(results_tbl)
csv_headers = ['Paddock',
                'Year',
                'Month',
                'Home Range Group']
                
pdk_land_type_names = [ft['LT_NAME'] for ft in land_type_lyr.getFeatures()]

for lt in pdk_land_type_names:
    csv_headers.append(f'{lt} Pdk Total km2')
    csv_headers.append(f'{lt} km2')
    csv_headers.append(f'{lt} % Used')
    csv_headers.append(f'{lt} % of HR')

csv_headers.append('HR Check Sum')

writer.writerow(csv_headers)

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
            homerange_land_types = calculate_homerange_land_type_percentage(paddock_lyr, homerange_lyr, land_type_lyr)
            print(homerange_land_types)

            hr_50_dict = homerange_land_types['50%_homerange']
            hr_50_csv_row = [paddock, yr, mnth, '50%_homerange']
            for lt_name in pdk_land_type_names:
                hr_50_csv_row.append(hr_50_dict[lt_name][0])
                hr_50_csv_row.append(hr_50_dict[lt_name][1])
                hr_50_csv_row.append(hr_50_dict[lt_name][2])
                hr_50_csv_row.append(hr_50_dict[lt_name][3])
            hr_50_csv_row.append(hr_50_dict['HR Check Sum'])
            writer.writerow(hr_50_csv_row)
            
            hr_75_dict = homerange_land_types['75%_homerange']
            hr_75_csv_row = [paddock, yr, mnth, '75%_homerange']
            for lt_name in pdk_land_type_names:
                hr_75_csv_row.append(hr_75_dict[lt_name][0])
                hr_75_csv_row.append(hr_75_dict[lt_name][1])
                hr_75_csv_row.append(hr_75_dict[lt_name][2])
                hr_75_csv_row.append(hr_75_dict[lt_name][3])
            hr_75_csv_row.append(hr_75_dict['HR Check Sum'])
            writer.writerow(hr_75_csv_row)
            
            hr_95_dict = homerange_land_types['95%_homerange']
            hr_95_csv_row = [paddock, yr, mnth, '95%_homerange']
            for lt_name in pdk_land_type_names:
                hr_95_csv_row.append(hr_95_dict[lt_name][0])
                hr_95_csv_row.append(hr_95_dict[lt_name][1])
                hr_95_csv_row.append(hr_95_dict[lt_name][2])
                hr_95_csv_row.append(hr_95_dict[lt_name][3])
            hr_95_csv_row.append(hr_95_dict['HR Check Sum'])
            writer.writerow(hr_95_csv_row)


results_tbl.close()
print('Done')