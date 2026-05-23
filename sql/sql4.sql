USE SocialNetwork;

DELIMITER $$


DROP PROCEDURE IF EXISTS sp_get_user_summary $$
CREATE PROCEDURE sp_get_user_summary(
    IN p_userId INT
)
BEGIN
    SELECT
        u.UserID,
        u.Username,
        u.Bio,
        u.ProfilePic,
        (SELECT COUNT(*) FROM FollowsApp f WHERE f.FollowingID = u.UserID) AS FollowersCount,
        (SELECT COUNT(*) FROM FollowsApp f WHERE f.FollowerID = u.UserID) AS FollowingsCount
    FROM Users u
    WHERE u.UserID = p_userId
    LIMIT 1;
END $$

DROP PROCEDURE IF EXISTS sp_get_my_posts $$
CREATE PROCEDURE sp_get_my_posts(
    IN p_userId INT
)
BEGIN
    SELECT
        p.PostID,
        p.Caption,
        p.MediaURL,
        p.MediaType,
        p.CommentsEnabled,
        p.ScheduledTime,
        p.CreatedAt,
        (SELECT COUNT(*) FROM Likes l WHERE l.PostID = p.PostID) AS LikeCount
    FROM Posts p
    WHERE p.UserID = p_userId
    ORDER BY p.CreatedAt DESC;
END $$

DROP PROCEDURE IF EXISTS sp_get_post_comments $$
CREATE PROCEDURE sp_get_post_comments(
    IN p_postId INT
)
BEGIN
    SELECT
        c.CommentID,
        u.Username,
        c.Content,
        c.CreatedAt
    FROM Comments c
    JOIN Users u ON u.UserID = c.UserID
    WHERE c.PostID = p_postId
    ORDER BY c.CreatedAt DESC;
END $$



DELIMITER ;
