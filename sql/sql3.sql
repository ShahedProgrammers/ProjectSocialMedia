
USE SocialNetwork;

ALTER TABLE Users MODIFY COLUMN ProfilePic LONGBLOB;

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_get_user_profile $$
CREATE PROCEDURE sp_get_user_profile(
    IN p_userId INT
)
BEGIN
    SELECT UserID, Username, Email, Bio, IsFaceIDEnabled
      FROM Users
     WHERE UserID = p_userId
     LIMIT 1;
END $$

DROP PROCEDURE IF EXISTS sp_update_user_profile $$
CREATE PROCEDURE sp_update_user_profile(
    IN p_userId INT,
    IN p_bio TEXT,
    IN p_profilePic LONGBLOB
)
BEGIN
    IF p_userId IS NULL OR p_userId <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'UserId is required';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Users WHERE UserID = p_userId) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User not found';
    END IF;

    IF p_bio IS NOT NULL THEN
        UPDATE Users SET Bio = p_bio WHERE UserID = p_userId;
    END IF;

    IF p_profilePic IS NOT NULL THEN
        UPDATE Users SET ProfilePic = p_profilePic WHERE UserID = p_userId;
    END IF;

    SELECT 1 AS Ok;
END $$

DROP PROCEDURE IF EXISTS sp_update_faceid_settings $$
CREATE PROCEDURE sp_update_faceid_settings(
    IN p_userId INT,
    IN p_isEnabled BOOLEAN,
    IN p_faceData TEXT
)
BEGIN
    IF p_userId IS NULL OR p_userId <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'UserId is required';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Users WHERE UserID = p_userId) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User not found';
    END IF;

    UPDATE Users
       SET IsFaceIDEnabled = IFNULL(p_isEnabled, IsFaceIDEnabled),
           FaceID_Data     = IFNULL(p_faceData, FaceID_Data)
     WHERE UserID = p_userId;

    SELECT 1 AS Ok;
END $$


DROP PROCEDURE IF EXISTS sp_set_face_embedding $$
CREATE PROCEDURE sp_set_face_embedding(
    IN p_userId INT,
    IN p_faceData TEXT
)
BEGIN
    IF p_userId IS NULL OR p_userId <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'UserId is required';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Users WHERE UserID = p_userId) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User not found';
    END IF;

    UPDATE Users
       SET FaceID_Data = p_faceData
     WHERE UserID = p_userId;

    SELECT 1 AS Ok;
END $$

DROP PROCEDURE IF EXISTS sp_get_enabled_face_embeddings $$
CREATE PROCEDURE sp_get_enabled_face_embeddings()
BEGIN
    SELECT UserID, FaceID_Data
      FROM Users
     WHERE IsFaceIDEnabled = TRUE
       AND FaceID_Data IS NOT NULL
       AND LENGTH(TRIM(FaceID_Data)) > 0;
END $$

DROP PROCEDURE IF EXISTS sp_change_password $$
CREATE PROCEDURE sp_change_password(
    IN p_userId INT,
    IN p_currentPassword VARCHAR(255),
    IN p_newPassword VARCHAR(255)
)
BEGIN
    IF p_userId IS NULL OR p_userId <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'UserId is required';
    END IF;

    IF p_currentPassword IS NULL OR LENGTH(p_currentPassword) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Current password is required';
    END IF;

    IF p_newPassword IS NULL OR LENGTH(p_newPassword) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'New password is required';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM Users
         WHERE UserID = p_userId
           AND PasswordHash = SHA2(p_currentPassword, 256)
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Current password is incorrect';
    END IF;

    UPDATE Users
       SET PasswordHash = SHA2(p_newPassword, 256)
     WHERE UserID = p_userId;

    SELECT 1 AS Ok;
END $$

DROP PROCEDURE IF EXISTS sp_delete_account $$
CREATE PROCEDURE sp_delete_account(
    IN p_userId INT,
    IN p_password VARCHAR(255)
)
BEGIN
    IF p_userId IS NULL OR p_userId <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'UserId is required';
    END IF;

    IF p_password IS NULL OR LENGTH(p_password) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Password is required';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM Users
         WHERE UserID = p_userId
           AND PasswordHash = SHA2(p_password, 256)
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Password is incorrect';
    END IF;

    START TRANSACTION;

    DELETE FROM FollowsApp WHERE FollowerID = p_userId OR FollowingID = p_userId;
    DELETE FROM Likes      WHERE UserID = p_userId;
    DELETE FROM Comments   WHERE UserID = p_userId;
    DELETE FROM Logs       WHERE UserID = p_userId;

    DELETE FROM Users WHERE UserID = p_userId;

    COMMIT;

    SELECT 1 AS Ok;
END $$

DELIMITER ;
