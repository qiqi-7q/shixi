import hashlib
import json
import time
from typing import Optional
import uuid
from datetime import date, timedelta, datetime

import requests

BASE_URL = "https://test-data-open-platform.leapmotor.com"
APP_ID = "57fb1e5c037a4e2ca0d8e20a20114173"
APP_SECRET = "czjVYxu1RqcD4TdGYmDDP7rcqay0zTKxUfLrfE/YUayCv0nkeHwD79a4FD3zqmIG"


def convert_value_to_string(value):
    """将参数值转换为签名字符串"""
    if value is None:
        return ""
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, (list, tuple)):
        return ",".join(str(x) for x in value)
    return str(value)


def generate_signature(timestamp, nonce, path_vars=None, query_params=None):
    """
    生成SHA-256 + HEX签名
    算法：收集所有参数(header的timestamp/nonce + path变量 + query参数 + appSecret)，
    值扁平化为字符串，按key字典序排序，拼接为 key1=value1#key2=value2#...，
    SHA256哈希后HEX编码
    """
    params = {}
    params["timestamp"] = str(timestamp)
    params["nonce"] = nonce
    params["appSecret"] = APP_SECRET

    if path_vars:
        for k, v in path_vars.items():
            params[k] = convert_value_to_string(v)

    if query_params:
        for k, v in query_params.items():
            params[k] = convert_value_to_string(v)

    sorted_keys = sorted(params.keys())
    content = "#".join(f"{k}={params[k]}" for k in sorted_keys)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def build_headers(path_vars=None, query_params=None):
    """构建请求头"""
    timestamp = int(time.time() * 1000)
    nonce = uuid.uuid4().hex
    signature = generate_signature(timestamp, nonce, path_vars, query_params)
    return {
        "X-App-Id": APP_ID,
        "X-Signature": signature,
        "X-Timestamp": str(timestamp),
        "X-Nonce": nonce,
    }


