import asyncio
import aiohttp
from datetime import date, timedelta

from app.core.aiohttp_client import get_session
from app.core.config import settings

API_CONFIG = {
    "duration": {
        "url": settings.DURATION_URL,
        "service_key": settings.DURATION_SERVICE_KEY,
    },
    "mileage": {
        "url": settings.MILEAGE_URL,
        "service_key": settings.MILEAGE_SERVICE_KEY,
    },
}


async def _fetch_one_vin(url: str, service_key: str, dt_range: str, vin: str):
    """单个 VIN 的异步请求"""
    session = await get_session()
    payload = {
        "dt": dt_range,
        "vin": vin,
        "serviceKey": service_key,
        "page": 1,
    }
    try:
        async with session.post(url, json=payload) as response:
            # 先判断 HTTP 状态码，非 2xx 视为失败
            if response.status < 200 or response.status >= 300:
                return vin, None
            res_json = await response.json(content_type=None)
            if res_json.get("success") is True:
                data = res_json.get("data")
                if data:
                    return vin, data
                else:
                    pass
            else:
                pass
    except aiohttp.ClientError:
        # 连接错误、超时、参数错误等异常，视为空失败
        return vin, None
    # 其他异常也视为空值
    return vin, None


async def call_leapmotor_api(vin_list, config_key="mileage"):
    config = API_CONFIG[config_key]
    url = config["url"]
    service_key = config["service_key"]

    # 1. 计算时间范围：过去一天
    now = date.today()
    two_days_ago = now - timedelta(days=5)
    dt_range = f"{two_days_ago},{now}"

    tasks = [_fetch_one_vin(url, service_key, dt_range, vin) for vin in vin_list]
    results = await asyncio.gather(*tasks)

    datas = {}
    fail_list = []
    for vin, data in results:
        if data is not None:
            datas[vin] = data
        else:
            fail_list.append(vin)
    return datas, fail_list
