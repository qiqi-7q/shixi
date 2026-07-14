<script setup lang="ts">
import { ref, computed } from "vue";
import Picture from "~icons/ep/picture";
import { message } from "@/utils/message";
import { uploadTestRecordAttach, updateTestRecordAttach } from "@/api/system";

const props = defineProps<{
  row: any;
  editRow?: any;
  editable: boolean;
}>();

const emit = defineEmits<{
  (e: "update", images: string[]): void;
}>();

const uploading = ref(false);

const currentImages = computed<string[]>(() => {
  const attach = props.editRow?.analyze_attach ?? props.row?.analyze_attach;
  if (!attach) return [];
  return Array.isArray(attach) ? attach : [attach];
});

const showUploadButton = computed(() => currentImages.value.length < 9);

const totalItems = computed(
  () => currentImages.value.length + (showUploadButton.value ? 1 : 0)
);

const blankPlaceholders = computed(() => {
  const remainder = totalItems.value % 3;
  return remainder === 0 ? 0 : 3 - remainder;
});

const readonlyBlankPlaceholders = computed(() => {
  const remainder = currentImages.value.length % 3;
  return remainder === 0 ? 0 : 3 - remainder;
});

const getFullImageUrl = (path: any) => {
  if (!path || typeof path !== "string") return "";
  return path;
};

const fileInputRef = ref<HTMLInputElement | null>(null);

const triggerFileSelect = () => {
  if (fileInputRef.value) {
    fileInputRef.value.click();
  }
};

const handleFileChange = async (event: Event) => {
  try {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) {
      return;
    }

    const selectedFiles = Array.from(input.files);
    const recordId = props.editRow?.id || props.row?.id;

    if (!recordId) {
      message("记录ID不存在，无法上传", { type: "error" });
      input.value = "";
      return;
    }

    uploading.value = true;

    console.log("📤 开始批量上传图片:", {
      recordId,
      fileCount: selectedFiles.length,
      fileNames: selectedFiles.map(f => f.name),
      currentCount: currentImages.value.length
    });

    if (currentImages.value.length + selectedFiles.length > 9) {
      message(
        `当前已有${currentImages.value.length}张，本次选择${selectedFiles.length}张，超过9张上限`,
        { type: "warning" }
      );
      input.value = "";
      return;
    }

    const uploadRes: any = await uploadTestRecordAttach(
      recordId,
      selectedFiles
    );

    console.log("✅ 批量上传接口返回:", uploadRes);

    if (uploadRes?.code === 200 && uploadRes.data?.uploaded_files?.length > 0) {
      const newFiles = uploadRes.data.uploaded_files;
      const allFiles = [...currentImages.value, ...newFiles];

      console.log(" 合并后的完整文件列表:", allFiles);

      emit("update", allFiles);
      message(
        `成功上传${newFiles.length}张图片（共${allFiles.length}张），请点击保存`,
        {
          type: "success"
        }
      );
    } else {
      message(uploadRes?.message || "文件上传失败", { type: "error" });
    }

    input.value = "";
  } catch (error: any) {
    console.error("❌ 批量上传失败详情:", error);
    message(error?.message || "上传失败", { type: "error" });
  } finally {
    uploading.value = false;
  }
};

const handleRemove = async (imgIndex: number) => {
  try {
    const removedImage = currentImages.value[imgIndex];
    console.log("🗑️ 删除图片:", {
      index: imgIndex,
      image: removedImage,
      beforeCount: currentImages.value.length,
      afterCount: currentImages.value.length - 1
    });

    const updatedImages = currentImages.value.filter((_, i) => i !== imgIndex);

    emit("update", updatedImages);
    message("删除成功，请点击保存", { type: "success" });
  } catch (error: any) {
    console.error("❌ 删除失败详情:", error);
    message(error?.message || "删除失败", { type: "error" });
  }
};
</script>

