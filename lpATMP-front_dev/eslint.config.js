import { defineConfig, globalIgnores } from "eslint/config";

// 禁用所有 ESLint 规则
export default defineConfig([
  globalIgnores(["**/**"]),
  {
    rules: {}
  }
]);
