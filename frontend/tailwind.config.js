/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        lumina: {
          50: "#f0f7ff",
          500: "#2563eb",
          600: "#1d4ed8",
          900: "#1e3a5f",
        },
      },
    },
  },
  plugins: [],
};
