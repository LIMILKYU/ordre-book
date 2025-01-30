# config/utils.py

import datetime
import time
import math
import logging
import functools
import requests

logger = logging.getLogger(__name__)

def timestamp_to_datetime(ts: int) -> datetime.datetime:
    """
    밀리초 혹은 초 단위 Unix Timestamp를 datetime 객체로 변환
    """
    # ts가 10자리면 초, 13자리면 밀리초
    if len(str(ts)) == 13:
        return datetime.datetime.utcfromtimestamp(ts / 1000)
    else:
        return datetime.datetime.utcfromtimestamp(ts)

def datetime_to_timestamp(dt: datetime.datetime, millis: bool = False) -> int:
    """
    datetime 객체를 timestamp(초 혹은 밀리초)로 변환
    """
    epoch = dt.timestamp()
    if millis:
        return int(epoch * 1000)
    else:
        return int(epoch)

def retry_on_exception(max_retries=3, delay=1.0):
    """
    예외가 발생하면 지정된 횟수만큼 재시도하는 데코레이터.
    :param max_retries: 재시도 횟수
    :param delay: 재시도 전 대기 시간(초)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Exception on attempt {attempt+1}: {e}")
                    if attempt + 1 == max_retries:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_on_exception(max_retries=3, delay=2.0)
def fetch_url(url: str) -> str:
    """
    단순히 지정 URL에서 텍스트를 가져오는 예시 함수,
    네트워크 에러 발생 시 3회 재시도
    """
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text
