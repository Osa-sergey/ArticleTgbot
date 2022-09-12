# Article-tgbot

## Для чего создано

Приложение представляет из себя Telegram бота для рассылки таргетированных вакансий 
студентам вузов. Бот поддерживает две основные роли: администратор (сотрудник центра карьеры)
 публикующий вакансии от партнеров вуза, студент вуза, который хочет получать актуальную информацию 
о стажировках и предложениях в сфере его рабочей деятельности или интересов. Для того, чтобы 
определить какие вакансии подходят каждому конкретному пользователю на пост при публикации 
навешиваются теги, соответствующие тематике вакансии. Если хотя бы один тег у поста совпадает с тегами, 
выбранными студентом, то данный пост с вакансией показывается студенту.

## Основные возможности

- Рассылка постов всем студентам в независимости от их выбранных тегов при помощи указания для статьи 
тега из переменной `TAG_FOR_ALL_STUDENTS`.
- Выбор нескольких тегов в каждой категории.
- Автоматическое формирование клавиатуры с тегами на основе данных из бд.
- Возможность редактирования поста до момента его публикации.
- Проверка наличия тегов у публикуемого поста и предупреждение в случае их отсутствия.
- Возможность публиковать как текстовые посты при помощи команды `/text `, так и посты с картинками.
- При смене выбранных студентом тегов отображаются подходящие посты за 3 последних месяца.
- Редактирование и публикация постов идет независимо для каждого из администраторов.

## Как запустить

> **Note:** Для любого из способов. Чтобы комады в боте отображались в меню пользователя необходимо 
настроить их в BotFather. Список команд:
> - `tags`
> - `student_number`
> - `start`
> - `help`

### Переменные окружения 

Данные переменные должны быть `ОБЯЗАТЕЛЬНО` заполнены:

- `BOT_TOKEN` - Токен TelegramAPI получаемый у BotFather.
- `DB_PASSWORD` - Пароль пользователя базы данных.
- `DB_HOST` - Host базы данных.
- `DB_NAME` - Название базы данных.
- `ID` - Уникальный идентификатор экземпляра. На его основе 
формируется название схемы для БД, он проставляется в метриках и логах.
По умолчанию `target_article` 

---
`НЕОБЯЗАТЕЛЬНЫЕ`:
- `TAG_FOR_ALL_STUDENTS` - Название тега для рассылки поста всем студентам. По умолчанию `Разослать всем`
- `TAG_OTHER` - Регулярное выражение для тега "другое" в категориях и для названия категории. По умолчанию `^[А-Яа-я a-zA-Z]*([Д|д]ругое)$` 
Данный тег привязывается к низу клавиатуры.

### Docker
#### Образ и сборка

Для того, чтобы воспользоваться ботом можно использовать готовый docker образ из репозитория:

```sh
    docker pull osasergey/article_tgbot:{dev_}compose-*
```
Либо создать новый образ при помощи Dockerfile в  `article_tgbot/`

#### Запуск
Минимальная конфигурация для запуска в docker-compose выглядит следующим образом:

```sh
  version: '3.1'
services:
  db:
    image: postgres
    restart: always
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=1234
      - POSTGRES_DB=hr_center
    volumes:
      - db_volume:/var/lib/postgresql/data
      - ./db.sql:/docker-entrypoint-initdb.d/db.sql


  article_bot:
    image: osasergey/article_tgbot
    restart: always
    depends_on:
      - db
    ports:
      - "8080:8080"
    environment:
      - BOT_TOKEN=
      - DB_PASSWORD=1234
      - DB_HOST=db
      - DB_NAME=hr_center
      - ID=target_article
    volumes:
      - ./res:/app/article_tgbot/res

volumes:
  db_volume:
```

для запуска:

```sh
docker compose up
```

#### Volumes

В файле `db.sql` размещен скрипт инициализации базы данных и создания всех необходимых функций 
и триггеров.
---
Для корректной работы необходимо составить несколько файлов конфигурации:

- `res/new_admins.yaml` Представляет из себя список telegramID администраторов бота.
Нужен для разграничения доступа.  
- `res/new_tags.yaml` Представляет из себя список категорий и соответсвующих им тегов.
Формирует клавиатуру для маркировки постов и выбора подходящих тегов студентами.

> **Note:** теги в системе являются уникальными объектами в рамках всех категорий. Для использования 
> тегов, схожих по названию, необходимо использовать уникальный префикс или суффикс.
> 
>**Пример:** подробнее данный пример смотрите в разделе `Переменные окружения`
> - IT:
>   - IT Другое
> - Экономика:
>   - Экономика другое
>
> Для студентов не отображается тег `TAG_FOR_ALL_STUDENTS`, а так же удаляется категория в которой 
> он содержится, в случае если больше тегов в данной категории нет.

Оба файла применяются при каждом старте бота, что дает возможность добавлять данные в списки
администраторов и теги. 
Примеры данных файлов можно найти в репозитории по пути `article_tgbot/res`.

### Руками 

Для запуска руками необходимо выполнить команду:

```sh
pip install -r article_tgbot/requirements.txt 
```
После чего прописать переменные окружения в `article_tgbot/src/settings/settings.py`.
Подробнее о переменных окружения смотрите выше. Потом заполните файлы в `article_tgbot/res`
в соответствии с вашими данными. Конфигурация dev окружения находится в `dev_env.yaml`.
Для PyCharm можно импортировать конфигурацию запуска из папки `dev.run` или запустить ее 
командой: 
```sh
docker compose up -f dev_env.yaml
```
Далее можно запускать бота:
```sh
python article_tgbot/src/bot.py
```