from pathlib import Path
import os

src_folder = 'Paddock_Power_GPS\\Brunette_Downs\\BDT_GPS'

for file in os.scandir(src_folder):
#    print(file.name)
    stem = Path(file).stem
#    print(stem)
    out_path = f'Paddock_Power_GPS\\Brunette_Downs\\Brunette_GPS\\{stem}.gpkg'
    
    save_params = {'INPUT':f'delimitedtext://file:///Paddock_Power_GPS/Brunette_Downs/BDT_GPS/{file.name}?type=csv&maxFields=10000&detectTypes=yes&xField=Longitude&yField=Latitude&crs=EPSG:4326&spatialIndex=no&subsetIndex=no&watchFile=no',
                    'OUTPUT':out_path,
                    'LAYER_NAME':'',
                    'DATASOURCE_OPTIONS':'',
                    'LAYER_OPTIONS':''}
    processing.run("native:savefeatures", save_params)
    
    iface.addVectorLayer(out_path, stem, 'ogr')
print('Done!')
