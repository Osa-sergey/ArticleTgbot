-- Создание базы. 
CREATE SCHEMA target_article;
SET SCHEMA 'target_article';
create table student
(
telegram_id int8 PRIMARY KEY,
university_id int4 CHECK ( university_id >= 1000000 AND university_id <= 10000000 )
);

create table tag
(
tag_name varchar primary key,
category varchar
);

create table students_to_tags
(
student_id int8 REFERENCES student,
tag_name_id varchar REFERENCES tag,
primary key (student_id, tag_name_id)
);

create table admins (
id int8 primary key
);

create table article (
id serial primary key,
text text not null,
is_posted boolean DEFAULT false,
id_who_created int8 REFERENCES admins,
id_image varchar,
date timestamptz DEFAULT NOW()
);

create table tags_to_articles (
article_id integer REFERENCES article,
tag_name_id varchar REFERENCES tag,
primary key (article_id, tag_name_id)
);
-- Функции и триггеры
CREATE OR REPLACE FUNCTION can_we_post_article() RETURNS trigger AS $can_we_post$
BEGIN
IF NOT old.is_posted THEN
    IF NOT EXISTS( SELECT 1 FROM tags_to_articles
    WHERE article_id = new.id) THEN
        RAISE EXCEPTION 'у статьи нет тегов';
    END IF;
END IF;
RETURN new;
END;
$can_we_post$ LANGUAGE plpgsql;


CREATE TRIGGER can_we_post BEFORE UPDATE OF is_posted ON article
FOR EACH ROW EXECUTE PROCEDURE can_we_post_article();

CREATE OR REPLACE FUNCTION  get_students_for_article(IN new_article_id integer)
RETURNS TABLE(telegram_ids int8)
LANGUAGE sql
AS $$
SELECT DISTINCT telegram_id
FROM
student AS stud
INNER JOIN students_to_tags AS stt ON stud.telegram_id = stt.student_id
INNER JOIN tags_to_articles AS att ON stt.tag_name_id = att.tag_name_id
WHERE att.article_id = new_article_id
$$;

CREATE OR REPLACE FUNCTION  get_articles_for_student(IN student_telegram_id int8)
RETURNS TABLE(text text, id_image varchar)
LANGUAGE sql
AS $$
SELECT DISTINCT ON (art.date) art.text, art.id_image
FROM article AS art
INNER JOIN tags_to_articles AS att ON art.id = att.article_id
INNER JOIN students_to_tags AS stt ON att.tag_name_id = stt.tag_name_id
WHERE stt.student_id = student_telegram_id
AND art.is_posted
AND CURRENT_TIMESTAMP <= (art.date + interval '3 month')
ORDER BY art.date
$$;

CREATE OR REPLACE FUNCTION  set_tag_to_student(IN student_telegram_id int8, IN tag_name varchar)
RETURNS void
AS $$
    BEGIN
        IF EXISTS (SELECT 1 FROM students_to_tags AS stt
                   WHERE stt.student_id = student_telegram_id AND stt.tag_name_id = tag_name) THEN
            DELETE FROM students_to_tags
            WHERE student_id = student_telegram_id AND tag_name_id = tag_name;
        ELSE
            INSERT INTO students_to_tags VALUES (student_telegram_id, tag_name);
        END IF;
    END;
    $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION  set_tag_to_article(IN approp_article_id int4, IN tag_name varchar)
RETURNS void
AS $$
    BEGIN
        IF EXISTS (SELECT 1 FROM tags_to_articles AS tta
                   WHERE tta.article_id = approp_article_id AND tta.tag_name_id = tag_name) THEN
            DELETE FROM tags_to_articles
            WHERE article_id = approp_article_id AND tag_name_id = tag_name;
        ELSE
            INSERT INTO tags_to_articles VALUES (approp_article_id, tag_name);
        END IF;
    END;
   $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION  set_text_and_img_to_article(IN publisher_id int4,
                                                       IN article_text text,
                                                       IN img_id varchar)
RETURNS void
AS $$
    DECLARE
        article_id int4;
    BEGIN
        article_id = (SELECT id FROM article
                      WHERE id_who_created = publisher_id AND is_posted = FALSE
                      ORDER BY date
                      LIMIT 1);
        IF article_id IS NOT NULL THEN
            IF  img_id <> '' THEN
                UPDATE article SET(text, id_image) = (article_text, img_id)
                WHERE id = article_id;
            ELSE
                UPDATE article AS a SET text = article_text
                WHERE id = article_id;
            END IF;
        ELSE
            INSERT INTO article (text, id_who_created, id_image) VALUES (article_text, publisher_id, img_id);
        END IF;
    END;

   $$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION  post_article(IN publisher_id int8)
RETURNS TABLE(id int4, text text, id_image varchar)
AS $$
    DECLARE
        article_id int4;
    BEGIN
        SELECT sa.id into article_id FROM article AS sa
                      WHERE is_posted = FALSE AND id_who_created = publisher_id
                      ORDER BY date
                      LIMIT 1;
        RETURN QUERY UPDATE article AS ua
        SET is_posted = true
        WHERE ua.id = article_id
        RETURNING article_id, ua.text, ua.id_image;
    END;
$$ LANGUAGE plpgsql;
