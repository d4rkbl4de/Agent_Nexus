import globals from "globals";
import pluginJs from "@eslint/js";
import tseslint from "typescript-eslint";
import pluginReactConfig from "eslint-plugin-react/configs/recommended.js";
import { fixupConfigRules } from "@eslint/js/lib/config/flat-eslint";
import nextConfig from "@next/eslint-plugin-next";

export default [
  { files: ["**/*.{js,jsx,ts,tsx}"] },
  { languageOptions: { parser: tseslint.parser } },
  { languageOptions: { globals: globals.browser } },

  pluginJs.configs.recommended,
  ...tseslint.configs.recommended,
  fixupConfigRules(pluginReactConfig),

  nextConfig.configs.recommended,
  nextConfig.configs["core-web-vitals"],
  
  {
    settings: {
      react: {
        version: "detect", 
      },
    },
    rules: {
      "react/prop-types": "off",
      "react/react-in-jsx-scope": "off",

      "@typescript-eslint/consistent-type-imports": "error",
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      
      "next/no-img-element": "error",
      "next/no-sync-scripts": "error",
    }
  }
];