# main.py

import os
import time
import logging
import multiprocessing
import threading
import asyncio

# 예: config 모듈 임포트
from config.config import Config
from config.logger import get_logger

# data_feed 모듈 임포트 (실시간 데이터 수집)
from data_feed.order_book_ws import BinanceOrderBookWS
from data_feed.trade_data_ws import BinanceTradeWS

# signal_generator
from signal_generator.signal_manager import run_signal_manager  # 예: Worker 함수 형태

# order_execution
from order_execution.exchange_api import BinanceFuturesAPI
from order_execution.trade_executor import TradeExecutor

# notification
from notification.discord_alerts import DiscordAlerts
from notification.telegram_alerts import TelegramAlerts
from notification.dashboard import Dashboard

################################################################
# 1) 데이터 피드 프로세스 (WebSocket)
################################################################
def data_feed_process(order_book_queue, trade_queue, config):
    """
    오더북, 체결 데이터를 WebSocket으로 받아 큐에 전달하는 프로세스.
    """
    logger = get_logger(name="DataFeedProcess", log_level=config.log_level, log_file="data_feed.log")

    # 오더북 WS
    ob_ws = BinanceOrderBookWS(
        uri="wss://fstream.binance.com/ws",
        max_retries=5,
        base_retry_delay=1.0,
        logger=logger
    )
    # trade WS
    td_ws = BinanceTradeWS(
        uri="wss://fstream.binance.com/ws",
        max_retries=5,
        base_retry_delay=1.0,
        logger=logger
    )

    # 큐에 전달하기 위해 on_message 콜백을 살짝 수정하거나,
    # 혹은 handle_depth/handle_trade에서 queue.put()를 호출하도록 커스터마이징해야 함.
    # 여기서는 간단히 "가정"한다고 표시.

    async def run_all():
        """
        두 개의 WebSocket을 동시에 실행 (asyncio.gather)
        """
        task1 = asyncio.create_task(ob_ws.listen())
        task2 = asyncio.create_task(td_ws.listen())
        await asyncio.gather(task1, task2)

    # 예시로 handle_depth/handle_trade 내부에서 queue.put(data)를 한다고 가정.
    try:
        asyncio.run(run_all())
    except KeyboardInterrupt:
        logger.info("Data Feed process stopped by user.")

################################################################
# 2) 메인 함수
################################################################
def main():
    # 1) 설정 로드
    config = Config(config_file="settings.json")  # 혹은 None
    logger = get_logger(name="Main", log_level=config.log_level, log_file="app.log")

    # 2) 멀티프로세싱 매니저 (큐 생성)
    manager = multiprocessing.Manager()
    order_book_queue = manager.Queue()
    trade_queue = manager.Queue()
    signal_queue = manager.Queue()   # 시그널을 담을 큐
    result_queue = manager.Queue()   # 시그널 분석 결과나 최종 신호를 담을 큐 (옵션)

    ############################################################
    # 2-1) 데이터피드 프로세스
    ############################################################
    feed_proc = multiprocessing.Process(
        target=data_feed_process,
        args=(order_book_queue, trade_queue, config),
        daemon=True
    )
    feed_proc.start()
    logger.info("Data Feed process started.")

    ############################################################
    # 2-2) 시그널 매니저 프로세스
    ############################################################
    # 예: signal_manager.py 안에 run_signal_manager(input_queue, output_queue)라는 함수가 있다고 가정
    # 실제로는 order_book, trade_data 둘 다 필요할 수 있으니, 2개 큐를 전달하거나 합쳐서 전달
    signal_proc = multiprocessing.Process(
        target=run_signal_manager,
        args=(order_book_queue, signal_queue),  # 단순 예시
        daemon=True
    )
    signal_proc.start()
    logger.info("Signal Manager process started.")

    ############################################################
    # 2-3) 알림 & 대시보드 스레드
    ############################################################
    # - Discord / Telegram 알림 객체 생성
    discord_alert = DiscordAlerts(config.discord_webhook_url)
    telegram_alert = TelegramAlerts(config.telegram_bot_token, config.telegram_chat_id)

    # - 대시보드 (Flask) 인스턴스
    dashboard = Dashboard(port=5000, logger=logger)

    # 대시보드용 스레드
    dashboard_thread = threading.Thread(target=dashboard.start, daemon=True)
    dashboard_thread.start()
    logger.info("Dashboard thread started on port 5000.")

    # 알림 스레드 예시 (주기적으로 특정 큐/이벤트 체크하여 알림 발송)
    def notification_loop():
        while True:
            # 예: 시그널 큐나 result_queue에서 중요한 알림 발생 시 메시지 전송
            try:
                # block=False, 예외 시 sleep
                signal_data = signal_queue.get(timeout=1)
                # 간단히 "BUY 신호 발생" 시 알림
                msg = f"[Signal] {signal_data}"
                discord_alert.send_message(msg)
                telegram_alert.send_message(msg)

                # 대시보드 업데이트도 가능
                # dashboard.update_data(...)  # 시세/포지션 등

            except Exception:
                pass
            time.sleep(1)

    notify_thread = threading.Thread(target=notification_loop, daemon=True)
    notify_thread.start()
    logger.info("Notification thread started.")

    ############################################################
    # 2-4) 트레이드 실행 스레드 (예: TradeExecutor)
    ############################################################
    # Exchange API
    binance_api = BinanceFuturesAPI(
        api_key=config.api_key,
        api_secret=config.api_secret,
        logger=logger
    )
    # 트레이드 실행기 (초기 계좌 잔고 등은 실제 조회 시 업데이트)
    trade_executor = TradeExecutor(
        exchange_api=binance_api,
        initial_balance=1000.0,  # 예시
        logger=logger
    )
    trade_executor.start()

    # 간단히 "신호 큐"에서 BUY/SELL 신호가 오면 executor에 전달
    def trade_execution_loop():
        while True:
            try:
                signal_data = signal_queue.get(timeout=1)
                # signal_data: {"action": "BUY", "symbol": "LTCUSDT", "price": 95.0, ...}
                trade_executor.add_signal(signal_data)
            except Exception:
                pass
            time.sleep(0.5)

    trade_thread = threading.Thread(target=trade_execution_loop, daemon=True)
    trade_thread.start()
    logger.info("Trade execution thread started.")

    ############################################################
    # 2-5) 메인 프로세스 대기
    ############################################################
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Main process shutting down...")

        # 각 프로세스/스레드 종료
        feed_proc.terminate()
        signal_proc.terminate()
        trade_executor.stop()  # 내부 스레드 join
        logger.info("Terminated all child processes/threads.")


if __name__ == "__main__":
    main()
