import os
import hashlib
from typing import List, Optional
import mysql.connector
from mysql.connector import errorcode
from models import User, Contact, Category


class DatabaseManager:
    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ):
        self.host = host or os.getenv("MYSQL_HOST", "localhost")
        self.port = port or int(os.getenv("MYSQL_PORT", "3306"))
        self.user = user or os.getenv("MYSQL_USER", "root")
        self.password = password if password is not None else os.getenv("MYSQL_PASSWORD", "")
        self.database = database or os.getenv("MYSQL_DATABASE", "phonebook")
        self._initialize_db()

    def _get_connection(self):
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
        )

    def _get_server_connection(self):
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
        )

    def _load_sql_statements(self, sql_file_path: str) -> List[str]:
        with open(sql_file_path, "r", encoding="utf-8") as file:
            raw_sql = file.read()

        statements: List[str] = []
        for statement in raw_sql.split(";"):
            sql = statement.strip()
            if not sql:
                continue

            normalized = sql.upper()
            # Avoid data loss on every application startup.
            if normalized.startswith("DROP TABLE"):
                continue

            statements.append(sql)

        return statements

    def _initialize_db(self):
        schema_path = os.path.join(os.path.dirname(__file__), "phonebook.sql")

        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        conn = self._get_server_connection()
        try:
            cursor = conn.cursor()
            for statement in self._load_sql_statements(schema_path):
                cursor.execute(statement)
            conn.commit()
        finally:
            conn.close()

    # ─────────────────────────────────────────────
    #  Password hashing
    # ─────────────────────────────────────────────

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    # ─────────────────────────────────────────────
    #  User operations
    # ─────────────────────────────────────────────

    def register_user(self, user_name: str, password: str) -> Optional[User]:
        """Register a new user.  Returns the User on success, None if username already exists."""
        hashed = self._hash_password(password)
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (user_name, password) VALUES (%s, %s)",
                    (user_name, hashed),
                )
                conn.commit()
                return User(userid=cursor.lastrowid, user_name=user_name, password=hashed)
            finally:
                conn.close()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                return None
            raise

    def login_user(self, user_name: str, password: str) -> Optional[User]:
        """Authenticate a user.  Returns the User on success, None on failure."""
        hashed = self._hash_password(password)
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT userid, user_name, password FROM users WHERE user_name = %s AND password = %s",
                (user_name, hashed),
            )
            row = cursor.fetchone()
            if row:
                return User(*row)
            return None
        finally:
            conn.close()

    # ─────────────────────────────────────────────
    #  Category operations
    # ─────────────────────────────────────────────

    def add_category(self, cate_name: str, userid: int) -> Optional[Category]:
        """Create a new category for a user.  Returns Category on success, None if duplicate."""
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO categories (cate_name, userid) VALUES (%s, %s)",
                    (cate_name, userid),
                )
                conn.commit()
                return Category(cate_id=cursor.lastrowid, cate_name=cate_name, userid=userid)
            finally:
                conn.close()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                return None
            raise

    def get_categories(self, userid: int) -> List[Category]:
        """Return all categories belonging to a user."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT cate_id, cate_name, userid FROM categories WHERE userid = %s ORDER BY cate_name",
                (userid,),
            )
            return [Category(*row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def delete_category(self, cate_id: int, userid: int) -> bool:
        """Delete a category.  Returns True on success."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # Unlink contacts that reference this category first
            cursor.execute(
                "UPDATE contacts SET cate_id = NULL WHERE cate_id = %s AND userid = %s",
                (cate_id, userid),
            )
            cursor.execute(
                "DELETE FROM categories WHERE cate_id = %s AND userid = %s",
                (cate_id, userid),
            )
            if cursor.rowcount == 0:
                return False
            conn.commit()
            return True
        finally:
            conn.close()

    # ─────────────────────────────────────────────
    #  Contact operations
    # ─────────────────────────────────────────────

    def add_contact(self, contact: Contact) -> bool:
        """Add a new contact.  Returns False if phone already exists."""
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO contacts (contact_name, phone, email, address, userid, cate_id)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (contact.contact_name, contact.phone, contact.email,
                     contact.address, contact.userid, contact.cate_id),
                )
                conn.commit()
                return True
            finally:
                conn.close()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                return False
            raise

    def update_contact(self, contact: Contact) -> bool:
        """Update an existing contact.  Returns False if not found or phone duplicated."""
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE contacts
                       SET contact_name=%s, phone=%s, email=%s, address=%s, cate_id=%s
                       WHERE contact_id=%s AND userid=%s""",
                    (contact.contact_name, contact.phone, contact.email,
                     contact.address, contact.cate_id,
                     contact.contact_id, contact.userid),
                )
                if cursor.rowcount == 0:
                    return False
                conn.commit()
                return True
            finally:
                conn.close()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                return False
            raise

    def delete_contact(self, contact_id: int, userid: int) -> bool:
        """Delete a contact.  Returns False if not found."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM contacts WHERE contact_id=%s AND userid=%s",
                (contact_id, userid),
            )
            if cursor.rowcount == 0:
                return False
            conn.commit()
            return True
        finally:
            conn.close()

    def get_all_contacts(self, userid: int) -> List[Contact]:
        """Return all contacts for a user, with category name populated."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT c.contact_id, c.contact_name, c.phone, c.email, c.address,
                          c.userid, c.cate_id, cat.cate_name
                   FROM contacts c
                   LEFT JOIN categories cat ON c.cate_id = cat.cate_id
                   WHERE c.userid = %s
                   ORDER BY c.contact_name""",
                (userid,),
            )
            return [Contact(*row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def search_contacts(self, query: str, userid: int) -> List[Contact]:
        """Search contacts by name or phone."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            search_str = f"%{query}%"
            cursor.execute(
                """SELECT c.contact_id, c.contact_name, c.phone, c.email, c.address,
                          c.userid, c.cate_id, cat.cate_name
                   FROM contacts c
                   LEFT JOIN categories cat ON c.cate_id = cat.cate_id
                   WHERE c.userid = %s AND (c.contact_name LIKE %s OR c.phone LIKE %s)
                   ORDER BY c.contact_name""",
                (userid, search_str, search_str),
            )
            return [Contact(*row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def filter_by_category(self, cate_id: int, userid: int) -> List[Contact]:
        """Return contacts in a specific category."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT c.contact_id, c.contact_name, c.phone, c.email, c.address,
                          c.userid, c.cate_id, cat.cate_name
                   FROM contacts c
                   LEFT JOIN categories cat ON c.cate_id = cat.cate_id
                   WHERE c.userid = %s AND c.cate_id = %s
                   ORDER BY c.contact_name""",
                (userid, cate_id),
            )
            return [Contact(*row) for row in cursor.fetchall()]
        finally:
            conn.close()
