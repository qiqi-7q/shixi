import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BASE_URL = "https://geo.datav.aliyun.com/areas_v3/bound";
const OUTPUT_DIR = path.join(__dirname, "public", "map-data");

// 确保目录存在
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function downloadFile(code, suffix) {
  const url = `${BASE_URL}/${code}${suffix}`;
  const filePath = path.join(OUTPUT_DIR, `${code}${suffix}`);

  try {
    console.log(`下载: ${url}`);
    const response = await fetch(url);
    if (!response.ok) {
      console.log(`  ✗ ${code}${suffix} 不存在 (HTTP ${response.status})`);
      return null;
    }
    const data = await response.json();
    fs.writeFileSync(filePath, JSON.stringify(data));
    console.log(`  ✓ 已保存: ${code}${suffix}`);
    return data;
  } catch (err) {
    console.log(`  ✗ 下载失败: ${err.message}`);
    return null;
  }
}

async function main() {
  console.log("开始下载浙江省地图数据...\n");

  // 1. 下载浙江省数据
  console.log("=== 下载浙江省 ===");
  const zhejiangFull = await downloadFile("330000", "_full.json");
  if (!zhejiangFull) {
    console.log("浙江省数据下载失败，退出");
    return;
  }

  // 2. 提取浙江省下的所有城市
  const cities = zhejiangFull.features
    .filter(f => f.properties.level === "city")
    .map(f => ({
      adcode: f.properties.adcode,
      name: f.properties.name
    }));

  console.log(`\n浙江省包含 ${cities.length} 个城市:`);
  cities.forEach(c => console.log(`  - ${c.name} (${c.adcode})`));

  // 3. 下载每个城市的完整数据（包含区县）
  console.log("\n=== 下载各城市数据 ===");
  for (const city of cities) {
    console.log(`\n处理: ${city.name}`);
    await downloadFile(city.adcode, "_full.json");
    await new Promise(resolve => setTimeout(resolve, 200)); // 防限流
  }

  console.log("\n=== 下载完成 ===");
  console.log(`所有文件已保存到: ${OUTPUT_DIR}`);
}

main().catch(console.error);
