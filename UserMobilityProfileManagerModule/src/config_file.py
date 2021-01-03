import configparser

config = configparser.ConfigParser()
config['settings'] = {
    'img_path': 'files/photos',
    'vehicle_port': '65432',
    'cloud_port': '55452',
    'cloud_url': 'localhost',
    'vehicle_url': 'localhost',
    'img_path': 'files/photos', 
    'mongo_con': 'localhost',
    'temp_path': 'files/temp',
    'sound_path': 'files/sounds',
    'mongo_con': 'localhost',
    'mtu': '1024'}
with open('../files/configurations.ini', 'w') as configfile:
    config.write(configfile)
