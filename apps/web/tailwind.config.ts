// Tailwind v4 uses CSS-first configuration.
// Dark mode "class" strategy is set via: @custom-variant dark (&:is(.dark *));
// in app/globals.css — equivalent to darkMode: ["class"] in Tailwind v3.
import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
}

export default config
