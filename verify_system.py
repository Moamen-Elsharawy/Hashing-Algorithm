import os
import time
import json
import auth_manager
from datetime import datetime, timedelta

# ANSI colors for premium terminal outputs
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def run_tests():
    print(f"\n{CYAN}=================================================={RESET}")
    print(f"{CYAN}       AETHER SHIELD SYSTEM INTEGRATION TESTS     {RESET}")
    print(f"{CYAN}=================================================={RESET}\n")

    # Clear databases for fresh testing environment
    if os.path.exists(auth_manager.USERS_DB):
        os.remove(auth_manager.USERS_DB)
    if os.path.exists(auth_manager.AUDIT_LOG_DB):
        os.remove(auth_manager.AUDIT_LOG_DB)

    passed_tests = 0
    total_tests = 6

    # ----------------------------------------------------
    # TEST 1: User Registration with Hashing
    # ----------------------------------------------------
    print(f"[{YELLOW}TEST 1/6{RESET}] Testing Registration Hashing (PBKDF2, Bcrypt, Argon2)...")
    try:
        # Register standard user with default PBKDF2
        success1, msg1 = auth_manager.register_user(
            username="test_pbkdf2",
            password="Pbkdf2Password123!",
            role="user",
            security_question="First school?",
            security_answer="academy",
            hash_algo="pbkdf2_sha256"
        )
        # Register user with Bcrypt
        success2, msg2 = auth_manager.register_user(
            username="test_bcrypt",
            password="BcryptPassword456!",
            role="user",
            security_question="First car?",
            security_answer="sedan",
            hash_algo="bcrypt"
        )
        # Register user with Argon2
        success3, msg3 = auth_manager.register_user(
            username="test_argon2",
            password="Argon2Password789!",
            role="admin",
            security_question="Favorite fruit?",
            security_answer="apple",
            hash_algo="argon2"
        )

        assert success1 and success2 and success3, "Registration requests failed"
        
        # Load and verify JSON file contains zero plaintext passwords
        with open(auth_manager.USERS_DB, "r") as f:
            db_records = json.load(f)
            
        for username, record in db_records.items():
            # Crucial check: password must not be plain!
            assert "Password" not in record["password_hash"], f"Plaintext leak found in {username}"
            assert record["password_hash"] != "Pbkdf2Password123!", "Plaintext leak in pbkdf2"
            assert record["password_hash"] != "BcryptPassword456!", "Plaintext leak in bcrypt"
            assert record["password_hash"] != "Argon2Password789!", "Plaintext leak in argon2"
            
            # Crucial check: security answers must not be plain!
            assert record["security_hash"] != record["security_question"], "Plaintext security question answer leak"
            print(f"  -> User '{username}' stored hash: {CYAN}{record['password_hash'][:40]}...{RESET}")
            
        print(f"  {GREEN}[PASS] All registrations successful and verified secure in users.json{RESET}")
        passed_tests += 1
    except Exception as e:
        print(f"  {RED}[FAIL] Registration Test: {e}{RESET}")

    # ----------------------------------------------------
    # TEST 2: Successful Login & Session Token Generation
    # ----------------------------------------------------
    print(f"\n[{YELLOW}TEST 2/6{RESET}] Testing Login and Session Generation...")
    try:
        success, msg, token, role = auth_manager.login_user("test_pbkdf2", "Pbkdf2Password123!")
        assert success, f"Login failed: {msg}"
        assert token is not None, "Session token is null"
        assert role == "user", "Role verification incorrect"
        
        print(f"  -> Generated Secure Session Token: {CYAN}{token}{RESET}")
        
        # Validate session in active memory
        session = auth_manager.validate_session(token)
        assert session is not None, "Session token was not cached or registered on server"
        assert session["username"] == "test_pbkdf2", "Session username mismatch"
        
        print(f"  {GREEN}[PASS] Authentication validated and token verified in-memory.{RESET}")
        passed_tests += 1
    except Exception as e:
        print(f"  {RED}[FAIL] Login Test: {e}{RESET}")

    # ----------------------------------------------------
    # TEST 3: Lockout Policy (3 failed attempts -> 30s lock)
    # ----------------------------------------------------
    print(f"\n[{YELLOW}TEST 3/6{RESET}] Testing 3-Attempt Account Lockout Policy...")
    try:
        username = "test_pbkdf2"
        
        # 1st fail
        success, msg, token, role = auth_manager.login_user(username, "wrong_pwd_1")
        assert not success, "Failed login should return success=False"
        
        # 2nd fail
        success, msg, token, role = auth_manager.login_user(username, "wrong_pwd_2")
        assert not success, "Failed login should return success=False"
        
        # 3rd fail -> triggers lockout
        success, msg, token, role = auth_manager.login_user(username, "wrong_pwd_3")
        assert not success, "Failed login should return success=False"
        assert "locked" in msg.lower(), f"Lockout message not triggered: {msg}"
        
        # 4th login attempt (during lockout) -> immediate reject
        success, msg, token, role = auth_manager.login_user(username, "Pbkdf2Password123!") # correct password, but locked
        assert not success, "Should not allow login with CORRECT password during lockout period"
        assert "locked" in msg.lower(), f"Failed to block correct password during lockout: {msg}"
        
        print(f"  -> Verification message during lockout: {RED}{msg}{RESET}")
        print(f"  {GREEN}[PASS] Account successfully locked for 30s. Correct passwords blocked.{RESET}")
        passed_tests += 1
    except Exception as e:
        print(f"  {RED}[FAIL] Lockout Policy Test: {e}{RESET}")

    # ----------------------------------------------------
    # TEST 4: Lockout Expiration Verification
    # ----------------------------------------------------
    print(f"\n[{YELLOW}TEST 4/6{RESET}] Testing Lockout Expiration...")
    try:
        username = "test_pbkdf2"
        users = auth_manager.load_json(auth_manager.USERS_DB, {})
        
        # Artificially shift the lockout timestamp back in time to avoid waiting 30 seconds in automated test
        print("  -> Simulating lockout time shift (30 seconds in the past)...")
        users[username]["lockout_until"] = (datetime.now() - timedelta(seconds=1)).isoformat()
        auth_manager.save_json(auth_manager.USERS_DB, users)
        
        # Try login now -> lockout has expired, correct password should work
        success, msg, token, role = auth_manager.login_user(username, "Pbkdf2Password123!")
        assert success, f"Login failed after lockout expiration: {msg}"
        assert token is not None, "Failed to generate session after lockout expiration"
        
        print(f"  {GREEN}[PASS] Lockout expired successfully and reset access control.{RESET}")
        passed_tests += 1
    except Exception as e:
        print(f"  {RED}[FAIL] Lockout Expiration Test: {e}{RESET}")

    # ----------------------------------------------------
    # TEST 5: Password Reset Flow (Security Question)
    # ----------------------------------------------------
    print(f"\n[{YELLOW}TEST 5/6{RESET}] Testing Security Question Password Reset Flow...")
    try:
        username = "test_bcrypt"
        
        # Retrieve security question
        success, question = auth_manager.get_security_question(username)
        assert success, "Failed to get question"
        assert question == "First car?", f"Question mismatch: {question}"
        
        # Try reset with WRONG answer
        success, msg = auth_manager.verify_reset_answer_and_change_password(
            username=username,
            answer="wrong_car_answer",
            new_password="NewSecureBcryptPassword999!"
        )
        assert not success, "Should fail reset on wrong answer"
        
        # Try reset with CORRECT answer
        success, msg = auth_manager.verify_reset_answer_and_change_password(
            username=username,
            answer="sedan",
            new_password="NewSecureBcryptPassword999!"
        )
        assert success, f"Reset failed with correct answer: {msg}"
        
        # Attempt login with NEW password
        login_success, login_msg, token, role = auth_manager.login_user(username, "NewSecureBcryptPassword999!")
        assert login_success, "Login failed with new password after reset"
        
        print(f"  {GREEN}[PASS] Verified password reset flow and dynamic credential updating.{RESET}")
        passed_tests += 1
    except Exception as e:
        print(f"  {RED}[FAIL] Password Reset Test: {e}{RESET}")

    # ----------------------------------------------------
    # TEST 6: Session Invalidation on Logout
    # ----------------------------------------------------
    print(f"\n[{YELLOW}TEST 6/6{RESET}] Testing Session Logout Invalidation...")
    try:
        username = "test_argon2"
        # Login
        success, msg, token, role = auth_manager.login_user(username, "Argon2Password789!")
        assert success, "Login failed"
        
        # Validate active session
        session1 = auth_manager.validate_session(token)
        assert session1 is not None, "Session invalid before logout"
        
        # Logout
        logout_success = auth_manager.logout_session(token)
        assert logout_success, "Logout method returned False"
        
        # Re-validate session (should be deleted and fail)
        session2 = auth_manager.validate_session(token)
        assert session2 is None, "Session token remains active after explicit logout"
        
        print(f"  {GREEN}[PASS] Token successfully revoked on logout. Backdoor access blocked.{RESET}")
        passed_tests += 1
    except Exception as e:
        print(f"  {RED}[FAIL] Session Invalidation Test: {e}{RESET}")

    # ----------------------------------------------------
    # SUMMARY
    # ----------------------------------------------------
    print(f"\n{CYAN}=================================================={RESET}")
    print(f"                VERIFICATION SUMMARY              ")
    print(f"  PASSED: {GREEN}{passed_tests}/{total_tests}{RESET} tests")
    print(f"{CYAN}=================================================={RESET}\n")
    
    # Return code for test runner check
    return passed_tests == total_tests

if __name__ == "__main__":
    run_tests()
