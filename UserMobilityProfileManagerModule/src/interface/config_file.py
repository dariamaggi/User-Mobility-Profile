import configparser
config = configparser.ConfigParser()
config['settings']={'img_path':'/Users/dariamargheritamaggi/Documents/GitHub/User-Mobility-Profile/UserMobilityProfileManagerModule/files/photo.png'}
with open('configurations.ini', 'w') as configfile:
    config.write(configfile)
