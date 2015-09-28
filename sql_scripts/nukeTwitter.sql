# nuke the database of any twitter material
use iac;
delete from hashtag_relations where dataset_id = 7;
delete from user_mentions where dataset_id = 7;
delete from tweets where dataset_id = 7;
delete from authors where dataset_id = 7;
delete from hashtags where dataset_id = 7;
delete from texts where dataset_id = 7;

