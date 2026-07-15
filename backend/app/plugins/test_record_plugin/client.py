# coding=utf-8

import os
import json
import requests
import time
from requests.exceptions import RequestException


class TagCondition:
    def __init__(
            self,
            comparable=False,
            fuzzy_match=False,
            key="",
            value="",
            min_time=0,
            max_time=0,
            continuous=False
    ):
        self.comparable = comparable
        self.fuzzy_match = fuzzy_match
        self.key = key
        self.value = value
        self.min_time = min_time
        self.max_time = max_time
        self.continuous = continuous

    def to_dict(self):
        return {
            "comparable": self.comparable,
            "fuzzyMatch": self.fuzzy_match,
            "key": self.key,
            "value": self.value,
            "minTime": self.min_time,
            "maxTime": self.max_time,
            "continuous": self.continuous
        }


class TagGroup:
    def __init__(
            self,
            op_type=0,  # type: int
            group=[],  # type: list[TagGroup]
            tag=None,  # type: TagCondition
            min_time=0,  # type: int
            max_time=0  # type: int
    ):
        self.op_type = op_type
        self.group = group
        self.tag = tag
        self.min_time = min_time
        self.max_time = max_time

    def to_dict(self):
        return {
            "opType": self.op_type,
            "group": [item.to_dict() for item in self.group] if self.group is not None else [],
            "tag": self.tag.to_dict() if self.tag is not None else None,
            "minTime": self.min_time,
            "maxTime": self.max_time
        }


class Sort:
    def __init__(self, key="", value=0):
        self.key = key
        self.value = value

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value
        }


class DataSetReqParam:
    def __init__(
            self,
            parent=0,  # type: int
            set_id=0,  # type: int
            start=0,  # type: int
            size=10,  # type: int
            tag=None,  # type: TagGroup
            corner_case_tag=None,  # type: TagGroup
            kind="",  # type: str
            sort=None,  # type: list[Sort]
            filter=None  # type: dict[str,any]
    ):
        self.parent = parent
        self.set_id = set_id
        self.start = start
        self.size = size
        self.tag = tag
        self.corner_case_tag = corner_case_tag
        self.kind = kind
        self.sort = sort
        self.filter = filter

    def to_dict(self):
        return {
            "parent": self.parent,
            "setId": self.set_id,
            "start": self.start,
            "size": self.size,
            "tag": self.tag.to_dict() if self.tag else None,
            "cornerCaseTag": self.corner_case_tag.to_dict() if self.corner_case_tag else None,
            "kind": self.kind,
            "sort": [item.to_dict() for item in self.sort] if self.sort else None,
            "filter": self.filter
        }


class Desc:
    def __init__(
            self,
            project,  # type: str
            branch,  # type: str
            commit_id,  # type: str
    ):
        self.project = project
        self.branch = branch
        self.commit_id = commit_id

    def to_dict(self):
        return {
            "project": self.project,
            "branch": self.branch,
            "commitId": self.commit_id,
        }


class ReqOpInfo:
    def __init__(
            self,
            op_id=0,
            script_url="",
            script_ver="",
            image_name="",
            image_ver="",
            args=[],
            desc=None  # type: Desc
    ):
        self.op_id = op_id
        self.script_url = script_url
        self.script_ver = script_ver
        self.image_name = image_name
        self.image_ver = image_ver
        self.args = args
        self.desc = desc

    def to_dict(self):
        return {
            "opId": self.op_id,
            "scriptUrl": self.script_url,
            "scriptVer": self.script_ver,
            "imageName": self.image_name,
            "imageVer": self.image_ver,
            "args": self.args,
            "desc": self.desc.to_dict() if self.desc else None
        }


class CicdParam:
    def __init__(
            self,
            pipeline_name="",
            template_id=0,
            is_update=False,
            is_start=False,
            custom_config={},
            req_op_info=None  # type: list[ReqOpInfo]
    ):
        self.pipeline_name = pipeline_name
        self.template_id = template_id
        self.is_update = is_update
        self.is_start = is_start
        self.custom_config = custom_config
        self.req_op_info = req_op_info if req_op_info else None

    def to_dict(self):
        return {
            "pipelineName": self.pipeline_name,
            "templateId": self.template_id,
            "isUpdate": self.is_update,
            "isStart": self.is_start,
            "customConfig": self.custom_config,
            "opInfo": [item.to_dict() for item in self.req_op_info] if self.req_op_info else None
        }


class JobEnv:
    def __init__(
            self,
            image_name,  # type: str
            image_ver,  # type: str
            type,  # type: str
            device=None,  # type: str
            priority=0,  # type: int
            cpu_num=0,  # type: int
            gpu_type=None,  # type: str
            gpu_num=0  # type: int
    ):
        self.cpu_num = cpu_num
        self.gpu_type = gpu_type
        self.gpu_num = gpu_num
        self.image_name = image_name
        self.image_ver = image_ver
        self.device = device
        self.priority = priority
        self.type = type

    def to_dict(self):
        return {
            "cpuNum": self.cpu_num,
            "gpuType": self.gpu_type,
            "gpuNum": self.gpu_num,
            "imageName": self.image_name,
            "imageVer": self.image_ver,
            "device": self.device,
            "priority": self.priority,
            "type": self.type
        }


class OperatorInfo:
    def __init__(
            self,
            type,  # type: str
            data_in_type,  # type: list[str]
            worker,  # type: str
            has_prev,  # type: bool
            env,  # type: JobEnv
            ver=0,  # type: int
            data_out_type=None,  # type: list[str]
            git_command=None,  # type: str
            script_url=None,  # type: str | None
            script_ver=None,  # type: str | None
            token=None,  # type: str | None
            user=None,  # type: str | None
            passwd=None  # type: str | None
    ):
        self.type = type
        self.data_in_type = data_in_type
        self.data_out_type = data_out_type
        self.env = env
        self.script_url = script_url
        self.script_ver = script_ver
        self.ver = ver
        self.worker = worker
        self.git_command = git_command
        self.token = token
        self.user = user
        self.passwd = passwd
        self.has_prev = has_prev

    def to_dict(self):
        data = {
            "type": self.type,
            "dataInType": self.data_in_type,
            "dataOutType": self.data_out_type,
            "env": self.env.to_dict() if self.env else None,
            "scriptUrl": self.script_url,
            "scriptVer": self.script_ver,
            "ver": self.ver,
            "worker": self.worker,
            "gitCommand": self.git_command,
            "hasPrev": self.has_prev
        }
        return {k: v for k, v in data.items() if v is not None}


class OpParams:
    def __init__(
            self,
            name,  # type: str
            operator_info,  # type: OperatorInfo
            folder=0,  # type: int
            id=0,  # type: int
            args=None,  # type: list[dict[str,any]]
            introduction=None,  # type: str
            description=None,  # type: str
            file_path=None,  # type: str
            tag=None  # type: list[str]
    ):
        self.id = id
        self.name = name
        self.folder = folder
        self.operator_info = operator_info
        self.args = args
        self.introduction = introduction
        self.description = description
        self.file_path = file_path
        self.tag = tag

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "folder": self.folder,
            "operatorInfo": self.operator_info.to_dict(),
            "args": self.args,
            "introduction": self.introduction,
            "description": self.description,
            "filePath": self.file_path,
            "tag": self.tag
        }


class LabelInfo:
    def __init__(
            self,
            key,  # type: str
            value,  # type: any
    ):
        self.key = key
        self.value = value

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value
        }


class LabelWriteReq:
    def __init__(
            self,
            category,  # type: str
            version,  # type: str
            label_info,  # type: list[LabelInfo]
            case_id=0,  # type: int
            bag_id=0,  # type: int
    ):
        self.case_id = case_id
        self.bag_id = bag_id
        self.category = category
        self.version = version
        self.label_info = label_info

    def to_dict(self):
        return {
            "caseId": self.case_id,
            "bagId": self.bag_id,
            "category": self.category,
            "version": self.version,
            "labelInfo": [item.to_dict() for item in self.label_info] if self.label_info is not None else [],
        }


class CreateCaseFinderFilter:
    def __init__(self, **kwargs):
        self.set_id = kwargs.get('set_id', None)
        self.display_start_time = kwargs.get('display_start_time', None)
        self.display_end_time = kwargs.get('display_end_time', None)
        self.tag = kwargs.get('tag', None)

    def to_dict(self):
        filter_dict = {
            "setId": self.set_id,
            "tag": self.tag,
            "and": False,
            "tagMode": "property",
            "excludeCaseId": False,
            "enableInversion": False,
            "enableDeduplication": True,
        }
        if self.display_end_time is not None and self.display_start_time is not None:
            filter_dict["displayStartTime"] = self.display_start_time
            filter_dict["displayEndTime"] = self.display_end_time
        return {k: v for k, v in filter_dict.items() if v is not None}


class CreateBagFinderFilter:
    def __init__(self, **kwargs):
        self.set_id = kwargs.get('set_id', None)
        self.display_start_time = kwargs.get('display_start_time', None)
        self.display_end_time = kwargs.get('display_end_time', None)
        self.tag = kwargs.get('tag', None)

    def to_dict(self):
        filter_dict = {
            "setId": self.set_id,
            "tag": self.tag,
            "and": False,
            "tagMode": "property",
            "excludeBagId": False,
            "enableInversion": False,
            "enableDeduplication": True,
        }
        if self.display_end_time is not None and self.display_start_time is not None:
            capture_time = {
                "displayStartTime": self.display_start_time,
                "displayEndTime": self.display_end_time
            }
            filter_dict["captureTime"] = capture_time
        return {k: v for k, v in filter_dict.items() if v is not None}


