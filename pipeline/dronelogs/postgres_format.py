"""Database connection and functions."""
import sys
from os import environ
import traceback
import logging
import numpy as np
import psycopg2
from utils.tools import flatten_list


def check_env():
    if "DB_HOST" not in environ:
        raise ValueError("ERROR:   DB_HOST in undefined in environment variables")
    if "DB_PORT" not in environ:
        raise ValueError("ERROR:   DB_PORT in undefined in environment variables")
    if "DB_NAME" not in environ:
        raise ValueError("ERROR:   DB_NAME in undefined in environment variables")
    if "DB_USER" not in environ:
        raise ValueError("ERROR:   DB_USER in undefined in environment variables")
    if "DB_PASS" not in environ:
        raise ValueError("ERROR:   DB_PASS in undefined in environment variables")
    if "LOGER_NAME" not in environ:
        raise ValueError("ERROR:  LOGER_NAME in undefined in environment variables")

def gen_format_str(num):
    """
    Formatter string
    """
    sql_str = "("
    sql_str += ", ".join(["%s"] * num)
    sql_str += ")"
    return sql_str

def dynamic_format_value_in(shape):
    # @TODO: this function may be improved
    """
    Return %s in format of shape.

    shape is one of: integer or tuple (Nx,Ny)
    Returns the sql string that allows for dynamic formating for insert statements.
    Ex: 2 -> '(%s, %s)'
    Ex: (3,2) -> '
    (%s, %s),
    (%s, %s),
    (%s, %s)''
    """
    sql_str = ""

    if np.isscalar(shape):
        sql_str = gen_format_str(shape)

    elif len(shape) == 1:
        sql_str = gen_format_str(shape[0])

    elif len(shape) == 2:

        repeated_str = [gen_format_str(shape[1])] * shape[0]
        sql_str = ",\n".join(repeated_str)

    return sql_str

def sql_sanitize(np_elem):
    """Sql sanitize."""
    sql_elem = None
    try:
        # pylint: disable=bad-continuation
        if (
            (np_elem is None)
            or (np_elem == "nan")
            or (np_elem == "'Null'")
            or (not isinstance(np_elem, str) and np.isnan(np_elem))
        ):
            sql_elem = None
        else:
            sql_elem = np_elem
    # pylint: disable=broad-except
    except Exception:
        sql_elem = np_elem

    return sql_elem

def stringify_row(row):
    """Return string for sql insert."""
    return "(" + ", ".join(["'" + e + "'" if isinstance(e, str) else str(e) for e in row]) + ")"

class PostgresFormatter():
    """
    Postgres Formatter.

    Connections are made in application level (ex Airflow).
    MUST CLOSE CONNECTION in application code.
    """

    def __init__(self):
        """Initialize connection."""
        check_env()
        self.db_host = environ["DB_HOST"]
        self.db_port = environ["DB_PORT"]
        self.db_name = environ["DB_NAME"]
        self.db_user = environ["DB_USER"]
        self.db_pass = environ["DB_PASS"]
        self.logger = logging.getLogger(environ["LOGER_NAME"])
        self.logger.setLevel(logging.DEBUG)
        self.make_conn()

    def close(self):
        """Close."""
        self.conn.close()

    def make_conn(self):
        """Connection is created using this function."""
        try:
            self.conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                host=self.db_host,
                port=self.db_port,
                password=self.db_pass,
            )
            self.cur = self.conn.cursor()
        except psycopg2.Error as err:
            self.logger.error(err)
            self.logger.error("I am unable to connect to the database")
            sys.exit(2)

    def fetch_data(self, query):
        """Fetch a particular query's data."""
        result = []
        try:
            self.cur.execute(query)
            raw = self.cur.fetchall()
            for line in raw:
                result.append(line)
            return result
        # pylint: disable=broad-except
        except Exception as error:
            self.logger.error("Query: %s", str(query))
            self.logger.error(traceback.format_exc())
            self.logger.error(error)
            self.conn.rollback()
            sys.exit(2)

    def execute(self, query):
        """Safe excute and rollback."""
        try:
            self.cur.execute(query)
        # pylint: disable=broad-except
        except Exception as error:
            self.logger.error("Query: %s", str(query))
            self.logger.error(traceback.format_exc())
            self.logger.error(error)
            self.conn.rollback()
            sys.exit(2)

    def safe_commit(self):
        """Commit all cursors on connection, conn. Reraises any errors."""
        try:
            self.conn.commit()
        except Exception as error:
            self.logger.error(error)
            self.logger.error(traceback.format_exc())
            self.conn.rollback()
            sys.exit(2)

    def execute_many(self, query, data):
        """Execute multiple queries at once."""
        self.cur.executemany(query, data)
        self.safe_commit()

    def insert_pandas(self, tbl_name, tbl_cols, pdf):
        """Insert a Pandas Dataframe, pdf, into tblName."""
        val_list = pdf.values.tolist()
        val_clean = list(map(sql_sanitize, flatten_list(val_list)))
        sql_txt = f'INSERT INTO {tbl_name} ('
        sql_txt += ", ".join(tbl_cols)
        sql_txt += ") VALUES "
        sql_txt += dynamic_format_value_in(pdf.values.shape)
        sql_txt += ";"
        sql = self.cur.mogrify(sql_txt, val_clean)
        self.execute(sql)
        return sql

    def insert_detail(self, tbl_name, const_cols, const_vals, var_cols, var_vals):
        """
        Insert records into given table.

        constVals list 1xL of record values associated with constCols column names
        varCols list MXN of record values associated with varCols column names
        """
        
        if len(np.array(const_vals).shape) < 2:
            const_vals = [const_vals]

        const_vals = const_vals * len(var_vals)

        val_array = np.hstack((const_vals, var_vals))
        sql_txt = f'INSERT INTO {tbl_name} ('
        sql_txt += ", ".join(const_cols + var_cols)
        sql_txt += ") VALUES "
        sql_txt += dynamic_format_value_in(val_array.shape)
        sql_txt += ";"
        flat_val_list = list(map(sql_sanitize, flatten_list(val_array)))
        sql = self.cur.mogrify(sql_txt, flat_val_list)
        self.execute(sql)
        return sql
