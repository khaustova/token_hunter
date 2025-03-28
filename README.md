
![Static Badge](https://img.shields.io/badge/Python-3.12.5-orange) ![Static Badge](https://img.shields.io/badge/Django-5.1-blue) ![Static Badge](https://img.shields.io/badge/Django_Telethon-1.4.0-blue) ![Static Badge](https://img.shields.io/badge/Celery-5.4.0-blue) ![Static Badge](https://img.shields.io/badge/Nodriver-0.36-blue) ![Static Badge](https://img.shields.io/badge/PostgreSQL-14.15-purple) ![Static Badge](https://img.shields.io/badge/Redis-6.0.16-purple) ![Static Badge](https://img.shields.io/badge/DEX_Screener_API-v1-purple) ![Static Badge](https://img.shields.io/badge/Solana-yellow) 

**Token Hunter** – веб-приложение на Django для настраиваемой торговли токенами в сети Solana и парсинга топовых кошельков.

## Используемые сервисы

:gem:  [DEX Screener](https://dexscreener.com/) – получение данных о токенах и кошельках   
:diamonds: [DEXTools](https://www.dextools.io/) – получение данных о токенах и кошельках  
:shield: [RugCheck](https://rugcheck.xyz/) – оценка безопасности токена   
:bar_chart: [Getmoni](https://discover.getmoni.io/) – анализ активности по токену в X (Twitter)   

## Основные функции

:mag_right: Мониторинг токенов по фильтру на DEX Screener   
:zap: Мониторинг забустенных токенов через DEX Screener API  
:alarm_clock: Мониторинг недавно добавленных токенов через DEX Screener API  
:gear: Настройка параметров для выбора токенов  
:shopping_cart: Сбор данных и эмуляция покупки токенов  
:robot: Реальная покупка токенов через Maestro Sniper Bot в Telegram   
:detective: Парсинг топовых кошельков по фильтру на DEX Screener  
:page_with_curl: Агрегация спарсенных кошельков по количеству    
:chart_with_upwards_trend: Экспорт данных в Excel  

## Запуск

1. Клонируйте репозиторий проекта на свой компьютер:

```
git clone https://github.com/khaustova/muiv_timetable.git
```

2. Переименуйте файл `.env.example` в `.env` и добавьте свои данные. 

3. Найдите в папке `token_hunter` файл `settings_example.py` и переименуйте его в `settings.py`. Добавьте собственные проверки в функции `check_api_data()` и `check_settings()`.
   
   Функция `check_api_data()` выполняет проверку в начале анализа токена и принимает данные, полученные через API.
   <details>
   <summary>Пример данных</summary>
      <code>{
        "chainId" : "solana",
        "dexId" : "raydium",  
        "url" : "https://dexscreener.com/solana/dqcj8kcnbdmm7kww4w4w9hvbhb7raellpt3raxsjmgnt",
        "pairAddress" : "DQcj8kcnBdMm7KWw4w4W9HVbhB7RAeLLPt3rAxsjmgnT",
        "baseToken" : {
            "address" : "B7NPUGvxC8BUF5a8BdxurBNxCjV3HwyN6DaRivtqNAjB",
            "name" : "Pi Network AI",
            "symbol" : "PiAI"
        },
        "quoteToken" : {
            "address" : "So11111111111111111111111111111111111111112",
            "name" : "Wrapped SOL",
            "symbol" : "SOL"
        },
        "priceNative" : "0.00000000000002174",
        "priceUsd" : "0.000000000004224",
        "txns" : {
            "m5" : {
                "buys" : 121,
                "sells" : 73
            },
            "h1" : {
                "buys" : 1050,
                "sells" : 706
            },
            "h6" : {
                "buys" : 8176,
                "sells" : 4854
            },
            "h24" : {
                "buys" : 8618,
                "sells" : 5078
            }
        },
        "volume" : {
            "h24" : 1017521.56,
            "h6" : 962844.46,
            "h1" : 120586.98,
            "m5" : 13581.37
        },
        "priceChange" : {
            "m5" : -28.15,
            "h1" : -40.1,
            "h6" : -49.48,
            "h24" : 507
        },
        "liquidity" : {
            "usd" : 30492.81,
            "base" : 3611984589615754,
            "quote" : 78.4331
        },
        "fdv" : 180343,
        "marketCap" : 180343,
        "pairCreatedAt" : 1739604349000,
        "info" : {
            "imageUrl" : "https://dd.dexscreener.com/ds-data/tokens/solana/B7NPUGvxC8BUF5a8BdxurBNxCjV3HwyN6DaRivtqNAjB.png?key=a838fa",
            "header" : "https://dd.dexscreener.com/ds-data/tokens/solana/B7NPUGvxC8BUF5a8BdxurBNxCjV3HwyN6DaRivtqNAjB/header.png?key=a838fa",
            "openGraph" : "https://cdn.dexscreener.com/token-images/og/solana/B7NPUGvxC8BUF5a8BdxurBNxCjV3HwyN6DaRivtqNAjB?timestamp=1739638500000",
            "websites" : [ {
                "label" : "Website",
                "url" : "https://pi-network.club"
            }, {
                "label" : "CoinMarketCap",
                "url" : "https://coinmarketcap.com/currencies/pi-network-ai/"
            } ],
            "socials" : [ {
                "type" : "twitter",
                "url" : "https://x.com/PiAICTO"
            }, {
                "type" : "telegram",
                "url" : "https://t.me/PiNetworkcto"
            } ]
        },
        "boosts" : {
            "active" : 500
        }
    }</code>

   </details>  
    
   Функция `check_settings()` выполняет проверку перед покупкой или её эмуляцией и принимает данные, полученные как через API, так и со страницы токена, которые включают в себя данные о топовых транзакциях, снайперах и основных держателях.  

4. Запустите приложение одним из двух способов:  
    <details>
      <summary>В Docker</summary>
      
      
      * Запустите приложение с помощью команды:  
      
        ```
        docker-compose up --build
        ```
      
    </details>  

    <details>
      <summary>В виртуальном окружении</summary>

      * Убедитесь, что у вас установлены и запущены Redis и PostgreSQL.


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
  

5. Приложение будет доступно по адресу http://127.0.0.1:8000.  

## Выбор источника данных

Сбор дополнительной информации о токене может вестись на сайте [DEX Screener](https://dexscreener.com/) или [DEXTools](https://www.dextools.io/). С обоих сайтов собираются данные о транзакциях топовых кошельков и основных держателях токенов. 

### Особенности сбора данных на DEX Screener:
- Используется библиотека nodriver.
- Браузер нельзя запускать в headless, так как раз в ~1.5 суток нужно вручную проходить проверку Cloudflare.
- Дополнительно собирает данных о первых 100 транзакциях в таблице Snipers на странице токена.
- На Билайне время от времени не подгружает таблицы с сообщением: "Failed connecting to server".

### Особенности сбора данных на DEXTools
- Используется библиотека Selenium.
- Браузер можно запускать в headless, не требуется вручную проходить проверку Cloudflare.
- Дополнительно собирает данные о последних (~100) транзакциях в таблице Trade History на странице токена

При использовании фильтра (для мониторинга токенов по фильтру и парсинга топовых кошельков) всегда будет запущен браузер для работы с сайтом DEX Screener.

## Настройка параметров выбора токенов

Параметры выбора токенов могут быть настроены несколькими способами:

- Создать новые объекты модели **Settings** в панели администратора.
- Написать проверки внутри функций `check_api_data()` и `check_settings()` в файле `token_hunter/settings.py`.

## Настройка реальной покупки и продажи токенов

### Разрешение реальной покупки токенов

В файле `.env` установите значение `IS_REAL_BUY=True`.

### Настройка интеграции с Telegram

Интеграция с Telegram требуется не только для автоматической покупки и продажи токенов через бота, но и для сбора данных о Telegram-каналах.

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

#### Настройка Maestro Sniper Bot

1. Найдите бота @MaestroSniperBot и начните диалог.
2. Отправьте команду `/sniper`.
3. В открывшемся меню выберите **Call Channels** и сеть **SOL**.
4. Выберите канал **Me**.
5. Включите **Auto Buy**.
6. Задайте сумму для покупки токенов в параметре **Buy Amount**.
7. При необходимости установите параметры **Sell-Hi** и **Sell-Lo** для автоматической продажи токенов.

## Скриншоты
![index](https://github.com/user-attachments/assets/96989498-e016-4550-858a-1ce0f576bc59)
![settings](https://github.com/user-attachments/assets/0a6e1f00-770b-4f6d-81c3-34f7e7897429)
![transactions](https://github.com/user-attachments/assets/38cf24cb-aacc-42be-b0c3-eedd725ec2f8)
![top_traders](https://github.com/user-attachments/assets/45892321-bbc7-45a8-a72f-518c94fcd523)

