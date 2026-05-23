use SocialNetwork;

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_create_post $$
CREATE PROCEDURE sp_create_post(
    IN p_userId INT,
    IN p_caption TEXT,
    IN p_mediaUrl VARCHAR(255),
    IN p_mediaType ENUM('image','video','text'),
    IN p_commentsEnabled BOOLEAN,
    IN p_scheduledTime DATETIME,
    IN p_tagsCsv TEXT
)
BEGIN
    DECLARE v_postId INT;
    DECLARE v_sched DATETIME;

    IF p_userId IS NULL OR p_userId <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'UserId is required';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM Users WHERE UserID = p_userId) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User not found';
    END IF;

    IF p_mediaType IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'MediaType is required';
    END IF;

    IF p_mediaType = 'text' THEN
        SET p_mediaUrl = NULL;
    ELSE
        IF p_mediaUrl IS NULL OR LENGTH(TRIM(p_mediaUrl)) = 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'MediaURL is required for image/video posts';
        END IF;
    END IF;

    IF p_scheduledTime IS NULL THEN
        SET v_sched = NULL;
    ELSEIF p_scheduledTime <= NOW() THEN
        SET v_sched = NULL;
    ELSE
        SET v_sched = p_scheduledTime;
    END IF;

    INSERT INTO Posts (UserID, Caption, MediaURL, MediaType, CommentsEnabled, ScheduledTime)
    VALUES (p_userId, p_caption, p_mediaUrl, p_mediaType, IFNULL(p_commentsEnabled, TRUE), v_sched);

    SET v_postId = LAST_INSERT_ID();

    IF p_tagsCsv IS NOT NULL AND LENGTH(TRIM(p_tagsCsv)) > 0 THEN
        BEGIN
            DECLARE v_rest TEXT;
            DECLARE v_piece TEXT;
            DECLARE v_comma INT;
            DECLARE v_tag VARCHAR(50);
            DECLARE v_hashtagId INT;

            SET v_rest = p_tagsCsv;

            tag_loop: WHILE v_rest IS NOT NULL AND LENGTH(v_rest) > 0 DO
                SET v_comma = LOCATE(',', v_rest);
                IF v_comma = 0 THEN
                    SET v_piece = v_rest;
                    SET v_rest = '';
                ELSE
                    SET v_piece = SUBSTRING(v_rest, 1, v_comma - 1);
                    SET v_rest = SUBSTRING(v_rest, v_comma + 1);
                END IF;

                SET v_tag = TRIM(v_piece);
                IF v_tag IS NOT NULL AND LENGTH(v_tag) > 0 THEN
                    IF LENGTH(v_tag) > 50 THEN
                        SET v_tag = LEFT(v_tag, 50);
                    END IF;

                    INSERT IGNORE INTO Hashtags (TagName) VALUES (v_tag);
                    SELECT HashtagID INTO v_hashtagId FROM Hashtags WHERE TagName = v_tag LIMIT 1;
                    IF v_hashtagId IS NOT NULL THEN
                        INSERT IGNORE INTO PostHashtags (PostID, HashtagID) VALUES (v_postId, v_hashtagId);
                    END IF;
                END IF;
            END WHILE;
        END;
    END IF;

    SELECT v_postId AS PostID;
END $$

DELIMITER ;