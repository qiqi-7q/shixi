<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from "vue";
import * as echarts from "echarts/core";
import {
  GeoComponent,
  TooltipComponent,
  TitleComponent
} from "echarts/components";
import { ScatterChart } from "echarts/charts";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  GeoComponent,
  TooltipComponent,
  TitleComponent,
  ScatterChart,
  CanvasRenderer
]);

const props = defineProps<{
  vehicleList?: any[];
}>();

const mapContainer = ref<HTMLElement>();
let chartInstance: echarts.ECharts | null = null;

const currentLevel = ref<"country" | "province" | "city" | "district">(
  "country"
);
const currentCode = ref<string>("100000");
const currentName = ref<string>("全国");
const breadcrumb = ref<Array<{ name: any; code: any }>>([
  { name: "全国", code: "100000" }
]);

const loading = ref(false);
const isInitialized = ref(false);

const geoJsonCache = new Map<string, any>();
const nameToCodeMap = new Map<string, number>(); // 名称到 adcode 的映射

// 优先使用本地数据，本地不存在时使用在线数据
const MAP_DATA_BASE = "/map-data";
const BASE_URL = "https://geo.datav.aliyun.com/areas_v3/bound";

// 从 100000_full_city.json 中过滤出指定层级的数据
function filterFeaturesByLevel(
  geoJson: any,
  level: string,
  parentCode?: number
): any {
  if (!geoJson || !geoJson.features) return geoJson;

  const filtered = geoJson.features.filter((f: any) => {
    if (f.properties.level !== level) return false;
    if (parentCode) {
      return (
        f.properties.acroutes && f.properties.acroutes.includes(parentCode)
      );
    }
    return true;
  });

  return {
    type: "FeatureCollection",
    features: filtered
  };
}

// 深度清理 geometry 数据，移除 null 值
function cleanGeometry(feature: any): any {
  if (!feature || !feature.geometry || !feature.geometry.coordinates) {
    return null;
  }

  const cleanCoords = (coords: any): any => {
    if (!coords) return null;
    if (Array.isArray(coords)) {
      const cleaned = coords
        .map(cleanCoords)
        .filter((c: any) => c !== null && c !== undefined);
      return cleaned.length > 0 ? cleaned : null;
    }
    return coords;
  };

  const cleanedCoordinates = cleanCoords(feature.geometry.coordinates);
  if (!cleanedCoordinates || cleanedCoordinates.length === 0) {
    return null;
  }

  return {
    type: feature.type,
    properties: feature.properties,
    geometry: {
      type: feature.geometry.type,
      coordinates: cleanedCoordinates
    }
  };
}

