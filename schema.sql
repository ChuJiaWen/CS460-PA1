CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Contains CASCADE;
DROP TABLE IF EXISTS Liked_By CASCADE;
DROP TABLE IF EXISTS Friends_Is_Friend CASCADE;
DROP TABLE IF EXISTS Comments_Leaves_Has CASCADE;
DROP TABLE IF EXISTS Tags_Associates CASCADE;
DROP TABLE IF EXISTS Photos CASCADE;
DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
    uid int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    first_name CHAR(50),
	last_name CHAR(50),
	hometown CHAR(50),
	gender CHAR(10),
    password varchar(255),
    DOB DATE,
    contribution integer DEFAULT 0,
    CONSTRAINT users_pk PRIMARY KEY (uid) );

CREATE TABLE Albums (
	aid int4 AUTO_INCREMENT,
	uid int4 NOT NULL,
	name VARCHAR(50),
	DOC DATE,
	FOREIGN KEY (uid) REFERENCES Users(uid),
    CONSTRAINT albums_pk PRIMARY KEY (aid));
    
CREATE TABLE Photos(
  pid int4 AUTO_INCREMENT,
  aid int4,
  uid int4,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (uid),
  FOREIGN KEY (aid) REFERENCES Albums(aid) ON DELETE CASCADE,
  FOREIGN KEY (uid) REFERENCES Users(uid),
  CONSTRAINT photos_pk PRIMARY KEY (pid));

INSERT INTO Users (efriends_is_friendmail, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
INSERT INTO Users (first_name, email, password) VALUES ('Anonymous','anonymous@bu.edu','123456');

CREATE TABLE Friends_Is_Friend (
	DOF DATE,
	fuid INTEGER NOT NULL,
	uid INTEGER NOT NULL,
	PRIMARY KEY (fuid,uid),
	FOREIGN KEY (uid) REFERENCES Users(uid) ON DELETE CASCADE,
	FOREIGN KEY (fuid) REFERENCES Users(uid) ON DELETE CASCADE);



CREATE TABLE Comments_Leaves_Has (
	cid int4 auto_increment,
	comment TEXT,
	date DATETIME,
	pid INTEGER NOT NULL,
	aid int4 NOT NULL,
	uid INTEGER,
	uname CHAR(50),
	PRIMARY KEY (cid),
	FOREIGN KEY (aid) REFERENCES Albums(aid) ON DELETE CASCADE,
	FOREIGN KEY (uid) REFERENCES Users(uid) ON DELETE NO ACTION,
	FOREIGN KEY (pid) REFERENCES Photos(pid) ON DELETE CASCADE);

CREATE TABLE Tags_Associates (
	tid int4 auto_increment,
	description CHAR(50),
	pid INTEGER,
    uid int4,
	PRIMARY KEY (tid));

CREATE TABLE Contains (
	pid INTEGER NOT NULL,
	aid INTEGER,
	PRIMARY KEY (pid,aid),

    FOREIGN KEY (aid) REFERENCES Albums(aid) ON DELETE CASCADE );


CREATE TABLE Liked_By(
    pid INTEGER NOT NULL,
    uid int4,
    uname CHAR(50),
    PRIMARY KEY (pid, uid),
    FOREIGN KEY (uid) REFERENCES Users(uid) ON DELETE CASCADE,
    FOREIGN KEY (pid) REFERENCES Photos(pid) ON DELETE CASCADE );
