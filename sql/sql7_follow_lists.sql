USE SocialNetwork;

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_get_followers $$
CREATE PROCEDURE sp_get_followers(
    IN p_userId INT,
    IN p_viewerUserId INT
)
BEGIN
    SELECT
        u.UserID,
        u.Username,
        u.ProfilePic,
        IF(p_viewerUserId IS NULL, 0,
            EXISTS(
                SELECT 1 FROM FollowsApp f
                 WHERE f.FollowerID = p_viewerUserId
                   AND f.FollowingID = u.UserID
            )
        ) AS IsFollowing
    FROM FollowsApp f
    JOIN Users u ON u.UserID = f.FollowerID
    WHERE f.FollowingID = p_userId
    ORDER BY u.Username;
END $$

DROP PROCEDURE IF EXISTS sp_get_followings $$
CREATE PROCEDURE sp_get_followings(
    IN p_userId INT,
    IN p_viewerUserId INT
)
BEGIN
    SELECT
        u.UserID,
        u.Username,
        u.ProfilePic,
        IF(p_viewerUserId IS NULL, 0,
            EXISTS(
                SELECT 1 FROM FollowsApp f
                 WHERE f.FollowerID = p_viewerUserId
                   AND f.FollowingID = u.UserID
            )
        ) AS IsFollowing
    FROM FollowsApp f
    JOIN Users u ON u.UserID = f.FollowingID
    WHERE f.FollowerID = p_userId
    ORDER BY u.Username;
END $$

DELIMITER ;
