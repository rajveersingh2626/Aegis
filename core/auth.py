
import bcrypt
import uuid
import sys
from core.db import initialize_db_and_connect
from core.audit import log_event


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def db_register_user(username, password, role='standard'):
    conn = initialize_db_and_connect()
    if not conn: return False
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            log_event(username, 'REGISTER_FAIL', 'Reason=UsernameExists') 
            return "EXISTS"

        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            (username, password_hash, role)
        )
        conn.commit()
        log_event(username, 'REGISTER_SUCCESS', f'NewUserID={cursor.lastrowid}')
        return True

    except Exception as e:
        print(f"[CORE ERROR] Registration: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def db_login_user(username, password):

    conn = initialize_db_and_connect()
    if not conn: return None
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, password_hash, role FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and verify_password(password, user[1]):
            log_event(username, 'LOGIN_SUCCESS', f'Role={user[2]}')
            session_token = str(uuid.uuid4())
            return {
                'id': user[0],
                'username': username,
                'role': user[2],
                'token': session_token
            }
        else:
            log_event(username, 'LOGIN_FAIL', 'Reason=InvalidCredentials')
            return None

    except Exception as e:
        print(f"[CORE ERROR] Login: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def db_change_password(user_id: int, old_password: str, new_password: str):

    conn = initialize_db_and_connect()
    if not conn: return None
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
        record = cursor.fetchone()

        if not record:
            return False

        current_hash = record[0]

        if not verify_password(old_password, current_hash):
            log_event(f'UserID={user_id}', 'PW_CHANGE_FAIL', 'Reason=OldPasswordMismatch')
            return False

        new_hash = hash_password(new_password)
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_hash, user_id)
        )
        conn.commit()
        log_event(f'UserID={user_id}', 'PW_CHANGE_SUCCESS', '')
        return True

    except Exception as e:
        print(f"[CORE ERROR] Password Change: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def db_delete_account(user_id: int, password: str):
    conn = initialize_db_and_connect()
    if not conn: return None
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
        record = cursor.fetchone()

        if not record:
            return False

        if not verify_password(password, record[0]):
            return False


        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return True

    except Exception as e:
        print(f"[CORE ERROR] Account Deletion: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def db_admin_reset_password(target_username: str, new_password: str):
    conn = initialize_db_and_connect()
    if not conn: return None
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (target_username,))
        user_record = cursor.fetchone()

        if not user_record:
            return False # Target user not found

        new_hash = hash_password(new_password)
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE username = %s",
            (new_hash, target_username)
        )
        conn.commit()
        return True

    except Exception as e:
        print(f"[CORE ERROR] Admin Password Reset: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
