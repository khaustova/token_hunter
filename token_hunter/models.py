from django.db import models


class TopTrader(models.Model):
    """Model for storing data about top wallets.

    Contains:
    - Token data
    - Wallet data
    - Trading results (PNL)
    """

    token_name = models.CharField(
        max_length=256,
        verbose_name="Token Name"
    )
    token_address = models.CharField(
        max_length=256,
        verbose_name="Token Address"
    )
    pair = models.CharField(
        max_length=256,
        verbose_name="Pair"
    )
    wallet_address = models.CharField(
        max_length=256,
        verbose_name="Wallet Address"
    )
    chain = models.CharField(
        max_length=256,
        default="Solana",
        verbose_name="Chain"
    )
    transaction_count = models.IntegerField(
        default=0,
        verbose_name="Transaction Count"
    )
    bought = models.IntegerField(
        verbose_name="Bought"
    )
    sold = models.IntegerField(
        verbose_name="Sold"
    )
    PNL = models.DecimalField(
        blank=True, 
        null=True,
        max_digits=12,
        decimal_places=2,
        verbose_name="PNL"
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created Date"
    )

    class Meta:
        verbose_name = "Top Wallet"
        verbose_name_plural = "Top Wallets"

    def __str__(self):
        return f"Wallet {self.wallet_address} with {self.PNL} on {self.token_name}"


class Mode(models.TextChoices):
    """Operating modes for tokens.

    Choices:
        DATA_COLLECTION: Data collection without trading
        SIMULATION: Purchase simulation
        REAL_BUY: Real trading
    """
    DATA_COLLECTION = "data_collection", "Data Collection"
    SIMULATION = "simulation", "Simulation"
    REAL_BUY = "real_buy", "Real Buy"


class MonitoringRule(models.TextChoices):
    """Rules for monitoring tokens.

    Choices:
        BOOSTED: Monitoring boosted tokens
        LATEST: Monitoring new tokens
        FILTER: Monitoring by specified filters
    """
    BOOSTED = "boosted", "Boosted"
    LATEST = "latest", "Latest"
    FILTER = "filter", "Filter"


