import json
import pyodbc
from Automation_DataAccess.data_loader import load_config


# koneksi DB MS SQL Server
def get_connection():
    config = load_config()
    db_config = config["databases"]["acs_db_uat"]
    return pyodbc.connect(
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={db_config['server']};"
        f"Database={db_config['database']};"
        f"UID={db_config['uid']};"
        f"PWD={db_config['pwd']};"
    )


def add_database_verification(
    database_verifications,
    step_no,
    query
):
    result = execute_query(query)

    database_verifications.append({
        "step": step_no,
        "query": query,
        "result": result
    })

    return result


def execute_query(query):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(query)

    columns = [column[0] for column in cursor.description]

    rows = [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return rows


def query_klaim_settlement(no_registrasi):
    return f"""
SELECT
    A.REGISTRATION_NO,
    A.POLICY_NO,
    A.ENDORSE_VALUE_TYPE,
    A.DOC_STATUS,
    D.NAME AS DOC_STATUS_KLAIM,
    C.SETTLE_NOTE_NO,
    B.POSTING_DATE,
    C.PAYMENT_STATUS,
    C.PAYMENT_DATE,
    C.BANK_NOTE_NUMBER,
    C.AMT_PAYMENT,
    A.MODIFIED_DATE 
FROM CLAIM.CLM_REGISTRATION A
JOIN CLAIM.CLM_SETTLEMENT B
    ON A.REGISTRATION_ID = B.REGISTRATION_ID
JOIN CLAIM.CLM_SETTLEMENT_SUMMARY C
    ON B.SETTLEMENT_ID = C.SETTLEMENT_ID
JOIN MASTER.M_DOCUMENT_STATUS D
    ON A.DOC_STATUS = D.DOC_STATUS
WHERE A.REGISTRATION_NO = '{no_registrasi}' 
    ORDER BY A.MODIFIED_DATE DESC ;
"""


def query_klaim_Dikembalikan_Ditolak(no_registrasi):
    return f"""
SELECT
    A.REGISTRATION_NO,
    A.POLICY_NO,
    A.ENDORSE_VALUE_TYPE,
    A.DOC_STATUS,
    B.NAME AS DOC_STATUS_KLAIM
FROM CLAIM.CLM_REGISTRATION A
JOIN MASTER.M_DOCUMENT_STATUS B
    ON A.DOC_STATUS =B.DOC_STATUS
WHERE A.REGISTRATION_NO = '{no_registrasi}';
"""
