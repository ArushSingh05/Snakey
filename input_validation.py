"""
Input validation and error handling utilities.
Ensures robustness against invalid player data, corrupted saves, and edge cases.
"""

import json
import os


def validate_profile_data(data):
    """
    Validate profile data structure and types.
    Corrects invalid values to safe defaults.
    
    Args:
        data (dict): Profile data to validate
        
    Returns:
        dict: Validated and corrected profile data
    """
    if not isinstance(data, dict):
        print("ERROR: Profile data is not a dictionary")
        return get_default_profile()
    
    # Validate numeric fields
    numeric_fields = {
        "high_score": 0,
        "food_consumed": 0,
        "games_played": 0,
        "deaths": 0,
        "xp": 0,
        "level": 1,
        "pvp_wins": 0
    }
    
    for field, default in numeric_fields.items():
        value = data.get(field, default)
        if not isinstance(value, (int, float)) or value < 0:
            print(f"WARNING: Invalid value for {field}: {value}. Using default: {default}")
            data[field] = default
        else:
            # Ensure reasonable bounds
            data[field] = int(value)
    
    # Validate string fields
    string_fields = {"player_name": "Player"}
    for field, default in string_fields.items():
        value = data.get(field, default)
        if not isinstance(value, str) or len(value) > 50:
            print(f"WARNING: Invalid value for {field}: {value}. Using default: {default}")
            data[field] = default
    
    # Validate settings
    if "settings" not in data or not isinstance(data["settings"], dict):
        data["settings"] = {}
    
    settings = data["settings"]
    settings_constraints = {
        "turn_sensitivity": (0.02, 0.18, 0.08),
        "acceleration_rate": (0.02, 0.18, 0.08)
    }
    
    for setting, (min_val, max_val, default) in settings_constraints.items():
        value = settings.get(setting, default)
        if not isinstance(value, (int, float)):
            print(f"WARNING: Invalid setting {setting}: {value}. Using default: {default}")
            settings[setting] = default
        elif not (min_val <= value <= max_val):
            print(f"WARNING: Setting {setting}={value} out of range [{min_val}, {max_val}]. Clamping.")
            settings[setting] = max(min_val, min(value, max_val))
    
    # Validate customization
    if "customization" not in data or not isinstance(data["customization"], dict):
        data["customization"] = {}
    
    customization = data["customization"]
    if not isinstance(customization.get("skin_index", 0), int) or customization["skin_index"] < 0:
        customization["skin_index"] = 0
    if not isinstance(customization.get("arena_index", 0), int) or customization["arena_index"] < 0:
        customization["arena_index"] = 0
    
    # Validate achievements
    if "achievements" not in data or not isinstance(data["achievements"], dict):
        data["achievements"] = {}
    
    return data


def validate_json_file(filepath):
    """
    Validate JSON file can be parsed without corruption.
    
    Args:
        filepath (str): Path to JSON file
        
    Returns:
        dict or None: Parsed JSON if valid, None otherwise
    """
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print(f"ERROR: JSON file {filepath} does not contain a dictionary")
            return None
        return data
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON corruption in {filepath}: {e}")
        return None
    except IOError as e:
        print(f"ERROR: Cannot read file {filepath}: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error reading {filepath}: {e}")
        return None


def get_default_profile():
    """
    Get default profile structure with all required fields.
    
    Returns:
        dict: Default profile data
    """
    return {
        "player_name": "Player",
        "high_score": 0,
        "food_consumed": 0,
        "games_played": 0,
        "deaths": 0,
        "xp": 0,
        "level": 1,
        "pvp_wins": 0,
        "settings": {
            "turn_sensitivity": 0.08,
            "acceleration_rate": 0.08
        },
        "customization": {
            "skin_index": 0,
            "arena_index": 0
        },
        "achievements": {}
    }


def clamp_value(value, min_val, max_val, default=None):
    """
    Clamp a numeric value between min and max.
    Returns default if value is invalid type.
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        default: Default if invalid
        
    Returns:
        float or int: Clamped value or default
    """
    if default is None:
        default = min_val
    
    if not isinstance(value, (int, float)):
        return default
    
    return max(min_val, min(value, max_val))