async function loadGeoJson(code: string): Promise<any> {
  if (geoJsonCache.has(code)) {
    return geoJsonCache.get(code);
  }

  // 默认加载 100000_full.json（全国省份边界）
  if (code === "100000") {
    try {
      const url = `${MAP_DATA_BASE}/100000_full.json`;
      const response = await fetch(url);
      if (response.ok) {
        const geoJson = await response.json();
        geoJsonCache.set(code, geoJson);
        return geoJson;
      }
    } catch {
      console.error("无法加载 100000_full.json");
    }
  }

  // 对于省份和城市，从预加载的完整数据中过滤
  await preloadFullData();
  const fullData = geoJsonCache.get("full_data");

  if (fullData && fullData.features) {
    const codeStr = String(code);
    const codeNum = parseInt(codeStr);

    // 省份：显示该省本身 + 该省的所有城市
    if (codeStr.endsWith("0000")) {
      // 找到省份本身
      const province = fullData.features.find(
        (f: any) =>
          f.properties.adcode === codeNum && f.properties.level === "province"
      );

      // 找到该省的所有城市
      const cities = fullData.features.filter(
        (f: any) =>
          f.properties.acroutes &&
          f.properties.acroutes.includes(codeNum) &&
          f.properties.level === "city"
      );

      // 合并省份和城市
      const features = province
        ? [
            cleanGeometry(province),
            ...cities.map(cleanGeometry).filter(Boolean)
          ]
        : cities.map(cleanGeometry).filter(Boolean);

      if (features.length > 0) {
        const result = { type: "FeatureCollection", features };
        geoJsonCache.set(code, result);
        console.log(`加载省份 ${codeStr}: 1个省 + ${cities.length}个城市`);
        return result;
      }
    }

    // 城市：只有浙江省的城市才下钻到区县
    if (codeStr.endsWith("00") && !codeStr.endsWith("0000")) {
      // 判断是否为浙江省的城市（adcode 以 33 开头）
      const isZhejiangCity = codeStr.startsWith("33");

      if (!isZhejiangCity) {
        console.log(`非浙江省城市 ${codeStr}，只显示城市本身，不下钻到区县`);
        // 返回城市本身的 geometry，保持地图显示
        const cityFeature = fullData.features.find(
          (f: any) =>
            f.properties.adcode === codeNum && f.properties.level === "city"
        );
        if (cityFeature) {
          const cleaned = cleanGeometry(cityFeature);
          if (cleaned) {
            const result = { type: "FeatureCollection", features: [cleaned] };
            geoJsonCache.set(code, result);
            return result;
          }
        }
        return { type: "FeatureCollection", features: [] };
      }

      // 浙江省城市：尝试从本地加载区县数据
      try {
        const cityUrl = `${MAP_DATA_BASE}/${codeStr}_full.json`;
        const response = await fetch(cityUrl);
        if (response.ok) {
          const cityData = await response.json();
          const districts = cityData.features
            .filter((f: any) => f.properties.level === "district")
            .map(cleanGeometry)
            .filter(Boolean);

          if (districts.length > 0) {
            const result = { type: "FeatureCollection", features: districts };
            geoJsonCache.set(code, result);
            console.log(
              `加载城市 ${codeStr} 的区县数量:`,
              districts.length,
              "（本地数据）"
            );
            return result;
          }
        }
      } catch {
        console.log(`本地没有 ${codeStr} 的区县数据`);
      }

      console.log(`本地没有 ${codeStr} 的区县数据，返回空`);
    }
  }

  return { type: "FeatureCollection", features: [] };
}

// 预加载完整数据供子区域查询使用
async function preloadFullData() {
  if (geoJsonCache.has("full_data")) return;

  const fullData: any = { type: "FeatureCollection", features: [] };

  // 加载 100000_full.json（包含省份数据）
  try {
    const url = `${MAP_DATA_BASE}/100000_full.json`;
    console.log(url);
    const response = await fetch(url);
    if (response.ok) {
      const geoJson = await response.json();
      if (geoJson.features) {
        const cleaned = geoJson.features.map(cleanGeometry).filter(Boolean);
        fullData.features.push(...cleaned);
        console.log("加载 100000_full.json features:", cleaned.length);
      }
    }
  } catch {
    console.error("无法加载 100000_full.json");
  }

  // 加载 100000_full_city.json（包含城市/区县数据）
  try {
    const url = `${MAP_DATA_BASE}/100000_full_city.json`;
    console.log(url);
    const response = await fetch(url);
    if (response.ok) {
      const geoJson = await response.json();
      if (geoJson.features) {
        const cleaned = geoJson.features.map(cleanGeometry).filter(Boolean);
        fullData.features.push(...cleaned);
        console.log("加载 100000_full_city.json features:", cleaned.length);
      }
    }
  } catch {
    console.error("无法加载 100000_full_city.json");
  }

  geoJsonCache.set("full_data", fullData);
  console.log("预加载完成，总 features 数量:", fullData.features.length);

  // 统计各层级数量
  const levels = fullData.features.reduce((acc: any, f: any) => {
    const level = f.properties.level || "unknown";
    acc[level] = (acc[level] || 0) + 1;
    return acc;
  }, {});
  console.log("各层级统计:", levels);
}

