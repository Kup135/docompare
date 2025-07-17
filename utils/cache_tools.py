import os
import json

def load_or_cache(path, generator_func, *args, **kwargs):
    """
    Loads a cached file from `path` if it exists.
    If not, calls `generator_func(*args, **kwargs)`, saves the result, and returns it.
    """
    if os.path.exists(path):
        print(f"DEBUG: Using cached result from {path}")
        with open(path, "r") as f:
            return json.load(f)
    
    print(f"DEBUG: Generating new result and caching to {path}")
    result = generator_func(*args, **kwargs)
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
    return result