def get_vehicle_status(vin):
    """查询整车状态"""
    path = f"/api/v1/cars/{vin}/vehicle-status"
    headers = build_headers(path_vars={"vin": vin})
    resp = requests.get(BASE_URL + path, headers=headers)
    print(f"整车状态 (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    # data["list"][0]. fireOnTime、fireOffTime、traceMileage
    return resp.json()


def get_fire_states(car_id, begin_time, end_time, page_num=1, page_size=20):
    """点火状态查询列表：分页查询车辆点火/熄火状态历史记录"""
    path = f"/api/v1/cars/{car_id}/trace-points/fire-states"
    query_params = {
        "beginTime": begin_time,
        "endTime": end_time,
        "pageNum": str(page_num),
        "pageSize": str(page_size),
    }
    headers = build_headers(path_vars={"car-id": str(car_id)}, query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"点火状态列表 (carId={car_id}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_charge_states(car_id, begin_time, end_time, page_num=1, page_size=20):
    """查询充电状态列表"""
    # begin_time, end_time 格式：yyyy-MM-dd HH:mm:ss
    path = f"/api/v1/cars/{car_id}/charge-profiles/states"
    query_params = {
        "beginTime": begin_time,
        "endTime": end_time,
        "pageNum": str(page_num),
        "pageSize": str(page_size),
    }
    headers = build_headers(path_vars={"car-id": str(car_id)}, query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"充电状态列表 (carId={car_id}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_mileage_states(vin, begin_time):
    """查询里程数据"""
    # begin_time 格式：yyyy-MM-dd HH:mm:ss
    path = f"/api/v1/cars/{vin}/trace-points/mileage"
    query_params = {
        "beginTime": begin_time,
    }
    headers = build_headers(path_vars={"vin": vin}, query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"里程数据 (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_speed_energy(vin, begin_time):
    """查询速度能耗数据"""
    # begin_time 格式：yyyy-MM-dd HH:mm:ss
    path = f"/api/v1/cars/{vin}/trace-points/speed-energy"
    query_params = {
        "beginTime": begin_time,
    }
    headers = build_headers(path_vars={"vin": vin}, query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"速度能耗数据 (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_acceleration_braking(vin, begin_time):
    """查询加减速数据"""
    # begin_time 格式：yyyy-MM-dd HH:mm:ss
    path = f"/api/v1/cars/{vin}/trace-points/acceleration-braking"
    query_params = {
        "beginTime": begin_time,
    }
    headers = build_headers(path_vars={"vin": vin}, query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"加减速数据 (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_steering_wheel(vin, begin_time):
    """查询方向盘数据"""
    # begin_time 格式：yyyy-MM-dd HH:mm:ss
    path = f"/api/v1/cars/{vin}/trace-points/steering-wheel"
    query_params = {
        "beginTime": begin_time,
    }
    headers = build_headers(path_vars={"vin": vin}, query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"方向盘数据 (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_trace_view(vin, type, begin_time, end_time:Optional[str] = None):
    """
    查询行车轨迹视图（行程详情）
    types: 数据类型列表，可选值 mileage/speed/energy/airConditioner/partEnergy/driveAction 例：["speed", "energy"]
    begin_time: 格式 'yyyy-MM-dd HH:mm:ss'，内部自动转为ISO8601带时区格式
    end_time: 可选，查询里程/速度/能耗时必填
    """
    # begin_time 格式：”yyyy-MM-dd’T’HH:mm:ss.SSSXXX” ’2026-06-08T12:20:30+8 202606-08T4:20:30Z’
    # type 格式:Array[String] 可选值 mileage/speed/energy/airConditioner/partEnergy/driveAction  例：["speed", "energy"]
    path = f"/api/v1/cars/{vin}/trace-points/view"
    query_params = {
        "type": type,
        "beginTime": begin_time,
    }
    if end_time:
        query_params["endTime"] = end_time
    headers = build_headers(path_vars={"vin": vin}, query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"行程轨迹视图（行程详情） (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_connection_records(begin_time, end_time, vin, page_num=1, page_size=20):
    """查询车辆 TCP/MQ 历史记录"""
    # begin_time, end_time 格式：yyyy-MM-dd HH:mm:ss
    path = f"/api/v1/cars/{vin}/connection-records"
    query_params = {
        "beginTime": begin_time,
        "endTime": end_time,
        "vin": vin,
        "pageNum": str(page_num),
        "pageSize": str(page_size),
    }
    headers = build_headers(path_vars={"vin": vin}, query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"车辆 TCP/MQ 历史记录 (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_stat_logs(vin,begin_time, end_time,searchVal:Optional[str] = None,types:Optional[str] = None, page_num=1, page_size=10):
    """查询统计日志"""
    # begin_time, end_time 格式：20260613000000 yyyyMMddHHmmss 
    path = f"/api/v1/stat-logs"
    query_params = {
        "vin": vin,
        "beginTime": begin_time,
        "endTime": end_time,
        "pageNum": str(page_num),
        "pageSize": str(page_size),
    }
    if searchVal:
        query_params["searchVal"] = searchVal
    if types:
        query_params["types"] = types
    headers = build_headers(query_params=query_params)
    resp = requests.post(BASE_URL + path, headers=headers, json=query_params)
    print(f"统计日志 (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_remote_controls(vin,begin_time, end_time, page_num=1, page_size=20):
    """查询远程控制列表"""
    # begin_time, end_time 格式：yyyy-MM-dd HH:mm:ss
    path = f"/api/v1/cars/{vin}/remote-controls"
    query_params = {
        "vin": vin,
        "beginTime": begin_time,
        "endTime": end_time,
        "pageNum": str(page_num),
        "pageSize": str(page_size),
    }
    headers = build_headers(path_vars={"vin": vin}, query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"远程控制列表 (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def vin_search(vin):
    """按VIN 搜索车辆"""
    path = f"/api/v1/cars/search"
    query_params = {
        "vin": vin,
    }
    headers = build_headers(query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"按VIN 搜索车辆 (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_component_records(packageId,vin, page_num=1, page_size=20):
    """升级详情-查看部件"""
    path = f"/api/v1/upgrade/component-records"
    query_params = {
        "packageId":packageId,
        "vin": vin,
        "pageNum": str(page_num),
        "pageSize": str(page_size),
    }
    headers = build_headers(query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"升级详情-查看部件 (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_did_versions(vin,searchVal : Optional[str] = None, page_num=1, page_size=20):
    """DID 信息查询"""
    path = f"/api/v1/cars/{vin}/did-versions"
    query_params = {
        "vin": vin,
        "pageNum": str(page_num),
        "pageSize": str(page_size),
    }
    if searchVal:
        query_params["searchVal"] = searchVal
    headers = build_headers(path_vars={"vin": vin}, query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"DID 信息查询 (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_cars(vehicle_code, fuel_type, page_num, page_size,
                 inner_flag: Optional[str] = None, car_type: Optional[str] = None, sim_card: Optional[str] = None,
                 plate_number: Optional[str] = None, region: Optional[int] = None):
    """车辆列表查询：分页查询车辆基础信息列表，支持多条件筛选"""
    path = "/api/v1/cars"
    query_params = {
        "vehicleCode": vehicle_code,
        "fuelType": fuel_type,
        "pageNum": str(page_num),
        "pageSize": str(page_size),
    }
    if inner_flag:
        query_params["innerFlag"] = inner_flag
    if car_type:
        query_params["carType"] = car_type
    if sim_card:
        query_params["simCard"] = sim_card
    if plate_number:
        query_params["plateNumber"] = plate_number
    if region:
        query_params["region"] = str(region)
    headers = build_headers(query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"车辆列表 (page={page_num}/{page_size}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_mileage_energy(vin,begin_time, end_time):
    """查询里程能耗数据"""
    # begin_time, end_time 格式：yyyy-MM-dd HH:mm:ss
    path = f"/api/v1/cars/{vin}/route-profiles/mileage-energy"
    query_params = {
        "vin": vin,
        "beginTime": begin_time,
        "endTime": end_time
    }
    headers = build_headers(path_vars={"vin": vin}, query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"里程能耗数据 (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_records(vin, signalCode:int):
    """记录查询：通用记录查询接口"""
    path = f"/api/v1/cars/{vin}/records"
    query_params = {
        "signalCode": str(signalCode),
    }
    headers = build_headers(path_vars={"vin": vin}, query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"记录查询 (VIN={vin}, signalCode={signalCode}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def get_usage_time_daily(vin, begin_date, end_date):
    """单日用车时长：查询指定时间范围内单车每日用车时长统计"""
    # begin_date, end_date 格式：yyyy-MM-dd
    path = "/api/v1/cars/statistics/usage-time/daily"
    query_params = {
        "vin": vin,
        "beginTime": begin_date,
        "endTime": end_date,
    }
    headers = build_headers(query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print(f"单日用车时长 (VIN={vin}):")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()


def search_car_info(search_value: Optional[str] = None, area_code: Optional[str] = None, car_types: Optional[list[str]] = None):
    """车辆搜索下拉列表：模糊搜索车辆信息，用于下拉列表展示"""
    path = "/api/v1/cars/car-info/search"
    query_params = {}
    if search_value:
        query_params["searchValue"] = search_value
    if area_code:
        query_params["areaCode"] = area_code
    if car_types:
        if isinstance(car_types, (list, tuple)):
            query_params["carTypes"] = ",".join(car_types)
        else:
            query_params["carTypes"] = car_types
    headers = build_headers(query_params=query_params)
    resp = requests.get(BASE_URL + path, headers=headers, params=query_params)
    print("车辆搜索下拉列表:")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    return resp.json()



if __name__ == "__main__":
    VIN = "LFZFWK35A82950002"
    CAR_ID = 10001
    
    # 升级详情-查看部件 升级包ID
    PACKAGE_ID = "001"
    
    # 车辆列表查询
    VEHICLECODE = "LFZTESTCJJ7654321"
    FUELTYPE = "0"
    
    PAGE_NUM = 1
    PAGE_SIZE = 20
    
    # 当前时间（格式：yyyy-MM-dd HH:mm:ss.ssssss）
    NOW_TIME = datetime.now()
    # 年月日（格式：yyyy-MM-dd）
    BEGIN_TIME_YMD = (NOW_TIME - timedelta(days=1)).strftime("%Y-%m-%d")
    END_TIME_YMD = NOW_TIME.strftime("%Y-%m-%d")
    # 时分秒（格式：yyyy-MM-dd HH:mm:ss）
    BEGIN_TIME_HMS = (NOW_TIME - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    END_TIME_HMS = NOW_TIME.strftime("%Y-%m-%d %H:%M:%S")
    # 字符串格式（格式：yyyyMMddHHmmss）
    BEGIN_TIME_STR = (NOW_TIME - timedelta(days=1)).strftime("%Y%m%d%H%M%S")
    END_TIME_STR = NOW_TIME.strftime("%Y%m%d%H%M%S")
    # T格式：”yyyy-MM-dd’T’HH:mm:ss.SSSXXX”
    BEGIN_TIME_T = (NOW_TIME - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    END_TIME_T = NOW_TIME.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")
    
    print("当前时间1:",NOW_TIME)
    print("当前时间2:",BEGIN_TIME_YMD, END_TIME_YMD)
    print("当前时间3:",BEGIN_TIME_HMS, END_TIME_HMS)
    print("当前时间4:",BEGIN_TIME_STR, END_TIME_STR)
    print("当前时间5:",BEGIN_TIME_T, END_TIME_T)
    
    print("-" * 60)
    get_vehicle_status(vin=VIN)
    print("-" * 60)
    get_fire_states(car_id=CAR_ID, begin_time=BEGIN_TIME_HMS, end_time=END_TIME_HMS, page_num=PAGE_NUM, page_size=PAGE_SIZE)
    print("-" * 60)
    get_charge_states(car_id=CAR_ID, begin_time=BEGIN_TIME_HMS, end_time=END_TIME_HMS, page_num=PAGE_NUM, page_size=PAGE_SIZE)
    print("-" * 60)
    get_mileage_states(vin=VIN, begin_time=BEGIN_TIME_HMS)
    print("-" * 60)
    get_speed_energy(vin=VIN, begin_time=BEGIN_TIME_HMS)
    print("-" * 60)
    get_acceleration_braking(vin=VIN, begin_time=BEGIN_TIME_HMS)
    print("-" * 60)
    get_steering_wheel(vin=VIN, begin_time=BEGIN_TIME_HMS)
    print("-" * 60)
    get_trace_view(vin=VIN, type=["mileage", "speed", "energy"], begin_time=BEGIN_TIME_T, end_time=END_TIME_T)
    print("-" * 60)
    get_connection_records(begin_time=BEGIN_TIME_HMS, end_time=END_TIME_HMS, vin=VIN, page_num=PAGE_NUM, page_size=PAGE_SIZE)
    print("-" * 60)
    get_stat_logs(vin=VIN, begin_time=BEGIN_TIME_STR, end_time=END_TIME_STR, page_num=1, page_size=10)
    print("-" * 60)
    get_remote_controls(vin=VIN, begin_time=BEGIN_TIME_HMS, end_time=END_TIME_HMS, page_num=PAGE_NUM, page_size=PAGE_SIZE)
    print("-" * 60)
    vin_search(vin=VIN)
    print("-" * 60)
    get_component_records(packageId=PACKAGE_ID, vin=VIN, page_num=PAGE_NUM, page_size=PAGE_SIZE)
    print("-" * 60)
    get_did_versions(vin=VIN, searchVal="状态", page_num=1, page_size=20)
    print("-" * 60)
    get_cars(vehicle_code=VEHICLECODE, fuel_type=FUELTYPE, page_num=PAGE_NUM, page_size=PAGE_SIZE, inner_flag="0", car_type="D19", sim_card="898608D5982590762920", plate_number="LFZTESTCJJ7654321", region=1)
    print("-" * 60)
    get_mileage_energy(vin=VIN, begin_time=BEGIN_TIME_HMS, end_time=END_TIME_HMS)
    print("-" * 60)
    get_records(vin=VIN, signalCode=1)
    print("-" * 60)
    get_usage_time_daily(vin=VIN, begin_date=BEGIN_TIME_YMD, end_date=END_TIME_YMD)
    print("-" * 60)
    search_car_info(search_value="", area_code="", car_types=["D19"])
    print("-" * 60)