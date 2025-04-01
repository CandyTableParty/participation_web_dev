CREATE TABLE participation (
    staffId VARCHAR(50) NOT NULL,
    userName VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    projectParticipationRate FLOAT(5,2) DEFAULT NULL,
    leadTaskCount INT DEFAULT NULL,

    -- 프로젝트 ID (사업 ID) 저장 컬럼 (VARCHAR로 변경됨)
    projectId1 VARCHAR(50) DEFAULT NULL,
    projectId2 VARCHAR(50) DEFAULT NULL,
    projectId3 VARCHAR(50) DEFAULT NULL,
    projectId4 VARCHAR(50) DEFAULT NULL,
    projectId5 VARCHAR(50) DEFAULT NULL,

    participationRate1 FLOAT(5,2) DEFAULT NULL,
    participationRate2 FLOAT(5,2) DEFAULT NULL,
    participationRate3 FLOAT(5,2) DEFAULT NULL,
    participationRate4 FLOAT(5,2) DEFAULT NULL,
    participationRate5 FLOAT(5,2) DEFAULT NULL,

    leadTaskFlag1 TINYINT(1) DEFAULT NULL,
    leadTaskFlag2 TINYINT(1) DEFAULT NULL,
    leadTaskFlag3 TINYINT(1) DEFAULT NULL,
    leadTaskFlag4 TINYINT(1) DEFAULT NULL,
    leadTaskFlag5 TINYINT(1) DEFAULT NULL,

    createTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    updateTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (staffId),

    -- projects 테이블과 외래키(Foreign Key) 관계 설정
    FOREIGN KEY (projectId1) REFERENCES projects(projectId),
    FOREIGN KEY (projectId2) REFERENCES projects(projectId),
    FOREIGN KEY (projectId3) REFERENCES projects(projectId),
    FOREIGN KEY (projectId4) REFERENCES projects(projectId),
    FOREIGN KEY (projectId5) REFERENCES projects(projectId)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;