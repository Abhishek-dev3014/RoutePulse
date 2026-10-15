import ts from "@typescript-eslint/eslint-plugin";
import parser from "@typescript-eslint/parser";
import hooks from "eslint-plugin-react-hooks";
export default [
  {
    ignores: [
      ".next/**",
      "node_modules/**",
      "next-env.d.ts",
      "lib/generated.ts",
    ],
  },
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parser,
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
        ecmaFeatures: { jsx: true },
      },
    },
    plugins: { "@typescript-eslint": ts, "react-hooks": hooks },
    rules: {
      ...ts.configs.recommended.rules,
      ...hooks.configs.recommended.rules,
    },
  },
];
