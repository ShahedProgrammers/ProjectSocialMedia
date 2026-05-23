
USE SocialNetwork;
DELIMITER $$


DROP PROCEDURE IF EXISTS sp_get_explore_feed $$
CREATE PROCEDURE sp_get_explore_feed(
    IN p_viewerUserId INT
)
BEGIN
   
    SELECT
        v.PostID,
        p.UserID AS AuthorUserID,
        v.Username AS AuthorUsername,
        u.ProfilePic,
        p.Caption,
        p.MediaURL,
        p.MediaType,
        p.CreatedAt,
        p.CommentsEnabled,
        v.LikeCount,
        v.Tags,
        IF(p_viewerUserId IS NULL, 0,
            EXISTS(SELECT 1 FROM Likes l WHERE l.PostID = v.PostID AND l.UserID = p_viewerUserId)
        ) AS IsLiked
    FROM View_Explore v
    JOIN Posts p ON p.PostID = v.PostID
    JOIN Users u ON u.UserID = p.UserID
    WHERE p.ScheduledTime IS NULL OR p.ScheduledTime <= NOW()
    ORDER BY p.CreatedAt DESC;
END $$

DROP PROCEDURE IF EXISTS sp_like_post $$
CREATE PROCEDURE sp_like_post(
    IN p_userId INT,
    IN p_postId INT
)
BEGIN
    IF p_userId IS NULL OR p_userId <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'UserId is required';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Users WHERE UserID = p_userId) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User not found';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Posts WHERE PostID = p_postId) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Post not found';
    END IF;

    INSERT IGNORE INTO Likes (UserID, PostID) VALUES (p_userId, p_postId);

    SELECT
        (SELECT COUNT(*) FROM Likes l WHERE l.PostID = p_postId) AS LikeCount,
        1 AS IsLiked;
END $$

DROP PROCEDURE IF EXISTS sp_unlike_post $$
CREATE PROCEDURE sp_unlike_post(
    IN p_userId INT,
    IN p_postId INT
)
BEGIN
    IF p_userId IS NULL OR p_userId <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'UserId is required';
    END IF;

    DELETE FROM Likes WHERE UserID = p_userId AND PostID = p_postId;

    SELECT
        (SELECT COUNT(*) FROM Likes l WHERE l.PostID = p_postId) AS LikeCount,
        0 AS IsLiked;
END $$

DROP PROCEDURE IF EXISTS sp_add_comment $$
CREATE PROCEDURE sp_add_comment(
    IN p_userId INT,
    IN p_postId INT,
    IN p_content TEXT
)
BEGIN
    IF p_userId IS NULL OR p_userId <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'UserId is required';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Users WHERE UserID = p_userId) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User not found';
    END IF;

    IF p_content IS NULL OR LENGTH(TRIM(p_content)) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Comment content is required';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Posts WHERE PostID = p_postId) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Post not found';
    END IF;

    IF EXISTS (SELECT 1 FROM Posts WHERE PostID = p_postId AND CommentsEnabled = FALSE) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Comments are disabled for this post';
    END IF;

    INSERT INTO Comments (PostID, UserID, Content) VALUES (p_postId, p_userId, p_content);

    SELECT LAST_INSERT_ID() AS CommentID;
END $$