class Settings(models.Model):
    """Settings for token selection.

    Contains parameters for filtering tokens by various metrics.
    """
    name = models.CharField(
        max_length=512,
        verbose_name="Name"
    )

    # Main settings:
    monitoring_rule = models.CharField(
        max_length=64,
        choices=MonitoringRule.choices,
        default=MonitoringRule.BOOSTED,
        verbose_name="Token Monitoring Rule"
    )
    mode = models.CharField(
        max_length=64,
        choices=Mode.choices,
        default=Mode.SIMULATION,
        verbose_name="Mode"
    )

    # Token price:
    price_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Minimum Price"
    )
    price_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Price"
    )

    # Token age:
    token_age_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Minimum Age"
    )
    token_age_max = models.FloatField(
        blank=True,
        null=True,
        default=5,
        verbose_name="Maximum Age"
    )

    # Number of buys and sells:
    buys_m5_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Minimum Buys (5 minutes)"
    )
    buys_m5_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum Buys (5 minutes)"
    )
    sells_m5_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Minimum Sells (5 minutes)"
    )
    sells_m5_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum Sells (5 minutes)"
    )
    buys_h1_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Minimum Buys (1 hour)"
    )
    buys_h1_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum Buys (1 hour)"
    )
    sells_h1_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Minimum Sells (1 hour)"
    )
    sells_h1_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum Sells (1 hour)"
    )
    buys_h6_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Minimum Buys (6 hours)"
    )
    buys_h6_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum Buys (6 hours)"
    )
    sells_h6_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Minimum Sells (6 hours)"
    )
    sells_h6_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum Sells (6 hours)"
    )
    buys_h24_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Minimum Buys (24 hours)"
    )
    buys_h24_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum Buys (24 hours)"
    )
    sells_h24_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Minimum Sells (24 hours)"
    )
    sells_h24_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum Sells (24 hours)"
    )

    # Volume:
    volume_m5_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Minimum Trading Volume (5 minutes)"
    )
    volume_m5_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Trading Volume (5 minutes)"
    )
    volume_h1_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Minimum Trading Volume (1 hour)"
    )
    volume_h1_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Trading Volume (1 hour)"
    )
    volume_h6_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Minimum Trading Volume (6 hours)"
    )
    volume_h6_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Trading Volume (6 hours)"
    )
    volume_h24_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Minimum Trading Volume (24 hours)"
    )
    volume_h24_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Trading Volume (24 hours)"
    )

    # Price change:
    price_change_m5_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Minimum Price Change (5 minutes)"
    )
    price_change_m5_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Price Change (5 minutes)"
    )
    price_change_h1_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Minimum Price Change (1 hour)"
    )
    price_change_h1_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Price Change (1 hour)"
    )
    price_change_h6_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Minimum Price Change (6 hours)"
    )
    price_change_h6_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Price Change (6 hours)"
    )
    price_change_h24_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Minimum Price Change (24 hours)"
    )
    price_change_h24_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Price Change (24 hours)"
    )

    # Liquidity:
    liquidity_min = models.FloatField(
        blank=True,
        null=True,
        default=1000,
        verbose_name="Minimum Liquidity"
    )
    liquidity_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Liquidity"
    )

    # FDV:
    fdv_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Minimum FDV"
    )
    fdv_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum FDV"
    )

    # Market capitalization:
    market_cap_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Minimum Market Cap"
    )
    market_cap_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Market Cap"
    )

    # Social media:
    is_socio = models.BooleanField(
        default=False,
        verbose_name="Presence of at least one social network or website"
    )
    is_telegram = models.BooleanField(
        default=False,
        verbose_name="Has Telegram"
    )
    is_twitter = models.BooleanField(
        default=False,
        verbose_name="Has Twitter"
    )
    is_website = models.BooleanField(
        default=False,
        verbose_name="Has Website"
    )

    # Sum of top trader buys:
    tt_bought_sum_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Minimum Top Trader Buy Sum"
    )
    tt_bought_sum_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Top Trader Buy Sum"
    )

    # Sum of top trader sells:
    tt_sold_sum_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Top Trader Sell Sum"
    )
    tt_sold_sum_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Maximum Top Trader Sell Sum"
    )

    # Number of negative PNLs for top traders:
    tt_pnl_loss_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum Top Traders with Negative PNL"
    )
    tt_pnl_loss_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum Top Traders with Negative PNL"
    )

    # Top traders without sells or buys:
    tt_no_bought_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Minimum Top Traders Without Buys"
    )
    tt_no_bought_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum Top Traders Without Buys"
    )
    tt_no_sold_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Minimum Top Traders Without Sells"
    )
    tt_no_sold_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum Top Traders Without Sells"
    )

    # Boost:
    boost_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Minimum Boost"
    )
    boost_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Maximum Boost"
    )

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"
        ordering = ['name']

    def __str__(self):
        return self.name


class Status(models.TextChoices):
    """Transaction statuses.

    Choices:
        OPEN: Open position
        CLOSED: Closed position
    """
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"


