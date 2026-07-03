"""
Achievements system for tracking player milestones
Includes achievement definitions, unlock conditions, and XP rewards.
"""

# Achievement definitions with unlock conditions and XP rewards
ACHIEVEMENTS = {
    "first_bite": {
        "name": "First Bite",
        "description": "Eat your first food",
        "icon": "S",
        "xp_reward": 10,
        "condition": "food_consumed >= 1"
    },
    "food_collector": {
        "name": "Food Collector",
        "description": "Eat 50 pieces of food",
        "icon": "F",
        "xp_reward": 50,
        "condition": "food_consumed >= 50"
    },
    "food_hoarder": {
        "name": "Food Hoarder",
        "description": "Eat 200 pieces of food",
        "icon": "T",
        "xp_reward": 150,
        "condition": "food_consumed >= 200"
    },
    "score_novice": {
        "name": "Score Novice",
        "description": "Achieve a score of 10",
        "icon": "*",
        "xp_reward": 25,
        "condition": "high_score >= 10"
    },
    "score_adept": {
        "name": "Score Adept",
        "description": "Achieve a score of 50",
        "icon": "**",
        "xp_reward": 100,
        "condition": "high_score >= 50"
    },
    "score_master": {
        "name": "Score Master",
        "description": "Achieve a score of 100",
        "icon": "C",
        "xp_reward": 250,
        "condition": "high_score >= 100"
    },
    "survivor": {
        "name": "Survivor",
        "description": "Complete 10 games",
        "icon": "M",
        "xp_reward": 50,
        "condition": "games_played >= 10"
    },
    "persistence": {
        "name": "Persistence",
        "description": "Complete 50 games",
        "icon": "!",
        "xp_reward": 150,
        "condition": "games_played >= 50"
    },
    "pvp_victor": {
        "name": "PvP Victor",
        "description": "Win a PvP match",
        "icon": "V",
        "xp_reward": 75,
        "condition": "pvp_wins >= 1"
    },
    "pvp_champion": {
        "name": "PvP Champion",
        "description": "Win 10 PvP matches",
        "icon": "G",
        "xp_reward": 200,
        "condition": "pvp_wins >= 10"
    }
}


def check_achievement_unlock(profile_data, achievement_key):
    """
    Check if an achievement should be unlocked based on profile stats.
    Validates input and handles missing data gracefully.
    
    Args:
        profile_data (dict): Player profile containing stats
        achievement_key (str): Achievement identifier
        
    Returns:
        bool: True if achievement conditions are met, False otherwise
    """
    if not isinstance(profile_data, dict):
        return False
    if achievement_key not in ACHIEVEMENTS:
        return False
    
    achievement = ACHIEVEMENTS[achievement_key]
    condition = achievement["condition"]
    
    try:
        # Parse condition string in format "stat >= value"
        if ">="in condition:
            stat_name, threshold_str = condition.split(">=")
            stat_name = stat_name.strip()
            threshold = int(threshold_str.strip())
            stat_value = profile_data.get(stat_name, 0)
            
            # Validate stat value is numeric
            if not isinstance(stat_value, (int, float)):
                return False
            return stat_value >= threshold
    except (ValueError, AttributeError, TypeError):
        return False
    
    return False


def update_achievements(profile_data):
    """
    Check all achievements and update profile with new unlocks and XP.
    Initializes missing fields with safe defaults.
    
    Args:
        profile_data (dict): Player profile data
        
    Returns:
        dict: Updated achievements data
    """
    if not isinstance(profile_data, dict):
        return {}
    
    if "achievements" not in profile_data:
        profile_data["achievements"] = {}
    if "xp" not in profile_data:
        profile_data["xp"] = 0
    if "level" not in profile_data:
        profile_data["level"] = 1
    
    achievements = profile_data["achievements"]
    xp_gained = 0
    
    # Check each achievement for unlock
    for achievement_key, achievement_data in ACHIEVEMENTS.items():
        if achievement_key not in achievements:
            if check_achievement_unlock(profile_data, achievement_key):
                achievements[achievement_key] = {
                    "unlocked": True,
                    "xp_reward": achievement_data["xp_reward"]
                }
                xp_gained += achievement_data["xp_reward"]
    
    # Update XP and level
    if xp_gained > 0:
        profile_data["xp"] = profile_data.get("xp", 0) + xp_gained
        # Level up every 500 XP
        profile_data["level"] = (profile_data.get("xp", 0) // 500) + 1
    
    profile_data["achievements"] = achievements
    return achievements


def get_unlocked_achievements(profile_data):
    """
    Get list of all unlocked achievements.
    
    Args:
        profile_data (dict): Player profile
        
    Returns:
        list: List of unlocked achievement keys
    """
    if not isinstance(profile_data, dict):
        return []
    achievements = profile_data.get("achievements", {})
    return [key for key, data in achievements.items() if data.get("unlocked", False)]