---
version: alpha
name: Meyo AgentOS
description: Private LangGraph-first AgentOS design system for framework docs, admin tools, and Meyo-specific product surfaces.
colors:
  primary: "#0F6B4C"
  primary-dark: "#094A34"
  primary-light: "#6FE8C7"
  secondary: "#3E5A50"
  tertiary: "#F59E0B"
  accent: "#FF4F40"
  neutral: "#FFFAF0"
  surface: "#FFFDF8"
  surface-muted: "#FFF6E5"
  ink: "#10221C"
  muted: "#3E5A50"
  border: "#DDE8E2"
  code-background: "#0B1713"
  dark-background: "#0A1720"
  dark-surface: "#0E231F"
  dark-surface-muted: "#102A24"
  dark-ink: "#C9EADC"
  dark-muted: "#8AB8AA"
typography:
  display:
    fontFamily: Space Grotesk
    fontSize: 48px
    fontWeight: 700
    lineHeight: 1.08
    letterSpacing: 0em
  h1:
    fontFamily: Space Grotesk
    fontSize: 36px
    fontWeight: 700
    lineHeight: 1.16
    letterSpacing: 0em
  h2:
    fontFamily: Space Grotesk
    fontSize: 28px
    fontWeight: 650
    lineHeight: 1.2
    letterSpacing: 0em
  body:
    fontFamily: Space Grotesk
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.7
    letterSpacing: 0em
  body-sm:
    fontFamily: Space Grotesk
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: 0em
  label:
    fontFamily: Space Grotesk
    fontSize: 13px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: 0em
  code:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: 0em
rounded:
  xs: 4px
  sm: 6px
  md: 8px
  lg: 12px
  xl: 14px
  full: 999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  content-max: 1200px
components:
  page:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    padding: 0px
  muted-panel:
    backgroundColor: "{colors.surface-muted}"
    textColor: "{colors.muted}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.md}"
    padding: 16px
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: 12px
  button-secondary:
    backgroundColor: "{colors.surface-muted}"
    textColor: "{colors.primary-dark}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: 12px
  navbar:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.full}"
    padding: 8px
  doc-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: 24px
  sidebar-item:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.secondary}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.sm}"
    padding: 8px
  code-block:
    backgroundColor: "{colors.code-background}"
    textColor: "{colors.dark-ink}"
    typography: "{typography.code}"
    rounded: "{rounded.md}"
    padding: 16px
  warning-badge:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.full}"
    padding: 4px
  critical-badge:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.full}"
    padding: 4px
  divider:
    backgroundColor: "{colors.border}"
    size: 1px
  dark-page:
    backgroundColor: "{colors.dark-background}"
    textColor: "{colors.dark-ink}"
    typography: "{typography.body}"
    padding: 0px
  dark-panel:
    backgroundColor: "{colors.dark-surface}"
    textColor: "{colors.dark-muted}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.md}"
    padding: 16px
  dark-rail:
    backgroundColor: "{colors.dark-surface-muted}"
    textColor: "{colors.primary-light}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: 8px
---

# Meyo AgentOS Design System

## Overview

Meyo is a private, LangGraph-first AgentOS framework shell. The interface should
feel precise, work-focused, and calm: a platform for runtime, knowledge, skill,
tool mesh, observability, and memory operations rather than a public marketing
site.

The visual language is compact and technical, with a warm documentation base and
quiet green accents. Product surfaces should prioritize scanning, comparison,
configuration, and repeated operation. Documentation can be more spacious, but
it should still keep Meyo's engineering tone.

## Colors

The canonical Meyo palette is derived from the current docs site theme.

- **Primary (#0F6B4C):** Deep operational green for links, active states,
  primary actions, and platform identity.
- **Primary Light (#6FE8C7):** Dark-mode accent and subtle status glow.
- **Secondary (#3E5A50):** Muted green-gray for metadata, descriptions, and
  secondary navigation.
- **Tertiary (#F59E0B):** Amber for warnings, queued work, and data-plane
  emphasis in diagrams.
- **Accent (#FF4F40):** Sparse coral accent for critical attention, never as
  the dominant UI color.
- **Neutral (#FFFAF0):** Warm page foundation for docs and explanatory
  surfaces.
- **Surface (#FFFDF8):** Main content, panels, and controls in light mode.
- **Dark Background (#0A1720):** Dark-mode foundation for docs and admin
  surfaces.

Use semantic colors intentionally. Do not turn the UI into a single green theme:
combine green identity, warm neutral surfaces, amber warnings, and restrained
coral exceptions.

## Typography

Meyo uses **Space Grotesk** for product and docs UI, matching the current docs
site. It gives technical density without feeling generic. Use **JetBrains Mono**
for code, identifiers, config keys, logs, and terminal output.

Headings should be direct and compact. Body copy should be readable for long
architecture notes and configuration instructions. Product panels, sidebars,
tables, and forms should use smaller type than hero or document titles.

## Layout

Use an 8px spacing rhythm with 4px available for micro-adjustments. Docs pages
can use a max content width around 1200px, while product tools should favor
dense, predictable layouts with persistent navigation and stable toolbars.

For Meyo-specific admin or agent surfaces, prefer full-width bands, tables,
split panes, inspectors, and panels. Avoid decorative landing-page structures
for operational tools. The first screen should be the usable workspace whenever
the task is an app, console, dashboard, or workflow tool.

## Elevation & Depth

Depth should come from tonal layering, borders, and subtle translucent surfaces.
Heavy shadows are reserved for floating menus and modals. The docs navbar may
use light blur and a thin border; operational screens should keep surfaces
plain, stable, and easy to inspect.

## Shapes

Default component radius is 8px. Small navigation rows and compact controls use
6px. Documentation surfaces that inherit Docusaurus theme styling may use 12px
or 14px, but new product cards and tool panels should stay closer to 8px.
Circular controls and pills use the `full` radius token.

## Components

Primary buttons use the deep green token on a light surface. Secondary buttons
use muted warm backgrounds with green text. Code blocks use the near-black
green background and JetBrains Mono.

Cards are for repeated items, modals, and genuinely framed tools. Do not nest
cards inside cards. For dashboards and workbenches, favor unframed sections,
tables, panels, and inspectors over decorative card grids.

## Do's and Don'ts

- Do keep Meyo interfaces calm, technical, and operation-first.
- Do reuse the root tokens for Meyo-specific docs, dashboards, and agent tools.
- Do preserve upstream app boundaries: `apps/meyo-chatbot` and
  `apps/meyo-studio-flow` can keep their native design systems unless a task
  explicitly asks for Meyo branding integration.
- Do use real product screenshots, diagrams, or generated assets when a page
  needs visual context.
- Don't port the `design.md` reference project's Bun/Turbo package structure
  into the root Python workspace unless the task is specifically to build a
  DESIGN.md CLI for Meyo.
- Don't use green as the only visible color family.
- Don't create marketing-style hero pages for tools, consoles, workflows, or
  admin surfaces.
