module.exports = {
  content: ["./pages/**/*.{js,jsx}", "./components/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        gold: "#C9A84C",
        "gold-light": "#E8D5A3",
        "gold-dark": "#8B6914",
        obsidian: "#0A0A0A",
        "obsidian-2": "#111111",
        "obsidian-3": "#1A1A1A",
        "obsidian-4": "#242424",
        "obsidian-5": "#2E2E2E",
        stone: "#888888",
        "stone-light": "#AAAAAA",
      },
      fontFamily: {
        display: ["'Cormorant Garamond'", "serif"],
        body: ["'DM Sans'", "sans-serif"],
        mono: ["'DM Mono'", "monospace"],
      },
    },
  },
  plugins: [],
};
