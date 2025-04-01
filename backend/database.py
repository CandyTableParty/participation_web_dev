import pymysql

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",  # HeidiSQL에서 사용 중인 계정 (root)
        password="jun1206",  # HeidiSQL에서 설정한 비밀번호 입력!
        database="jun",  # 사용할 데이터베이스 이름
        port=3306,  # MySQL/MariaDB 기본 포트
        cursorclass=pymysql.cursors.DictCursor
    )
