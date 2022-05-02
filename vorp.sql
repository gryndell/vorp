PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE Control(
  Password varchar(80),
  Language char(2),
  Workstation char(8),
  url_input varchar(128),
  url_output varchar(128)
);
INSERT INTO Control VALUES(
  '$5$rounds=535000$mWznH9DhjR/41jbl$OHfW5.KXqkibFMQpK6Dx4IWSwnJIGLdYll42rytjxy3',
  'en',
  'Unknown',
  'http://localhost/testfile.json',
  'http://localhost/results.json'
);
CREATE TABLE Labels(
  Language char(2),
  Term varchar(20),
  Label varchar(20)
);
INSERT INTO Labels VALUES('en','Orders','Orders');
INSERT INTO Labels VALUES('en','Component','Component');
INSERT INTO Labels VALUES('en','Components','Components');
INSERT INTO Labels VALUES('en','Exit','Exit');
INSERT INTO Labels VALUES('en','Order Nbr','Order Nbr');
INSERT INTO Labels VALUES('en','Action','Action');
INSERT INTO Labels VALUES('en','Order ID','Order ID');
INSERT INTO Labels VALUES('en','Item Code','Item Code');
INSERT INTO Labels VALUES('en','Qty Open','Qty Open');
INSERT INTO Labels VALUES('th','Orders','สั่งงาน');
INSERT INTO Labels VALUES('th','Component','ส่วนประกอบ');
INSERT INTO Labels VALUES('th','Components','ส่วนประกอบ');
INSERT INTO Labels VALUES('th','Exit','ไปจาก');
INSERT INTO Labels VALUES('th','Order Nbr','สั่งงาน');
INSERT INTO Labels VALUES('th','Action','หนังบู๊');
INSERT INTO Labels VALUES('th','Order ID','ไอดี');
INSERT INTO Labels VALUES('th','Item Code','รหัสสินค้า');
INSERT INTO Labels VALUES('th','Qty Open','โควต้า');
CREATE TABLE operationHdr(
  toStation char(8),
  id char(8),
  nr char(18),
  op integer,
  product char(18),
  productDesc char(50),
  orderType char(8),
  qty real,
  receipt char(3),
  backflush char(3),
  qty_comp real,
  qty_rjct real
);
CREATE TABLE operationDtl(
  id char(8),
  op integer,
  component char(18),
  componentDesc char(50),
  qty real,
  task char(16),
  qty_done real
);
CREATE UNIQUE INDEX idx_langterm ON Labels(
  Language,
  Term
);
CREATE UNIQUE INDEX idx_idop ON operationHdr(
  id,
  op
);
CREATE UNIQUE INDEX idx_idopcomptask ON operationDtl(
  id,
  op,
  component,
  task
);
COMMIT;
