ALTER TABLE inbox ADD encodingtype int DEFAULT '2';

ALTER TABLE inbox ADD read bool DEFAULT '1';

ALTER TABLE sent ADD encodingtype int DEFAULT '2';
