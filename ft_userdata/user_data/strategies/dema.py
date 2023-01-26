# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
from functools import reduce
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from datetime import datetime
from typing import Optional
from freqtrade.strategy import (
    BooleanParameter,
    CategoricalParameter,
    DecimalParameter,
    IStrategy,
    IntParameter,
)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta 
import freqtrade.vendor.qtpylib.indicators as qtpylib

# This class is a sample. Feel free to customize it.
def heikin_ashi(self, df: DataFrame) -> None:
    df_shifted = df.shift()
    df['ha_open'] = (df_shifted['open'] + df_shifted['close']) / 2
    df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    df['ha_high'] = df[['high', 'open', 'close']].max(axis=1)
    df['ha_low'] = df[['low', 'open', 'close']].min(axis=1)
class dema(IStrategy):
    

    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short: True

    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: Optional[str], side: str,
                 **kwargs) -> float:

        return 10

    # Trailing stoploss

    timeframe = '15m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False


    startup_candle_count: int = 110

    # Optional order type mapping.

    # Optional order time in force.
    order_time_in_force = {
        'entry': 'GTC',
        'exit': 'GTC'
    }
    def informative_pairs(self):
        """
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df_shifted = dataframe.shift()
        dataframe['ha_open'] = (df_shifted['open'] + df_shifted['close']) / 2
        dataframe['ha_close'] = (dataframe['open'] + dataframe['high'] + dataframe['low'] + dataframe['close']) / 4
        dataframe['ha_high'] = dataframe[['high', 'open', 'close']].max(axis=1)
        dataframe['ha_low'] = dataframe[['low', 'open', 'close']].min(axis=1)
        dataframe['dema20'] = ta.DEMA(dataframe['ha_close'], timeperiod=20)
        dataframe['dema100'] = ta.DEMA(dataframe['ha_close'], timeperiod=100)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['dema20'], dataframe['dema100'])) &  
                (dataframe['dema20'] >= dataframe['dema100']) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'enter_long'] = 1
        dataframe.loc[
            (
                (qtpylib.crossed_below(dataframe['dema20'], dataframe['dema100'])) &  
                (dataframe['dema20'] <= dataframe['dema100']) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'enter_short'] = 1
        

        return dataframe
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (qtpylib.crossed_below(dataframe['dema20'], dataframe['dema100'])) &  
                (dataframe['dema20'] <= dataframe['dema100']) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
        'exit_long'] = 1
         dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['dema20'], dataframe['dema100'])) &  
                (dataframe['dema20'] >= dataframe['dema100']) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'exit_short'] = 1
        return dataframe