<template>
  <!-- 编辑模式：自适应宽度，图片固定尺寸自然换行 -->
  <div
    v-if="editable"
    style="width: 140px; display: flex; justify-content: center"
  >
    <div
      style="
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        padding-top: 12px;
        width: 132px;
      "
    >
      <!-- 已上传的图片列表（每个固定40px） -->
      <div
        v-for="(img, imgIndex) in currentImages"
        :key="imgIndex"
        class="upload-item has-image"
        style="width: 40px; height: 40px"
      >
        <el-image
          :src="getFullImageUrl(img)"
          fit="cover"
          :preview-src-list="currentImages.map(getFullImageUrl)"
          :initial-index="imgIndex"
          preview-teleported
          class="item-image"
          hideOnClickModal
        />
        <!-- <div class="item-mask">
          <span class="mask-text">预览</span>
        </div> -->
        <span
          @click.stop="handleRemove(imgIndex)"
          class="delete-icon"
          title="删除此图片"
        >
          ✕
        </span>
      </div>

      <!-- 上传按钮（原生input实现批量上传） -->
      <div
        v-if="currentImages.length < 9"
        class="upload-box"
        style="width: 40px; height: 40px"
        :style="{
          opacity: uploading ? 0.6 : 1,
          cursor: uploading ? 'not-allowed' : 'pointer'
        }"
        @click="!uploading && triggerFileSelect()"
      >
        <div
          v-if="uploading"
          style="
            width: 40px;
            height: 40px;
            border: 2px solid #e4e7ed;
            border-top-color: #409eff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
          "
        ></div>
        <template v-else>
          <div class="upload-icon">+</div>
          <div class="upload-text">
            {{ `上传${currentImages.length}/9` }}
          </div>
        </template>

        <!-- 隐藏的文件选择器（支持多选） -->
        <input
          ref="fileInputRef"
          type="file"
          accept="image/*"
          multiple
          :style="{ display: 'none' }"
          @change="handleFileChange"
        />
      </div>

      <!-- 空白占位符，确保最后一行从左侧开始 -->
      <!-- <div
        v-for="n in blankPlaceholders"
        :key="'blank-' + n"
        style="
          width: 40px;
          height: 40px;
          visibility: hidden;
          pointer-events: none;
        "
      ></div> -->
    </div>

    <!-- <div v-if="currentImages.length >= 9" class="upload-tip">
      已达到上限 ({{ currentImages.length }}/9)
    </div> -->
  </div>

  <!-- 只读模式：自适应宽度，图片固定尺寸自然换行 -->
  <div
    v-else-if="currentImages.length > 0"
    style="display: block; width: 150px"
  >
    <div
      style="display: flex; flex-wrap: wrap; gap: 6px; align-content: center"
    >
      <el-image
        v-for="(img, imgIndex) in currentImages"
        :key="imgIndex"
        :src="getFullImageUrl(img)"
        fit="cover"
        :preview-src-list="currentImages.map(getFullImageUrl)"
        :initial-index="imgIndex"
        preview-teleported
        class="readonly-item"
        style="width: 20px; height: 20px"
        hideOnClickModal
      >
        <template #error>
          <div class="image-error">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-image>
      <!-- 空白占位符，确保最后一行从左侧开始 -->
      <!-- <div
        v-for="n in readonlyBlankPlaceholders"
        :key="'readonly-blank-' + n"
        style="
          width: 20px;
          height: 20px;
          visibility: hidden;
          pointer-events: none;
        "
      ></div> -->
    </div>
  </div>

  <span v-else class="empty-text">-</span>
</template>

<style scoped>
/* 容器 */
.upload-wrapper {
  width: 100%;
  padding: 12px 0;
}

/* 网格布局：Flex + 固定尺寸，确保横向排列 */
.upload-grid {
  display: flex;
  flex-wrap: wrap; /* 允许换行 */
  gap: 6px; /* 统一间距 */
  justify-content: center;
}

/* 图片项/上传框 统一样式 */
.upload-item,
.upload-box {
  width: 20px; /* 固定宽度 */
  height: 20px; /* 固定高度 */
  flex-shrink: 0; /* 防止压缩 */
  border-radius: 4px;
  position: relative;
  overflow: hidden;
  border: 1px solid #dcdfe6;
  box-sizing: border-box;
}

/* 已上传的图片项 */
.upload-item.has-image {
  border-color: transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: visible; /* 允许删除按钮显示在边界外 */
  transition:
    transform 0.25s ease,
    box-shadow 0.25s ease;
}

.upload-item.has-image:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

/* 图片填充 */
.item-image {
  width: 100%;
  height: 100%;
  display: block;
  border-radius: 4px; /* 保持圆角 */
  overflow: hidden; /* 确保图片不超出 */
}

/* 悬停遮罩层 */
.item-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.25s ease;
  z-index: 5;
}

.upload-item.has-image:hover .item-mask {
  opacity: 1;
}

.mask-text {
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 1px;
}

/* 删除按钮 */
.delete-icon {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 16px;
  height: 16px;
  background: #ff4d4f;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 11px;
  line-height: 1;
  z-index: 20;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(255, 77, 79, 0.35);
  transition:
    transform 0.2s ease,
    background 0.2s ease;
}

.delete-icon:hover {
  transform: scale(1.15);
  background: #ff7875;
  box-shadow: 0 3px 12px rgba(255, 77, 79, 0.45);
}

/* 上传框样式 */
.upload-box {
  border-style: dashed;
  background: #fafafa;
  cursor: pointer;
  transition:
    border-color 0.25s ease,
    background 0.25s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.upload-box:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.upload-icon {
  font-size: 18px;
  color: #c0c4cc;
  line-height: 1;
  font-weight: 300;
  transition: color 0.25s ease;
}

.upload-box:hover .upload-icon {
  color: #409eff;
}

.upload-text {
  font-size: 8px;
  color: #909399;
  text-align: center;
  line-height: 1.2;
  transition: color 0.25s ease;
}

.upload-box:hover .upload-text {
  color: #409eff;
}

/* 提示文字 */
.upload-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #e6a23c;
  padding: 4px 8px;
  background: #fdf6ec;
  border-radius: 3px;
  display: inline-block;
}

/* 只读模式 */
.readonly-wrapper {
  width: 100%;
}

.readonly-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
}

.readonly-item {
  width: 20px; /* 固定宽度 */
  height: 20px; /* 固定高度 */
  flex-shrink: 0; /* 防止压缩 */
  border-radius: 4px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s ease;
}

.readonly-item:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 空状态 */
.empty-text {
  color: #c0c4cc;
  font-size: 14px;
}

/* 图片加载失败样式 */
.image-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #c0c4cc;
  font-size: 12px;
}

/* 加载旋转动画 */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
