import mysql.connector
from colorama import Fore, Style
from mysql.connector import errorcode
import os
import configparser


CONFIG_FILE = '.aegisconfig'
DATABASE_NAME = "aegis_db"
DB_CONFIG = {}



DATABASE_NAME = "aegis_db"
TABLES = {}
TABLES['users'] = (
    "CREATE TABLE `users` ("
    "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
    "  `username` VARCHAR(50) UNIQUE NOT NULL,"
    "  `password_hash` VARCHAR(255) NOT NULL,"
    "  `role` ENUM('admin', 'standard') DEFAULT 'standard'"
    ") ENGINE=InnoDB"
)

TABLES['resources'] = (
    "CREATE TABLE `resources` ("
    "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
    "  `user_id` INT NOT NULL,"
    "  `name` VARCHAR(255),"
    "  `encrypted_path` VARCHAR(255),"
    "  `secondary_secret` VARCHAR(255),"
    "  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB"
)

def initialize_db_and_connect():
    if not _load_db_config():
        return None

    conn = connect_db()

    return conn


def _load_db_config():
    config = configparser.ConfigParser()

    if not config.read(CONFIG_FILE):
        print(Fore.RED + f"[CRITICAL] Configuration file '{CONFIG_FILE}' not found!" + Style.RESET_ALL)
        return False

    try:
        global DB_CONFIG
        DB_CONFIG = {
            "host": config['MYSQL']['HOST'],
            "user": config['MYSQL']['USER'],
            "password": config['MYSQL']['PASSWORD'],
        }
        return True
    except KeyError as e:
        print(Fore.RED + f"[CRITICAL] Missing required key in {CONFIG_FILE} under [MYSQL]: {e}" + Style.RESET_ALL)
        return False


def connect_db(database_name=DATABASE_NAME):
    conn = None
    try:
        config = DB_CONFIG.copy()
        config['database'] = database_name
        conn = mysql.connector.connect(**config)

        if conn:
            initialize_database(conn, database_name)

        return conn

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print(Fore.RED + "\n Database Error: Access Denied! (Check password in db_connector.py)" + Style.RESET_ALL)
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            return create_database_and_reconnect(database_name)
        else:
            print(Fore.RED + f"\n Database Connection Error: {err}" + Style.RESET_ALL)
        return None

def create_database_and_reconnect(database_name):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} DEFAULT CHARACTER SET 'utf8'")
        conn.database = database_name

        print(Fore.YELLOW + f"Database '{database_name}' created successfully." + Style.RESET_ALL)

        initialize_database(conn, database_name)

        cursor.close()
        return conn

    except mysql.connector.Error as err:
        print(Fore.RED + f"\nFailed to create database: {err}" + Style.RESET_ALL)
        return None


def initialize_database(conn, database_name):
    cursor = conn.cursor()

    for table_name, table_sql in TABLES.items():
        try:
            cursor.execute(f"SELECT 1 FROM `{table_name}` LIMIT 1")
            cursor.fetchall()

        except mysql.connector.Error as err:

            if err.errno == errorcode.ER_NO_SUCH_TABLE:
                print(Fore.YELLOW + f"Creating table: {table_name}" + Style.RESET_ALL)
                try:
                    cursor.execute(table_sql)
                    conn.commit()
                except mysql.connector.Error as err_create:
                    print(Fore.RED + f"Table creation failed: {err_create}" + Style.RESET_ALL)
            else:
                print(Fore.RED + f"Unexpected error during table check: {err}" + Style.RESET_ALL)

        try:
            cursor.fetchall()
        except:
            pass

    cursor.close()
