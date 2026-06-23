import hashlib
import json
import re
from urllib.parse import urlparse, parse_qs, parse_qsl

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


async def usage_rate() -> dict:
    # parame = {}
    print(2)
    #  query获取URL中？后的所有参数，如?name=foo&type=bar
    url = "https://xxx.com/api?name=foo&type=bar&ids=1&empty="
    return parse_url_query(url)
