import { defineConfig } from "../frontend/node_modules/vite/dist/node/index.js";
import { evaluationProxy } from "./proxy.mjs";
export default defineConfig({ server:{host:"127.0.0.1",port:4175,strictPort:true}, plugins:[evaluationProxy()] });
