# Парсер книг с сайта tululu.org

## Запуск

- Скачайте код.
- Cоздайте файл `.env` в директории проекта, на основе файла `.env.example` командой 
(при необходимости скорректируйте значения переменных окружения):
```
cp .env.example .env
```
<details>
  <summary>Переменные окружения</summary>
  <pre>
    ROOT_PATH=downloads
    IMG_PATH=images
    BOOK_PATH=books
    SITE_URL_ROOT=https://tululu.org
    SITE_URI_TXT=txt.php
    TIMEOUT=10
    RETRY_COUNT=5
    STATUS_FORCE_LIST=429,500,502,503,504
    ALLOWED_METHODS=HEAD,GET,OPTIONS
  </pre>
</details>

- Установите актуальную версию poetry в `UNIX`-подобных дистрибутивах с помощью команды:
```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
```
или в `Windows Powershell`:
```
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
```
- Добавьте к переменной окружения `$PATH` команду poetry:
```
source $HOME/.poetry/bin
```
- Установите виртуальное окружение в директории с проектом командой:
```
poetry config virtualenvs.in-project true
```
- Установите все зависимости (для установки без dev зависимостей можно добавить аргумент `--no-dev`):
```
poetry install
```
- Активируйте виртуальное окружение командой: 
```
source .venv/bin/activate
```
- Запустите скрипт командой:
```
python3 tululu.py
```
- Есть возможность указать значения начального и конечного значения идентификатора книг через следующие опции:

- `-s` или `--start-id` c указанием начального значения идентификатора книги. По умолчанию значение равно 1.
- `-e` или `--end-id` c указанием конечного значения идентификатора книги. По умолчанию значение равно 10.
```
python3 tululu.py -s 50 -e 100
```
- Для запуска линтеров используем команду:
```
flake8 . && mypy . && isort .
```

## Цели проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [Devman](https://dvmn.org).
