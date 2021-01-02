import configparser

config = configparser.ConfigParser()
config['settings'] = {
    'img_path': 'files/photos',
    'mongo_con': 'localhost',
    'img_path': 'files/photos', 
    'vehicle_url': 'localhost',
    'cloud_url': 'localhost',
    'vehicle_port': '65432',
    'cloud_port': '55452',
    'mtu': '1024'}
with open('../files/configurations.ini', 'w') as configfile:
    config.write(configfile)
