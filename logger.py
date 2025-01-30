# config/logger.py

import logging
import os
from logging.handlers import RotatingFileHandler

def get_logger(
    name: str = __name__,
    log_level: str = "DEBUG",
    log_file: str = "app.log",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3
) -> logging.Logger:
    """
    로거를 생성 및 반환. (RotatingFileHandler + StreamHandler)
    :param name: 로거 이름
    :param log_level: 로깅 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    :param log_file: 로그 파일 경로
    :param max_bytes: 파일이 이 크기를 초과하면 롤오버
    :param backup_count: 백업 파일 최대 개수
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level.upper())

    # 이미 핸들러가 있으면 중복 추가하지 않음
    if logger.handlers:
        return logger

    # 포맷
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 콘솔 핸들러
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # 파일 핸들러 (회전 로그)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
