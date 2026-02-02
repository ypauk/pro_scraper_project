import random
import time
#from loguru import logger

def human_delay(min_sec=1, max_sec=3):
    """Імітує роздуми людини"""
    sleep_time = random.uniform(min_sec, max_sec)
    time.sleep(sleep_time)