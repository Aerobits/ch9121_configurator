import yaml

# workaround to enforce ordering of the .yaml file
def create_temporary_dict(full_config, name: str):
    partial_config = dict()
    partial_config[name] = full_config[name]

    return partial_config

def config_save(config, filename):
    with open(filename, 'w') as file:
        yaml.dump(create_temporary_dict(config, 'HW config'), file)
        yaml.dump(create_temporary_dict(config, 'Default port config'), file)
        yaml.dump(create_temporary_dict(config, 'Auxiliary port config'), file)

def config_load(filename):

    with open(filename, 'r') as f:
        config = yaml.load(f, yaml.loader.FullLoader)

    return config


