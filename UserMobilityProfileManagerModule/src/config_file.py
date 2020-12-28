import configparser

config = configparser.ConfigParser()
config['settings'] = {
    'img_path': '/Users/dariamargheritamaggi/Documents/GitHub/User-Mobility-Profile/UserMobilityProfileManagerModule'
                '/files/photos.png'}
with open('../files/configurations.ini', 'w') as configfile:
    config.write(configfile)
