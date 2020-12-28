import configparser

config = configparser.ConfigParser()
config['settings'] = {
    'img_path': 'files/photos'}
with open('../files/configurations.ini', 'w') as configfile:
    config.write(configfile)
