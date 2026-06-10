

def update_with_global_config(module_config):
    """Updates the module config with global config values. Prints a warning if keys are overwritten."""
    global_config = config["global"]
    overwritten_keys = set(module_config.keys()) & set(global_config.keys())
    if overwritten_keys:
        print(f"Warning: The following keys in the module config will be overwritten by global config: {overwritten_keys}")
    module_config.update(global_config)
    return module_config
