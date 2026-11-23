//  @ts-check

import { tanstackConfig } from "@tanstack/eslint-config"
import pluginQuery from "@tanstack/eslint-plugin-query"
import pluginRouter from "@tanstack/eslint-plugin-router"
import reactHooks from "eslint-plugin-react-hooks"

export default [
  ...tanstackConfig,
  ...pluginQuery.configs["flat/recommended"],
  ...pluginRouter.configs["flat/recommended"],
  reactHooks.configs.flat.recommended,
  {
    rules: {
      "import/no-cycle": "off",
      "import/order": "off",
      "sort-imports": "off",
      "@typescript-eslint/array-type": "off",
      "@typescript-eslint/require-await": "off",
      "pnpm/json-enforce-catalog": "off",
    },
  },
  {
    files: ["src/components/ui/**"],
    rules: {
      // The official shadcn registry emits inline type imports in its maintained primitives.
      "import/consistent-type-specifier-style": "off",
      // Its Sidebar names the updater's argument `open` inside the provider that holds `open`.
      "no-shadow": "off",
    },
  },
  {
    files: ["src/hooks/use-mobile.ts"],
    rules: {
      // The registry's useIsMobile, added with the Sidebar: it reads the viewport once after
      // hydration, so the server and the first client render agree (ExecPlan 0036).
      "react-hooks/set-state-in-effect": "off",
    },
  },
  {
    ignores: ["eslint.config.js", ".prettierrc"],
  },
]
