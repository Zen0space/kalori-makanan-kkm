import os
import libsql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database credentials from environment
DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
DATABASE_TOKEN = os.getenv("TURSO_DATABASE_TOKEN")

if not DATABASE_URL or not DATABASE_TOKEN:
    raise ValueError("Missing Turso database credentials in .env file")

def get_database():
    """Get Turso database connection"""
    try:
        # For remote-only connection to Turso
        if DATABASE_URL.startswith(("libsql://", "https://")):
            # Use remote-only connection (no local replica)
            conn = libsql.connect(DATABASE_URL, auth_token=DATABASE_TOKEN)
            return conn
        else:
            raise ValueError("Invalid database URL format. Use libsql:// or https://")
    except Exception as e:
        raise Exception(f"Failed to connect to database: {str(e)}")

def test_connection():
    """Test if database connection works"""
    try:
        conn = get_database()
        # Simple query to test connection
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return False

def get_food_by_name(name):
    """Search for foods by name"""
    try:
        conn = get_database()
        cursor = conn.cursor()
        query = """
        SELECT f.id, f.name, f.serving, f.weight_g, f.calories_kcal, f.reference, c.name as category
        FROM foods f
        LEFT JOIN categories c ON f.category_id = c.id
        WHERE f.name LIKE ?
        """
        cursor.execute(query, [f"%{name}%"])
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        raise Exception(f"Error searching for food: {str(e)}")

def get_food_by_id(food_id):
    """Get food by ID"""
    try:
        conn = get_database()
        cursor = conn.cursor()
        query = """
        SELECT f.id, f.name, f.serving, f.weight_g, f.calories_kcal, f.reference, c.name as category
        FROM foods f
        LEFT JOIN categories c ON f.category_id = c.id
        WHERE f.id = ?
        """
        cursor.execute(query, [food_id])
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        raise Exception(f"Error getting food by ID: {str(e)}")

def get_all_foods(limit=50, offset=0):
    """Get all foods with pagination"""
    try:
        conn = get_database()
        cursor = conn.cursor()
        query = """
        SELECT f.id, f.name, f.serving, f.weight_g, f.calories_kcal, f.reference, c.name as category
        FROM foods f
        LEFT JOIN categories c ON f.category_id = c.id
        LIMIT ? OFFSET ?
        """
        cursor.execute(query, [limit, offset])
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        raise Exception(f"Error getting foods: {str(e)}")

def get_total_foods():
    """Get total count of foods"""
    try:
        conn = get_database()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM foods")
        result = cursor.fetchone()
        count = result[0] if result else 0
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        raise Exception(f"Error getting food count: {str(e)}")

def get_all_categories():
    """Get all categories"""
    try:
        conn = get_database()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY name")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        raise Exception(f"Error getting categories: {str(e)}")
