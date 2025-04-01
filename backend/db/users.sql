CREATE TABLE users (
    userId INT AUTO_INCREMENT PRIMARY KEY,   
    username VARCHAR(50) UNIQUE NOT NULL,   
    passwordHash VARCHAR(255) NOT NULL,      
    email VARCHAR(100) UNIQUE,               
    department VARCHAR(100),                 
    role ENUM('admin', 'manager') NOT NULL,  
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
);