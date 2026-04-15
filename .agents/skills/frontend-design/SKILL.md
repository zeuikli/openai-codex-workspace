---
name: frontend-design
description: 以產品化標準設計前端介面，強調可讀性、視覺層級、互動回饋與跨裝置一致性，避免模板化 AI 風格。
---

# Frontend Design

## Use when

- 你要新建或重做頁面 UI，並希望結果可直接進產品。
- 需要同時兼顧資訊架構、視覺語言與互動狀態（hover/focus/loading/error）。
- 你想建立可延伸的設計 token（色彩、字級、間距、圓角、陰影）。

## Do not use when

- 專案已有嚴格 design system 且本次只允許小幅維護。
- 任務主要是後端邏輯修復，前端只需最小顯示調整。
- 你無法驗證實際畫面（例如無法啟動前端或無法預覽）。

## Design Rules

- 先定義版面層級，再寫元件細節。
- 避免預設字體堆疊；字體選擇需有角色分工（標題/內文/程式碼）。
- 建立語義化色彩變數，不直接硬編色碼到元件。
- 互動動畫以意圖為核心，優先簡短且有意義的轉場。
- 桌機與行動版都需驗證主流程可用性。

## Done Criteria

- 有明確的視覺系統變數（CSS variables 或同等機制）。
- 主要頁面在 desktop/mobile 可正常使用。
- 元件狀態完整：default/hover/focus/disabled/loading/error。
