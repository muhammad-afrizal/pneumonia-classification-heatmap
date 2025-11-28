import mysql.connector
from mysql.connector import Error
from env import DB_CONFIG
from werkzeug.security import generate_password_hash, check_password_hash

def create_connection():
    """Create a database connection to MySQL"""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Connected to MySQL database")
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    return connection

def init_db():
    """Create the users and history tables if they don't exist and update structure if needed"""
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create history table with basic structure first
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    filename TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Add missing columns to history table if they don't exist
            try:
                # Check if clahe_filename column exists
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'history' 
                    AND COLUMN_NAME = 'clahe_filename'
                """)
                result = cursor.fetchone()
                if result[0] == 0:  # Column doesn't exist
                    cursor.execute("ALTER TABLE history ADD COLUMN clahe_filename TEXT NULL")
                    print("Added clahe_filename column to history table")
                
                # Check if saliency_filename column exists
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'history' 
                    AND COLUMN_NAME = 'saliency_filename'
                """)
                result = cursor.fetchone()
                if result[0] == 0:  # Column doesn't exist
                    cursor.execute("ALTER TABLE history ADD COLUMN saliency_filename TEXT NULL")
                    print("Added saliency_filename column to history table")
                
                # Check if overlay_filename column exists
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'history' 
                    AND COLUMN_NAME = 'overlay_filename'
                """)
                result = cursor.fetchone()
                if result[0] == 0:  # Column doesn't exist
                    cursor.execute("ALTER TABLE history ADD COLUMN overlay_filename TEXT NULL")
                    print("Added overlay_filename column to history table")
            except Error as e:
                print(f"Note: {e}")
            
            # Create feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    history_id INT,
                    is_accurate BOOLEAN,
                    usefulness_rating INT,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (history_id) REFERENCES history(id) ON DELETE CASCADE
                )
            """)
            
            connection.commit()
            print("Database initialized and updated successfully")
        except Error as e:
            print(f"Error while initializing database: {e}")
        finally:
            cursor.close()
            connection.close()

def insert_history(user_id, filename, prediction, confidence, clahe_filename=None, saliency_filename=None, overlay_filename=None):
    """Insert a new record into the history table"""
    print(f"DEBUG: Inserting history for user_id={user_id}, filename={filename}")
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO history (user_id, filename, prediction, confidence, clahe_filename, saliency_filename, overlay_filename)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, filename, prediction, confidence, clahe_filename, saliency_filename, overlay_filename))
            connection.commit()
            print("Record inserted successfully")
            # Return the last inserted id
            last_id = cursor.lastrowid
            print(f"DEBUG: Inserted history record with ID: {last_id}")
            return last_id
        except Error as e:
            print(f"Error while inserting record: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def get_all_history(user_id=None):
    """Retrieve all records from the history table, optionally filtered by user_id"""
    print(f"DEBUG: Getting history for user_id={user_id}")
    connection = create_connection()
    records = []
    if connection is not None:
        try:
            cursor = connection.cursor()
            if user_id:
                cursor.execute("""SELECT id, user_id, filename, prediction, confidence, 
                               clahe_filename, saliency_filename, overlay_filename, timestamp 
                               FROM history WHERE user_id = %s ORDER BY timestamp DESC""", (user_id,))
                print(f"DEBUG: Executing query for user_id {user_id}")
            else:
                cursor.execute("""SELECT h.id, h.user_id, h.filename, h.prediction, h.confidence, 
                               h.clahe_filename, h.saliency_filename, h.overlay_filename, h.timestamp, u.username 
                               FROM history h JOIN users u ON h.user_id = u.id ORDER BY h.timestamp DESC""")
                print("DEBUG: Executing query for all users")
            records = cursor.fetchall()
            print(f"DEBUG: Retrieved {len(records)} records")
        except Error as e:
            print(f"Error while retrieving records: {e}")
        finally:
            cursor.close()
            connection.close()
    return records

def register_user(username, password):
    """Register a new user"""
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (username, password)
                VALUES (%s, %s)
            """, (username, hashed_password))
            connection.commit()
            print("User registered successfully")
            return True
        except Error as e:
            print(f"Error while registering user: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False

def authenticate_user(username, password):
    """Authenticate a user"""
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[1], password):
                return user[0]  # Return user ID
            return None
        except Error as e:
            print(f"Error while authenticating user: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            return user
        except Error as e:
            print(f"Error while retrieving user: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def get_all_users():
    """Get all users with their prediction count"""
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT u.id, u.username, u.created_at, u.role, COUNT(h.id) as prediction_count 
                FROM users u 
                LEFT JOIN history h ON u.id = h.user_id 
                GROUP BY u.id, u.username, u.created_at, u.role 
                ORDER BY u.created_at DESC
            """)
            users = cursor.fetchall()
            return users
        except Error as e:
            print(f"Error while retrieving users: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

def update_user_role(user_id, role):
    """Update user role"""
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET role = %s WHERE id = %s", (role, user_id))
            connection.commit()
            return True
        except Error as e:
            print(f"Error while updating user role: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False

# Feedback functions
def insert_feedback(history_id, is_accurate, usefulness_rating, reason=None):
    """Insert feedback for a prediction"""
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO feedback (history_id, is_accurate, usefulness_rating, reason)
                VALUES (%s, %s, %s, %s)
            """, (history_id, is_accurate, usefulness_rating, reason))
            connection.commit()
            print("Feedback inserted successfully")
            return True
        except Error as e:
            print(f"Error while inserting feedback: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    return False

def get_feedback_by_history_id(history_id):
    """Get feedback for a specific history record"""
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM feedback WHERE history_id = %s", (history_id,))
            feedback = cursor.fetchone()
            return feedback
        except Error as e:
            print(f"Error while retrieving feedback: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def get_all_feedback():
    """Get all feedback with user and history information"""
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT f.*, h.filename, h.prediction, h.confidence, u.username
                FROM feedback f
                JOIN history h ON f.history_id = h.id
                JOIN users u ON h.user_id = u.id
                ORDER BY f.created_at DESC
            """)
            feedback = cursor.fetchall()
            return feedback
        except Error as e:
            print(f"Error while retrieving feedback: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

def get_feedback_stats():
    """Get feedback statistics"""
    connection = create_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            
            # Total predictions
            cursor.execute("SELECT COUNT(*) FROM history")
            total_predictions = cursor.fetchone()[0]
            
            # Total feedback
            cursor.execute("SELECT COUNT(*) FROM feedback")
            total_feedback = cursor.fetchone()[0]
            
            # Accuracy rate
            cursor.execute("SELECT COUNT(*) FROM feedback WHERE is_accurate = 1")
            accurate_predictions = cursor.fetchone()[0]
            
            accuracy_rate = (accurate_predictions / total_feedback * 100) if total_feedback > 0 else 0
            
            # Rating distribution
            cursor.execute("""
                SELECT usefulness_rating, COUNT(*) as count
                FROM feedback
                GROUP BY usefulness_rating
                ORDER BY usefulness_rating
            """)
            rating_distribution = cursor.fetchall()
            
            return {
                'total_predictions': total_predictions,
                'total_feedback': total_feedback,
                'accuracy_rate': accuracy_rate,
                'rating_distribution': rating_distribution
            }
        except Error as e:
            print(f"Error while retrieving feedback stats: {e}")
            return {}
        finally:
            cursor.close()
            connection.close()
    return {}
