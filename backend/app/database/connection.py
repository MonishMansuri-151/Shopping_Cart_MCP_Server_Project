import mysql.connector
import os
import logging

from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)


def get_db_connection():

    try:

        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )

        logger.info("Database connection successful")

        return connection

    except mysql.connector.Error as error:

        logger.error(
            "Database connection failed: %s",
            error
        )

        raise