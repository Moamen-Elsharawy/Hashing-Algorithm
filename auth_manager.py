import json
import os
import secrets
import hashlib
from datetime import datetime, timedelta

# Import advanced hashing libraries if needed (already verified available)
import bcrypt
import argon2

# Paths
USERS_DB = "users.json"
AUDIT_LOG_DB = "audit_log.json"

# In-memory active session store
# Structure: { session_token: { "username": username, "role": role, "login_time": datetime_iso } }
ACTIVE_SESSIONS = {}

# --- HELPER FUNCTIONS FOR STORAGE ---

def load_json(filepath, default_value):
    if not os.path.exists(filepath):
        save_json(filepath, default_value)
        return default_value
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_value

def save_json(filepath, data):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False

# --- AUDIT LOGS MANAGER ---

def log_event(event_type, username, status, details=""):
    """
    Log security and authentication events for auditing.
    """
    logs = load_json(AUDIT_LOG_DB, [])
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "username": username,
        "status": status,
        "details": details
    }
    logs.append(log_entry)
    save_json(AUDIT_LOG_DB, logs)
    return log_entry

def get_audit_logs():
    return load_json(AUDIT_LOG_DB, [])

# --- CRYPTOGRAPHIC UTILITIES ---

def hash_pbkdf2_sha256(password: str, salt: str = None, iterations: int = 100000) -> tuple[str, str]:
    """
    Hashes a password using PBKDF2-HMAC-SHA256.
    Generates a cryptographically secure 16-byte salt if not provided.
    Returns: (salt_hex, hash_hex)
    """
    if salt is None:
        # Generate 16 bytes (32 hex characters) of cryptographically secure random salt
        salt = secrets.token_hex(16)
    
    # Compute salted hash
    pwd_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    dk = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt_bytes, iterations)
    return salt, dk.hex()

