-- CREATE DATABASE IF NOT EXISTS `basketball_matches`;
-- USE `basketball_matches`;

--
-- Table structure for table `country`
--
CREATE TABLE country (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL
);
INSERT INTO country VALUES (253,'Afghanistan'),(254,'Albania'),(255,'Algeria'),(256,'Andorra'),(257,'Angola'),(258,'Anguilla'),(259,'Antigua & Barbuda'),(260,'Argentina'),(261,'Armenia'),(262,'Australia'),(263,'Austria'),(264,'Azerbaijan'),(265,'Bahamas'),(266,'Bahrain'),(267,'Bangladesh'),(268,'Barbados'),(269,'Belarus'),(270,'Belgium'),(271,'Belize'),(272,'Benin'),(273,'Bermuda'),(274,'Bhutan'),(275,'Bolivia'),(276,'Bosnia & Herzegovina'),(277,'Botswana'),(278,'Brazil'),(279,'Brunei Darussalam'),(280,'Bulgaria'),(281,'Burkina Faso'),(282,'Myanmar/Burma'),(283,'Burundi'),(284,'Cambodia'),(285,'Cameroon'),(286,'Canada'),(287,'Cape Verde'),(288,'Cayman Islands'),(289,'Central African Republic'),(290,'Chad'),(291,'Chile'),(292,'China'),(293,'Colombia'),(294,'Comoros'),(295,'Congo'),(296,'Costa Rica'),(297,'Croatia'),(298,'Cuba'),(299,'Cyprus'),(300,'Czech Republic'),(301,'Democratic Republic of the Congo'),(302,'Denmark'),(303,'Djibouti'),(304,'Dominican Republic'),(305,'Dominica'),(306,'Ecuador'),(307,'Egypt'),(308,'El Salvador'),(309,'Equatorial Guinea'),(310,'Eritrea'),(311,'Estonia'),(312,'Ethiopia'),(313,'Fiji'),(314,'Finland'),(315,'France'),(316,'French Guiana'),(317,'Gabon'),(318,'Gambia'),(319,'Georgia'),(320,'Germany'),(321,'Ghana'),(322,'Great Britain'),(323,'Greece'),(324,'Grenada'),(325,'Guadeloupe'),(326,'Guatemala'),(327,'Guinea'),(328,'Guinea-Bissau'),(329,'Guyana'),(330,'Haiti'),(331,'Honduras'),(332,'Hungary'),(333,'Iceland'),(334,'India'),(335,'Indonesia'),(336,'Iran'),(337,'Iraq'),(338,'Israel'),(339,'Italy'),(340,'Ivory Coast (Cote d''Ivoire)'),(341,'Jamaica'),(342,'Japan'),(343,'Jordan'),(344,'Kazakhstan'),(345,'Kenya'),(346,'Kosovo'),(347,'Kuwait'),(348,'Kyrgyzstan'),(349,'Laos'),(350,'Latvia'),(351,'Lebanon'),(352,'Lesotho'),(353,'Liberia'),(354,'Libya'),(355,'Liechtenstein'),(356,'Lithuania'),(357,'Luxembourg'),(358,'Republic of Macedonia'),(359,'Madagascar'),(360,'Malawi'),(361,'Malaysia'),(362,'Maldives'),(363,'Mali'),(364,'Malta'),(365,'Martinique'),(366,'Mauritania'),(367,'Mauritius'),(368,'Mayotte'),(369,'Mexico'),(370,'Moldova'),(371,'Monaco'),(372,'Mongolia'),(373,'Montenegro'),(374,'Montserrat'),(375,'Morocco'),(376,'Mozambique'),(377,'Namibia'),(378,'Nepal'),(379,'Netherlands'),(380,'New Zealand'),(381,'Nicaragua'),(382,'Niger'),(383,'Nigeria'),(384,'Korea, Democratic Republic of (North Korea)'),(385,'Norway'),(386,'Oman'),(387,'Pacific Islands'),(388,'Pakistan'),(389,'Panama'),(390,'Papua New Guinea'),(391,'Paraguay'),(392,'Peru'),(393,'Philippines'),(394,'Poland'),(395,'Portugal'),(396,'Puerto Rico'),(397,'Qatar'),(398,'Reunion'),(399,'Romania'),(400,'Russia'),(401,'Rwanda'),(402,'Saint Kitts and Nevis'),(403,'Saint Lucia'),(404,'Saint Vincent''s & Grenadines'),(405,'Samoa'),(406,'Sao Tome and Principe'),(407,'Saudi Arabia'),(408,'Senegal'),(409,'Serbia'),(410,'Seychelles'),(411,'Sierra Leone'),(412,'Singapore'),(413,'Slovak Republic (Slovakia)'),(414,'Slovenia'),(415,'Solomon Islands'),(416,'Somalia'),(417,'South Africa'),(418,'Korea, Republic of (South Korea)'),(419,'South Sudan'),(420,'Spain'),(421,'Sri Lanka'),(422,'Sudan'),(423,'Suriname'),(424,'Swaziland'),(425,'Sweden'),(426,'Switzerland'),(427,'Syria'),(428,'Tajikistan'),(429,'Tanzania'),(430,'Thailand'),(431,'Timor Leste'),(432,'Togo'),(433,'Trinidad & Tobago'),(434,'Tunisia'),(435,'Turkey'),(436,'Turkmenistan'),(437,'Turks & Caicos Islands'),(438,'Uganda'),(439,'Ukraine'),(440,'United Arab Emirates'),(441,'USA'),(442,'Uruguay'),(443,'Uzbekistan'),(444,'Vatican City'),(445,'Venezuela'),(446,'Vietnam'),(447,'Yemen'),(448,'Zambia'),(449,'Zimbabwe');

