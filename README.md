
![Static Badge](https://img.shields.io/badge/Python-3.12.5-orange) ![Static Badge](https://img.shields.io/badge/Django-5.1-blue) ![Static Badge](https://img.shields.io/badge/Django_Telethon-1.4.0-blue) ![Static Badge](https://img.shields.io/badge/Celery-5.4.0-blue) ![Static Badge](https://img.shields.io/badge/Nodriver-0.36-blue) ![Static Badge](https://img.shields.io/badge/PostgreSQL-14.15-purple) ![Static Badge](https://img.shields.io/badge/Redis-6.0.16-purple) ![Static Badge](https://img.shields.io/badge/DEX_Screener_API-v1-purple) ![Static Badge](https://img.shields.io/badge/Solana-yellow) 

**Token Hunter** – Django web application for custom token trading on Solana and top wallet parsing.

## :exclamation: Warning
This application is not a magical money-making machine. It's just a tool.  

Using this application requires not only an understanding of which tokens you want to trade but also at least a basic proficiency in Python to customize it effectively.  

The graphical interface for configuring trading settings is quite limited, so it is highly recommended to manually adjust the settings in the `token_hunter/settings.py` file within the `check_api_data()` and `check_settings()` functions.  
  
The key difference between these functions is that `check_api_data()` performs an initial validation of data fetched via the DEX Screener API, before parsing details like recent transactions, token holders, and top wallets. The `token_hunter/settings.py` file also includes formats and examples of the data collected by the application.  
  
Additionally, the file `token_hunter/src/utils/preprocessing_data.py` contains predefined functions for data preprocessing, such as calculating total trade volumes or counting buy/sell-less transactions.  
  
I personally use this application to trade new Solana tokens, executing a few trades per week with a success rate of around 65–70%. However, I do not publicly share my trading algorithms or provide guidance on them, as I do not wish to assume such responsibility.

Yes, the application works and can generate modest profits, but wrong settings + meme coins risks = you could lose everything.

## Integrated Services

:gem:  [DEX Screener](https://dexscreener.com/) – token and wallet data aggregation  
:diamonds: [DEXTools](https://www.dextools.io/) – token and wallet analytics  
:shield: [RugCheck](https://rugcheck.xyz/) – token security assessment  
:bar_chart: [Getmoni](https://discover.getmoni.io/) – Twitter/X activity analysis for tokens  

## Key Features

:zap: Boosted token tracking via DEX Screener API  
:alarm_clock: Newly listed token monitoring via DEX Screener API  
:mag_right: Token monitoring with customizable filters via DEX Screener  
:gear: Customizable token selection parameters  
:shopping_cart: Data collection and simulated token purchases  
:robot: Real token purchases via Telegram’s Maestro Sniper Bot  
:detective: Top wallet parsing with filters  
:page_with_curl: Wallet activity aggregation  
:chart_with_upwards_trend: Excel export  

## Setup

1. Clone the repository:

```
git clone https://github.com/khaustova/muiv_timetable.git
```

2. Rename `.env.example` to `.env` and populate with your credentials.

3. In the `token_hunter` folder, rename `settings_example.py` to `settings.py`. Add custom checks to:
    - `check_api_data()` – validates initial token data from API (see example below).
    - `check_settings()` – pre-trade validation (includes on-page data like top transactions/holders).
   
   <details>
   <summary>Example API response</summary>
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

4. Launch the app with Docker:

    ```
    docker-compose up --build
    ```
    Note: In the `.env` file, don’t forget to change `REDIS_HOST` and `POSTGRES_HOST` to `redis` and `postgres` respectively.

    <details>
      <summary>Or use virtual environment</summary>

      * Ensure Redis and PostgreSQL are running.


      * Create venv:
        

      ```
      python3 -m venv .venv
      ```

      * Activate venv:

        * Linux/MacOS:  

        ```
        source .venv/bin/activate
        ```
      
        * Windows:  

        ```
        .venv\Scripts\activate
        ```

      * Install dependencies:

      ```
      pip install -r requirements.txt
      ```

      * Migrate DB:
        
      ```
      python3 manage.py migrate
      ```

      * Start Celery:
      
      ```
      celery -A core worker -l info
      ```

      * Run the server:  

      ```
      python3 manage.py runserver
      ```
      
    </details> 
  

5. Access at: http://127.0.0.1:8000 

## Data Source Selection

Token data can be scraped from [DEX Screener](https://dexscreener.com/) and [DEXTools](https://www.dextools.io/).

### DEX Screener Specifics:
- Uses nodriver (non-headless browser required due to Cloudflare checks every ~36 hours).
- May fail to load tables with "Failed connecting to server" errors (common on Beeline ISP).
- Filter-based monitoring (tokens/wallets) always uses DEX Screener.

### DEXTools Specifics
- Uses Selenium (supports headless mode; no manual Cloudflare checks).
- Extracts additional trade history (~100 recent transactions).

## Token Selection Parameters

Configure via:

- **Admin panel**: create Settings model instances.
- **Code**: modify `check_api_data()` and `check_settings()` in `token_hunter/settings.py`.

## Real Buy/Sell Configuration

### Enable Real Purchases

Set `IS_REAL_BUY=True` in `.env`.

### Telegram Integration

Required for automated trading via Maestro Sniper Bot and Telegram channel data collection.

#### Obtaining API ID and Hash

1. Visit https://my.telegram.org/auth.
2. Log in with the phone number linked to your trading account.
3. Navigate to **API development tools** → **Create a new app**.
4. Copy `App api_id` and `App api_hash` to .env:
```
TELETHON_API_ID=your_id
TELETHON_API_HASH=your_hash
```
#### Telegram Authorization

1. Set `TELEGRAM_PHONE_NUMBER` in `.env`.
2. Run: 

```
python manage.py authtelegram
```

3. Follow on-screen prompts to complete login.

#### Maestro Sniper Bot Setup

1. Open **@MaestroSniperBot** in Telegram.
2. Send the command `/sniper`.
3. In the menu that appears, select **Call Channels** and choose the **SOL** network.
4. Select the **Me** channel.
5. Enable **Auto Buy**.
6. Set the token purchase amount in the **Buy Amount** parameter.
7. Optionally, configure **Sell-Hi** and **Sell-Lo** parameters for automatic token selling.

## Screenshots
![screen 1](https://github.com/user-attachments/assets/db6a02e7-709e-471f-a421-1cc77ab6f9a5)
![screen 2](https://github.com/user-attachments/assets/37f8ce23-cb62-4a8f-a746-6207b6800c07)
![screen 3](https://github.com/user-attachments/assets/8a72cfb5-f4ed-4308-b41f-2a7c4a9d86ba)
![screen 4](https://github.com/user-attachments/assets/055a2a89-b87a-4f86-aa5d-a794f9476b97)