class Transaction(models.Model):
    """Model for storing transaction data.

    Contains:
    - Token data and its metrics
    - Trade information
    - Social metrics
    - Trading results (PNL)
    - Links to settings
    """

    # Token data:
    pair = models.CharField(
        max_length=256,
        verbose_name='Pair'
    )
    token_name = models.CharField(
        verbose_name="Token Name",
        max_length=256
    )
    token_address = models.CharField(
        verbose_name="Token Address",
        max_length=256
    )
    price_b = models.FloatField(
        verbose_name="Buying Price, USD"
    )
    price_s = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Selling Price, USD"
    )
    token_age_b = models.FloatField(
        verbose_name="Age at Buy, min."
    )
    token_age_s = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Age at Sell, min."
    )
    buys_m5 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Buys (5 minutes)"
    )
    sells_m5 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Sells (5 minutes)"
    )
    buys_h1 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Buys (1 hour)"
    )
    sells_h1 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Sells (1 hour)"
    )
    buys_h6 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Buys (6 hours)"
    )
    sells_h6 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Sells (6 hours)"
    )
    buys_h24 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Buys (24 hours)"
    )
    sells_h24 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Sells (24 hours)"
    )
    volume_m5 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Trading Volume (5 minutes), %"
    )
    volume_h1 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Trading Volume (1 hour), %"
    )
    volume_h6 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Trading Volume (6 hours), %"
    )
    volume_h24 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Trading Volume (24 hours), %"
    )
    price_change_m5 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Price Change (5 minutes), %"
    )
    price_change_h1 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Price Change (1 hour), %"
    )
    price_change_h6 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Price Change (6 hours), %"
    )
    price_change_h24 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Price Change (24 hours), %"
    )
    liquidity = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Liquidity (5 minutes), %"
    )
    fdv = models.FloatField(
        blank=True,
        null=True,
        verbose_name="FDV, USD"
    )
    market_cap = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Market Cap, USD"
    )
    is_mutable_metadata = models.BooleanField(
        blank=True,
        null=True,
        default=True,
        verbose_name="Mutable Metadata"
    )
    is_telegram = models.BooleanField(
        default=False,
        verbose_name="Has Telegram"
    )
    is_twitter = models.BooleanField(
        default=False,
        verbose_name="Has Twitter"
    )
    is_website = models.BooleanField(
        default=False,
        verbose_name="Has Website"
    )
    boosts = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        verbose_name="Boosts"
    )
    boosts_ages = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Age at Boosts, min."
    )
    dextscore = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        verbose_name="DextScore"
    )
    telegram_members = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Telegram Members"
    )
    is_telegram_error = models.BooleanField(
        blank=True,
        null=True,
        default=False,
        verbose_name="Telegram provided but does not exist"
    )
    twitter_days = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Twitter Age, days"
    )
    twitter_tweets = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Twitter Posts"
    )
    twitter_followers = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Twitter Followers"
    )
    twitter_smart_followers = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Twitter Smart Followers"
    )
    is_twitter_error = models.BooleanField(
        blank=True,
        null=True,
        default=False,
        verbose_name="Twitter provided but does not exist"
    )
    # Transaction data:
    prices = models.CharField(
        max_length=16384,
        blank=True,
        null=True,
        verbose_name="Price Change"
    )
    date = models.CharField(
        max_length=16384,
        blank=True,
        null=True,
        verbose_name="Transaction Dates"
    )
    operations = models.CharField(
        max_length=16384,
        blank=True,
        null=True,
        verbose_name="Operations"
    )
    trades_sum = models.CharField(
        max_length=16384,
        blank=True,
        null=True,
        verbose_name="Operation Amounts"
    )
    trades_makers = models.CharField(
        max_length=16384,
        blank=True,
        null=True,
        verbose_name="Trading Wallets"
    )
    trades_for_maker = models.CharField(
        max_length=16384,
        blank=True,
        null=True,
        verbose_name="Transactions per Wallet"
    )
    transactions = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Total Transactions"
    )

    # Top wallet data:
    tt_bought = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Top Trader Buys"
    )
    tt_sold = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Top Trader Sells"
    )
    tt_unrealized = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Top Trader Unrealized Amount"
    )
    tt_speed = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Top Trader Speed"
    )

    # Holders:
    holders_percentages = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Percentage of Tokens Held by Main Holders"
    )
    holders_liquidity = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Percentage of Tokens in Liquidity"
    )
    holders_total = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Total Holders"
    )

    # Final data:
    PNL = models.DecimalField(
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2,
        verbose_name="PNL, %"
    )
    PNL_10 = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="PNL 10 %"
    )
    PNL_20 = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="PNL 20 %"
    )
    PNL_30 = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="PNL 30 %"
    )
    PNL_40 = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="PNL 40 %"
    )
    PNL_50 = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="PNL 50 %"
    )
    status = models.CharField(
        max_length=64,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name="Status"
    )

    # Mode settings:
    monitoring_rule = models.CharField(
        max_length=64,
        choices=MonitoringRule.choices,
        default=MonitoringRule.BOOSTED,
        verbose_name="Type"
    )
    mode = models.CharField(
        max_length=64,
        choices=Mode.choices,
        default=Mode.DATA_COLLECTION,
        verbose_name="Mode"
    )

    # Transaction settings:
    settings = models.ForeignKey(
        Settings,
        on_delete=models.CASCADE,
        verbose_name="Settings",
        blank=True,
        null=True,
    )

    # Opening and closing date:
    opening_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created Date"
    )
    closing_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Closing Date"
    )

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return self.pair