--
-- Table structure for table `match_format`
--
CREATE TABLE match_format (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL
);
INSERT INTO match_format VALUES (2,'Player match'),(3,'Team match');

--
-- Table structure for table `tournament_format`
--
CREATE TABLE tournament_format (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL
);
INSERT INTO tournament_format VALUES (1,'Knockout'),(2,'League');

--
-- Table structure for table `team`
--
CREATE TABLE team (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  CONSTRAINT name_UNIQUE UNIQUE (name)
);

--
-- Table structure for table `player`
--
CREATE TABLE player (
  id SERIAL PRIMARY KEY,
  first_name VARCHAR NOT NULL,
  second_name VARCHAR NOT NULL,
  team_id INTEGER DEFAULT NULL,
  country_id INTEGER DEFAULT NULL,
  CONSTRAINT fk_player_country1 FOREIGN KEY (country_id) REFERENCES country (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT fk_player_team1 FOREIGN KEY (team_id) REFERENCES team (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

--
-- Table structure for table `match`
--
CREATE TABLE match (
  id SERIAL PRIMARY KEY,
  title VARCHAR NOT NULL,
  played_at DATE NOT NULL,
  match_format_id INTEGER NOT NULL,
  CONSTRAINT fk_match_match_format1 FOREIGN KEY (match_format_id) REFERENCES match_format (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

--
-- Table structure for table `tournament`
--
CREATE TABLE tournament (
  id SERIAL PRIMARY KEY,
  title VARCHAR NOT NULL,
  prize VARCHAR NOT NULL,
  tournament_format_id INTEGER NOT NULL,
  winner INTEGER DEFAULT NULL,
  CONSTRAINT fk_tournament_player1 FOREIGN KEY (winner) REFERENCES player (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT fk_tournament_tournament_format1 FOREIGN KEY (tournament_format_id) REFERENCES tournament_format (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

--
-- Table structure for table `users`
--
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR NOT NULL,
  password VARCHAR NOT NULL,
  role VARCHAR NOT NULL,
  name VARCHAR NOT NULL
  CONSTRAINT email_UNIQUE UNIQUE (email)
);

--
-- Table structure for table `matchups`
--
CREATE TABLE matchups (
  id SERIAL PRIMARY KEY,
  tournament_id INTEGER NOT NULL,
  played_at DATE NOT NULL,
  tournament_phase INTEGER NOT NULL,
  player_one INTEGER DEFAULT NULL,
  player_two INTEGER DEFAULT NULL,
  player_one_score INTEGER DEFAULT NULL,
  player_two_score INTEGER DEFAULT NULL,
  CONSTRAINT fk_game_tournament1 FOREIGN KEY (tournament_id) REFERENCES tournament (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT fk_round_player1 FOREIGN KEY (player_one) REFERENCES player (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT fk_round_player2 FOREIGN KEY (player_two) REFERENCES player (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

--
-- Table structure for table `team_match_detail`
--
CREATE TABLE team_match_detail (
  match_id INTEGER,
  team_id INTEGER,
  score INTEGER DEFAULT NULL,
  CONSTRAINT fk_match_detail_copy1_team1 FOREIGN KEY (team_id) REFERENCES team (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT fk_match_detail_match10 FOREIGN KEY (match_id) REFERENCES match (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT pk_team_match_detail PRIMARY KEY (match_id, team_id)
);

--
-- Table structure for table `player_match_detail`
--
CREATE TABLE player_match_detail (
  player_id INTEGER,
  match_id INTEGER,
  score INTEGER DEFAULT NULL,
  CONSTRAINT fk_match_detail_match1 FOREIGN KEY (match_id) REFERENCES match (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT fk_match_detail_player FOREIGN KEY (player_id) REFERENCES player (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT pk_player_match_detail PRIMARY KEY (player_id, match_id)
);