async function getChildren(code: string): Promise<any[]> {
  try {
    const codeStr = String(code);
    const isCounty =
      codeStr.endsWith("00") === false ||
      (parseInt(codeStr.slice(-2)) !== 0 &&
        parseInt(codeStr.slice(-4, -2)) !== 0);
    if (isCounty) {
      console.log("已到县级，没有子区域");
      return [];
    }

    // 确保完整数据已加载
    await preloadFullData();
    const fullData = geoJsonCache.get("full_data");

    if (fullData && fullData.features) {
      // 如果是全国，提取省份
      if (codeStr === "100000") {
        const provinces = fullData.features.filter(
          (f: any) => f.properties.level === "province"
        );
        console.log("从完整数据提取省份数量:", provinces.length);
        return provinces;
      }

      // 如果是省份（xx0000），提取城市
      if (codeStr.endsWith("0000")) {
        // 从区县数据中提取唯一城市
        const districts = fullData.features.filter(
          (f: any) =>
            f.properties.acroutes &&
            f.properties.acroutes.includes(parseInt(codeStr)) &&
            f.properties.level === "district"
        );

        // 通过 acroutes 提取城市（acroutes 的倒数第二个就是城市 code）
        const cityMap = new Map();
        districts.forEach((d: any) => {
          const routes = d.properties.acroutes || [];
          // acroutes: [100000, 330000, 330100] - 最后一个是城市
          if (routes.length >= 3) {
            const cityCode = routes[routes.length - 1];
            if (!cityMap.has(cityCode)) {
              // 从区县名称推断城市名称（去掉区/县/市后缀）
              const cityName = d.properties.name.replace(/区$|县$|市$/, "");
              cityMap.set(cityCode, {
                properties: {
                  adcode: cityCode,
                  name: cityName,
                  level: "city",
                  acroutes: routes.slice(0, -1)
                }
              });
            }
          }
        });

        const citiesFromDistricts = Array.from(cityMap.values());
        if (citiesFromDistricts.length > 0) {
          console.log("从区县提取城市数量:", citiesFromDistricts.length);
          console.log(
            "城市列表:",
            citiesFromDistricts.map((c: any) => c.properties.name)
          );
          return citiesFromDistricts;
        }
      }

      // 如果是城市（xxxx00），提取区县
      if (codeStr.endsWith("00") && !codeStr.endsWith("0000")) {
        const districts = fullData.features.filter(
          (f: any) =>
            f.properties.acroutes &&
            f.properties.acroutes.includes(parseInt(codeStr)) &&
            f.properties.level === "district"
        );
        if (districts.length > 0) {
          console.log("从完整数据提取区县数量:", districts.length);
          return districts;
        }
      }
    }

    return [];
  } catch (error) {
    console.error("获取子区域失败:", error);
    return [];
  }
}

function initChart() {
  if (!mapContainer.value) return;
  if (
    mapContainer.value.clientWidth === 0 ||
    mapContainer.value.clientHeight === 0
  ) {
    return;
  }
  chartInstance = echarts.init(mapContainer.value);
  chartInstance.on("click", onMapClick);
}

async function initMap() {
  if (isInitialized.value) return;
  await nextTick();
  if (!mapContainer.value || mapContainer.value.clientWidth === 0) {
    return;
  }
  isInitialized.value = true;
  initChart();
  await loadMap("100000", "全国", "country");
}

