CREATE TABLE participation (
    staffId VARCHAR(20) NOT NULL,
    projectId VARCHAR(50) NOT NULL,
    participationRate FLOAT NOT NULL,
    leadTaskFlag BOOLEAN DEFAULT FALSE,
    createTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    updateTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (staffId, projectId),
    FOREIGN KEY (staffId) REFERENCES staff(staffId),
    FOREIGN KEY (projectId) REFERENCES projects(projectId)
);