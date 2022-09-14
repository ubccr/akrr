try:
    # PyYAML yaml.load(input) Deprecation
    from yaml import full_load as yaml_load
except:
    from yaml import load as yaml_load
