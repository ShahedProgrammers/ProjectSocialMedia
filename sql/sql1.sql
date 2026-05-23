create database SocialNetwork;

use SocialNetwork;

create table Users (
UserID int auto_increment primary key ,
Username varchar(50) unique not null,
Email varchar(100) unique not null,
PasswordHash varchar(255) not null,
Bio text ,
ProfilePic blob,
FaceID_Data text ,
 IsFaceIDEnabled BOOLEAN DEFAULT FALSE,
 CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
 
create table Posts (
PostID int auto_increment primary key ,
UserID int ,
Caption Text ,
MediaURL varchar(255) ,
MediaType enum('image' , 'video' , 'text') ,
CommentsEnabled boolean default true ,
ScheduledTime DATETIME NULL,
CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE);

create table Hashtags (
HashtagID INT AUTO_INCREMENT PRIMARY KEY,
TagName VARCHAR(50) UNIQUE NOT NULL);

create table PostHashtags (
PostID INT,
HashtagID INT,
PRIMARY KEY (PostID, HashtagID),
FOREIGN KEY (PostID) REFERENCES Posts(PostID) ON DELETE CASCADE,
FOREIGN KEY (HashtagID) REFERENCES Hashtags(HashtagID));

create table FollowsApp (
 FollowerID INT,
 FollowingID INT,
CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (FollowerID, FollowingID),
FOREIGN KEY (FollowerID) REFERENCES Users(UserID),
FOREIGN KEY (FollowingID) REFERENCES Users(UserID));

create table Comments (
CommentID INT AUTO_INCREMENT PRIMARY KEY,
PostID INT,
UserID INT,
Content TEXT NOT NULL,
CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (PostID) REFERENCES Posts(PostID) ON DELETE CASCADE,
FOREIGN KEY (UserID) REFERENCES Users(UserID));

create table Likes (
UserID INT,
PostID INT,
PRIMARY KEY (UserID, PostID),
FOREIGN KEY (UserID) REFERENCES Users(UserID),
FOREIGN KEY (PostID) REFERENCES Posts(PostID) ON DELETE CASCADE);

create table Logs (
LogID INT AUTO_INCREMENT PRIMARY KEY,
UserID INT,
ActionType enum('Login' , 'Register'),
LogTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (UserID) REFERENCES Users(UserID));


CREATE VIEW View_Explore AS
SELECT 
    p.PostID,
    u.Username,
    p.Caption,
    p.MediaURL,
    (SELECT COUNT(*) FROM Likes l WHERE l.PostID = p.PostID) AS LikeCount,
    (SELECT GROUP_CONCAT(h.TagName) FROM PostHashtags ph 
     JOIN Hashtags h ON ph.HashtagID = h.HashtagID WHERE ph.PostID = p.PostID) AS Tags
FROM Posts p
JOIN Users u ON p.UserID = u.UserID;



DELIMITER $$

DROP PROCEDURE IF EXISTS sp_register_user $$
CREATE PROCEDURE sp_register_user(
    IN p_email VARCHAR(100),
    IN p_username VARCHAR(50),
    IN p_password VARCHAR(255)
)
BEGIN
    IF p_email IS NULL OR LENGTH(TRIM(p_email)) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Email is required';
    END IF;

    IF p_username IS NULL OR LENGTH(TRIM(p_username)) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Username is required';
    END IF;

    IF p_password IS NULL OR LENGTH(p_password) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Password is required';
    END IF;

    IF EXISTS (SELECT 1 FROM Users WHERE Username = p_username) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Username already exists';
    END IF;

    IF EXISTS (SELECT 1 FROM Users WHERE Email = p_email) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Email already exists';
    END IF;

    INSERT INTO Users (Username, Email, PasswordHash)
    VALUES (p_username, p_email, SHA2(p_password, 256));

    INSERT INTO Logs (UserID, ActionType) VALUES (LAST_INSERT_ID(), 'Register');

    SELECT LAST_INSERT_ID() AS UserID;
END $$

DROP PROCEDURE IF EXISTS sp_login_user $$
CREATE PROCEDURE sp_login_user(
    IN p_username VARCHAR(50),
    IN p_password VARCHAR(255)
)
BEGIN
    DECLARE v_userId INT DEFAULT NULL;

    SELECT UserID
      INTO v_userId
      FROM Users
     WHERE Username = p_username
       AND PasswordHash = SHA2(p_password, 256)
     LIMIT 1;

    IF v_userId IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid username or password';
    END IF;

    INSERT INTO Logs (UserID, ActionType) VALUES (v_userId, 'Login');

    SELECT v_userId AS UserID;
END $$

DELIMITER ;
