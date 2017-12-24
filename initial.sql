create database ytcrawler character set UTF8;

USE ytcrawler;

CREATE TABLE video (
    video_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(100),
    views INT NOT NULL,
    duration INT NOT NULL,
    video_url VARCHAR(100),
    thumb_url VARCHAR(200),
    thumb_path VARCHAR(200),
    full_thumb_url VARCHAR(200),
    full_thumb_path VARCHAR(200)
);
