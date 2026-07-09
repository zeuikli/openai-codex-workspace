# 根目錄 × TPKI 重構裁決（Fable 5，2026-07-05）

## 裁決：nest（TPKI 續任知識路由，Schema 層指向 v3 四層）

| 決策 | 內容 | 理由 |
|------|------|------|
| D1 | TPKI 三層與 v3 四層**正交共存**：TPKI 管「知識放哪、怎麼查」；L1–L4 管「行為怎麼約束」。TPKI Schema 層的 canonical = v3 harness | replace 會丟掉 9+ scripts 依賴的 O(1) 路由，零收益 |
| D2 | `memory/` `evolution/` `config/` `schemas/` `scripts/` `tests/` `reports/` `tasks/` **物理留原地**，以 INDEX 層標籤宣告所屬 harness 層（L3/L4） | 已在正確層位；搬移 = 17 scripts + 9 hooks codemod 風險換純美觀 |
| D3 | 根散檔歸位（帶 codemod）：`OPERATIONS.md` → `playbooks/operations.md`；`prompts.md` → 併入 `prompts/README.md`；`SPEC.md`（86KB 舊系統規格）→ `docs/archive/SPEC-system-v1.md` | 根目錄只留：入口（CLAUDE/AGENTS/README/BRAIN/WORKSPACE-INDEX）+ 機讀狀態（SYNC-STATUS/harness-model-fit.json） |
| D4 | `BRAIN.md`、`WORKSPACE-INDEX.md` 檔名不動（10 scripts 斷言）、內容改寫為 v3-aware：Intent 表補四層路由、三層地圖對映 L1–L4 | 名 = 介面（穩定）、內容 = 實作（可換） |
| D5 | 每個根目錄 INDEX.md 增一行「Harness-Layer: L3-mechanism / L4-evolution / L4-knowledge」型別標記（TPKI typed-edge 延伸） | 讓四層架構可被 grep 稽核，非口頭宣告 |

## 對映表（TPKI type × harness layer）

| 目錄/檔 | TPKI type | Harness layer |
|---------|-----------|---------------|
| .claude/rules + CLAUDE/AGENTS | schema:contract | L1 |
| .claude/refs/model-profiles.md + profiles.json + harness-model-fit.json | schema:calibration | L2 |
| .claude/hooks + scripts/ + config/ + schemas/ + tests/ + playbooks/ + prompts/ | schema:mechanism | L3 |
| memory/ + evolution/ + reports/ + tasks/ | raw:state | L4-evolution |
| docs/ + templates/ | wiki:reference | L4-knowledge |
| research/ | raw→wiki | L4-knowledge（保留區） |
| portal/ | 產出物 | 保留區 |

執行：ceiling/quality 檔位；Fable 終審。驗收 = healthcheck FAIL=0 + 懸空引用 0 + BRAIN/WORKSPACE-INDEX 斷言錨點存活。
