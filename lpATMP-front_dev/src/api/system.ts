import { http } from "@/utils/http";

/** 车辆固定字段查询 */
export const fixsearch = (params?: object) => {
  return http.request("get", "/api/vehicle/fixsearch", { params });
};

/** 获取车辆概览统计 */
export const getVehicleOverview = (params?: object) => {
  return http.request("get", "/api/vehicle/stats/overview", { params });
};

/** 获取车型分布统计 */
export const getVehicleModelDistribution = (params?: object) => {
  return http.request("get", "/api/vehicle/model_distribution", {
    params
  });
};

/** 获取所有车型枚举 */
export const getVehicleModels = () => {
  return http.request("get", "/api/vehicle/models");
};

/** 获取车辆使用率统计 */
export const getVehicleUtilization = (params?: object) => {
  return http.request("get", "/api/vehicle/stats/utilization", {
    params
  });
};

/** 获取车辆状态分布统计 */
export const getVehicleStatusDistribution = (params?: object) => {
  return http.request("get", "/api/vehicle/stats/status_distribution", {
    params
  });
};

/** 车辆高级查询 */
export const advsearch = (conditions: object[], params?: object) => {
  return http.request("post", "/api/vehicle/advsearch", {
    data: conditions,
    params
  });
};

/** 创建车辆 */
export const createVehicle = (data: object) => {
  return http.request("post", "/api/vehicle/createvehicle", { data });
};

/** 获取单个车辆信息 */
export const getVehicle = (id: number) => {
  return http.request("get", `/api/vehicle/getvehicle/${id}`);
};

/** 获取车辆状态 */
export const getVehicleStatus = (id: number) => {
  return http.request("get", `/api/vehicle/getstatus/${id}`);
};

/** 更新车辆信息 */
export const updateVehicle = (id: number, data: object) => {
  return http.request("put", `/api/vehicle/updatevehicle/${id}`, { data });
};

/** 删除车辆 */
export const deleteVehicle = (id: number) => {
  return http.request("delete", `/api/vehicle/delvehicle/${id}`);
};

