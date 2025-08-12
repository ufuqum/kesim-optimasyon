import json
import os
from typing import Optional, Dict, Any

USER_DATA_FILE = "users.json"

def load_users() -> Dict[str, Any]:
    if not os.path.exists(USER_DATA_FILE):
        return {}
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users: Dict[str, Any]) -> None:
    try:
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"User save error: {e}")

def add_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return False
    users[username] = {"password": password, "projects": []}
    save_users(users)
    return True

def validate_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users and users[username]["password"] == password:
        return True
    return False

def add_project_for_user(username: str, project_data: dict) -> None:
    users = load_users()
    if username in users:
        users[username]["projects"].append(project_data)
        save_users(users)

# Daha gelişmiş yetkilendirme, oturum yönetimi eklenebilir.
