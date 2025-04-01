from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import pymysql
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from backend.auth import JWTBearer
from fastapi import Depends
from fastapi import FastAPI, Query, HTTPException, Depends  # ← ✅ 여기서 Depends 추가!
from fastapi import Request  # 추가 필요 시
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정 (외부에서 접근 가능하도록 설정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (테스트용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ✅ "static" 폴더를 정적 파일 디렉토리로 설정
# app.mount("/static", StaticFiles(directory="static"), name="static")
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# ✅ "index.html"을 기본 페이지로 제공
@app.get("/", response_class=HTMLResponse)
def serve_index():
    path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(path, "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())


def get_db_connection():
    ca_path = os.path.join(os.path.dirname(__file__), "isrgrootx1.pem")  # CA 인증서 위치
    return pymysql.connect(
        host="gateway01.ap-northeast-1.prod.aws.tidbcloud.com",
        port=4000,
        user="4RGaKiyfHpPuAt3.root",
        password="eK8HW6w0cLFf8sbE",
        database="test",
        cursorclass=pymysql.cursors.DictCursor,
        ssl={"ca": ca_path}
    )
class LoginInput(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(request: Request):
    from backend.auth import verify_password, create_access_token

    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="username 또는 password가 누락되었습니다.")

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # ✅ dict 형태로 받기
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        db_user = cursor.fetchone()

        if not db_user:
            raise HTTPException(status_code=401, detail="해당 아이디가 존재하지 않습니다.")

        if not verify_password(password, db_user["passwordHash"]):
            raise HTTPException(status_code=401, detail="비밀번호가 올바르지 않습니다.")

        token = create_access_token({"username": db_user["username"], "role": db_user["role"]})
        return {"access_token": token}
    finally:
        cursor.close()
        conn.close()

# ✅ 참여율 입력 모델
class ParticipationInput(BaseModel):
    staffId: str
    projectId: str
    participationRate: float
    leadTaskFlag: bool = False  # ✅ 기본값 False 설정

# ✅ 참여율 저장 API
@app.get("/participation")
def get_participation(staffId: str = Query(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT p.projectId, p.participationRate, p.leadTaskFlag, pr.projectName
            FROM participation p
            JOIN projects pr ON p.projectId = pr.projectId
            WHERE p.staffId = %s
        """, (staffId,))
        return cursor.fetchall()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"참여율 조회 오류: {str(e)}")

    finally:
        cursor.close()
        conn.close()
@app.post("/participation/delete")
def delete_participation(data: dict):
    staffId = data.get("staffId")
    if not staffId:
        raise HTTPException(status_code=400, detail="staffId는 필수입니다.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM participation WHERE staffId = %s", (staffId,))
        conn.commit()
        return {"message": "참여율 정보가 삭제되었습니다."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ✅ 기존 참여율 저장 API 수정 (삭제 기능 추가)
@app.post("/participation")
def save_participation(data: List[ParticipationInput]):
    print("🚀 DEBUG: 들어온 데이터 ->", data)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        staff_id = data[0].staffId if data else None  # 직원 ID 가져오기
        if not staff_id:
            raise HTTPException(status_code=400, detail="staffId가 제공되지 않았습니다.")

        # ✅ 현재 직원의 기존 참여율 목록 가져오기
        cursor.execute("SELECT projectId FROM participation WHERE staffId = %s", (staff_id,))
        existing_projects = {row["projectId"] for row in cursor.fetchall()}  # 기존 사업 ID 목록

        # ✅ 현재 남아있는 프로젝트 ID 목록
        new_projects = {entry.projectId for entry in data}

        # ✅ 삭제할 프로젝트 찾기 (기존에 있었으나 새 요청에는 없는 항목)
        projects_to_delete = existing_projects - new_projects
        if projects_to_delete:
            print(f"🗑 삭제할 프로젝트: {projects_to_delete}")
            cursor.executemany("DELETE FROM participation WHERE staffId = %s AND projectId = %s",
                               [(staff_id, project_id) for project_id in projects_to_delete])

        # ✅ 새로운 데이터 저장 (삽입 또는 업데이트)
        for entry in data:
            print(f"🎯 저장할 데이터: staffId={entry.staffId}, projectId={entry.projectId}, rate={entry.participationRate}, lead={entry.leadTaskFlag}")
            cursor.execute("""
                INSERT INTO participation (staffId, projectId, participationRate, leadTaskFlag)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    participationRate = VALUES(participationRate),
                    leadTaskFlag = VALUES(leadTaskFlag)
            """, (entry.staffId, entry.projectId, entry.participationRate, entry.leadTaskFlag))

        conn.commit()
        return {"message": "참여율이 성공적으로 저장되었습니다!"}

    except Exception as e:
        conn.rollback()
        print(f"🔥 SQL 실행 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SQL 실행 오류: {str(e)}")

    finally:
        cursor.close()
        conn.close()
# ✅ 부서 목록 조회 (인원 관리)
@app.get("/departments/staff")
def get_staff_departments():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT staffDepartment FROM staff")
        departments = cursor.fetchall()
        return [dept["staffDepartment"] for dept in departments if dept["staffDepartment"]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# ✅ 부서 목록 조회 (사업 관리)
@app.get("/departments/projects")
def get_project_departments():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT department FROM projects")
        departments = cursor.fetchall()
        return [dept["department"] for dept in departments if dept["department"]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# ✅ 직원 목록
@app.get("/staff")
def get_staff(department: str = Query(None)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT s.staffId, s.staffClass, s.userName, s.staffDepartment,
                IFNULL(SUM(p.participationRate), 0) AS totalParticipation,
                SUM(CASE WHEN p.leadTaskFlag = 1 THEN 1 ELSE 0 END) AS leadTaskCount
            FROM staff s
            LEFT JOIN participation p ON s.staffId = p.staffId
            WHERE s.staffDepartment = %s
            GROUP BY s.staffId, s.staffClass, s.userName, s.staffDepartment
        """, (department,))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.get("/participation/summary")
def get_total_participation(staffId: str = Query(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SUM(participationRate) AS total FROM participation WHERE staffId = %s", (staffId,))
        result = cursor.fetchone()
        return {"total": result["total"] or 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"참여율 합계 조회 실패: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# ✅ 사업 목록
@app.get("/projects")
def get_projects(department: str = Query(None)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT projectId, projectName FROM projects WHERE department = %s", (department,))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# ✅ FastAPI 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # ✅ 변경된 실행 방식

# ✅ 토큰 확인용 테스트 API
@app.get("/protected-api")
def protected_api(user=Depends(JWTBearer())):
    return {"message": f"안녕하세요, {user['username']}님! 권한: {user['role']}"}