class CreateImageFinderFilter:
    def __init__(self, **kwargs):
        self.set_id = kwargs.get('set_id', None)
        self.display_start_time = kwargs.get('display_start_time', None)
        self.display_end_time = kwargs.get('display_end_time', None)
        self.tag = kwargs.get('tag', None)

    def to_dict(self):
        filter_dict = {
            "setId": self.set_id,
            "excludeImageName": False,
            "enableInversion": False,
            "enableDeduplication": True,
        }
        if self.display_end_time is not None and self.display_start_time is not None:
            overlap_time = {
                "displayStartTime": self.display_start_time,
                "displayEndTime": self.display_end_time
            }
            filter_dict["overlapTime"] = overlap_time
        return {k: v for k, v in filter_dict.items() if v is not None}


class APIClient:
    def __init__(self, base_url, token=None, debug=False):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json", "User-Agent": "python-client"}
        self.token = token or self.get_token_from_file()
        self.debug = debug
        self.finder = {}

    def do_request(self, endpoint, body):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(url, headers=self.headers, json=body, cookies={"token": self.token})
            if 'token' in response.cookies and response.cookies['token'] != self.token:
                self.token = response.cookies['token']
                if self.debug:
                    self.update_token_in_file(self.token)
            if response.text:
                return response.json()
        except RequestException as e:
            return {"error": {"code": -1, "message": f"Request failed: {e}"}}

    def get_token_from_file(self):
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "token.json")
        if not file_path:
            raise ValueError("no $TrainParamsJson")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            return content.get('token')
        except Exception as e:
            raise ValueError(f"Failed to load token from file: {e}")

    def update_token_in_file(self, new_token):
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "token.json")
        if not file_path:
            raise ValueError("no $TrainParamsJson")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            data['token'] = new_token
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            raise ValueError(f"Failed to update token in file: {e}")

    def get_vehicle_info(self, vehicle_id):
        """
        获取车辆基本信息
        :param vehicle_id: 车辆id
        :return: 车辆基本信息
        正常响应示例
        {
            "result": {
                "id": 1000,
                "name": "Car05",
                "model": "C11-纯电",
                "vin": "LFZ63AL45MD004265",
                "number": "浙AAU8338",
                "type": "real",
                "diffTime": 28800,  # 与零时区的时差，单位：秒
                "systemArch": "eea3.5"   # 系统架构
            }
        }

        异常响应示例
        {
            "error": {
                "code": 104,
                "message": "记录不存在"
            }
        }
        """
        body = {
            "id": vehicle_id
        }
        return self.do_request("/data-mgr/vehicle/info", body)

    def get_vehicle_detail(self, hardware_id):
        """
        获取车辆采集设备信息
        :param hardware_id: 车辆硬件id
        :return: 车辆硬件相关信息
        正常响应示例
         {
            "result": {
                "hardWareInfo": {
                    "id": 1241,
                    "vehicle": 1000,
                    "sensor": [
                        {
                            "type": "摄像头",
                            "name": "Cam-FrontWide",
                            "model": "SG8-AR0820C-5300-GSML2-H120Y",
                            "supplier": "森云",
                            "dataType": "",
                            "desc": "前视广角",
                            "version": ""
                        },
                        {
                            "type": "其他",
                            "name": "Chassis",
                            "model": "C11",
                            "supplier": "Leapmotor",
                            "dataType": "",
                            "desc": "车身",
                            "version": ""
                        }
                    ],
                    "parseFile": "http://bkrepo.leapmotor.com/generic/intelligent-cockpit/custom/Artifacts/LP-ALG-DATA-PLATFORM/SourceDataPreprocessing/SourceDataPreprocessing@1.35.00",
                    "desc": "昆易数采工控机-修改2",
                    "image": "",
                    "startTime": 1704470400,
                    "endTime": 1738252800,
                    "displayStartTime": 1704499200,
                    "displayEndTime": 1738281600,
                    "state": "normal"
                },
                "softWareInfo": [
                    {
                        "id": 1242,
                        "hardware": 1241,
                        "calibrate": "/dataSet/resource/calibrate/1242",
                        "desc": "更新lidar2camera",
                        "startTime": 1712764800,
                        "endTime": 1712880000,
                        "displayStartTime": 1712793600,
                        "displayEndTime": 1712908800
                    }
                ]
            }
        }

        异常响应示例
        {
            "error": {
                "code": 104,
                "message": "记录不存在"
            }
        }
        """
        body = {
            "id": hardware_id
        }
        return self.do_request("/data-mgr/vehicle/detail", body)

    def get_pack_info(self, pack_id):
        """
        查看指定原始文件包信息
        :param pack_id: 原始文件包id
        :return: 原始文件包信息
        正常响应示例
        {
            "result": {
                "id": 1416,
                "vehicle": 1315,
                "hardware": 1318,
                "software": 1319,
                "year": 2024,
                "month": 5,
                "day": 18,
                "createTime": 1716021322,
                "startTime": 1716028378110000,
                "endTime": 1716028677176000,
                "displayStartTime": 1716028378110000,
                "displayEndTime": 1716028677176000,
                "path": "/originalData/1315/2024/05/18/20240518103257",
                "sensorData": [
                    {
                        "name": "Imu",
                        "csv": [
                            {
                                "name": "20240518103257_imu_data_PBOX.csv",
                                "size": 3946303,
                                "modifyTime": 1716019961
                            }
                        ],
                        "startTime": 1716028378110430,
                        "endTime": 1716028677176765,
                        "displayStartTime": 1716028378110430,
                        "displayEndTime": 1716028677176765
                    },
                    {
                        "name": "Ins",
                        "csv": [
                            {
                                "name": "20240518103257_ins_data_PBOX.csv",
                                "size": 10535355,
                                "modifyTime": 1716019965
                            }
                        ],
                        "startTime": 1716028378110507,
                        "endTime": 1716028677186847,
                        "displayStartTime": 1716028378110507,
                        "displayEndTime": 1716028677186847
                    }
                ],
                "tag": [
                    {
                        "source": "检验&解析-804",
                        "sensor": "pack",
                        "key": "packComplete",
                        "value": "incomplete",
                        "startTime": 1716028378110000,
                        "endTime": 1716028677176000,
                        "displayStartTime": 0,
                        "displayEndTime": 0
                    }
                ],
                "size": 1657144691,
                "uploadTaskId": 0,
                "pipelineId": 0,
                "demandInfo": {
                    "templateId": 0,
                    "recordId": 0
                }
            }
        }

        异常响应示例
        {
            "error": {
                "code": 104,
                "message": "记录不存在"
            }
        }
        """
        body = {
            "packId": pack_id
        }
        return self.do_request("/data-mgr/stream/pack-info", body)

    def find_pack_infos(self, start=0, size=1, sort=[{"key": "displayStartTime", "value": 1}, {"key": "_id", "value": -1}], filter={}):
        """
        分页获取原始文件包列表
        :param start: 从第几个开始（用于分页展示）
        :param size: 展示几个（用于分页展示）
        :param sort: 排序字段，支持按原始文件名称、上传时间、采集起始和结束时间、硬件、软件版本等字段排序
        :param filter: 过滤字段，支持按车辆id、采集时间戳范围过滤
        {
            "vehicleId": 1000,
            "startTime": 1694416306282000,
            "endTime": 1694416307282000
        }
        :return: 原始文件包列表
        正常响应示例：
        {
            "result": {
                "total": 1,
                "infos": [{
                    "id": 1551,
                    "vehicle": 1000,
                    "hardware": 1241,
                    "software": 1242,
                    "year": 2024,
                    "month": 6,
                    "day": 14,
                    "createTime": 1718608150,
                    "startTime": 1718328989202000,
                    "endTime": 1718329289208000,
                    "displayStartTime": 1718357789202000,
                    "displayEndTime": 1718358089208000,
                    "path": "/originalData/1000/2024/06/14/20240614093629",
                    "sensorData": [{
                            "name": "Gnss+imu",
                            "asc": {
                                "name": "20240614093629_can3_IMU.asc",
                                "size": 18980390,
                                "modifyTime": 1718607677
                            },
                            "csv": [{
                                    "name": "20240614093629_can3_IMU_Gnss.csv",
                                    "size": 713659,
                                    "modifyTime": 1718607856
                                }
                            ],
                            "startTime": 1718328989202000,
                            "endTime": 1718329289208854,
                            "displayStartTime": 0,
                            "displayEndTime": 0
                        }

                    ],
                    "size": 22637352068,
                    "uploadTaskId": 0,
                    "pipelineId": 0,
                    "demandInfo": {
                        "templateId": 0,
                        "recordId": 0
                    }
                }]
            }
        }

        异常响应示例
        {
            "error": {
                "code": 104,
                "message": "记录不存在"
            }
        }
        """
        body = {
            "start": start,
            "size": size,
            "sort": sort,
            "filter": filter
        }
        return self.do_request("/data-mgr/stream/find", body)

    def list_pcd_streams(self, id, streamId=0, sensor="", startTime=0, endTime=0, start=0, size=1):
        """
        分页获取指定原始文件包下的pcd列表
        :param id: 原始包id
        :param streamId: 车辆id
        :param sensor: 采集设备名称
        :param startTime: 起始时间
        :param endTime: 结束时间
        :param start: 从第几个开始（用于分页展示）
        :param size: 展示几个（用于分页展示）
        :return: pcd列表
        正常响应示例：
        {
            "result": {
                "total": 2996,
                "infos": [{
                        "streamId": 1000,
                        "packId": 1088,
                        "sensor": "Lidar-Front",
                        "timestamp": 1712798337452894,
                        "displayTimestamp": 1712827137452894,
                        "data": {
                            "name": "/originalData/1000/2024/04/11/20240411091856/pcd_AT128/1000_Lidar-Front_20240411_011857_1712798337.452894.pcd",
                            "size": 2587196,
                            "modifyTime": 1714273427
                        },
                        "label": {
                            "name": "",
                            "size": 0,
                            "modifyTime": -62135596800
                        }
                    }
                ]
            }
        }

        异常响应示例
        {
            "error": {
                "code": 104,
                "message": "记录不存在"
            }
        }
        """
        body = {
            "id": id,
            "streamId": streamId,
            "sensor": sensor,
            "startTime": startTime,
            "endTime": endTime,
            "start": start,
            "size": size,
        }
        return self.do_request("/data-mgr/stream/list-pcd", body)

    def set_stream_tag(self, packId=[], tag=[], isTagCover=True, fullCover=False):
        """
        设置原始文件包标签
        :param packId: 原始包id
        :param tag: 打的标签信息
        :param isTagCover: 是否覆盖
        :param fullCover: 全量覆盖
        :return: None
        正常响应示例：
        {
	        "result": null
        }

        异常响应示例
        {
            "error": {
                "code": 105,
                "message": "参数无效"
            }
        }
        """
        body = {
            "packId": packId,
            "tag": tag,
            "isTagCover": isTagCover,
            "fullCover": fullCover,
        }
        return self.do_request("/data-mgr/stream/tag/set", body)

    def search_data_set(self, param: DataSetReqParam):
        """
        数据集查询

        请求示例：
        {
            "size": 10,
            "start": 0,
            "kind": "case_pool",
            "filter": {
                "name": {
                    "$regex": "B"
                }
            },
            "tag": {
                "group": [
                    {
                        "opType": 2,
                        "group": [
                            {
                                "opType": 2,
                                "tag": {
                                    "key": "modelType",
                                    "value": "dynamicBEV",
                                    "fuzzyMatch": false
                                }
                            }
                        ]
                    }
                ]
            },
            "cornerCaseTag": {
                "group": [

                ]
            },
            "parent": 1032,
            "sort": [
                {
                    "key": "createTime",
                    "value": -1
                },
                {
                    "key": "_id",
                    "value": -1
                }
            ]
        }

        正常响应示例：
        {
            "result": {
                "total": 1,
                "infos": [
                    {
                        "id": 1046,
                        "parent": 1032,
                        "name": "BEV静态",
                        "kind": "case_pool",
                        "perm": {
                            "user": {
                                "1025": 2147483647,
                                "1039": 1
                            },
                            "group": {}
                        },
                        "desc": "BEV静态",
                        "from": 0,
                        "creator": 1025,
                        "createTime": 1714034276,
                        "modifyTime": 1718616155,
                        "syncTime": -62135596800,
                        "state": "",
                        "quotaId": "",
                        "tag": [
                            {
                                "source": "manual",
                                "sensor": "",
                                "key": "SpecialPoleBoard",
                                "value": "MultiBoardBondPole",
                                "startTime": 0,
                                "endTime": 0,
                                "displayStartTime": 0,
                                "displayEndTime": 0
                            },
                            {
                                "source": "manual",
                                "sensor": "",
                                "key": "modelType",
                                "value": "dynamicBEV",
                                "startTime": 0,
                                "endTime": 0,
                                "displayStartTime": 0,
                                "displayEndTime": 0
                            }
                        ],
                        "cornerCaseTag": [
                            {
                                "source": "manual",
                                "sensor": "",
                                "key": "Weather",
                                "value": "Overcast",
                                "startTime": 0,
                                "endTime": 0,
                                "displayStartTime": 0,
                                "displayEndTime": 0
                            }
                        ],
                        "recycleTime": -62135596800,
                        "path": ""
                    }
                ]
            }
        }

        异常响应示例
        {
            "error": {
                "code": 105,
                "message": "参数无效"
            }
        }
        """
        return self.do_request("/data-mgr/case/node/list", param.to_dict())

    def create_data_set(self, parent, name: str, kind: str, desc: str):
        """
        创建数据集
        :param parent: 父节点id
        :param name: 数据集名称
        :param kind: 类型（数据集、训练/测试交付集，训练/测试集）
        :param desc: 描述

        正常响应示例：
        {
            "result": {
                "id": 3741,
                "parent": 1034,
                "name": "1111",
                "kind": "train_delivery",
                "perm": {
                    "user": {
                        "1025": 2147483647
                    },
                    "group": {}
                },
                "desc": "1111",
                "from": 0,
                "creator": 1025,
                "createTime": 1739864438,
                "modifyTime": 1739864438,
                "syncTime": -62135596800,
                "state": "",
                "quotaId": "",
                "tag": [],
                "cornerCaseTag": [],
                "recycleTime": -62135596800,
                "path": "/dataset-2/set/1034/3741"
            }
        }

        异常响应示例
        {
            "error": {
                "code": 105,
                "message": "参数无效"
            }
        }
        """
        body = {
            "parent": parent,
            "name": name,
            "kind": kind,
            "desc": desc,
        }
        return self.do_request("/data-mgr/case/node/create", body)

    def get_temp_ver_dataset(self, setId):
        """
        获取训练/测试交付集，训练/测试集临时版本
        :param setId: 训练/测试交付集，训练/测试集id
        """
        body = {
            "parent": setId,
            "start": 0,
            "size": 1,
        }
        response = self.do_request("/data-mgr/case/node/list", body)
        if 'error' in response:
            return response
        else:
            print(response)
            if response['result']['infos'] and response['result']['infos'][0]:
                if response['result']['infos'][0]['kind'] == 'ver' and response['result']['infos'][0]['state'] == 'temp':
                    return {'result': response['result']['infos'][0]}
                else:
                    return {'error': {'code': -2, "message": "no temp ver dataset. please check your setId"}}
            else:
                return {'error': {'code': -2, "message": "no temp ver dataset. please check your setId"}}

    def save_temp_ver_dataset(self, srcId, desc: str):
        """
        保存编辑版本数据集为正式版本
        :param id: 版本id
        :param desc: 版本描述

        正常响应示例：
        {
	        "result": null
        }

        异常响应示例
        {
            "error": {
                "code": 105,
                "message": "参数无效"
            }
        }
        """
        body = {
            "srcId": srcId,
            "desc": desc,
        }
        return self.do_request("/data-mgr/case/set/clone", body)

    def get_case_info(self, set_id=0, case_ids=[]):
        """
        获取case信息
        :param set_id: case集id、训练集或测试集版本id（非必填，不传时查询有读权限的集合）
        :param case_ids: 想要查看的caseId数组（长度必须<=1000）
        :return: case列表
        正常响应示例
        {
            "result": [
                {
                    "setId": 1045,
                    "kind": "case_pool",
                    "caseId": 1395,
                    "vehicle": 1000,
                    "hardware": 1241,
                    "software": 1313,
                    "createTime": 1714283428,
                    "startTime": 1712798396489000,
                    "endTime": 1712798456336000,
                    "displayStartTime": 1712827196489000,
                    "displayEndTime": 1712827256336000,
                    "path": "/dataSet/case/0/0/1395",
                    "sensorData": [
                        {
                            "name": "Cam-Back",
                            "video": {
                                "name": "20240411091856_video_05_Back.mkv",
                                "size": 395444161,
                                "modifyTime": 1719824153
                            },
                            "startTime": 1712798396489000,
                            "endTime": 1712798456390000,
                            "displayStartTime": 1712827196489000,
                            "displayEndTime": 1712827256390000
                        }
                    ],
                    "extraVer": [
                        {
                            "name": "3DStaticReconstruction-2482",
                            "pipelineId": 9351,
                            "createTime": 1730424602,
                            "tag": []
                        }
                    ],
                    "state": "",
                    "pipeline": {
                        "id": 1067,
                        "attr": "public"
                    },
                    "genVer": "生成case-822",
                    "inSet": {
                        "1045": {
                            "path": "/3D感知/BEV动态"
                        }
                    },
                    "inTime": 1730690863,
                    "redmineURL": [],
                    "labelInfo": ""
                }
            ]
        }

        异常响应示例
        {
            "error": {
                "code": 104,
                "message": "记录不存在"
            }
        }
        """
        body = {
            "setId": set_id,
            "caseId": case_ids,
        }
        return self.do_request("/data-mgr/case/info", body)

    def list_cases(self, set_id, start=0, size=1, sort=[{"key": "inTime", "value": -1}, {"key": "_id", "value": -1}], filter={}):
        """
        分页获取指定集合下的case列表
        :param set_id: case集id、训练集或测试集版本id
        :param start: 从第几个开始（用于分页展示）
        :param size: 展示几个（用于分页展示，必须>0）
        :param sort: 排序字段，支持按caseId,名称，生成时间等字段排序
        :param filter：过滤字段，支持按车辆id、采集时间戳范围过滤
        {
            "vehicleId": 1000,
            "startTime": 1712814113725000,
            "endTime": 1712814173623000
        }
        :return: case列表
        正常响应示例：
        {
            "result": {
                "total": 1,
                "infos": [
                    {
                        "setId": 2265,
                        "kind": "case_pool",
                        "caseId": 1185,
                        "vehicle": 1000,
                        "hardware": 1241,
                        "software": 1313,
                        "createTime": 1714131775,
                        "startTime": 1712814113725000,
                        "endTime": 1712814173623000,
                        "displayStartTime": 1712842913725000,
                        "displayEndTime": 1712842973623000,
                        "path": "/dataSet/case/0/0/1185",
                        "sensorData": [
                            {
                                "name": "Cam-Back360",
                                "video": {
                                    "name": "20240411133953_video_01_Back360.mkv",
                                    "size": 391257653,
                                    "modifyTime": 1714131693
                                },
                                "startTime": 1712814113684000,
                                "endTime": 1712814174353000,
                                "displayStartTime": 1712842913684000,
                                "displayEndTime": 1712842974353000
                            }
                        ],
                        "tag": [
                            {
                                "source": "manual",
                                "sensor": "pack",
                                "key": "BasicRoadStructure",
                                "value": "Highway",
                                "startTime": 1712814113725000,
                                "endTime": 1712814173623000,
                                "displayStartTime": 1712842913725000,
                                "displayEndTime": 1712842973623000
                            }
                        ],
                        "extraVer": [
                            {
                                "name": "lly_sleep-2661",
                                "pipelineId": 9127,
                                "createTime": 1728884727,
                                "tag": {}
                            }
                        ],
                        "state": "",
                        "pipeline": {
                            "id": 1045,
                            "attr": "public"
                        },
                        "genVer": "生成case-822",
                        "inSet": {},
                        "inTime": 1728522607,
                        "redmineURL": [],
                        "labelInfo": ""
                    }
                ]
            }
        }

        异常响应示例
        {
            "error": {
                "code": 104,
                "message": "记录不存在"
            }
        }
        """
        body = {
            "setId": set_id,
            "start": start,
            "size": size,
            "sort": sort,
            "filter": filter
        }
        return self.do_request("/data-mgr/case/list", body)

    def list_pcd_case(self, case_id, sensor="", start=0, size=1):
        """
        分页获取指定case下的pcd列表
        :param case_id: case id
        :param sensor: 采集设备名称
        :param start: 从第几个开始（用于分页展示）
        :param size: 展示几个（用于分页展示）
        :return: pcd列表
        正常响应示例
        {
            "result": {
                "total": 600,
                "infos": [
                    {
                        "streamId": 1337,
                        "caseId": 23929,
                        "sensor": "Lidar-Front",
                        "timestamp": 1726940412510006,
                        "displayTimestamp": 1726940412510006,
                        "data": {
                            "name": "/dataSet/pcd/1337/Lidar-Front/20240921/1337_Lidar-Front_20240921_174012_1726940412.510006.pcd",
                            "size": 2085604,
                            "modifyTime": 1727181211
                        },
                        "label": {
                            "name": "",
                            "size": 0,
                            "modifyTime": -62135596800
                        }
                    }
                ]
            }
        }

        异常响应示例
        {
            "error": {
                "code": 102,
                "message": "数据库出错"
            }
        }
        """
        body = {
            "caseId": case_id,
            "sensor": sensor,
            "start": start,
            "size": size,

        }
        return self.do_request("/data-mgr/case/list-pcd", body)

    def set_case_tag(self, caseId=[], tag=[], isTagCover=True, fullCover=False):
        """
        设置case包标签
        :param caseId: case的Id数组
        :param tag: 想要打上的新标签
        :param isTagCover: 是否覆盖
        :param fullCover: 全量覆盖
        :return: None
        正常响应示例：
        {
	        "result": null
        }

        异常响应示例
        {
            "error": {
                "code": 105,
                "message": "参数无效"
            }
        }
        """
        body = {
            "caseId": caseId,
            "tag": tag,
            "isTagCover": isTagCover,
            "fullCover": fullCover,
        }
        return self.do_request("/data-mgr/case/tag/set", body)

    def get_case_adjoining(self, setId, caseId, range, type):
        """
        获取指定case的前后序case
        :param setId: 在该setId数据集内查询指定case的前后case
        :param caseId: 要查询的caseID
        :param range: 查询范围，最大60s。eg：{range:60,type:0}，查询指定case前60s范围内的case。
        :param type: 查询类型，0：前序case，1：后序case，2：both
        """
        body = {
            "caseId": caseId,
            "setId": setId,
            "range": range,
            "type": type,
        }
        return self.do_request("/data-mgr/case/adjoining", body)

    def list_case_images(self, set_id, start=0, size=1, sort=[{"key": "displayTimestamp", "value": 1}, {"key": "_id", "value": -1}], filter={}):
        """
        分页获取指定集合下的图片列表
        :param set_id: 图片集id、训练集或测试集版本id
        :param start: 从第几个开始（用于分页展示）
        :param size: 展示几个（用于分页展示）
        :param sort: 排序字段，支持按图片名称、大小、生成任务Id、采集车、采集设备、采集/生成/加入时间等字段排序
        :param filter: 过滤字段，支持按车辆id、采集设备名称、起始采集时间戳范围过滤
        {
            "vehicle": 1012,
            "sensor": "Cam-FrontWide",
            "display_timestamp": {
                "$gte": 1713571200000000,
                "$lte": 1713657599000000
            }
        }
        :return: 图片列表
        正常响应示例：
        {
            "result": {
                "total": 1,
                "infos": [
                    {
                        "setId": 3161,
                        "kind": "case_pool",
                        "vehicle": 1012,
                        "software": 1244,
                        "sensor": "Cam-FrontWide",
                        "timestamp": 1713545117213566,
                        "displayTimestamp": 1713573917213566,
                        "file": {
                            "name": "/dataSet/video/frame/1012/Cam-FrontWide/20240420/Car07_20240420_004517_1713545117.213566_FrontWide.jpg",
                            "size": 2087215,
                            "modifyTime": 1714273197
                        },
                        "extraFile": {
                            "name": "/compliance-data/video/frame/1012/Cam-FrontWide/20240420/Car07_20240420_004517_1713545117.213566_FrontWide.jpg",
                            "size": 780950,
                            "modifyTime": 1721025201
                        },
                        "pipeline": {
                            "id": 1066,
                            "attr": "private"
                        },
                        "inSet": {},
                        "inTime": 1728955728,
                        "labelInfo": ""
                    }
                ]
            }
        }

        异常响应示例
        {
            "error": {
                "code": 104,
                "message": "记录不存在"
            }
        }
        """
        body = {
            "setId": set_id,
            "start": start,
            "size": size,
            "sort": sort,
            "filter": filter,
        }
        return self.do_request("/data-mgr/case/list-image", body)

    def get_bag_info(self, set_id, bag_ids):
        """
        查看指定集合下的bag信息
        :param set_id: bag集id、训练集或测试集版本id
        :param bag_ids: 想要查看的bagId数组（长度必须<=1000）
        :return: bag列表
        正常响应示例：
        {
            "result": [
                {
                    "bagId": 2167,
                    "setId": 2684,
                    "kind": "case_pool",
                    "name": "record_data_20240511_16_25_34",
                    "path": "/bag-data/0/0/2167",
                    "vehicleId": 1315,
                    "vin": "LFZ63AN53PD000241",
                    "createTime": 1726122013,
                    "startTime": 1715444742446000,
                    "endTime": 1715444861069000,
                    "displayStartTime": 1715444742446000,
                    "displayEndTime": 1715444861069000,
                    "tag": [
                        {
                            "source": "BagDataPreprocessing-2639",
                            "sensor": "pack",
                            "key": "car_type",
                            "value": "B11",
                            "startTime": 1715444742446845,
                            "endTime": 1715444861069073,
                            "displayStartTime": 1715444742446845,
                            "displayEndTime": 1715444861069073
                        }
                    ],
                    "extraVer": [],
                    "pipelineInfo": {
                        "id": 8836,
                        "attr": "private"
                    },
                    "uploadId": 1673,
                    "inSet": {
                        "2684": {
                            "path": "/bag/bag_round_6"
                        }
                    },
                    "inTime": 1726122013,
                    "redmineURL": [],
                    "status": "success",
                    "labelInfo": ""
                }
            ]
        }

        异常响应示例
        {
            "error": {
                "code": 104,
                "message": "记录不存在"
            }
        }
        """
        body = {
            "setId": set_id,
            "bagId": bag_ids
        }
        return self.do_request("/data-mgr/bag/info", body)

    def list_bags(self, set_id, start=0, size=1, sort=[{"key": "inTime", "value": -1}, {"key": "_id", "value": -1}], filter={}):
        """
        分页获取指定集合下的bag列表
        :param set_id: bag集id、训练集或测试集版本id
        :param start: 从第几个开始（用于分页展示）
        :param size: 展示几个（用于分页展示，必须>0）
        :param sort: 排序字段，支持按bagId、名称、生成时间等字段排序
        :param filter: 过滤字段，支持按车辆id、采集时间戳范围过滤
        {
            "vehicleId": 1000,
            "startTime": 1694416306282000,
            "endTime": 1694416307282000
        }
        :return: bag列表
        正常响应示例：
        {
            "result": {
                "total": 1,
                "infos": [
                    {
                        "bagId": 2582,
                        "setId": 1173,
                        "kind": "case_pool",
                        "name": "2582_record_data_20240725_09_19_56",
                        "path": "/bag-data-develop/0/0/2582",
                        "vehicleId": 1000,
                        "vin": "",
                        "createTime": 1721870396,
                        "startTime": 1694416306282000,
                        "endTime": 1694416307282000,
                        "displayStartTime": 1694445106282000,
                        "displayEndTime": 1694445107282000,
                        "tag": [
                            {
                                "source": "生成新bag不删旧bag示例-2526",
                                "sensor": "pack",
                                "key": "key1",
                                "value": "value1",
                                "startTime": 1694416306282000,
                                "endTime": 1694416307282006,
                                "displayStartTime": 1694445106282000,
                                "displayEndTime": 1694445107282006
                            }
                        ],
                        "extraVer": [
                            {
                                "name": "补充bag原始文件示例-2507",
                                "pipelineId": 14567,
                                "createTime": 1727353623,
                                "tag": {}
                            }
                        ],
                        "pipelineInfo": {
                            "id": 11178,
                            "attr": ""
                        },
                        "uploadId": 0,
                        "inSet": {},
                        "inTime": 1721870396,
                        "redmineURL": [],
                        "status": "success",
                        "labelInfo": ""
                    }
                ]
            }
        }

        异常响应示例
        {
            "error": {
                "code": 104,
                "message": "记录不存在"
            }
        }
        """
        body = {
            "setId": set_id,
            "start": start,
            "size": size,
            "sort": sort,
            "filter": filter
        }
        return self.do_request("/data-mgr/bag/list", body)

    def get_next_bag_id(self):
        """
        用于生成新bag时获取新bag的Id与存放路径
        :return: 新bag的bagId，名称，路径，bag包路径
        正常响应示例：
        {
            "result": {
                "bagId": 2300,
                "name": "2300_record_data_20241016_14_55_06",
                "path": "/bag-data/0/0/2300",
                "bagPath": "/bag-data/0/0/2300/2300_record_data_20241016_14_55_06"
            }
        }

        异常响应示例
        {
            "error": {
                "code": 888888,
                "message": "登录过期"
            }
        }
        """
        return self.do_request("/data-mgr/bag/next-id", {})

    def set_bag_tag(self, bagId=[], tag=[], isTagCover=True, fullCover=False):
        """
        设置bag包标签
        :param bagId: bag的Id数组
        :param tag: 想要打上的新标签
        :param isTagCover: 是否覆盖
        :param fullCover: 全量覆盖
        :return: None
        正常响应示例：
        {
	        "result": null
        }

        异常响应示例
        {
            "error": {
                "code": 105,
                "message": "参数无效"
            }
        }
        """
        body = {
            "bagId": bagId,
            "tag": tag,
            "isTagCover": isTagCover,
            "fullCover": fullCover,
        }
        return self.do_request("/data-mgr/bag/tag/set", body)

    def get_object(self, ver, stream_id, start_time, end_time, category: str = "", filter={}, fields=[]):
        """
        获取标注对象
        :param ver: 标注版本
        :param stream_id: 车辆id
        :param category: 业务来源，读取latest版本必传
        :param start_time: 起始时间，单位：us，例：1712813702175792
        :param end_time: 结束时间，单位：us，例：1712813702175792
        :param filter: 过滤条件，例如{"ver":1}，批量查询时间戳{"timestamp":{"$in":[213123,32131]}}
        :param fields: 过滤需要返回的字段,为空时返回所有字段
        :return: 标注数据信息
        正常响应示例
        {
            "result": [
                {
                    "ver": 1005,
                    "streamId": 1000,
                    "sensor": "Cam-FrontWide",
                    "mediaType": 1,
                    "imgSize": [
                        3840,
                        2160
                    ],
                    "timestamp": 1712813702175792,
                    "object": [
                        {
                            "originId": 103,
                            "id": 3,
                            "instId": 0,
                            "class": "WhiteSolidLine",
                            "shape": "mask",
                            "coords": [
                                [
                                    1954,
                                    1700
                                ],
                                [
                                    2017,
                                    1759
                                ]
                            ],
                            "prop": [],
                            "extra": {
                                "taskId": 1045
                            },
                            "rle": "28 12 91 12 154 12 217 12 276 20 339 20 402 20 465 20 528 24 591 24 654 24 717 24 776 36 839 36 902 36 965 36 1028 40 1091 40 1154 40 1217 40 1276 47 1339 47 1402 47 1465 47 1528 47 1591 47 1654 47 1717 47 1776 51 1839 51 1902 51 1965 51 2028 48 2091 48 2154 48 2217 48 2276 52 2339 52 2402 52 2465 52 2528 52 2591 52 2654 52 2717 52 2780 48 2843 48 2906 48 2969 48 3028 52 3091 52 3154 52 3217 52 3280 52 3343 52 3406 52 3469 52 3528 56 3591 56 3654 56",
                            "maskId": 6
                        }
                    ]
                }
            ]
        }

        异常响应示例
        {
            "error": {
                "code": 105,
                "message": "参数无效"
            }
        }
        """
        body = {
            "ver": ver,
            "streamId": stream_id,
            "category": category,
            "startTime": start_time,
            "endTime": end_time,
            "filter": filter,
            "fields": fields,
        }
        return self.do_request("/data-mgr/label/object/get", body)

    def read_label(self, ver, stream_id, start_time, end_time, category: str = "", filter={}, fields=[]):
        """
        读取标注数据，并拿到handle用于分批读取数据
        :param ver: 标注版本
        :param stream_id: 车辆id
        :param category: 业务来源，读取latest版本必传
        :param start_time: 起始时间，单位：us，例：1712813702175792
        :param end_time: 结束时间，单位：us，例：1712813702175792
        :param filter: 过滤条件，例如{"ver":1}，批量查询时间戳{"timestamp":{"$in":[213123,32131]}}
        :param fields: 过滤需要返回的字段,为空时返回所有字段
        :return: 标注数据信息
        正常响应示例
        {
            "result": {
                "infos": [
                    {
                        "ver": 1005,
                        "streamId": 1000,
                        "sensor": "Cam-FrontWide",
                        "mediaType": 1,
                        "imgSize": [
                            3840,
                            2160
                        ],
                        "timestamp": 1712813702175792,
                        "object": [
                            {
                                "originId": 101,
                                "id": 1,
                                "instId": 0,
                                "class": "WhiteDottedLine",
                                "shape": "mask",
                                "coords": [
                                    [
                                        510,
                                        1384
                                    ],
                                    [
                                        1485,
                                        1759
                                    ]
                                ],
                                "prop": [],
                                "extra": {
                                    "taskId": 1045
                                },
                                "rle": "960 12 1935 12 2910 12 3885 12 4840 35 5815 35 6790 35 7765 35 8732 40 9707 40 10682 40 11657 40 12620 40 13595 40 14570 40 15545 40 16512 40 17487 40 18462 40 19437 40 20400 40 21375 40 22350 40 23325 40 24292 40 25267 40 26242 40 27217 40 28180 44 29155 44 30130 44 31105 44 32072 40 33047 40 34022 40 34997 40 35960 44 36935 44 37910 44 38885 44 39852 44 40827 44 41802 44 42777 44 43740 44 44715 44 45690 44 46665 44 47632 44 48607 44 49582 44 50557 44 51520 44 52495 44 53470 44 54445 44 55412 44 56387 44 57362 44 58337 44 59300 48 60275 48 61250 48 62225 48 63192 44 64167 44 65142 44 66117 44 67084 44 68059 44 69034 44 70009 44 70972 48 71947 48 72922 48 73897 48 74860 48 75835 48 76810 48 77785 48 78752 48 79727 48 80702 48 81677 48 82640 48 83615 48 84590 48 85565 48 86532 48 87507 48 88482 48 89457 48 90424 48 91399 48 92374 48 93349 48 94312 48 95287 48 96262 48 97237 48 98204 48 99179 48 100154 48 101129 48 102092 48 103067 48 104042 48 105017 48 105984 48 106959 48 107934 48 108909 48 109872 52 110847 52 111822 52 112797 52 113760 52 114735 52 115710 52 116685 52 117652 52 118627 52 119602 52 120577 52 121540 52 122515 52 123490 52 124465 52 125432 52 126407 52 127382 52 128357 52 129320 52 130295 52 131270 52 132245 52 133212 52 134187 52 135162 52 136137 52 137100 52 138075 52 139050 52 140025 52 140988 56 141963 56 142938 56 143913 56 144880 52 145855 52 146830 52 147805 52 148768 56 149743 56 150718 56 151693 56 152660 52 153635 52 154610 52 155585 52 156548 56 157523 56 158498 56 159473 56 160440 52 161415 52 162390 52 163365 52 164328 56 165303 56 166278 56 167253 56 168220 56 169195 56 170170 56 171145 56 172108 56 173083 56 174058 56 175033 56 176000 56 176975 56 177950 56 178925 56 179888 56 180863 56 181838 56 182813 56 183780 56 184755 56 185730 56 186705 56 187668 56 188643 56 189618 56 190593 56 191560 56 192535 56 193510 56 194485 56 195448 56 196423 56 197398 56 198373 56 199340 56 200315 56 201290 56 202265 56 203228 56 204203 56 205178 56 206153 56 207120 56 208095 56 209070 56 210045 56 211008 60 211983 60 212958 60 213933 60 214896 60 215871 60 216846 60 217821 60 218788 56 219763 56 220738 56 221713 56 222676 60 223651 60 224626 60 225601 60 226564 60 227539 60 228514 60 229489 60 230456 60 231431 60 232406 60 233381 60 234344 60 235319 60 236294 60 237269 60 238236 60 239211 60 240186 60 241161 60 242124 60 243099 60 244074 60 245049 60 246016 60 246991 60 247966 60 248941 60 249904 60 250879 60 251854 60 252829 60 253792 64 254767 64 255742 64 256717 64 257684 64 258659 64 259634 64 260609 64 261572 64 262547 64 263522 64 264497 64 265460 68 266435 68 267410 68 268385 68 269352 68 270327 68 271302 68 272277 68 273240 68 274215 68 275190 68 276165 68 277132 68 278107 68 279082 68 280057 68 281020 68 281995 68 282970 68 283945 68 284912 68 285887 68 286862 68 287837 68 288800 68 289775 68 290750 68 291725 68 292688 68 293663 68 294638 68 295613 68 296580 68 297555 68 298530 68 299505 68 300468 68 301443 68 302418 68 303393 68 304356 72 305331 72 306306 72 307281 72 308248 72 309223 72 310198 72 311173 72 312136 72 313111 72 314086 72 315061 72 316028 72 317003 72 317978 72 318953 72 319916 72 320891 72 321866 72 322841 72 323804 72 324779 72 325754 72 326729 72 327696 72 328671 72 329646 72 330621 72 331584 72 332559 72 333534 72 334509 72 335472 76 336447 76 337422 76 338397 76 339364 72 340339 72 341314 72 342289 72 343252 76 344227 76 345202 76 346177 76 347140 76 348115 76 349090 76 350065 76 351032 76 352007 76 352982 76 353957 76 354920 76 355895 76 356870 76 357845 76 358808 80 359783 80 360758 80 361733 80 362700 80 363675 80 364650 80",
                                "maskId": 2
                            }
                        ]
                    }
                ],
                "handle": 0
            }
        }

        异常响应示例
        {
            "error": {
                "code": 105,
                "message": "参数无效"
            }
        }
        """
        body = {
            "ver": ver,
            "streamId": stream_id,
            "category": category,
            "startTime": start_time,
            "endTime": end_time,
            "filter": filter,
            "fields": fields,
        }
        return self.do_request("/data-mgr/label/read", body)

    def next_label(self, handle, size=10000):
        """
        通过handle读取下一批标注数据
        :param handle: handle
        :param size: 本次读取标注数据量大小
        :return: 下一批标注数据信息
        正常响应示例
        {
            "result": {
                "infos": [
                    {
                        "ver": 1005,
                        "streamId": 1000,
                        "sensor": "Cam-FrontWide",
                        "mediaType": 1,
                        "imgSize": [
                            3840,
                            2160
                        ],
                        "timestamp": 1712814110185561,
                        "object": [
                            {
                                "originId": 104,
                                "id": 4,
                                "instId": 0,
                                "class": "WhiteSolidLine",
                                "shape": "mask",
                                "coords": [
                                    [
                                        250,
                                        1180
                                    ],
                                    [
                                        1689,
                                        1675
                                    ]
                                ],
                                "prop": [],
                                "extra": {
                                    "taskId": 1045
                                },
                                "rle": "1424 15 2863 15 4302 15 5741 15 7168 20 8607 20 10046 20 11485 20 12908 24 14347 24 15786 24 17225 24 18652 24 20091 24 21530 24 22969 24
        24396 24 25835 24 27274 24 28713 24 30136 28 31575 28 33014 28 34453 28 35880 28 37319 28 38758 28 40197 28 41624 24 43063 24 44502 24 45941 24 47368 24 48807 24 50246 24 51685 24 53112 24 54551 24 55990 24 57429 24 58856 24 60295 24 61734 24 63173 24 64596 28 66035 28 67474 28 68913 28 70340 28 71779 28 73218 28 74657 28 76084 28 77523 28 78962 28 80401 28 81828 28 83267 28 84706 28 86145 28 87572 28 89011 28 90450 28 91889 28 93316 28 94755 28 96194 28 97633 28 99060 28 100499 28 101938 28 103377 28 104804 28 106243 28 107682 28 109121 28 110548 28 111987 28 113426 28 114865 28 116292 28 117731 28 119170 28 120609 28 122032 36 123471 36 124910 36 126349 36 127776 36 129215 36 130654 36 132093 36 133520 32 134959 32 136398 32 137837 32 139264 32 140703 32 142142 32 143581 32 145008 32 146447 32 147886 32 149325 32 150752 32 152191 32 153630 32 155069 32 156496 32 157935 32 159374 32 160813 32 162240 32 163679 32 165118 32 166557 32 167984 32 169423 32 170862 32 172301 32 173728 32 175167 32 176606 32 178045 32 179472 32 180911 32 182350 32 183789 32 185216 32 186655 32 188094 32 189533 32 190960 36 192399 36 193838 36 195277 36 196704 36 198143 36 199582 36 201021 36 202448 36 203887 36 205326 36 206765 36 208196 32 209635 32 211074 32 212513 32 213940 32 215379 32 216818 32 218257 32 219684 32 221123 32 222562 32 224001 32 225428 36 226867 36 228306 36 229745 36 231172 36 232611 36 234050 36 235489 36 236916 36 238355 36 239794 36 241233 36 242660 36 244099 36 245538 36 246977 36 248404 36 249843 36 251282 36 252721 36 254148 36 255587 36 257026 36 258465 36 259892 36 261331 36 262770 36 264209 36 265636 40 267075 40 268514 40 269953 40 271380 40 272819 40 274258 40 275697 40 277124 40 278563 40 280002 40 281441 40 282872 36 284311 36 285750 36 287189 36 288616 36 290055 36 291494 36 292933 36 294356 40 295795 40 297234 40 298673 40 300104 36 301543 36 302982 36 304421 36 305848 36 307287 36 308726 36 310165 36 311592 36 313031 36 314470 36 315909 36 317336 40 318775 40 320214 40 321653 40 323080 40 324519 40 325958 40 327397 40 328824 40 330263 40 331702 40 333141 40 334568 40 336007 40 337446 40 338885 40 340312 40 341751 40 343190 40 344629 40 346056 40 347495 40 348934 40 350373 40 351800 40 353239 40 354678 40 356117 40 357544 44 358983 44 360422 44 361861 44 363288 44 364727 44 366166 44 367605 44 369036 40 370475 40 371914 40 373353 40 374776 44 376215 44 377654 44 379093 44 380524 40 381963 40 383402 40 384841 40 386268 40 387707 40 389146 40 390585 40 392012 40 393451 40 394890 40 396329 40 397752 44 399191 44 400630 44 402069 44 403496 44 404935 44 406374 44 407813 44 409240 44 410679 44 412118 44 413557 44 414988 40 416427 40 417866 40 419305 40 420728 44 422167 44 423606 44 425045 44 426476 44 427915 44 429354 44 430793 44 432216 48 433655 48 435094 48 436533 48 437964 44 439403 44 440842 44 442281 44 443704 48 445143 48 446582 48 448021 48 449452 44 450891 44 452330 44 453769 44 455192 48 456631 48 458070 48 459509 48 460940 44 462379 44 463818 44 465257 44 466684 44 468123 44 469562 44 471001 44 472428 44 473867 44 475306 44 476745 44 478172 48 479611 48 481050 48 482489 48 483916 48 485355 48 486794 48 488233 48 489660 48 491099 48 492538 48 493977 48 495404 48 496843 48 498282 48 499721 48 501148 48 502587 48 504026 48 505465 48 506892 48 508331 48 509770 48 511209 48 512636 48 514075 48 515514 48 516953 48 518380 48 519819 48 521258 48 522697 48 524124 48 525563 48 527002 48 528441 48 529868 48 531307 48 532746 48 534185 48 535612 52 537051 52 538490 52 539929 52 541356 52 542795 52 544234 52 545673 52 547100 52 548539 52 549978 52 551417 52 552844 52 554283 52 555722 52 557161 52 558588 52 560027 52 561466 52 562905 52 564332 52 565771 52 567210 52 568649 52 570076 52 571515 52 572954 52 574393 52 575820 56 577259 56 578698 56 580137 56 581564 56 583003 56 584442 56 585881 56 587308 56 588747 56 590186 56 591625 56 593052 56 594491 56 595930 56 597369 56 598796 56 600235 56 601674 56 603113 56 604540 56 605979 56 607418 56 608857 56 610284 56 611723 56 613162 56 614601 56 616028 60 617467 60 618906 60 620345 60 621772 60 623211 60 624650 60 626089 60 627516 60 628955 60 630394 60 631833 60 633260 60 634699 60 636138 60 637577 60 639004 60 640443 60 641882 60 643321 60 644748 60 646187 60 647626 60 649065 60 650492 60 651931 60 653370 60 654809 60 656240 56 657679 56 659118 56 660557 56 661984 56 663423 56 664862 56 666301 56 667728 60 669167 60 670606 60 672045 60 673468 64 674907 64 676346 64 677785 64 679212 64 680651 64 682090 64 683529 64 684964 56 686403 56 687842 56 689281 56 690720 44 692159 44 693598 44 695037 44 696476 32 697915 32 699354 32 700793 32 702232 20 703671 20 705110 20 706549 20 707988 8 709427 8 710866 8",
                                "maskId": 6
                            }
                        ]
                    }
                ],
                "handle": 1
            }
        }

        异常响应示例
        {
            "error": {
                "code": 107,
                "message": "句柄失效"
            }
        }
        """
        body = {
            "handle": handle,
            "size": size,
        }
        return self.do_request("/data-mgr/label/next", body)

    def close_label(self, handle):
        """
        关闭读取标注句柄。
        :param handle: 句柄
        :return: None
        正常响应示例
        {
            "result": null
        }

        异常响应示例
        {
            "error": {
                "code": 107,
                "message": "句柄失效"
            }
        }
        """
        body = {
            "handle": handle
        }
        return self.do_request("/data-mgr/label/close", body)

    def write_label_map(self, label: [LabelWriteReq]):
        """
        请求示例：
        {
            "label": [
                {
                    "caseId": 1,
                    "bagId": 2,
                    "category": "category",
                    "labelInfo":[
                        {
                            "key":"1",
                            "value":"abd"
                        }
                    ],
                    "version":"1"
                }
            ]
        }

        正常响应示例：
        {
	        "result": null
        }

        异常响应示例
        {
            "error": {
                "code": 105,
                "message": "参数无效"
            }
        }
        """
        body = {
            "label": [item.to_dict() for item in label] if label is not None else [],
        }
        return self.do_request("/data-mgr/label/map/write", body)

    def read_label_map(self, bag_id=0, case_id=0, filter={}, start=0, size=20):
        """
        读取地图标注数据
        :param case_id: case_id
        :param filter: 过滤条件,例：获取指定业务来源和版本的标注{"category":"bev","version":"v1.1"}
        :return: 地图标注数据信息
        正常响应示例
        {
            "result": {
                "total": 1,
                "infos": [
                    {
                        "bagId": 3110,
                        "category": "debug_urp",
                        "version": "1.0",
                        "labelInfo": [
                            {
                                "key": "sq3_path",
                                "value": "/bag-data/0/0/3109/LFZ93AN90RD017583_URPMap_data_20250218111826/1739877503712882944_5_dd50c6.sq3"
                            },
                            {
                                "key": "score",
                                "value": 110
                            }
                        ]
                    }
                ]
            }
        }

        异常响应示例
        {
            "error": {
                "code": 102,
                "message": "数据库出错"
            }
        }
        """
        body = {
            "bagId": bag_id,
            "caseId": case_id,
            "filter": filter,
            "start": start,
            "size": size
        }
        return self.do_request("/data-mgr/label/map/read", body)

    def read_label_map_ex(self, category: str = "", filter={}):
        """
        读取地图标注数据，并拿到handle用于分批读取数据
        :param category: 业务来源，读取latest版本必传
        :param filter: 过滤条件，例：{"case_id":24036,"version":"1.1.1"}
        :return: 标注数据信息
        正常响应示例
        {
            "result": {
                "infos": [
                    {
                        "caseId": 24036,
                        "category": "Det",
                        "version": "1.1.1",
                        "labelInfo": [
                            {
                                "key": "labelPath",
                                "value": "/lib/doc/a.txt"
                            },
                            {
                                "key": "verPath",
                                "value": "/dataSet/case/0/5/24036/2DLaneVisualization-2613"
                            }
                        ]
                    }
                ],
                "handle": 0
            }
        }

        异常响应示例
        {
            "error": {
                "code": 105,
                "message": "参数无效"
            }
        }
        """
        body = {
            "category": category,
            "filter": filter,
        }
        return self.do_request("/data-mgr/label/map/read_ex", body)

    def read_label_map_ex_bag(self, category: str = "", filter={}):
        """
        读取bag地图标注数据，并拿到handle用于分批读取数据
        :param category: 业务来源，读取latest版本必传
        :param filter: 过滤条件，例：{"bag_id":24036,"version":"1.1.1"}
        :return: 标注数据信息
        正常响应示例
        {
            "result": {
                "infos": [
                    {
                        "bagId": 24036,
                        "category": "Det",
                        "version": "1.1.1",
                        "labelInfo": [
                            {
                                "key": "labelPath",
                                "value": "/lib/doc/a.txt"
                            },
                            {
                                "key": "verPath",
                                "value": "/dataSet/case/0/5/24036/2DLaneVisualization-2613"
                            }
                        ]
                    }
                ],
                "handle": 0
            }
        }

        异常响应示例
        {
            "error": {
                "code": 105,
                "message": "参数无效"
            }
        }
        """
        body = {
            "category": category,
            "filter": filter,
        }
        return self.do_request("/data-mgr/label/map/read_ex_bag", body)

    def next_label_map_ex(self, handle, size=10000):
        """
        通过handle读取下一批地图标注数据
        :param handle: handle
        :param size: 本次读取标注数据量大小
        :return: 下一批标注数据信息
        正常响应示例
        {
            "result": {
                "infos": [
                    {
                        "caseId": 24036,
                        "category": "Det",
                        "version": "1.1.1",
                        "labelInfo": [
                            {
                                "key": "labelPath",
                                "value": "/lib/doc/a.txt"
                            },
                            {
                                "key": "verPath",
                                "value": "/dataSet/case/0/5/24036/2DLaneVisualization-2613"
                            }
                        ]
                    }
                ],
                "handle": 0
            }
        }

        异常响应示例
        {
            "error": {
                "code": 107,
                "message": "句柄失效"
            }
        }
        """
        body = {
            "handle": handle,
            "size": size,
        }
        return self.do_request("/data-mgr/label/map/next", body)

    def close_label_map_ex(self, handle):
        """
        关闭读取地图标注句柄。
        :param handle: 句柄
        :return: None
        正常响应示例
        {
            "result": null
        }

        异常响应示例
        {
            "error": {
                "code": 107,
                "message": "句柄失效"
            }
        }
        """
        body = {
            "handle": handle
        }
        return self.do_request("/data-mgr/label/map/close", body)

    def cicd_create(self, param: CicdParam):
        """
        新建CI/CD任务

        正常请求示例
        {
            "pipelineName": "工作流名称", // 工作流名称
            "templateId": 800,  // 非必填，模板id
            "isUpdate": true,   // 是否更新模板，默认false
            "isStart": true,    // 是否启动工作流，默认false
            "customConfig": {
                "a": 1
            }, // 工作流自定义配置
            "opInfo":[
                {
                    "opId": 1001, // 组件id
                    "scriptUrl": "http://bkrepo.leapmotor.com/generic/intelligent-cockpit/custom/Artifacts/LP-ALG-DATA-PLATFORM/3DStaticReconstruction/3DStaticReconstruction", // 新的组件产物下载地址
                    "scriptVer": "1.00.05",  // 新的组件产物下载版本
                    "desc": {           // 描述信息
                        "project":"xxx",  // 仓库项目名称
                        "branch": "xxx",  // 分支
                        "commitId": "xxx" // commitId
                    }
                }
            ] //必填，组件信息，支持更新多个组件
        }

        正常响应示例:
        {
            "result": "a2Z1C5cjGof4pwkAdpSUYA"
        }

        异常响应示例
        {
            "error": {
                "code": 107,
                "message": ""
            }
        }
        """
        return self.do_request("/workflow/operator/cicd/create", param.to_dict())

    def cicd_status(self, id: str):
        """
        获取CI/CD任务状态

        正常请求示例:
        {
            "id": "a2Z1C5cjGof4pwkAdpSUYA"
        }

        正常响应示例:
        {
            "result": {
                "creator": 1006,  // 创建人id
                "status": "failed",  // 任务状态：running succeed failed
                "errInfo": "组件运行文件获取失败", // failed状态时错误信息
                "newOpVer": {
                    "1001":1002
                }, // 组件id：新的组件ver
                "pipelineId": 3334,  // 启动的工作流id
                "pipelineUrl": "http://10.195.131.161:10085/#/workFlow?taskId=100103" // 启动的工作流链接
            }
        }

        异常响应示例
        {
            "error": {
                "code": 107,
                "message": ""
            }
        }
        """
        body = {
            "id": id,
        }
        return self.do_request("/workflow/operator/cicd/status", body)

    def frame_tag_list(self, bag_id=0, case_id=0, category="", version="", source="", pipeline=0, start=0, size=20):
        """
        读取帧级标签数据
        :param bag_id: bag_id
        :param case_id: case_id
        :param category: 业务类型
        :param version: 版本
        :param source: 来源（组件名称-版本）
        :param pipeline: 工作流ID
        :param start: 分页参数从第几条开始
        :param size: 分页参数查询多少条数据
        :return: 帧级标签数据信息
        正常响应示例
        {
            "result": {
                "total": 10000,
                "infos": [
                    {
                        "caseId": 3966,
                        "vehicle": 1055,
                        "sensor": "pack",
                        "timestamp": 1719344672246013,
                        "category": "E2E",
                        "version": "0.0.0",
                        "tag": [
                            {
                                "attribute": [],
                                "key": "EgoNudgeLeaveAndGoBack",
                                "value_bool": false
                            }
                        ],
                        "extra": {
                            "source": "FrameDataMining-3438",
                            "pipeline": 100028
                        }
                    }
                ]
            }
        }

        异常响应示例
        {
            "error": {
                "code": 102,
                "message": "数据库出错"
            }
        }
        """
        body = {
            "bagId": bag_id,
            "caseId": case_id,
            "category": category,
            "version": version,
            "source": source,
            "pipeline": pipeline,
            "start": start,
            "size": size
        }
        return self.do_request("/data-mgr/frame-tag/list", body)

    def frame_tag_delete(self, bag_id=0, case_id=0, category="", version="", source="", pipeline=0):
        """
        读取帧级标签数据
        :param bag_id: bag_id
        :param case_id: case_id
        :param category: 业务类型
        :param version: 版本
        :param source: 来源（组件名称-版本）
        :param pipeline: 工作流ID
        :return: 帧级标签数据信息
        正常响应示例
        {
            "result": null
        }

        异常响应示例
        {
            "error": {
                "code": 102,
                "message": "数据库出错"
            }
        }
        """
        body = {
            "bagId": bag_id,
            "caseId": case_id,
            "category": category,
            "version": version,
            "source": source,
            "pipeline": pipeline
        }
        return self.do_request("/data-mgr/frame-tag/delete", body)

    def frame_tag_search(self, category="case", search="{}"):
        """
        读取地图标注数据
        :param category: case or bag
        :param search: 查询条件,例："{\"query\":{\"match\":{\"vehicle\":1055}},\"size\":1}"
        :return: 帧级标签数据信息
        正常响应示例
        {
            "result": {
                "total": 10000,
                "infos": [
                    {
                        "caseId": 3966,
                        "vehicle": 1055,
                        "sensor": "pack",
                        "timestamp": 1719344672246013,
                        "category": "E2E",
                        "version": "0.0.0",
                        "tag": [
                            {
                                "attribute": [],
                                "key": "EgoNudgeLeaveAndGoBack",
                                "value_bool": false
                            }
                        ],
                        "extra": {
                            "source": "FrameDataMining-3438",
                            "pipeline": 100028
                        }
                    }
                ]
            }
        }

        异常响应示例
        {
            "error": {
                "code": 102,
                "message": "数据库出错"
            }
        }
        """
        body = {
            "category": category,
            "search": search
        }
        return self.do_request("/data-mgr/frame-tag/search", body)

    def frame_tag_write(self, frame_tag):
        """
        帧级标签入库
        :param frame_tag: 帧级标签数组
        :return: 帧级标签数据信息
        正常请求示例
        {
            "tag": [
                {
                    "caseId": 1001,
                    "vehicle": 10010,
                    "sensor": "Cam-FrontLeft",
                    "timestamp": 1721468103694114,
                    "category": "point",
                    "version": "1.2",
                    "tag": [
                        {
                            "key": "EgoDistanceToCurb",
                            "value_float": 4.2729494180355285,
                            "attribute": [
                                {
                                    "key": "VRU_speed",
                                    "value_float": 1.5
                                }
                            ]
                        },
                        {
                            "key": "EgoComfortablilityLevel",
                            "value_text": "LEVEL_1",
                            "attribute": [
                                {
                                    "key": "VRU_speed",
                                    "value_float": 1.5
                                },
                                {
                                    "key": "VRU_distance_to_ego",
                                    "value_int": 14
                                }
                            ]
                        },
                        {
                            "key": "Enable",
                            "value_bool": true
                        }
                    ]
                }
            ]
        }

        正常响应示例
        {
            "result": null
        }
        """
        body = {
            "tag": frame_tag
        }
        return self.do_request("/data-mgr/frame-tag/write", body)

    def create_finder(self, task_type, specified_class, **kwargs):
        body = {
            "taskType": task_type,
            "param": specified_class(**kwargs).to_dict(),
        }
        response = self.do_request("/data-mgr/finder/create", body)
        if "error" in response:
            return response
        finder_id = response["result"]
        self.finder[finder_id] = 0
        return response

    def create_case_search_finder(self, **kwargs):
        """
        获取case高级查询id
        :param set_id: 数据集id
        :param tag: 标签查询条件
        :param display_start_time: 采集起始时间（十六位，例如1715904322000000）
        :param display_end_time: 采集终止时间（十六位，例如1715904322000000）
        :return: 响应数据

        tag字段示例：(可在平台上使用前端页面选择标签条件，查询前按F12查看请求内容，复制粘贴)
        单个标签条件：
        {
            "group": [
                {
                    "opType": 2,
                    "group": [
                        {
                            "opType": 2,
                            "tag": {
                                "key": "ContinuousRoadStructure",
                                "value": "BumpyRoad",
                                "fuzzyMatch": False
                            }
                        }
                    ]
                }
            ]
        }

        两个标签并集（有标签A或标签B）：
        {
            "group": [
                {
                    "opType": 2,
                    "group": [
                        {
                            "opType": 2,
                            "tag": {
                                "key": "Weather",
                                "value": "Fog"
                            }
                        },
                        {
                            "opType": 2,
                            "tag": {
                                "key": "DayTime",
                                "value": "Night"
                            }
                        }
                    ]
                }
            ]
        }

        两个标签交集（A和B都要有）：
        {
            "group": [
                {
                    "opType": 2,
                    "group": [
                        {
                            "opType": 4,
                            "tag": {
                                "key": "Weather",
                                "value": "Fog"
                            }
                        },
                        {
                            "opType": 4,
                            "tag": {
                                "key": "DayTime",
                                "value": "Night"
                            }
                        }
                    ]
                }
            ]
        }

        正常响应示例
        {
            "result": "IGffl1lU6CLx4ggAwBfpVg"
        }
        异常响应示例
        {
            "error": {
                "code": 105,
                "message": "参数无效"
            }
        }
        """
        return self.create_finder("caseFinder", CreateCaseFinderFilter, **kwargs)

    def create_bag_search_finder(self, **kwargs):
        """
        获取bag高级查询id
        :param set_id: 数据集id
        :param tag: 标签查询条件
        :param display_start_time: 采集起始时间（十位，例如1726102556）
        :param display_end_time: 采集终止时间（十位，例如1726102556）
        :return: 响应数据，示例同上
        """
        return self.create_finder("bagFinder", CreateBagFinderFilter, **kwargs)

    def create_image_search_finder(self, **kwargs):
        """
        获取image高级查询id
        :param set_id: 数据集id
        :param display_start_time: 采集起始时间（十六位，例如1714003200000000）
        :param display_end_time: 采集终止时间（十六位，例如1714003200000000）
        :return: 响应数据，示例同上
        """
        return self.create_finder("imageFinder", CreateImageFinderFilter, **kwargs)

    def read_search_results(self, size=10, finder_id=None):
        """
        获取case/bag/image高级查询的结果
        :param finder_id: 高级查询id
        :param size: 每次读取的个数
        :return: 响应数据
        正常响应示例，以case为例
        {
            "result": {
                "infos": [
                    {
                        "setId": 1050,
                        "kind": "case_pool",
                        "caseId": 2345,
                        "vehicle": 1000,
                        "hardware": 1241,
                        "software": 1242,
                        "createTime": 1717502351,
                        "startTime": 1715915032823000,
                        "endTime": 1715915122772000,
                        "displayStartTime": 1715943832823000,
                        "displayEndTime": 1715943922772000,
                        "path": "/dataSet/case/0/0/2345",
                        "pipeline": {
                            "id": 1981,
                            "attr": "private"
                        },
                        "genVer": "\u751f\u6210case-822",
                        "inTime": 1717502351
                    }
                ],
                "total": 4,
                "state": "succeed"
            }
        }
        异常响应示例
        {
            "error": {
                "code": 208,
                "message": "会话超时，请刷新页面再试"
            }
        }
        """
        if finder_id is None:
            return {"error": {"code": "105", "message": "no finder_id"}}
        if finder_id not in self.finder:
            return {"error": {"code": "105", "message": "invalid finder_id"}}
        start = self.finder[finder_id]
        body = {
            "session": finder_id
        }
        response = self.do_request("/data-mgr/finder/read", body)

        if "error" in response:
            error = response["error"]
            return {"error": {"code": error["code"], "message": error["message"]}}

        result = response["result"]
        state = result["state"]

        if state == "running":
            while True:
                body = {
                    "session": finder_id
                }
                response = self.do_request("/data-mgr/finder/read", body)
                if "error" in response:
                    error = response["error"]
                    return {"error": {"code": error["code"], "message": error["message"]}}

                result = response["result"]
                state = result["state"]
                if state != 'running':
                    break
                time.sleep(1)

        body = {
            "session": finder_id,
            "size": size,
            "start": start,
            "sort": [{"key": "inTime", "value": -1}, {"key": "_id", "value": -1}]
        }
        final_response = self.do_request("/data-mgr/finder/read", body)

        if "error" in final_response:
            return {"error": {"code": final_response["error"]["code"], "message": final_response["error"]["message"]}}

        self.finder[finder_id] += size
        return final_response

    def stop_search_finder(self, finder_id=None):
        """
        结束高级查询
        :return: 响应数据
        正常响应示例
        null
        异常响应示例
        {
            "error": {
                "code": 105,
                "message": "参数无效"
            }
        }
        """
        if finder_id is None:
            return {"error": {"code": "105", "message": "no finder_id"}}
        if finder_id not in self.finder:
            return {"error": {"code": "105", "message": "invalid finder_id"}}

        body = {"session": finder_id}
        response = self.do_request("/data-mgr/finder/stop", body)
        if response is not None:
            if "error" in response:
                error = response["error"]
                return {"error": {"code": error["code"], "message": error["message"]}}
        del self.finder[finder_id]
        return response

    def finder_set_tag(self, case_id=None, bag_id=None, image_id=None, mode=0, tag=None):
        """
        case、bag、图片 设置标签

        正常请求示例
        {
            "mode": 1,
            "imageId": [
                {
                    "vehicle": 1000,
                    "sensor": "Cam-Back",
                    "timestamp": 1712798341822465
                },
                {
                    "vehicle": 1000,
                    "sensor": "Cam-Back",
                    "timestamp": 1712798342422465
                }
            ],
            "tag": [
                {
                    "key": "ContinuousRoadStructure",
                    "value": "BumpyRoad",
                    "source": "manual",
                    "sensor": "pack"
                }
            ]
        }

        正常响应示例:
        {
            "result": "1743665534667-0"
        }

        异常响应示例
        {
            "error": {
                "code": 107,
                "message": ""
            }
        }
        """

        body = {
            "caseId": case_id,
            "bagId": bag_id,
            "imageId": image_id,
            "mode": mode,
            "tag": tag,
        }
        return self.do_request("/data-mgr/finder/tag/set", body)

    def finder_progress(self, msg_id: str):
        """
        获取任务进度

        正常请求示例:
        {
            "msgId": "1743665534667-0"
        }

        正常响应示例:
        {
            "result": {
                "info": {
                    "remain": 0,
                    "total": 2
                },
                "state": "succeed"
            }
        }

        异常响应示例
        {
            "error": {
                "code": 351,
                "message": "异步任务失败: 参数无效"
            }
        }
        """
        body = {
            "msgId": msg_id,
        }
        return self.do_request("/data-mgr/finder/progress", body)

    def list_dds_case(self, case_id, sensor="", start=0, size=1):
        """
        分页获取指定case下的bag、mcap列表
        :param case_id: case id
        :param sensor: 采集设备名称
        :param start: 从第几个开始（用于分页展示）
        :param size: 展示几个（用于分页展示）
        :return: bag、mcap列表
        正常响应示例
        {
            "result": {
                "total": 1,
                "infos": [
                    {
                        "caseId": 34108,
                        "streamId": 1409,
                        "sensor": "DDS_Bag",
                        "startTime": 1747882525265334,
                        "endTime": 1747882825484153,
                        "displayStartTime": 1747911325265334,
                        "displayEndTime": 1747911625484153,
                        "data": {
                            "name": "/dataset-1/bag/1409/DDS_Bag/20250522/1409_DDS_Bag_20250522105524.bag",
                            "size": 242415147,
                            "modifyTime": 1748396411
                        }
                    }
                ]
            }
        }

        异常响应示例
        {
            "error": {
                "code": 102,
                "message": "数据库出错"
            }
        }
        """
        body = {
            "caseId": case_id,
            "sensor": sensor,
            "start": start,
            "size": size,

        }
        return self.do_request("/data-mgr/case/dds-list", body)

    def create_finder_all(self, task_type, param):
        body = {
            "taskType": task_type,
            "param": param,
        }
        response = self.do_request("/data-mgr/finder/create", body)
        if "error" in response:
            return response
        finder_id = response["result"]
        self.finder[finder_id] = 0
        return response

    def workflow_template_start(self, template_id=0, pipeline_name="", custom_config={},op_id_ver=[]):
        """
        工作流模板启动工作流
        :param template_id: 模板id
        :param pipeline_name: 工作流名称
        :param custom_config: 工作流自定义配置
        :param op_id_ver: 工作流组件运行版本
        :return:
        正常响应示例
        {
            "result": {
                "creator": 1025,
                "pipelineId": 101250,
                "pipelineUrl": "http://10.195.131.161:10085/#/workFlow?taskId=101250"
            }
        }

        异常响应示例
        {
            "error": {
                "code": 102,
                "message": "数据库出错"
            }
        }
        """
        body = {
            "id": template_id,
            "pipelineName": pipeline_name,
            "customConfig": custom_config,
            "opIdVer": op_id_ver,
        }
        return self.do_request("/workflow/template/start", body)

    def get_next_case_id(self):
        """
        用于生成新case时获取新case的Id与存放路径
        :return: 新case的caseId，路径
        正常响应示例：
        {
            "result": {
                "caseId": 34482,
                "path": "/dataset-develop-2/case/0/8/34482"
            }
        }

        异常响应示例
        {
            "error": {
                "code": 888888,
                "message": "登录过期"
            }
        }
        """
        return self.do_request("/data-mgr/case/next-id-path", {})


