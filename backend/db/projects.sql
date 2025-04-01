CREATE TABLE projects (
    projectId INT PRIMARY KEY AUTO_INCREMENT,  -- 사업 ID (자동 증가)
    projectName VARCHAR(255) UNIQUE NOT NULL,  -- 사업명 (중복 방지)
    department VARCHAR(100) NOT NULL           -- 담당 부서
);