async function loadMap(
  code: string,
  name: string,
  level: "country" | "province" | "city"
) {
  console.log("加载地图:", code, name, level);
  loading.value = true;
  try {
    const geoJson = await loadGeoJson(code);

    // 构建名称到 adcode 的映射
    nameToCodeMap.clear();
    if (geoJson.features) {
      geoJson.features.forEach((f: any) => {
        if (f.properties && f.properties.name && f.properties.adcode) {
          nameToCodeMap.set(f.properties.name, f.properties.adcode);
        }
      });
    }

    echarts.registerMap("currentMap", geoJson);

    const vehiclePositions = getVehiclePositions();

    chartInstance?.setOption(
      {
        title: {
          text: name,
          left: "center",
          textStyle: { fontSize: 18, fontWeight: "bold" }
        },
        tooltip: {
          trigger: "item",
          formatter: (params: any) => {
            if (params.componentType === "series") {
              const data = params.data;
              return `
              <div style="padding: 8px;">
                <p style="margin: 0; font-weight: bold;">${data.vin_code || "未知车辆"}</p>
                <p style="margin: 4px 0 0;">车型: ${data.model || "-"}</p>
                <p style="margin: 4px 0 0;">位置: ${data.position || "-"}</p>
                <p style="margin: 4px 0 0;">上电状态: ${data.power === 1 ? "已上电" : "未上电"}</p>
              </div>
            `;
            }
            return params.name || "";
          }
        },
        geo: {
          map: "currentMap",
          roam: true,
          zoom: 1,
          label: {
            show: true,
            fontSize: 12,
            color: "#333"
          },
          itemStyle: {
            areaColor: "#e8f4ff",
            borderColor: "#409EFF",
            borderWidth: 1
          },
          emphasis: {
            itemStyle: {
              areaColor: "#b3d9ff"
            },
            label: {
              color: "#000"
            }
          }
        },
        series: [
          {
            type: "scatter",
            coordinateSystem: "geo",
            data: vehiclePositions.map(v => ({
              name: v.vin_code,
              value: [v.longitude, v.latitude],
              ...v
            })),
            symbolSize: 12,
            itemStyle: {
              color: "#409EFF"
            },
            emphasis: {
              itemStyle: {
                color: "#67C23A",
                symbolSize: 16
              }
            }
          }
        ]
      },
      true
    );
    console.log(vehiclePositions);
    currentLevel.value = level;
    currentCode.value = code;
    currentName.value = name;
  } catch (error) {
    console.error("加载地图失败:", error);
  } finally {
    loading.value = false;
  }
}

function getVehiclePositions() {
  if (!props.vehicleList || props.vehicleList.length === 0) return [];

  return props.vehicleList
    .filter(v => v.longitude && v.latitude)
    .map(v => ({
      vin_code: v.vin_code,
      model: v.model,
      position: v.position,
      power: v.power,
      longitude: parseFloat(v.longitude),
      latitude: parseFloat(v.latitude)
    }));
}

function onMapClick(params: any) {
  if (params.componentType !== "geo") return;
  if (!params.name) return;

  // 优先尝试从 region 获取 adcode
  const regionAdcode = params.region?.adcode;

  // 判断是否为区县级别（adcode 不以 00 结尾）
  if (regionAdcode) {
    const adcodeStr = String(regionAdcode);
    if (!adcodeStr.endsWith("00")) {
      console.log("已到区县级别，不再下钻");
      return;
    }
  }

  // 如果当前已经是区县级别，不再下钻
  if (currentLevel.value === "district") {
    console.log("已到区县级别，不再下钻");
    return;
  }

  // 优先尝试从 region 获取 adcode
  if (regionAdcode) {
    console.log("从 region 获取 adcode:", regionAdcode);

    // 如果当前是省份级别，点击城市时：只有浙江省才下钻
    if (currentLevel.value === "province") {
      const adcodeStr = String(regionAdcode);
      const isZhejiangCity = adcodeStr.startsWith("33");
      if (!isZhejiangCity) {
        console.log(`非浙江省城市，点击不下钻`);
        return;
      }
    }

    breadcrumb.value.push({ name: params.name, code: regionAdcode });

    // 根据当前级别确定下一级
    let nextLevel: "province" | "city" | "district" = "province";
    if (currentLevel.value === "province") nextLevel = "city";
    else if (currentLevel.value === "city") nextLevel = "district";

    loadMap(regionAdcode, params.name, nextLevel);
    return;
  }

  // 从名称映射中获取 adcode
  const mappedCode = nameToCodeMap.get(params.name);
  if (mappedCode) {
    console.log("从名称映射获取 adcode:", mappedCode);

    // 判断是否为区县级别
    const adcodeStr = String(mappedCode);
    if (!adcodeStr.endsWith("00")) {
      console.log("已到区县级别，不再下钻");
      return;
    }

    // 如果当前是省份级别，点击城市时：只有浙江省才下钻
    if (currentLevel.value === "province") {
      const isZhejiangCity = adcodeStr.startsWith("33");
      if (!isZhejiangCity) {
        console.log(`非浙江省城市，点击不下钻`);
        return;
      }
    }

    breadcrumb.value.push({ name: params.name, code: mappedCode });

    // 根据当前级别确定下一级
    let nextLevel: "province" | "city" | "district" = "province";
    if (currentLevel.value === "province") nextLevel = "city";
    else if (currentLevel.value === "city") nextLevel = "district";

    loadMap(mappedCode, params.name, nextLevel);
    return;
  }

  // 如果都没有，通过名称匹配子区域
  console.log("未获取到 adcode，通过名称匹配子区域");
  getChildren(currentCode.value).then(children => {
    const target = children.find((f: any) => f.properties.name === params.name);

    if (target) {
      const newCode = target.properties.adcode;
      const newName = target.properties.name;

      // 判断是否为区县级别
      const adcodeStr = String(newCode);
      if (!adcodeStr.endsWith("00")) {
        console.log("已到区县级别，不再下钻");
        return;
      }

      // 如果当前是省份级别，点击城市时：只有浙江省才下钻
      if (currentLevel.value === "province") {
        const isZhejiangCity = adcodeStr.startsWith("33");
        if (!isZhejiangCity) {
          console.log(`非浙江省城市，点击不下钻`);
          return;
        }
      }

      breadcrumb.value.push({ name: newName, code: newCode });

      // 根据当前级别确定下一级
      let nextLevel: "province" | "city" | "district" = "province";
      if (currentLevel.value === "province") nextLevel = "city";
      else if (currentLevel.value === "city") nextLevel = "district";

      loadMap(newCode, newName, nextLevel);
    } else {
      console.log("未找到匹配的子区域");
    }
  });
}

