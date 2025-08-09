# File: database.py
import mysql.connector
from dotenv import load_dotenv
import os
import json

load_dotenv()

def get_db_connection():
    """Establishes and returns a MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def create_conversations_table():
    """Creates the conversations table if it doesn't exist."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    thread_id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    history JSON NOT NULL
                )
            """)
            connection.commit()
            print("Conversations table ensured.")
        except mysql.connector.Error as err:
            print(f"Error creating table: {err}")
        finally:
            cursor.close()
            connection.close()

def save_conversation(thread_id, user_id, history):
    """Saves or updates the conversation history for a given thread_id."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Check if the thread_id exists
            cursor.execute("SELECT thread_id FROM conversations WHERE thread_id = %s", (thread_id,))
            exists = cursor.fetchone()

            history_json = json.dumps(history)

            if exists:
                # Update existing conversation
                cursor.execute(
                    "UPDATE conversations SET history = %s, last_updated = CURRENT_TIMESTAMP WHERE thread_id = %s",
                    (history_json, thread_id)
                )
            else:
                # Insert new conversation
                cursor.execute(
                    "INSERT INTO conversations (thread_id, user_id, history) VALUES (%s, %s, %s)",
                    (thread_id, user_id, history_json)
                )
            connection.commit()
            print(f"Conversation {thread_id} saved successfully.")
        except mysql.connector.Error as err:
            print(f"Error saving conversation: {err}")
        finally:
            cursor.close()
            connection.close()

def get_conversation(thread_id):
    """Retrieves the conversation history for a given thread_id."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT history FROM conversations WHERE thread_id = %s", (thread_id,))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
        except mysql.connector.Error as err:
            print(f"Error retrieving conversation: {err}")
            return None
        finally:
            cursor.close()
            connection.close()

if __name__ == '__main__':
    # This block runs when the script is executed directly, creating the table.
    create_conversations_table()
