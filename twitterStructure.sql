# twitterStructure.sql
# modify IAC database for twitter insertions

ALTER TABLE `iac`.`authors` 
ADD COLUMN `twitter_followers` MEDIUMINT(8) UNSIGNED NULL COMMENT '' AFTER `reputation`;

ALTER TABLE `iac`.`posts` 
ADD COLUMN `retweets` MEDIUMINT(8) UNSIGNED NULL COMMENT '' AFTER `votes`;

CREATE TABLE `iac`.`hashtags` (
  `dataset_id` TINYINT(3) UNSIGNED NOT NULL COMMENT '',
  `hashtag_id` INT(20) UNSIGNED NOT NULL COMMENT '',
  `hashtag_text` VARCHAR(140) NULL COMMENT '',
  PRIMARY KEY (`dataset_id`, `hashtag_id`)  COMMENT '');

CREATE TABLE `iac`.`hashtag_relations` (
  `dataset_id` TINYINT UNSIGNED NOT NULL COMMENT '',
  `hashtag_relation_id` INT(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '',
  `hashtag_id` INT(20) UNSIGNED NOT NULL COMMENT '',
  `post_id` INT(20) UNSIGNED NOT NULL COMMENT '',
  PRIMARY KEY (`dataset_id`, `hashtag_relation_id`)  COMMENT '',
  INDEX `hashtag_fk1_idx` (`dataset_id` ASC, `hashtag_id` ASC)  COMMENT '',
  INDEX `post_fk1_idx` (`dataset_id` ASC, `post_id` ASC)  COMMENT '',
  CONSTRAINT `hashtag_fk1`
    FOREIGN KEY (`dataset_id`,`hashtag_id`)
    REFERENCES `iac`.`hashtags` (`dataset_id`,`hashtag_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `post_fk1`
    FOREIGN KEY (`dataset_id`,`post_id`)
    REFERENCES `iac`.`posts` (`dataset_id`,`post_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE TABLE `iac`.`user_mentions` (
  `dataset_id` TINYINT(6) UNSIGNED NOT NULL COMMENT '',
  `user_mentions_id` INT(20) UNSIGNED NOT NULL COMMENT '',
  `post_id` INT(20) UNSIGNED NOT NULL COMMENT '',
  `author_id` INT(10) UNSIGNED NOT NULL COMMENT '',
  PRIMARY KEY (`dataset_id`, `user_mentions_id`)  COMMENT '',
  INDEX `author_fk1_idx` (`dataset_id` ASC, `author_id` ASC)  COMMENT '',
  INDEX `post_fk1_idx` (`dataset_id` ASC, `post_id` ASC)  COMMENT '',
  CONSTRAINT `author_fk1`
    FOREIGN KEY (`dataset_id` , `author_id`)
    REFERENCES `iac`.`authors` (`dataset_id` , `author_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `post_fk1`
    FOREIGN KEY (`dataset_id` , `post_id`)
    REFERENCES `iac`.`posts` (`dataset_id` , `post_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);