function onBreadcrumbClick(index: number) {
  if (index === breadcrumb.value.length - 1) return;

  const target = breadcrumb.value[index];
  breadcrumb.value = breadcrumb.value.slice(0, index + 1);

  const level =
    index === 0
      ? "country"
      : index === 1
        ? "province"
        : index === 2
          ? "city"
          : "district";
  loadMap(target.code, target.name, level);
}

function resetView() {
  breadcrumb.value = [{ name: "全国", code: "100000" }];
  loadMap("100000", "全国", "country");
}

function resize() {
  chartInstance?.resize();
}

watch(
  () => props.vehicleList,
  () => {
    if (chartInstance) {
      const vehiclePositions = getVehiclePositions();
      chartInstance.setOption({
        series: [
          {
            data: vehiclePositions.map(v => ({
              name: v.vin_code,
              value: [v.longitude, v.latitude],
              ...v
            }))
          }
        ]
      });
    }
  },
  { deep: true }
);

onMounted(async () => {
  await initMap();
});

onUnmounted(() => {
  chartInstance?.dispose();
});

defineExpose({ resetView, resize });
</script>

<template>
  <div class="vehicle-map">
    <div class="map-header">
      <div class="breadcrumb">
        <span
          v-for="(item, index) in breadcrumb"
          :key="item.code"
          class="breadcrumb-item"
          :class="{ active: index === breadcrumb.length - 1 }"
          @click="onBreadcrumbClick(index)"
        >
          {{ item.name }}
          <span v-if="index < breadcrumb.length - 1" class="separator">
            /
          </span>
        </span>
      </div>
      <el-button type="primary" size="small" @click="resetView">
        返回全国
      </el-button>
    </div>
    <div v-loading="loading" class="map-container">
      <div ref="mapContainer" class="map-content"></div>
    </div>
    <div class="map-legend">
      <div class="legend-item">
        <span class="legend-dot blue"></span>
        <span>车辆位置</span>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.vehicle-map {
  height: 75vh;
  min-height: 600px;
  display: flex;
  flex-direction: column;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.breadcrumb-item {
  cursor: pointer;
  color: #409eff;
  transition: color 0.2s;

  &:hover:not(.active) {
    color: #66b1ff;
    text-decoration: underline;
  }

  &.active {
    color: #303133;
    cursor: default;
    font-weight: 500;
  }
}

.separator {
  margin: 0 4px;
  color: #909399;
}

.map-container {
  flex: 1;
  position: relative;
  background: #fff;
  min-height: 500px;
}

.map-content {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

.map-legend {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  background: #f5f7fa;
  border-top: 1px solid #e4e7ed;
  font-size: 12px;
  flex-shrink: 0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;

  &.blue {
    background: #409eff;
  }
}
</style>
