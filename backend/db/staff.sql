CREATE TABLE staff (
    staffId VARCHAR(50) PRIMARY KEY,  -- 사번 (기본 키)
    userName VARCHAR(100) NOT NULL,   -- 직원 이름
    department VARCHAR(100) NOT NULL  -- 소속 부서
);
