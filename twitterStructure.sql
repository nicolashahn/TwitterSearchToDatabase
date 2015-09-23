# twitterStructure.sql
# modify IAC database for twitter insertions
/*
ALTER TABLE `iac`.`authors` 
ADD COLUMN `twitter_followers` MEDIUMINT(8) UNSIGNED NULL COMMENT '' AFTER `reputation`;
ALTER TABLE `iac`.`authors` 
ADD COLUMN `twitter_favorites` MEDIUMINT(8) UNSIGNED NULL COMMENT '' AFTER `twitter_followers`;

CREATE TABLE `iac`.`hashtags` (
  `dataset_id` TINYINT(3) UNSIGNED NOT NULL COMMENT '',
  `hashtag_id` INT(20) UNSIGNED NOT NULL COMMENT '',
  `hashtag_text` VARCHAR(140) NULL COMMENT '',
  PRIMARY KEY (`dataset_id`, `hashtag_id`)  COMMENT '');
  
CREATE TABLE `iac`.`tweets` (
  `dataset_id` TINYINT(3) UNSIGNED NOT NULL COMMENT '',
  `tweet_id` INT(20) UNSIGNED NOT NULL COMMENT '',
  `author_id` INT(10) UNSIGNED NOT NULL COMMENT '',
  `timestamp` DATETIME NOT NULL COMMENT '',
  `in_reply_to_author_id` INT(10) UNSIGNED NULL COMMENT '',
  `native_tweet_id` VARCHAR(30) NOT NULL COMMENT '',
  `text_id` INT(20) UNSIGNED NOT NULL COMMENT '',
  `retweets` MEDIUMINT(8) ZEROFILL NOT NULL COMMENT '',
  `favorites` MEDIUMINT(8) ZEROFILL NOT NULL COMMENT '',
  PRIMARY KEY (`dataset_id`, `tweet_id`)  COMMENT '',
  UNIQUE INDEX `tweet_id_UNIQUE` (`tweet_id` ASC)  COMMENT '',
  UNIQUE INDEX `text_id_UNIQUE` (`text_id` ASC)  COMMENT '',
  INDEX `t_auth_fk_idx` (`dataset_id` ASC, `author_id` ASC)  COMMENT '',
  INDEX `t_text_fk_idx` (`dataset_id` ASC, `text_id` ASC)  COMMENT '',
  CONSTRAINT `t_auth_fk`
    FOREIGN KEY (`dataset_id` , `author_id`)
    REFERENCES `iac`.`authors` (`dataset_id` , `author_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `t_text_fk`
    FOREIGN KEY (`dataset_id` , `text_id`)
    REFERENCES `iac`.`texts` (`dataset_id` , `text_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `t_dataset_fk`
    FOREIGN KEY (`dataset_id`)
    REFERENCES `iac`.`datasets` (`dataset_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
    
CREATE TABLE `iac`.`hashtag_relations` (
  `dataset_id` TINYINT(3) UNSIGNED NOT NULL COMMENT '',
  `tweet_id` INT(20) UNSIGNED NOT NULL COMMENT '',
  `hashtag_id` INT(20) UNSIGNED NOT NULL COMMENT '',
  PRIMARY KEY (`dataset_id`, `tweet_id`, `hashtag_id`)  COMMENT '',
  INDEX `tweet_fk_idx` (`dataset_id` ASC, `tweet_id` ASC)  COMMENT '',
  INDEX `hashtag_fk_idx` (`dataset_id` ASC, `hashtag_id` ASC)  COMMENT '',
  CONSTRAINT `hr_dataset_fk`
    FOREIGN KEY (`dataset_id`)
    REFERENCES `iac`.`datasets` (`dataset_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `hr_tweet_fk`
    FOREIGN KEY (`dataset_id` , `tweet_id`)
    REFERENCES `iac`.`tweets` (`dataset_id` , `tweet_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `hr_hashtag_fk`
    FOREIGN KEY (`dataset_id` , `hashtag_id`)
    REFERENCES `iac`.`hashtags` (`dataset_id` , `hashtag_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE TABLE `iac`.`user_mentions` (
  `dataset_id` TINYINT(3) UNSIGNED NOT NULL COMMENT '',
  `user_mention_id` INT(20) UNSIGNED NOT NULL COMMENT '',
  `tweet_id` INT(20) UNSIGNED NOT NULL COMMENT '',
  `author_id` INT(20) UNSIGNED NOT NULL COMMENT '',
  PRIMARY KEY (`dataset_id`, `user_mention_id`)  COMMENT '',
  UNIQUE INDEX `user_mention_id_UNIQUE` (`user_mention_id` ASC)  COMMENT '',
  INDEX `um_tweet_fk_idx` (`tweet_id` ASC, `dataset_id` ASC)  COMMENT '',
  INDEX `um_authour_fk_idx` (`dataset_id` ASC, `author_id` ASC)  COMMENT '',
  CONSTRAINT `um_dataset_fk`
    FOREIGN KEY (`dataset_id`)
    REFERENCES `iac`.`datasets` (`dataset_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `um_tweet_fk`
    FOREIGN KEY (`tweet_id` , `dataset_id`)
    REFERENCES `iac`.`tweets` (`tweet_id` , `dataset_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `um_authour_fk`
    FOREIGN KEY (`dataset_id` , `author_id`)
    REFERENCES `iac`.`authors` (`dataset_id` , `author_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
    
insert into datasets values(7,'twitter','https://twitter.com/', '144-character limited messages');

ALTER TABLE `iac`.`hashtag_relations` 
ADD COLUMN `hashtag_relation_id` INT(20) UNSIGNED NOT NULL COMMENT '' AFTER `dataset_id`,
DROP PRIMARY KEY,
ADD PRIMARY KEY (`dataset_id`, `hashtag_relation_id`)  COMMENT '';

alter table user_mentions modify author_id int(10) unsigned not null;

alter table tweets add in_reply_to_tweet_id int(20) unsigned;

alter table tweets add in_reply_to_native_tweet_id varchar(30);

ALTER TABLE `iac`.`tweets` 
ADD UNIQUE INDEX `native_tweet_id_UNIQUE` (`native_tweet_id` ASC)  COMMENT '';

*/
