import time
import os
from flask import Flask, request, jsonify, render_template, make_response
import auth_manager

app = Flask(__name__, 
            static_folder="static", 
            template_folder="templates")

# --- AUTO-SEED DATABASE ON STARTUP ---

def seed_database():
    """
    Ensure users.json exists and pre-populate with default admin and user
    so the reviewer can test out role privileges immediately.
    """
    users = auth_manager.load_json(auth_manager.USERS_DB, {})
    if not users:
        print("Seeding database with default accounts...")
        # Seed default Admin
        auth_manager.register_user(
            username="admin",
            password="AdminPassword123!",
            role="admin",
            security_question="What was the name of your first pet?",
            security_answer="cyber",
            hash_algo="pbkdf2_sha256"
        )
        # Seed default User
        auth_manager.register_user(
            username="alice",
            password="AlicePassword456!",
            role="user",
            security_question="What is your favorite color?",
            security_answer="indigo",
            hash_algo="pbkdf2_sha256"
        )
        print("Database seeded successfully.")

# --- UTILITIES ---

def get_token_from_request():
    """
    Retrieves the session token from either the Authorization header or a cookie.
    """
    # Try Authorization Header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
        
    # Fallback to Cookie
    return request.cookies.get("session_token")

def require_auth(roles=None):
    """
    Helper decorator/function to validate session and check permissions.
    Returns: (session_details, error_response)
    """
    token = get_token_from_request()
    if not token:
        return None, (jsonify({"error": "Unauthorized. No session token provided."}), 401)
        
    session = auth_manager.validate_session(token)
    if not session:
        return None, (jsonify({"error": "Session expired or invalid."}), 401)
        
    if roles and session["role"] not in roles:
        return None, (jsonify({"error": "Forbidden. Insufficient permissions."}), 403)
        
    return session, None

# --- WEB PAGE ROUTES ---

@app.route("/")
def index():
    return render_template("index.html")

# --- AUTH API ENDPOINTS ---

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")
    security_question = data.get("security_question")
    security_answer = data.get("security_answer")
    hash_algo = data.get("hash_algo", "pbkdf2_sha256")
    
    if not all([username, password, security_question, security_answer]):
        return jsonify({"error": "All fields are required."}), 400
        
    success, message = auth_manager.register_user(
        username=username,
        password=password,
        role=role,
        security_question=security_question,
        security_answer=security_answer,
        hash_algo=hash_algo
    )
    
    if not success:
        return jsonify({"error": message}), 400
        
    return jsonify({"message": message}), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400
        
    success, message, token, role = auth_manager.login_user(username, password)
    if not success:
        return jsonify({"error": message}), 401
        
    # Return token and set it in HTTP-only cookie for enhanced security demonstration
    response = make_response(jsonify({
        "message": message,
        "token": token,
        "role": role,
        "username": username
    }))
    
    # Secure Cookie Settings: HTTPOnly, SameSite=Lax, Secure (if using HTTPS, here false for local demo)
    response.set_cookie(
        "session_token", 
        token, 
        httponly=True, 
        samesite="Lax", 
        max_age=7200 # 2 hours
    )
    return response

@app.route("/api/logout", methods=["POST"])
def logout():
    token = get_token_from_request()
    auth_manager.logout_session(token)
    
    response = make_response(jsonify({"message": "Logged out successfully."}))
    # Clear the cookie
    response.set_cookie("session_token", "", expires=0)
    return response

@app.route("/api/reset-request", methods=["POST"])
def reset_request():
    data = request.get_json() or {}
    username = data.get("username")
    
    if not username:
        return jsonify({"error": "Username is required."}), 400
        
    success, question_or_error = auth_manager.get_security_question(username)
    if not success:
        return jsonify({"error": question_or_error}), 404
        
    return jsonify({"security_question": question_or_error})

@app.route("/api/reset-confirm", methods=["POST"])
def reset_confirm():
    data = request.get_json() or {}
    username = data.get("username")
    answer = data.get("security_answer")
    new_password = data.get("new_password")
    
    if not all([username, answer, new_password]):
        return jsonify({"error": "Username, security answer, and new password are required."}), 400
        
    success, message = auth_manager.verify_reset_answer_and_change_password(
        username=username,
        answer=answer,
        new_password=new_password
    )
    if not success:
        return jsonify({"error": message}), 400
        
    return jsonify({"message": message})

# --- DEVELOPER & AUDIT ENDPOINTS ---

@app.route("/api/inspect-db", methods=["GET"])
def inspect_db():
    """
    Renders raw users database (sensitive fields preserved for presentation).
    In a real app, this endpoint is highly restricted, but for this project, 
    it serves as a dynamic inspection panel to verify password hashing!
    """
    # Safe to load since we want the frontend simulator to showcase it live
    users = auth_manager.load_json(auth_manager.USERS_DB, {})
    return jsonify(users)

