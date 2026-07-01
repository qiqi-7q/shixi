import requests
from datetime import date, timedelta
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


def call_leapmotor_api(vin_list, config_key="mileage"):
    config = API_CONFIG[config_key]
    url = config["url"]
    service_key = config["service_key"]

    # 1. 计算时间范围：过去两天
    now = date.today()
    two_days_ago = now - timedelta(days=1)

    dt_range = f"{two_days_ago},{now}"

    datas = {}
    fail_list = []
    # 2. 遍历 VIN
    for vin in vin_list:
        payload = {
            "dt": dt_range,  # 修正后的格式
            "vin": vin,
            "serviceKey": service_key,
            "page": 1,
        }

        try:
            # 发送 POST 请求
            response = requests.post(url, json=payload, timeout=10)
            res_json = response.json()

            # 检查是否有数据
            if res_json.get("success") == True:
                data = res_json.get("data")
                if data:
                    datas[vin] = data
                else:
                    pass
            else:
                pass
        except requests.exceptions.RequestException as e:
            fail_list.append(vin)
    return datas, fail_list
