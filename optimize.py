import itertools
import numpy as np
from martin_strategy import martin_backtest

def optimize_martingale(
    prices_close, prices_high, prices_low, times,   # << 必須傳入的歷史K棒資料
    initial_balance, add_amount,                    # 固定參數
    add_multiple=1.0,                               # 加倉價差倍數（如不搜尋，可固定）
    direction = 1,                                     # 1 做多 / -1 做空
    leverage = 10,                                  #槓桿
    max_add_times = 7,                               #最大加碼次數
    add_amount_multiple = 2 ,                       #加碼金額倍數
):
    # ===== 搜尋空間 =====
    add_pct_list = list(np.arange(1.0, 4.1, 0.1))         # 1% ~ 10%
    take_profit_pct_list = list(np.arange(1.0, 4.1, 0.1)) # 1% ~ 10%
    stop_loss_pct_list = list(np.arange(1, 11, 1))   # 1% ~ 10%
    # ===========================================================

    best_params = None
    best_profit = -float("inf")

    for add_pct,take_profit_pct, stop_loss_pct in itertools.product(
        add_pct_list,take_profit_pct_list, stop_loss_pct_list
    ):
        # martin_backtest 會回傳 (df_trades, df_stats)
        _, df_stats = martin_backtest(
            prices_close, prices_high, prices_low, times, direction,
            initial_balance=initial_balance,
            leverage=leverage,
            add_pct=add_pct,
            add_multiple=add_multiple,
            max_add_times=int(max_add_times),
            add_amount=add_amount,
            add_amount_multiple=add_amount_multiple,
            take_profit_pct=take_profit_pct,
            stop_loss_pct=stop_loss_pct
        )

        # 取出止盈/停損累計金額
        total_take_profit = float(df_stats.loc["止盈累計金額", "數值"])
        total_stop_loss = float(df_stats.loc["停損累計金額", "數值"])
        # 你的 backtest 把虧損累加為「負數」，因此淨利 = 止盈累計 + 停損累計
        net_profit = total_take_profit + total_stop_loss

        if net_profit > best_profit:
            best_profit = net_profit
            best_params = {
                "加碼百分比": add_pct,
                "止盈百分比": float(take_profit_pct),
                "停損百分比": float(stop_loss_pct),
                "淨利潤": float(net_profit),
            }

    return best_params
