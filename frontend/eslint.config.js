import js from '@eslint/js';
import ts from 'typescript-eslint';
export default ts.config({ignores:['dist/**','node_modules/**','.npm-cache/**','e2e/**','**/*.jsx','src/services/api.js','vite.config.js','eslint.config.js']},js.configs.recommended,...ts.configs.recommended,{files:['**/*.ts','**/*.tsx'],rules:{'@typescript-eslint/no-explicit-any':'error'}});
