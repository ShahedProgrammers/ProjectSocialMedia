CREATE VIEW View_HomeFeed AS
SELECT 
    f.FollowerID,
    p.PostID,
    u.Username AS Author,
    p.Caption,
    p.MediaURL,
    p.CreatedAt
FROM followsapp f
JOIN Posts p ON f.FollowingID = p.UserID
JOIN Users u ON p.UserID = u.UserID
WHERE p.ScheduledTime IS NULL OR p.ScheduledTime <= NOW(); 



CREATE INDEX idx_hashtags_tagname ON Hashtags(TagName);

CREATE UNIQUE INDEX idx_users_username ON Users(Username);

CREATE INDEX idx_follows_followerid ON followsapp(FollowerID);

CREATE INDEX idx_posthashtags_postid ON PostHashtags(PostID);


USE SocialNetwork;

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_get_home_feed $$
CREATE PROCEDURE sp_get_home_feed(
    IN p_viewerUserId INT
)
BEGIN
    IF p_viewerUserId IS NULL OR p_viewerUserId <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Viewer userId is required';
    END IF;

    SELECT
        vh.PostID,
        p.UserID AS AuthorUserID,
        u.Username AS AuthorUsername,
        u.ProfilePic,
        p.Caption,
        p.MediaURL,
        p.MediaType,
        p.CreatedAt,
        p.CommentsEnabled,
        (SELECT COUNT(*) FROM Likes l WHERE l.PostID = p.PostID) AS LikeCount,
        (SELECT GROUP_CONCAT(h.TagName)
           FROM PostHashtags ph
           JOIN Hashtags h ON h.HashtagID = ph.HashtagID
          WHERE ph.PostID = p.PostID) AS Tags,
        EXISTS(
            SELECT 1 FROM Likes l
             WHERE l.PostID = p.PostID
               AND l.UserID = p_viewerUserId
        ) AS IsLiked
    FROM View_HomeFeed vh
    JOIN Posts p ON p.PostID = vh.PostID
    JOIN Users u ON u.UserID = p.UserID
    WHERE vh.FollowerID = p_viewerUserId
      AND (p.ScheduledTime IS NULL OR p.ScheduledTime <= NOW())
    ORDER BY p.CreatedAt DESC;
END $$

DROP PROCEDURE IF EXISTS sp_follow_user $$
CREATE PROCEDURE sp_follow_user(
    IN p_followerId INT,
    IN p_followingId INT
)
BEGIN
    IF p_followerId IS NULL OR p_followerId <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'FollowerId is required';
    END IF;

    IF p_followingId IS NULL OR p_followingId <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'FollowingId is required';
    END IF;

    IF p_followerId = p_followingId THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot follow yourself';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Users WHERE UserID = p_followingId) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Target user not found';
    END IF;

    INSERT IGNORE INTO FollowsApp (FollowerID, FollowingID) VALUES (p_followerId, p_followingId);

    SELECT
        (SELECT COUNT(*) FROM FollowsApp f WHERE f.FollowingID = p_followingId) AS FollowersCount,
        1 AS IsFollowing;
END $$

DROP PROCEDURE IF EXISTS sp_unfollow_user $$
CREATE PROCEDURE sp_unfollow_user(
    IN p_followerId INT,
    IN p_followingId INT
)
BEGIN
    IF p_followerId IS NULL OR p_followerId <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'FollowerId is required';
    END IF;

    DELETE FROM FollowsApp WHERE FollowerID = p_followerId AND FollowingID = p_followingId;

    SELECT
        (SELECT COUNT(*) FROM FollowsApp f WHERE f.FollowingID = p_followingId) AS FollowersCount,
        0 AS IsFollowing;
END $$

DROP PROCEDURE IF EXISTS sp_is_following $$
CREATE PROCEDURE sp_is_following(
    IN p_followerId INT,
    IN p_followingId INT
)
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM FollowsApp f
         WHERE f.FollowerID = p_followerId
           AND f.FollowingID = p_followingId
    ) AS IsFollowing;
END $$

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
        ) AS IsLiked,
        IF(p_viewerUserId IS NULL, 0,
            EXISTS(
                SELECT 1 FROM FollowsApp fa
                 WHERE fa.FollowerID = p_viewerUserId
                   AND fa.FollowingID = p.UserID
            )
        ) AS IsFollowing
    FROM View_Explore v
    JOIN Posts p ON p.PostID = v.PostID
    JOIN Users u ON u.UserID = p.UserID
    WHERE p.ScheduledTime IS NULL OR p.ScheduledTime <= NOW()
    ORDER BY p.CreatedAt DESC;
END $$

DELIMITER ;
