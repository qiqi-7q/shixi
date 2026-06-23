import hashlib
import json
import re
from urllib.parse import urlparse, parse_qs, parse_qsl
import time
import random
import string
import requests


from app.core.config import settings

# def generate_signature(params: dict, app_secret: str) -> str:
#     # 1. 追加 appSecret
#     params["appSecret"] = app_secret
#
#     # 2. 转换值为字符串
#     flat = {}
#     for k, v in params.items():
#         if isinstance(v, (dict, list)):
#             # JSON 序列化，key 排序
#             flat[k] = json.dumps(
#                 v, sort_keys=True, ensure_ascii=False, separators=(",", ":")
#             )
#         elif isinstance(v, list):
#             flat[k] = ",".join(str(x) for x in v)
#         elif v is None:
#             flat[k] = ""
#         else:
#             flat[k] = str(v)
#
#     # 3. 按 key 排序
#     sorted_keys = sorted(flat.keys())
#
#     # 4. 拼接
#     content = "#".join(f"{k}={flat[k]}" for k in sorted_keys)
#
#     # 5. SHA-256 + HEX
#     sha256_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
#
#     return sha256_hash  # 64 位小写十六进制字符串

# ===================== 2、接口基础信息 =====================
BASE_URL = "https://test-data-open-platform.leapmotor.com"
# 接口路径，{vin} 后面替换成真实车辆vin
API_PATH = "/api/v1/cars/LFZ63AC54TH142878/vehicle-status"
full_url = BASE_URL + API_PATH

# URL 查询参数（没有就空字典，分页/时间筛选在这里填）
query_params = {}


def parse_url_query(url: str) -> str | None:
    # 解析URL查询参数规则
    # Key       原始值         转换后
    # name      "张三"        "张三"
    # tags      ["a", "b"]  "a,b"
    # info      {"age":30,"city":"Shanghai"} {"age":30,"city":"Shanghai"} (JSON 解析后重新序列化，key 已排序)
    # id (path) "123"       "123"
    # appSecret "my_secret_key" "my_secret_key"

    # 1. 先拆分URL，拿到?后的query字符串
    parsed = urlparse(url)
    query_str = parsed.query  # 输出: name=foo&type=bar&ids=1&ids=2&empty=
    print("Query String:", query_str)
    # 按照解析URL查询参数规则，解析参数，保留empty=
    params_dict = parse_qs(query_str, keep_blank_values=True)
    print("Parsed Query Params:", params_dict)
    single_params = {
        k: ",".join(v) if v else "" for k, v in params_dict.items()
    }  # {'name': 'foo', 'type': '{"age":30,"city":"Shanghai"}', 'ids': '1,2', 'empty': ''}
    print("Single Params:", single_params)
    return "1"


def parse_path_var(url: str) -> str | None:
    """提取路径模板里所有 {变量名}"""
    # 匹配 {任意字符，非}
    parsed = urlparse(url).path
    print("Parsed Path:", parsed)
    path_vars = re.search(r"/[^/]+/(\d+)(/|$)", parsed)
    if path_vars:
        print("Path Variables:", path_vars.group(1))
        return path_vars.group(1)

    return None
    print("Path Variables:", path_vars)


# async def usage_rate() -> dict:
#     # parame = {}
#     print(2)
#     #  query获取URL中？后的所有参数，如?name=foo&type=bar
#     url = "https://xxx.com/api?name=foo&type=bar&ids=1&empty="
#     return parse_url_query(url)


# ===================== 工具函数 =====================
def get_nonce(length=16):
    """生成随机字符串 X-Nonce"""
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def get_timestamp():
    """毫秒级时间戳 X-Timestamp"""
    return str(int(time.time() * 1000))


def convert_value(v):
    """参数值标准化规则"""
    if v is None:
        return ""
    if isinstance(v, list):
        return ",".join([str(i) for i in v])
    if isinstance(v, dict):
        import json

        return json.dumps(v, sort_keys=True, separators=(",", ":"))
    return str(v)


def calc_signature(timestamp, nonce, url):
    """
    计算 X-Signature
    :param timestamp: 毫秒时间戳
    :param nonce: 随机串
    :return: sha256小写hex签名
    """
    sign_dict = {}
    # 固定头部参数
    sign_dict["timestamp"] = timestamp
    sign_dict["nonce"] = nonce
    # 路径变量
    sign_dict.update(parse_path_var(url))
    # query参数
    sign_dict.update(parse_url_query(url))
    # 密钥放进去参与签名
    sign_dict["appSecret"] = settings.PLATFORM_APP_SECRET

    # 全部值标准化
    flat = {}
    for k, v in sign_dict.items():
        flat[k] = convert_value(v)

    # key升序排列，key=value#拼接
    sorted_keys = sorted(flat.keys())
    sign_str = "#".join([f"{k}={flat[k]}" for k in sorted_keys])

    # SHA256 + HEX小写
    sha256_obj = hashlib.sha256(sign_str.encode("utf-8"))
    signature = sha256_obj.hexdigest()
    print("【签名原始拼接串】", sign_str)
    print("【生成X-Signature】", signature)
    return signature


# ===================== 3、组装请求发送 =====================
if __name__ == "__main__":
    # 1. 生成头部动态参数
    ts = get_timestamp()
    nonce_str = get_nonce()

    # 路径变量提取示例（从API_PATH里的vin拿出来）
    # path_variables = {"vin": "LFZ63AC54TH142878"}

    # 计算签名
    sign = calc_signature(timestamp=ts, nonce=nonce_str, url=full_url)

    # 请求头
    headers = {
        "X-App-Id": settings.PLATFORM_APP_ID,
        "X-Timestamp": ts,
        "X-Nonce": nonce_str,
        "X-Signature": sign,
        "Content-Type": "application/json",
    }

    # 发送GET请求
    resp = requests.get(url=full_url, headers=headers, params=query_params)
    print("\n【响应状态码】", resp.status_code)
    print("【返回数据】", resp.json())
