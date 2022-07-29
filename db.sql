-- Создание базы. 
CREATE SCHEMA target_article;

create table target_article.student
(
telegram_id int8 PRIMARY KEY,
university_id int4 CHECK ( university_id >= 1000000 AND university_id <= 10000000 )
);

create table target_article.tag
(
tag_name varchar primary key,
category varchar
);

create table target_article.students_to_tags
(
student_id int8 REFERENCES target_article.student,
tag_name_id varchar REFERENCES target_article.tag,
primary key (student_id, tag_name_id)
);

create table target_article.admins (
id int8 primary key
);

create table target_article.article (
id serial primary key,
text text not null,
is_posted boolean DEFAULT false,
id_who_created int8 REFERENCES target_article.admins,
id_image varchar,
date timestamptz DEFAULT NOW()
);

create table target_article.tags_to_articles (
article_id integer REFERENCES target_article.article,
tag_name_id varchar REFERENCES target_article.tag,
primary key (article_id, tag_name_id)
);
-- Функции и триггеры
CREATE OR REPLACE FUNCTION target_article.can_we_post_article() RETURNS trigger AS $can_we_post$
BEGIN
IF NOT old.is_posted THEN
    IF NOT EXISTS( SELECT 1 FROM target_article.tags_to_articles
    WHERE article_id = new.id) THEN
        RAISE EXCEPTION 'у статьи нет тегов';
    END IF;
END IF;
RETURN new;
END;
$can_we_post$ LANGUAGE plpgsql;


CREATE TRIGGER can_we_post BEFORE UPDATE OF is_posted ON target_article.article
FOR EACH ROW EXECUTE PROCEDURE target_article.can_we_post_article();

CREATE OR REPLACE FUNCTION  target_article.get_students_for_article(IN new_article_id integer)
RETURNS TABLE(telegram_ids int8)
LANGUAGE sql
AS $$
SELECT DISTINCT telegram_id
FROM
target_article.student AS stud
INNER JOIN target_article.students_to_tags AS stt ON stud.telegram_id = stt.student_id
INNER JOIN target_article.tags_to_articles AS att ON stt.tag_name_id = att.tag_name_id
WHERE att.article_id = new_article_id
$$;

CREATE OR REPLACE FUNCTION  target_article.get_articles_for_student(IN student_telegram_id int8)
RETURNS TABLE(text text, id_image varchar)
LANGUAGE sql
AS $$
SELECT DISTINCT ON (art.date) art.text, art.id_image
FROM target_article.article AS art
INNER JOIN target_article.tags_to_articles AS att ON art.id = att.article_id
INNER JOIN target_article.students_to_tags AS stt ON att.tag_name_id = stt.tag_name_id
WHERE stt.student_id = student_telegram_id
AND art.is_posted
AND CURRENT_TIMESTAMP <= (art.date + interval '3 month')
ORDER BY art.date
$$;

CREATE OR REPLACE FUNCTION  target_article.set_tag_to_student(IN student_telegram_id int8, IN tag_name varchar)
RETURNS void
AS $$
    BEGIN
        IF EXISTS (SELECT 1 FROM target_article.students_to_tags AS stt
                   WHERE stt.student_id = student_telegram_id AND stt.tag_name_id = tag_name) THEN
            DELETE FROM target_article.students_to_tags
            WHERE student_id = student_telegram_id AND tag_name_id = tag_name;
        ELSE
            INSERT INTO target_article.students_to_tags VALUES (student_telegram_id, tag_name);
        END IF;
    END;
    $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION  target_article.set_tag_to_article(IN approp_article_id int4, IN tag_name varchar)
RETURNS void
AS $$
    BEGIN
        IF EXISTS (SELECT 1 FROM target_article.tags_to_articles AS tta
                   WHERE tta.article_id = approp_article_id AND tta.tag_name_id = tag_name) THEN
            DELETE FROM target_article.tags_to_articles
            WHERE article_id = approp_article_id AND tag_name_id = tag_name;
        ELSE
            INSERT INTO target_article.tags_to_articles VALUES (approp_article_id, tag_name);
        END IF;
    END;
   $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION  target_article.set_text_and_img_to_article(IN publisher_id int4,
                                                       IN article_text text,
                                                       IN img_id varchar)
RETURNS void
AS $$
    DECLARE
        article_id int4;
    BEGIN
        article_id = (SELECT id FROM target_article.article
                      WHERE id_who_created = publisher_id AND is_posted = FALSE
                      ORDER BY date
                      LIMIT 1);
        IF article_id IS NOT NULL THEN
            IF  img_id <> '' THEN
                UPDATE target_article.article SET(text, id_image) = (article_text, img_id)
                WHERE id = article_id;
            ELSE
                UPDATE target_article.article AS a SET text = article_text
                WHERE id = article_id;
            END IF;
        ELSE
            INSERT INTO target_article.article (text, id_who_created, id_image) VALUES (article_text, publisher_id, img_id);
        END IF;
    END;

   $$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION  target_article.post_article(IN publisher_id int8)
RETURNS TABLE(id int4, text text, id_image varchar)
AS $$
    DECLARE
        article_id int4;
    BEGIN
        SELECT sa.id into article_id FROM target_article.article AS sa
                      WHERE is_posted = FALSE AND id_who_created = publisher_id
                      ORDER BY date
                      LIMIT 1;
        RETURN QUERY UPDATE target_article.article AS ua
        SET is_posted = true
        WHERE ua.id = article_id
        RETURNING article_id, ua.text, ua.id_image;
    END;
$$ LANGUAGE plpgsql;
