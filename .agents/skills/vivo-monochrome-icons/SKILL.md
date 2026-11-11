---
name: vivo-monochrome-icons
description: >-
  Enforces strict visual standards for icons in UI, dashboards, and documents:
  never use colored emojis or multi-colored icons; always use monochrome
  silhouette SVG icons in a single solid color — Vivo Purple (#660099).
  Activate this skill whenever creating or editing HTML, CSS, React, or UI components.
---

# Vivo Monochrome Silhouette Icons Standard

Whenever creating, updating, or styling any user interface, dashboard, button, tab, badge, or visual component, follow these mandatory icon rules:

## 1. Zero Colored Emojis or Multi-Color Icons
- **NEVER** use Unicode colored emojis (such as `📊`, `⚡`, `🔄`, `📥`, `📂`, `🔎`, `⚠️`, `🏢`, etc.) in HTML templates, buttons, notifications, or headers.
- **NEVER** use multi-colored SVG illustrations or multi-tone icons.

## 2. Always Use Single-Color Silhouette Icons (Vivo Purple `#660099`)
- Every icon must be a clean, minimalist **monochrome silhouette** (solid fill or single-color stroke `currentColor` / `#660099`).
- Default icon color: **Roxo Vivo (`#660099`)** (`fill: #660099` or `color: #660099`).

## 3. Standard Silhouette SVG Helper Pattern
Use inline `<svg class="icon-vivo" viewBox="0 0 24 24">` with:
```css
.icon-vivo {
  width: 16px;
  height: 16px;
  fill: #660099;
  flex-shrink: 0;
  display: inline-block;
  vertical-align: middle;
}
```