/** 批量导入车辆资源 */
export const batchImportVehicle = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return http.request("post", "/api/vehicle/vehicle_import", {
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
};

/** 获取员工列表 */
export const getEmployeeList = (params?: object) => {
  return http.request("get", "/api/employee/fixsearch", { params });
};

// ==================== 借用管理模块 API ====================

/** 获取借用概览统计 */
export const getBorrowOverview = (params?: object) => {
  return http.request("get", "/api/borrow/stats/overview", { params });
};

/** 获取借用状态分布统计 */
export const getBorrowStatusDistribution = (params?: object) => {
  return http.request("get", "/api/borrow/stats/status_distribution", {
    params
  });
};

/** 借用记录固定字段查询 */
export const fixBorrowSearch = (params?: object) => {
  return http.request("get", "/api/borrow/fixsearch", { params });
};

/** 借用记录高级查询 */
export const advBorrowSearch = (conditions: object[], params?: object) => {
  return http.request("post", "/api/borrow/advsearch", {
    data: conditions,
    params
  });
};

/** 创建借用记录 */
export const createBorrow = (data: object) => {
  return http.request("post", "/api/borrow/createborrow", { data });
};

/** 获取单个借用记录 */
export const getBorrow = (id: number) => {
  return http.request("get", `/api/borrow/getborrow/${id}`);
};

/** 更新借用记录 */
export const updateBorrow = (id: number, data: object) => {
  return http.request("put", `/api/borrow/updateborrow/${id}`, { data });
};

/** 删除借用记录 */
export const deleteBorrow = (id: number) => {
  return http.request("delete", `/api/borrow/delborrow/${id}`);
};

/** 归还车辆 */
export const returnVehicle = (id: number) => {
  return http.request("post", `/api/borrow/returnvehicle/${id}`);
};

/** 取消借用 */
export const cancelBorrow = (id: number) => {
  return http.request("post", `/api/borrow/cancelborrow/${id}`);
};

/** 获取车辆其他借用记录 */
export const getBorrowedRecords = (params: {
  record_id: number;
  vehicle_id: number;
}) => {
  return http.request("post", "/api/borrow/borrowed", { params });
};

/** 获取可用司机列表（内照有效期内） */
export const getAvailableDrivers = () => {
  return http.request("post", "/api/borrow/borrowedriver");
};

/** 获取员工详情 */
export const getEmployeeDetail = (id: number) => {
  return http.request("get", `/api/employee/${id}`);
};

/** 新增员工 */
export const createEmployee = (data: object) => {
  return http.request("post", "/api/employee/", { data });
};

/** 更新员工信息 */
export const updateEmployee = (id: number, data: object) => {
  return http.request("put", `/api/employee/${id}`, { data });
};

/** 删除员工 */
export const deleteEmployee = (id: number) => {
  return http.request("delete", `/api/employee/${id}`);
};

/** 获取测试里程列表 */
export const getTestMilesList = (params?: object) => {
  return http.request("get", "/api/test_miles/", { params });
};

/** 获取测试里程详情 */
export const getTestMilesDetail = (id: number) => {
  return http.request("get", `/api/test_miles/${id}`);
};

/** 获取测试里程统计 */
export const getMileageStats = (params?: object) => {
  return http.request("get", "/api/test_miles/stats", { params });
};

/** 获取当前项目列表 */
export const getCurrentProjects = () => {
  return http.request("post", "/api/test_miles/get_cur_project");
};

/** 新增测试里程 */
export const createTestMiles = (data: object) => {
  return http.request("post", "/api/test_miles/", { data });
};

/** 更新测试里程 */
export const updateTestMiles = (id: number, data: object) => {
  return http.request("put", `/api/test_miles/${id}`, { data });
};

/** 删除测试里程 */
export const deleteTestMiles = (id: number) => {
  return http.request("delete", `/api/test_miles/${id}`);
};

// ==================== NAP 统计分析模块 API ====================

/** 获取 NAP 列表 */
export const getNapList = (params?: object) => {
  return http.request("get", "/api/kpi_main/", { params });
};

/** 获取 NAP 概览统计 */
export const getNapOverview = (params?: object) => {
  return http.request("get", "/api/kpi_main/stats/overview", { params });
};

/** 获取 NAP 版本得分趋势 */
export const getNapVersionScore = (params?: object) => {
  return http.request("get", "/api/kpi_main/stats/version_score", { params });
};

/** 创建 NAP 记录 */
export const createNap = (data: object) => {
  return http.request("post", "/api/kpi_main/", { data });
};

/** 更新 NAP 记录 */
export const updateNap = (id: number, data: object) => {
  return http.request("put", `/api/kpi_main/${id}`, { data });
};

/** 删除 NAP 记录 */
export const deleteNap = (id: number) => {
  return http.request("delete", `/api/kpi_main/${id}`);
};

// ==================== 数据分析模块 API ====================

/** 创建分析数据 */
export const createAnalysis = (params: any) => {
  return http.request("post", "/api/analysis/create_analysis", { params });
};

/** 获取分析列表 */
export const getAnalysisList = (params?: any) => {
  return http.request("get", "/api/analysis/fixsearch", { params });
};

/** 获取单个分析详情 */
export const getAnalysisDetail = (analysisId: number) => {
  return http.request("get", `/api/analysis/get_analysis/${analysisId}`);
};

/** 对比分析数据 */
export const compareAnalysis = (params: {
  analysis_id1: number;
  analysis_id2: number;
}) => {
  return http.request("put", "/api/analysis/analysis_compare", { params });
};

/** 删除分析数据 */
export const deleteAnalysis = (analysisId: number) => {
  return http.request("delete", "/api/analysis/delete_analysis", {
    params: { analysis_id: analysisId }
  });
};

/** 获取分析数据总览统计 */
export const getAnalysisOverview = (params?: {
  project?: string;
  carModel?: string;
  funcMode?: string;
}) => {
  return http.request("get", "/api/analysis/stats/overview", { params });
};

/** 获取项目列表 */
export const getAnalysisProjects = () => {
  return http.request("get", "/api/analysis/stats/projects");
};

/** 获取版本得分统计 */
export const getVersionStats = (params?: {
  project?: string;
  carModel?: string;
  funcMode?: string;
}) => {
  return http.request("get", "/api/analysis/stats/version", { params });
};

/** 更新成功率指标 */
export const updateSuccessRate = (data: object) => {
  return http.request("put", "/api/analysis/update_success_rate", { data });
};

// ==================== 测试记录模块 API ====================

/** 创建测试记录 */
export const createTestRecord = (data: object) => {
  return http.request("post", "/api/test_record/createrecord", { data });
};

/** 获取测试记录列表 */
export const getTestRecordList = (params?: {
  skip?: number;
  limit?: number;
  project?: string;
  car_type?: string;
  function_mode?: string;
}) => {
  return http.request("get", "/api/test_record/fixsearch", { params });
};

/** 获取测试记录详情 */
export const getTestRecordDetail = (recordId: number) => {
  return http.request("get", `/api/test_record/getrecord/${recordId}`);
};

/** 更新测试记录 */
export const updateTestRecord = (recordId: number, data: object) => {
  return http.request("put", `/api/test_record/updaterecord/${recordId}`, {
    data
  });
};

/** 删除测试记录 */
export const deleteTestRecord = (recordId: number) => {
  return http.request("delete", `/api/test_record/delrecord/${recordId}`);
};

/** 测试记录高级查询 */
export const advsearchTestRecord = (conditions: object[], params?: object) => {
  return http.request("post", "/api/test_record/advsearch", {
    data: conditions,
    params
  });
};

/** 批量导入测试记录 */
export const batchImportTestRecord = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return http.request("post", "/api/test_record/batch_import", {
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
};

/** 批量导出测试记录 */
export const batchExportTestRecord = (params?: {
  project?: string;
  car_type?: string;
  function_mode?: string;
  problem_category?: string;
  kpi_type?: string;
}) => {
  return http.request("get", "/api/test_record/batch_export", {
    params,
    responseType: "blob"
  });
};

// ==================== 系统管理模块 API ====================
/** 获取部门列表 */
export const getDeptList = (params?: object) => {
  return http.request("get", "/api/system/dept/list", { params });
};
/** 获取菜单列表 */
export const getMenuList = (params?: object) => {
  return http.request("get", "/api/system/menu/list", { params });
};
/** 获取角色列表 */
export const getRoleList = (params?: object) => {
  return http.request("get", "/api/system/role/list", { params });
};
/** 获取角色菜单 */
export const getRoleMenu = (params?: object) => {
  return http.request("get", "/api/system/role/menu", { params });
};
/** 获取角色菜单ID列表 */
export const getRoleMenuIds = (params?: object) => {
  return http.request("get", "/api/system/role/menuIds", { params });
};
/** 获取用户角色ID列表 */
export const getRoleIds = (params?: object) => {
  return http.request("get", "/api/system/user/roleIds", { params });
};
/** 获取用户列表 */
export const getUserList = (params?: object) => {
  return http.request("get", "/api/system/user/list", { params });
};
/** 获取所有角色列表 */
export const getAllRoleList = (params?: object) => {
  return http.request("get", "/api/system/role/all", { params });
};

// ==================== 权限管理模块 API（auth） ====================
/** 获取部门列表 */
export const getAuthDeptList = (params?: object) => {
  return http.request("get", "/api/auth/depts", { params });
};

/** 获取角色列表 */
export const getAuthRoleList = (params?: {
  skip?: number;
  limit?: number;
  search?: string;
}) => {
  return http.request("get", "/api/auth/roles", { params });
};

/** 获取角色详情（按 ID） */
export const getAuthRoleDetail = (roleId: number) => {
  return http.request("get", `/api/auth/roles/${roleId}`);
};

/** 创建角色 */
export const createAuthRole = (data: {
  code: string;
  name: string;
  description?: string;
  permission_ids: number[];
  platform_uuid?: string;
  level?: number;
}) => {
  return http.request("post", "/api/auth/roles", { data });
};

/** 更新角色 */
export const updateAuthRole = (
  roleId: number,
  data: {
    code?: string;
    name?: string;
    description?: string;
    permission_ids?: number[];
    platform_uuid?: string;
    level?: number;
  }
) => {
  return http.request("put", `/api/auth/roles/${roleId}`, { data });
};

/** 删除角色 */
export const deleteAuthRole = (roleId: number) => {
  return http.request("delete", `/api/auth/roles/${roleId}`);
};

/** 获取权限列表（按模块分组） */
export const getAuthPermissions = (params?: { platform?: string }) => {
  return http.request("get", "/api/auth/permissions", { params });
};

/** 获取平台列表 */
export const getAuthPlatforms = () => {
  return http.request("get", "/api/auth/platforms");
};

// ==================== 测试任务模块 API ====================
/** 获取测试任务列表 */
export const getTaskList = (params?: object) => {
  return http.request("get", "/api/test_task/", { params });
};
/** 获取测试任务详情 */
export const getTaskDetail = (id: number) => {
  return http.request("get", `/api/test_task/${id}`);
};
/** 获取测试任务统计 */
export const getTaskStats = (params?: object) => {
  return http.request("get", "/api/test_task/stats/", { params });
};
/** 新增测试任务 */
export const createTask = (data: object) => {
  return http.request("post", "/api/test_task/", { data });
};
/** 更新测试任务 */
export const updateTask = (id: number, data: object) => {
  return http.request("put", `/api/test_task/${id}`, { data });
};
/** 删除测试任务 */
export const deleteTask = (id: number) => {
  return http.request("delete", `/api/test_task/${id}`);
};

// ==================== 测试路线模块 API ====================
/** 获取路线列表 */
export const getRouteList = (params?: object) => {
  return http.request("get", "/api/test_route/fixsearch", { params });
};

/** 获取路线详情 */
export const getRouteDetail = (id: number) => {
  return http.request("get", `/api/test_route/getroute/${id}`);
};

/** 创建路线 */
export const createRoute = (data: object) => {
  return http.request("post", "/api/test_route/createroute", { data });
};

/** 更新路线 */
export const updateRoute = (id: number, data: object) => {
  return http.request("put", `/api/test_route/updateroute/${id}`, { data });
};

/** 删除路线 */
export const deleteRoute = (id: number) => {
  return http.request("delete", `/api/test_route/delroute/${id}`);
};

// ==================== 司机监控模块 API ====================
/** 获取司机监控列表 */
export const getDriverMonitorList = (params?: object) => {
  return http.request("get", "/api/driver_monitor/fixsearch", { params });
};

/** 获取司机监控详情 */
export const getDriverMonitorDetail = (id: number) => {
  return http.request("get", `/api/driver_monitor/getmonitor/${id}`);
};

/** 创建司机监控记录 */
export const createDriverMonitor = (data: object) => {
  return http.request("post", "/api/driver_monitor/createmonitor", { data });
};

/** 更新司机监控记录 */
export const updateDriverMonitor = (id: number, data: object) => {
  return http.request("put", `/api/driver_monitor/updatemonitor/${id}`, {
    data
  });
};

/** 删除司机监控记录 */
export const deleteDriverMonitor = (id: number) => {
  return http.request("delete", `/api/driver_monitor/delmonitor/${id}`);
};

/** 获取监控概览统计 */
export const getDriverMonitorOverview = (params?: object) => {
  return http.request("get", "/api/driver_monitor/stats/overview", { params });
};

/** 获取每日疲劳状态统计 */
export const getDriverMonitorDailyFatigue = (params?: object) => {
  return http.request("get", "/api/driver_monitor/stats/daily_fatigue", {
    params
  });
};

/** 获取每日DMS触发次数 */
export const getDriverMonitorDailyDms = (params?: object) => {
  return http.request("get", "/api/driver_monitor/stats/daily_dms", { params });
};

/** 获取司机疲劳次数排行 */
export const getDriverMonitorDriverFatigue = (params?: object) => {
  return http.request("get", "/api/driver_monitor/stats/driver_fatigue", {
    params
  });
};

/** 获取状态分布统计 */
export const getDriverMonitorStatusDistribution = (params?: object) => {
  return http.request("get", "/api/driver_monitor/stats/status_distribution", {
    params
  });
};

// ==================== 车辆监控模块 API ====================
/** 获取单条监控详情 */
export const getVehicleMonitor = (id: number) => {
  return http.request("get", `/api/vehicle_monitor/getmonitor/${id}`);
};

/** 高级搜索（分页） */
export const advSearchVehicleMonitor = (
  conditions: object[],
  params?: { skip: number; limit: number }
) => {
  return http.request("post", "/api/vehicle_monitor/advsearch", {
    data: conditions,
    params: params || { skip: 0, limit: 100 }
  });
};

/** 获取车辆VIN列表 */
export const getVinList = (keyword?: string) => {
  return http.request("get", "/api/vehicle_monitor/getvinlist", {
    params: keyword ? { keyword } : {}
  });
};

/** 获取单车用车信息（按VIN查询） */
export const getCarInfoByVin = (vin_code: string) => {
  return http.request("get", `/api/vehicle_monitor/carinfo/${vin_code}`);
};

/** 获取车辆用车信息 */
export const getCarInfo = (params?: {
  vin_code?: string;
  model?: string;
  start_date?: string;
  end_date?: string;
}) => {
  return http.request("get", "/api/vehicle_monitor/getcarinfo", { params });
};

/** 按组别获取使用率（按车型查询） */
export const getGroups = (params?: { model?: string }) => {
  return http.request("get", "/api/vehicle_monitor/getgroups", { params });
};

/** 获取指定日期的使用率和时长（天梯图） */
/** 获取车辆使用率统计（天梯图） */
export const getUsagesByDate = (params: {
  models: string;
  start_date?: string;
  end_date?: string;
}) => {
  return http.request("get", "/api/vehicle_monitor/getusages", { params });
};

/** 获取车辆里程统计（天梯图） */
export const getDistancesByDate = (params: {
  models: string;
  start_date?: string;
  end_date?: string;
}) => {
  return http.request("get", "/api/vehicle_monitor/getdistences", { params });
};

/** 获取测试记录字段选项（项目、车型、软件版本） */
export const getFieldOptions = () => {
  return http.request("get", "/api/test_record/field_options");
};

/** 获取数据字典配置 */
export const getLabelQuery = (params: { module_name: string }) => {
  return http.request("get", "/api/label/query", { params });
};

// ==================== 认证模块 API ====================
/** 用户注册 */
export const register = (data: object) => {
  return http.request("post", "/api/auth/register", { data });
};

/** 忘记密码（直接返回密码） */
export const forgetPassword = (params: object) => {
  return http.request("put", "/api/auth/forgetpwd", { params });
};

// ==================== 用户管理 API ====================
/** 获取权限用户列表 */
export const getAuthUserList = (params: object) => {
  return http.request("get", "/api/auth/users/fixsearch", { params });
};

/** 创建权限用户 */
export const createAuthUser = (data: object) => {
  return http.request("post", "/api/auth/users", { data });
};

/** 获取权限用户详情 */
export const getAuthUserDetail = (userId: number) => {
  return http.request("get", `/api/auth/users/${userId}`);
};

/** 更新权限用户 */
export const updateAuthUser = (userId: number, data: object) => {
  return http.request("put", `/api/auth/users/${userId}`, { data });
};

/** 删除权限用户 */
export const deleteAuthUser = (userId: number) => {
  return http.request("delete", `/api/auth/users/${userId}`);
};

/** 创建项目计划 */
export const createProjectPlan = (params: object) => {
  return http.request("post", "/api/project_plan/create_plan", { params });
};

/** 分片上传项目计划文件 */
export const uploadPlanFile = (data: FormData) => {
  return http.request("post", "/api/project_plan/upload_planfile", {
    data,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
};

/** 上传测试记录附件图片 */
export const uploadTestRecordAttach = (recordId: number, files: File[]) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append("files", file);
  });
  return http.request("post", `/api/upload/test_records/${recordId}`, {
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
};

/** 更新测试记录附件路径 */
export const updateTestRecordAttach = (
  recordId: number,
  filePaths: string[]
) => {
  return http.request("put", `/api/test_record/updaterecord/${recordId}`, {
    data: { analyze_attach: filePaths }
  });
};

/** 获取全部数据表字段注释缓存 */
export const getLabelAll = () => {
  return http.request("get", "/api/label/all");
};

/** 获取指定表的字段注释 */
export const getLabelField = (table_name: string) => {
  return http.request("get", "/api/label/field", { params: { table_name } });
};

/** 获取模块标签列表 */
export const getAbellList = (params?: {
  module_name?: string;
  field_name?: string;
}) => {
  return http.request("get", "/api/label/query", { params });
};

/** 保存模块标签 */
export const saveAbellList = (data: {
  module_name?: string;
  field_name: string;
  labels: string[];
}) => {
  return http.request("post", "/api/label/save", { data });
};

/** 删除模块标签 */
export const deleteAbellList = (params?: {
  module_name?: string;
  field_name?: string;
}) => {
  return http.request("delete", "/api/label/delete", { params });
};