def hash_bcrypt(password: str) -> str:
    """
    Hashes a password using bcrypt. The salt is embedded inside the returned hash.
    """
    pwd_bytes = password.encode('utf-8')
    # Generate bcrypt salt (rounds = 12 is a secure default)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_bcrypt(password: str, hashed_password: str) -> bool:
    """
    Verifies a password against a bcrypt hash in constant-time.
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def hash_argon2(password: str) -> str:
    """
    Hashes a password using Argon2id. The salt and parameters are embedded in the hash string.
    """
    ph = argon2.PasswordHasher()
    return ph.hash(password)

def verify_argon2(password: str, hashed_password: str) -> bool:
    """
    Verifies a password against an Argon2 hash.
    """
    ph = argon2.PasswordHasher()
    try:
        ph.verify(hashed_password, password)
        return True
    except Exception:
        return False

# --- USER REGISTRATION ---

def register_user(username, password, role, security_question, security_answer, hash_algo="pbkdf2_sha256"):
    """
    Registers a new user, ensuring the plaintext password is NEVER stored.
    Hashing methods: 'pbkdf2_sha256', 'bcrypt', 'argon2'
    """
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."
    
    users = load_json(USERS_DB, {})
    
    # Check if user already exists
    # Timing attack warning: username lookups are usually fast, but we can make this robust
    if username in users:
        return False, f"Username '{username}' is already registered."
    
    # Role validation
    if role not in ["user", "admin"]:
        role = "user"
        
    # Salting and hashing password
    salt = None
    stored_hash = None
    
    if hash_algo == "bcrypt":
        stored_hash = hash_bcrypt(password)
        salt = "embedded" # Bcrypt manages salt internally within the hash string
    elif hash_algo == "argon2":
        stored_hash = hash_argon2(password)
        salt = "embedded" # Argon2 manages salt internally
    else: # Default PBKDF2
        hash_algo = "pbkdf2_sha256"
        salt, stored_hash = hash_pbkdf2_sha256(password)
        
    # Salt and hash the security question answer as well! 
    # Having security answers in plaintext is a common vulnerability.
    sec_salt, sec_hash = hash_pbkdf2_sha256(security_answer.strip().lower())
    
    # Create user record
    users[username] = {
        "username": username,
        "hash_algo": hash_algo,
        "salt": salt,
        "password_hash": stored_hash,
        "role": role,
        "security_question": security_question,
        "security_salt": sec_salt,
        "security_hash": sec_hash,
        # Lockout tracking fields
        "failed_attempts": 0,
        "lockout_until": None,
        "created_at": datetime.now().isoformat()
    }
    
    save_json(USERS_DB, users)
    log_event("REGISTRATION", username, "SUCCESS", f"Registered role={role} using {hash_algo}")
    return True, "User registered successfully."

# --- AUTHENTICATION & LOGIN ---

def login_user(username, password):
    """
    Authenticates a user, checking for lockout policy and using timing-safe comparisons.
    Returns: (success_bool, status_message, session_token, role)
    """
    username = username.strip()
    users = load_json(USERS_DB, {})
    
    # 1. Check if user exists
    if username not in users:
        # Dummy verification to slow down timing attacks on non-existent users
        # This mitigates User Enumeration via timing response
        _ = hash_pbkdf2_sha256("dummy_password", salt="dummy_salt")
        log_event("LOGIN", username, "FAILURE", "Non-existent username")
        return False, "Invalid username or password.", None, None
        
    user = users[username]
    
    # 2. Check Lockout Status
    current_time = datetime.now()
    if user.get("lockout_until"):
        lockout_time = datetime.fromisoformat(user["lockout_until"])
        if current_time < lockout_time:
            remaining_seconds = int((lockout_time - current_time).total_seconds())
            log_event("LOGIN", username, "FAILURE", f"Attempted login while locked (remaining: {remaining_seconds}s)")
            return False, f"Account is locked. Try again in {remaining_seconds} seconds.", None, None
        else:
            # Lockout expired, reset counter (or let it reset on successful login)
            user["lockout_until"] = None
            save_json(USERS_DB, users)
            
    # 3. Verify Password using the appropriate hashing algorithm
    hash_algo = user.get("hash_algo", "pbkdf2_sha256")
    stored_hash = user.get("password_hash")
    stored_salt = user.get("salt")
    
    match = False
    if hash_algo == "bcrypt":
        match = verify_bcrypt(password, stored_hash)
    elif hash_algo == "argon2":
        match = verify_argon2(password, stored_hash)
    else: # pbkdf2_sha256
        # Generate hash with stored salt
        _, calculated_hash = hash_pbkdf2_sha256(password, stored_salt)
        # Use secrets.compare_digest for constant-time comparison
        # This prevents Timing Attacks
        match = secrets.compare_digest(calculated_hash, stored_hash)
        
    if match:
        # Successful login
        # Reset lockout and failed attempt counts
        user["failed_attempts"] = 0
        user["lockout_until"] = None
        save_json(USERS_DB, users)
        
        # Generate session token (32 secure random bytes, hex/URL safe)
        session_token = secrets.token_urlsafe(32)
        role = user.get("role", "user")
        
        # Save session in-memory
        ACTIVE_SESSIONS[session_token] = {
            "username": username,
            "role": role,
            "login_time": current_time.isoformat(),
            "expires_at": (current_time + timedelta(hours=2)).isoformat()
        }
        
        log_event("LOGIN", username, "SUCCESS", f"Session token created. Role: {role}")
        return True, "Login successful.", session_token, role
    else:
        # Failed login attempt
        failed_attempts = user.get("failed_attempts", 0) + 1
        user["failed_attempts"] = failed_attempts
        
        message = "Invalid username or password."
        
        if failed_attempts >= 3:
            # Set lockout for 30 seconds
            lockout_time = current_time + timedelta(seconds=30)
            user["lockout_until"] = lockout_time.isoformat()
            message = "Account locked for 30 seconds due to 3 consecutive failed login attempts."
            log_event("LOCKOUT", username, "TRIGGERED", "3 failed attempts. Locked for 30 seconds.")
        else:
            log_event("LOGIN", username, "FAILURE", f"Incorrect password (Attempt {failed_attempts}/3)")
            
        save_json(USERS_DB, users)
        return False, message, None, None

# --- SESSION MANAGEMENT ---

def validate_session(token):
    """
    Timing-safe token check and retrieval of active session.
    """
    if not token:
        return None
        
    current_time = datetime.now()
    
    # Iterate through session keys in a timing-safe way (if desired) or simple lookup.
    # In standard web apps, a dictionary lookup is O(1) and safe, but secrets.compare_digest
    # can be demonstrated for matching strings. Let's do standard dictionary verification,
    # but we can verify the actual token string.
    
    # Iterate keys to find match using secrets.compare_digest to prevent token timing attacks.
    target_session = None
    for active_token, details in list(ACTIVE_SESSIONS.items()):
        # Compare digests of active token and target token to protect against timing attacks
        if secrets.compare_digest(active_token, token):
            # Check expiration
            expires_at = datetime.fromisoformat(details["expires_at"])
            if current_time < expires_at:
                target_session = details
                break
            else:
                # Expired session cleanup
                ACTIVE_SESSIONS.pop(active_token, None)
                log_event("SESSION", details["username"], "EXPIRED", "Session token expired")
                
    return target_session

def logout_session(token):
    """
    Invalidates the session token on logout.
    """
    if not token:
        return False
        
    removed_username = None
    for active_token in list(ACTIVE_SESSIONS.keys()):
        if secrets.compare_digest(active_token, token):
            details = ACTIVE_SESSIONS.pop(active_token, None)
            if details:
                removed_username = details["username"]
                log_event("LOGOUT", removed_username, "SUCCESS", "User logged out successfully")
                return True
                
    return False

# --- PASSWORD RESET FLOW (SECURITY QUESTION) ---

def get_security_question(username):
    """
    Retrieves the security question for a user.
    """
    username = username.strip()
    users = load_json(USERS_DB, {})
    if username in users:
        return True, users[username].get("security_question", "No security question configured.")
    return False, "Username not found."

def verify_reset_answer_and_change_password(username, answer, new_password):
    """
    Verifies the hashed security question answer and updates the password if correct.
    Resets the failed attempts and lockouts.
    """
    username = username.strip()
    users = load_json(USERS_DB, {})
    
    if username not in users:
        log_event("RESET_PASSWORD", username, "FAILURE", "Non-existent user reset attempt")
        return False, "User not found."
        
    user = users[username]
    stored_sec_hash = user.get("security_hash")
    stored_sec_salt = user.get("security_salt")
    
    # Standardize the user's answer (case insensitive, trimmed)
    normalized_answer = answer.strip().lower()
    
    # Compute the hash of the user's input answer using the stored security salt
    _, calculated_sec_hash = hash_pbkdf2_sha256(normalized_answer, stored_sec_salt)
    
    # Timing-safe comparison of the security answer hash
    if secrets.compare_digest(calculated_sec_hash, stored_sec_hash):
        # Answer is correct! Update password
        hash_algo = user.get("hash_algo", "pbkdf2_sha256")
        
        salt = None
        stored_hash = None
        
        if hash_algo == "bcrypt":
            stored_hash = hash_bcrypt(new_password)
            salt = "embedded"
        elif hash_algo == "argon2":
            stored_hash = hash_argon2(new_password)
            salt = "embedded"
        else:
            salt, stored_hash = hash_pbkdf2_sha256(new_password)
            
        user["salt"] = salt
        user["password_hash"] = stored_hash
        user["failed_attempts"] = 0
        user["lockout_until"] = None
        
        save_json(USERS_DB, users)
        log_event("RESET_PASSWORD", username, "SUCCESS", f"Password reset successful via security question. Hashing: {hash_algo}")
        return True, "Password reset successful! You can now log in with your new password."
    else:
        # Increment failed login attempts because a failed reset attempt shows malicious intent / brute force
        failed_attempts = user.get("failed_attempts", 0) + 1
        user["failed_attempts"] = failed_attempts
        
        message = "Incorrect answer to security question."
        
        if failed_attempts >= 3:
            lockout_time = datetime.now() + timedelta(seconds=30)
            user["lockout_until"] = lockout_time.isoformat()
            message = "Incorrect answer. Account locked for 30 seconds due to repeated failed attempts."
            log_event("LOCKOUT", username, "TRIGGERED", "Reset attempt failed. Account locked.")
        else:
            log_event("RESET_PASSWORD", username, "FAILURE", f"Incorrect security question answer (Attempt {failed_attempts}/3)")
            
        save_json(USERS_DB, users)
        return False, message

# --- ADMINISTRATIVE ACTIONS (RBAC) ---

def get_all_users_admin(admin_username):
    """
    Fetches all users.
    """
    users = load_json(USERS_DB, {})
    # Return user records, keeping it transparent for the Admin dashboard demonstration,
    # but removing private elements in production. For educational visualization, we'll keep
    # the salts and hashes visible so the admin can inspect them!
    return list(users.values())

def admin_unlock_user(admin_username, target_username):
    """
    Unlocks a locked account instantly.
    """
    users = load_json(USERS_DB, {})
    if target_username in users:
        users[target_username]["failed_attempts"] = 0
        users[target_username]["lockout_until"] = None
        save_json(USERS_DB, users)
        log_event("ADMIN_ACTION", admin_username, "SUCCESS", f"Unlocked account: {target_username}")
        return True, f"Unlocked account '{target_username}'."
    return False, "User not found."

def admin_change_role(admin_username, target_username, new_role):
    """
    Changes the user's role.
    """
    if new_role not in ["user", "admin"]:
        return False, "Invalid role type."
        
    users = load_json(USERS_DB, {})
    if target_username in users:
        old_role = users[target_username].get("role", "user")
        users[target_username]["role"] = new_role
        save_json(USERS_DB, users)
        log_event("ADMIN_ACTION", admin_username, "SUCCESS", f"Changed {target_username} role from {old_role} to {new_role}")
        return True, f"Role for '{target_username}' updated to '{new_role}'."
    return False, "User not found."

def admin_delete_user(admin_username, target_username):
    """
    Deletes a user.
    """
    if admin_username == target_username:
        return False, "Admin cannot delete their own account."
        
    users = load_json(USERS_DB, {})
    if target_username in users:
        users.pop(target_username)
        save_json(USERS_DB, users)
        log_event("ADMIN_ACTION", admin_username, "SUCCESS", f"Deleted user account: {target_username}")
        return True, f"User '{target_username}' deleted."
    return False, "User not found."