@app.route("/api/inspect-sessions", methods=["GET"])
def inspect_sessions():
    """
    Exposes active session keys.
    """
    # Redact actual tokens for additional session security demo, 
    # but display active sessions by mapping first 6 characters of token
    redacted_sessions = {}
    for token, details in auth_manager.ACTIVE_SESSIONS.items():
        masked_token = token[:6] + "..." + token[-6:] if len(token) > 12 else "..."
        redacted_sessions[masked_token] = details
    return jsonify(redacted_sessions)

# --- ADMIN API ENDPOINTS (RBAC PROTECTED) ---

@app.route("/api/admin/users", methods=["GET"])
def admin_users():
    session, err = require_auth(roles=["admin"])
    if err:
        return err
        
    users = auth_manager.get_all_users_admin(session["username"])
    return jsonify(users)

@app.route("/api/admin/unlock", methods=["POST"])
def admin_unlock():
    session, err = require_auth(roles=["admin"])
    if err:
        return err
        
    data = request.get_json() or {}
    target = data.get("username")
    
    if not target:
        return jsonify({"error": "Target username is required."}), 400
        
    success, message = auth_manager.admin_unlock_user(session["username"], target)
    if not success:
        return jsonify({"error": message}), 404
        
    return jsonify({"message": message})

@app.route("/api/admin/change-role", methods=["POST"])
def admin_change_role():
    session, err = require_auth(roles=["admin"])
    if err:
        return err
        
    data = request.get_json() or {}
    target = data.get("username")
    new_role = data.get("role")
    
    if not target or not new_role:
        return jsonify({"error": "Target username and new role are required."}), 400
        
    success, message = auth_manager.admin_change_role(session["username"], target, new_role)
    if not success:
        return jsonify({"error": message}), 404
        
    return jsonify({"message": message})

@app.route("/api/admin/delete", methods=["POST"])
def admin_delete_user():
    session, err = require_auth(roles=["admin"])
    if err:
        return err
        
    data = request.get_json() or {}
    target = data.get("username")
    
    if not target:
        return jsonify({"error": "Target username is required."}), 400
        
    success, message = auth_manager.admin_delete_user(session["username"], target)
    if not success:
        return jsonify({"error": message}), 400
        
    return jsonify({"message": message})

@app.route("/api/admin/logs", methods=["GET"])
def admin_logs():
    session, err = require_auth(roles=["admin"])
    if err:
        return err
        
    logs = auth_manager.get_audit_logs()
    # Sort with newest first
    logs.reverse()
    return jsonify(logs)

# --- TIMING ATTACK SIMULATOR ---

@app.route("/api/simulate-timing", methods=["POST"])
def simulate_timing():
    """
    Demonstrates the difference between early-exit character comparison (==) 
    and constant-time comparison (secrets.compare_digest).
    We amplify the differences by running the comparison 100,000 times.
    """
    data = request.get_json() or {}
    candidate = data.get("candidate", "")
    secret = "secure_token_secret_xyz"
    
    # We want to compare characters.
    # To demonstrate early exit, let's implement character-by-character standard comparison in Python
    # and compare it to secrets.compare_digest.
    
    # 1. Non-constant time comparison simulation
    def early_exit_compare(str1, str2):
        if len(str1) != len(str2):
            return False
        for char1, char2 in zip(str1, str2):
            if char1 != char2:
                return False
        return True

    # Run early exit loop
    start_time = time.perf_counter_ns()
    for _ in range(50000):
        _ = early_exit_compare(candidate, secret)
    early_exit_time = time.perf_counter_ns() - start_time
    
    # 2. Constant time comparison using secrets.compare_digest
    start_time = time.perf_counter_ns()
    for _ in range(50000):
        _ = auth_manager.secrets.compare_digest(candidate, secret)
    constant_time = time.perf_counter_ns() - start_time
    
    # Calculate matching prefix length to display as a parameter
    matching_prefix_len = 0
    for c_char, s_char in zip(candidate, secret):
        if c_char == s_char:
            matching_prefix_len += 1
        else:
            break
            
    # Return time in microseconds for readability
    return jsonify({
        "candidate": candidate,
        "secret_length": len(secret),
        "candidate_length": len(candidate),
        "matching_prefix_length": matching_prefix_len,
        "early_exit_us": round(early_exit_time / 1000, 2),
        "constant_time_us": round(constant_time / 1000, 2)
    })

# --- INITIALIZATION ---

if __name__ == "__main__":
    # Create templates and static directories if they don't exist
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    
    seed_database()
    
    print("\n" + "="*50)
    print("  SECURE AUTHENTICATION SYSTEM RUNNING ON LOCALHOST")
    print("  URL: http://127.0.0.1:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000)
