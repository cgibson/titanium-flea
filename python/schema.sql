drop table if exists entries;
drop table if exists tags;
drop table if exists tagsXentries;

pragma foreign_keys = ON;

create table entries (
  id integer primary key autoincrement,
  title string not null,
  urltitle string not null,
  text string not null,
  html string not null,
  author string not null,
  created datetime not null,
  modified datetime not null,
  unique(urltitle)
);

/*
create table categories (
  id integer primary key autoincrement,
  name string not null
);
*/

create table tags (
  id integer primary key autoincrement,
  name string not null
);

create table tagsXentries (
  entryid integer not null,
  tagid integer not null,

  foreign key(entryid) references entries(id),
  foreign key(tagid) references tags(id),
  primary key(entryid, tagid)
);
