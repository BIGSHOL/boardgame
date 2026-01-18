# Implementation Plan - Hanyang Project Setup

## Goal
Initialize the web application for "Hanyang: The Foundation" using Vite, React, and TypeScript, and configure the base styling with Vanilla CSS variables.

## User Review Required
- **Framework**: Vite + React + TypeScript
- **Styling**: Vanilla CSS (no Tailwind, per user request/rule)
- **Directory Structure**:
  - `src/components`: Reusable UI components
  - `src/pages`: Game screens (Main Board, Personal Board)
  - `src/assets`: Images and icons
  - `src/styles`: Global CSS and variables

## Proposed Changes

### [Project Initialization]
#### [NEW] [Project Scaffolding]
- Run `npm create vite@latest . -- --template react-ts`
- Install dependencies: `npm install`

### [Styling Setup]
#### [NEW] [src/styles/variables.css](file:///f:/boardgame/name1/src/styles/variables.css)
- Define CSS variables for the color palette:
  - `--color-gray: #373d41` (Architecture)
  - `--color-navy: #081429` (Scholars/Night)
  - `--color-yellow: #fdb813` (Wealth)

#### [MODIFY] [src/index.css](file:///f:/boardgame/name1/src/index.css)
- Import `variables.css`
- Reset default styles used by Vite template

### [Component Structure]
#### [NEW] [src/App.tsx](file:///f:/boardgame/name1/src/App.tsx)
- Clean up default Vite code
- Add placeholder layout for Main Board and Personal Board

## Verification Plan

### Automated Tests
- Run `npm run dev` to ensure the dev server starts without errors.
- Run `npm run build` to verify the build process.

### Manual Verification
- Open the local server URL.
- Inspect the page to verify that CSS variables are correctly applied (check for the specific hex codes).
- Visual check of the placeholder layout.
