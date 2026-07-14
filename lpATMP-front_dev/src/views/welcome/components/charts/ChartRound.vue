<script setup lang="ts">
import { ref, computed } from "vue";
import { useDark, useECharts } from "@pureadmin/utils";
import { chartData } from "../../data";

const { isDark } = useDark();

const theme = computed(() => (isDark.value ? "dark" : "light"));

const chartRef = ref();
const { setOptions } = useECharts(chartRef, {
  theme,
  renderer: "svg"
});

// 取 chartData 中最后一个数据项（用户满意度）的占比模拟成环形饼图
const satisfactionValue = chartData[3]?.value ?? 100;

setOptions({
  container: ".line-card",
  tooltip: {
    trigger: "item"
  },
  series: [
    {
      type: "pie",
      radius: ["60%", "80%"],
      center: ["50%", "50%"],
      avoidLabelOverlap: false,
      label: { show: false },
      emphasis: { scale: false },
      data: [
        {
          value: satisfactionValue,
          name: "满意",
          itemStyle: { color: "#7846e5" }
        },
        {
          value: 100 - satisfactionValue,
          name: "其他",
          itemStyle: { color: "#dfe7ef" }
        }
      ]
    }
  ]
});
</script>

<template>
  <div ref="chartRef" style="width: 100%; height: 60px" />
</template>
