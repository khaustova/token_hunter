
![Static Badge](https://img.shields.io/badge/Python-3.12.5-orange) ![Static Badge](https://img.shields.io/badge/Django-5.1-blue) ![Static Badge](https://img.shields.io/badge/Django_REST_framework-3.15.2-blue) ![Static Badge](https://img.shields.io/badge/Django_Telethon-1.4.0-blue) ![Static Badge](https://img.shields.io/badge/Celery-5.4.0-blue) ![Static Badge](https://img.shields.io/badge/Nodriver-0.36-blue) ![Static Badge](https://img.shields.io/badge/PostgreSQL-14.15-purple) ![Static Badge](https://img.shields.io/badge/Redis-6.0.16-purple) ![Static Badge](https://img.shields.io/badge/DEX_Screener_API-v1-purple)

**Token Hunter** – веб-приложение на Django для настраиваемой торговли токенами в сети Solana и парсинга топовых кошельков.

## Используемые сервисы

:gem:  [DEX Screener](https://dexscreener.com/) – получение данных о токенах и кошельках   
:shield: [RugCheck](https://rugcheck.xyz/) – оценка безопасности токена   
:bar_chart: [Getmoni](https://rugcheck.xyz/) – анализ активности по токену в X (Twitter)   

## Основные функции

:mag_right: Мониторинг токенов по фильтрам   
:zap: Мониторинг boosted токенов   
:shopping_cart: Эмуляция покупки токенов  
:gear: Настройка параметров для выбора токенов   
:robot: Покупка токенов через Maestro Sniper Bot в Telegram  
:chart_with_upwards_trend: Экспорт данных в Excel  
:detective: Парсинг топовых кошельков  

## Запуск

1. Клонируйте репозиторий проекта на свой компьютер:

```
git clone https://github.com/khaustova/muiv_timetable.git
```

2. Запустите приложение одним из двух способов:
<details>
  <summary>В Docker</summary>
  
  * Переименуйте файл `.env.example` в `.env` и добавьте свои данные.   
  
  * Запустите приложение с помощью команды:  
  
    ```
    docker-compose up --build
    ```
  
</details>  

<details>
  <summary>В виртуальном окружении</summary>

  * Убедитесь, что у вас установлены и запущены Redis и PostgreSQL.

  * Переименуйте файл `.env.example` в `.env` и добавьте свои данные.  

  * Создайте виртуальное окружение:
    

  ```
  python3 -m venv .venv
  ```

  * Активируйте виртуальное окружение:  

    * Для Linux/MacOS:  

    ```
    source .venv/bin/activate
    ```
   
    * Для Windows:  

    ```
    .venv\Scripts\activate
    ```

  * Установите необходимые библиотеки:

  ```
  pip install -r requirements.txt
  ```

  * Выполните миграции базы данных:
    

  ```
  python3 manage.py migrate
  ```

  * Запустите Celery:
  
  ```
  celery -A core worker -l info
  ```

  * Запустите сервер:

  ```
  python3 manage.py runserver
  ```
  
</details> 
  

3. Приложение будет доступно по адресу http://127.0.0.1:8000.  

## Настройка Telegram

Для автоматической покупки и продажи токенов, а также для взаимодействия с Telegram-каналом, требуется настроить интеграцию с Telegram.

#### Получение API ID и Hash

1. Перейдите на сайт https://my.telegram.org/auth.
2. Авторизуйтесь с номером телефона, который будете использовать для торговли.
3. Перейдите в **API development tools** и создайте новое приложение.
4. Скопируйте полученные значения `App api_id` и `App api_hash`.
5. Откройте файл `.env` и вставьте эти значения в соответствующие переменные:
    

```
TELETHON_API_ID=ваш_идентификатор
TELETHON_API_HASH=ваш_хэш
```

#### Авторизация в Telegram

1. Убедитесь, что в файле `.env` в переменной `TELEGRAM_PHONE_NUMBER` указан правильный номер телефона.
2. Выполните команду для авторизации:
    

```
python3 manage.py authtelegram
```

3. Следуйте инструкциям на экране для завершения процесса авторизации.

## Настройка Maestro Sniper Bot

Для автоматической покупки токенов необходимо настроить взаимодействие с ботом Maestro Sniper Bot в Telegram.

1. Найдите бота @MaestroSniperBot и начните диалог.
2. Отправьте команду `/sniper`.
3. В открывшемся меню выберите **Call Channels** и сеть **SOL**.
4. Выберите канал **Me**.
5. Включите **Auto Buy**.
6. Задайте сумму для покупки токенов в параметре **Buy Amount**.
7. При необходимости установите параметры **Sell-Hi** и **Sell-Lo** для автоматической продажи токенов.

## Настройка параметров выбора токенов

Параметры выбора токенов могут быть настроены несколькими способами:

- Создать новые объекты модели **Settings** в панели администратора.
- Написать проверку внутри функции `check_settings()` в файле `settings.py`.

Функция `check_settings()` проверяет параметры в любом режиме работы и независимо от настроек, созданных в панели администратора.

## Скриншоты

![screen 1](https://github.com/user-attachments/assets/560bfbae-61f5-4f05-b6c1-e5352a15b0bf) 
![screen 2](https://github.com/user-attachments/assets/0a6e1f00-770b-4f6d-81c3-34f7e7897429)
