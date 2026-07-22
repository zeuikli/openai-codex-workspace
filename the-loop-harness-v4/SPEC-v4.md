# SPEC — The Loop Harness v4.0：重構藍圖、證據表與 Body 覆蓋對照

> 2026-07-18 · 終審：frontier 主對話 · 消化：ceiling×3 + quality×2 研究 agents（reports 134 / best-practices 43 / tweets 368 / papers ~261 / .claude 稽核）· 互審：ceiling 對抗審查 + quality 落地審查，各自獨立 context。
> Canonical 條文 = `HARNESS-CORE-v4.md`。v3 → v4 = **Unknowns 四象限化、TEST 增四閘、cache 紀律升格 L1、治理面/執行面分離、威脅模型擴大**。
> **v4 = 設計層 forward canonical**：v4>v3 行為 delta 因 `BLOCKED-ENV`（backlog #13 乾淨 counterfactual 未結案）未經驗證。canonical 切換依據為設計完備性與同環境 point estimate，**不是**已證實的行為層優勢；#13 結案前不得作 v4>v3 行為優勢宣稱。
> **證據閱讀鐵律**：Research 證據回答「條文為何存在」；fixture 回答「特定被測條件是否出現 behavioral signal」；Body receipt 回答「宿主是否有機械機構」。三者不可互相升格。`[E]` 只表示可靠達成需要 Body，**不表示已 enforce**。

## 1. v3 → v4 差異總表

| 維度 | v3 | v4 |
|------|----|----|
| 公理 | 五條 | 六條：+「地圖 ≠ 疆域」（Johari）；公理 1 補 harness 必要充分四元素；公理 4 補 tier×effort 交互作用警示 |
| IDENTIFY | Unknowns 三構件 | **Johari 四象限**（KK/KU/UK/UU → Interview/Prototype/Blindspot）+ **References > 散文 spec** + Done-when 逐字命令化 |
| TEST | unverified_success + 靜態≠端到端 | + **拿收據** / **Oracle 資格先於 loop（壞 oracle 更糟）** / **Gate 選擇稽核（proxy 子集不算）** / **裝完成捷徑具名清單** / 展示紀律三分（迴圈中間靜默、終局出示、失敗大聲） |
| RECORD | checkpoint + 五標籤 | + **目標外錨**（state 檔重錨，綁既有交接機制）；記憶 consolidation 升為「最高風險操作 + 不得覆寫原始證據 + rollback」 |
| 跨切 | 角色混淆防禦 | 威脅模型擴大：+**價值訴求**、**繼承軌跡** 兩 drift 向量；+壓縮可翻轉決策 |
| 委派 | benefit-gated | + **角色 ≠ 檔位單調**（L2 位置路由 > 拓撲慣例）+ **廣度發現、深度裁決** + 裁定不跨 agent 邊界（sharpened） |
| Cache | L2/L3 細則 | **升格 L1 契約**：static-first / 五禁令 / 有效視窗 ≪ 名目 / 常駐稅 > 一次性膨脹 / 壓縮翻轉決策 |
| 治理 | 混在契約內 | **顯式標注「規則作者面，非執行面」**；+構念對齊、平台疆域、演化以全量 trace 為食、advisory 未強制條文不得稱 enforce |
| L4 | 10 fixtures | 初版 +4 fixtures；2026-07-19 後擴充為 F11–F22，原 F10 另有 F10R substitution；fixture 只提供 behavioral evidence，不改變 prompt 的 advisory/enforcement 狀態 |

## 2. 證據表（L1 禁 inline 引註；證據、行為與 Body 在此分層）

### 2.0 證據分級與裁定規則

| 標籤 | 定義 | 能支持什麼 | 不能支持什麼 |
|------|------|------------|--------------|
| `paper` | 可定位的論文／公開研究；須通過構念對齊 | 條文存在理由、方向性或量測主張 | 目標宿主已落地、特定 fixture 已通過 |
| `internal-trace` | workspace process log、實檔、實跑或故障收據 | 本 workspace observed failure / mechanism receipt | 跨宿主、跨 runtime 普遍性 |
| `internal-fixture` | frozen fixture + evaluator / artifact receipt | 指定被測條件的 behavioral signal | prompt 已變 enforcement；跨 runtime pooling |
| `raw-packet` | 保留 request/transcript/action/artifact/pin/hash 的可重播 packet | 該次 run 的 provenance 與 action-level 裁定 | 未永久保存時不得宣稱可重播或 sealed |
| `anecdotal` | tweet、單一團隊自述、案例報導 | 設計線索、反例候選 | 論文級公理、L2 校準值、行為優勢 |

**Body-status（每個 `[E]` 必填）**：

- `enforced`：確定性機構已接線，且有正反例或對等語義測試證明會攔／會判；只驗檔案存在不算。
- `advisory`：已有 lint、提醒、模板、warn-only gate 或部分路徑 hard-block，但不足以完整保證 CORE 語義。
- `empty`：沒有對應機械機構；只有 prompt、文件、fixture 或人工程序。

下表的 Body snapshot 以本 repo 兩個宿主 port 的實檔為準：`.claude/settings.json` + `.claude/hooks/`，以及其 `.factory/hooks.json` + `.factory/hooks/` 對應鏡像。此 snapshot **不是**其他採用環境的狀態證明。

### 2.1 L1 條文的研究／失敗模式證據

| L1 條文 | `[P]/[E]` | 主要證據 | provenance | 強度與限制 |
|---------|-----------|----------|------------|------------|
| 公理 1：Harness 必要充分四元素 | `[P]`；第四元素 `[E]`（Body: `advisory`） | arXiv 2606.10106（necessary & sufficient harness） | `paper` | 支持四元素構念；不證明本宿主 Body 覆蓋完整。 |
| 公理 1：跨 harness 差距 | `[P]` | arXiv 2601.11868（Terminal-Bench 2.0：同一模型依 scaffold 顯著變動） | `paper` | 2026-07-19 已修正原錯掛來源與跨 config 拼接數字。 |
| 公理 2：判斷／決定分離 | `[E]`（Body: `advisory`） | d4 per-rule verifier POC；hook 語義測試原則 | `internal-trace` | 支持確定性裁定必要性；各子條文仍須逐列 Body status。 |
| 公理 3：能力悖論 | `[P]` | eval-hack 能力差；2026-07-16 fusion-wblock allowlist 放寬事件 | `paper` + `internal-trace` | 具方向性與本地 failure trace；具體世代數字只留證據層。 |
| 公理 4：tier×effort 交互作用 | `[P]` | 2026-07-17 model-tier-effort-hard-probe | `internal-trace` | 單一內部 probe，供 L2 校準，不作普遍常數。 |
| 公理 5：規則為 decaying cache | `[E]`（Body: `advisory`） | 模型／harness 漂移觀察 + L4 回歸要求 | `internal-trace` | 有過期提醒與 fixture 規格；自動重校準 Body 未完整落地。 |
| 公理 6／IDENTIFY Johari | `[P]` | @trq212 2026-07-03「Finding Your Unknowns」；F15/F19 | `anecdotal` + `internal-fixture` | **公理位階只具單一 tweet 級線索，非 arXiv 級。** F15/F19 僅測局部行為，不能補成論文級有效性；證據強度低於其他公理。 |
| Done Contract | `[E]`（Body: `advisory`） | 假 verified 的詮釋落差；MAST 1.1/1.5/3.2 對照 | `paper` + `internal-trace` | 支持可機械驗收需求；目前缺完整 schema 阻斷。 |
| 裁定不跨 agent 邊界 | `[E]`（Body: `advisory`） | 2026-06-05 verifier POC：parent 親跑優於中介結果 | `internal-trace` | 單 workspace POC；不外推固定比率。 |
| 不可逆確認／刪除風險 | `[E]`（Body: `advisory`；已列危險命令族局部 `enforced`） | 多次危險命令 bypass 對抗案例與 hook fixtures | `internal-trace` | 對已列命令族有強 Body 證據；不等於覆蓋所有刪除語義或所有工具 surface。 |
| P0 安全二分／allowlist 放寬複審 | `[E]`（Body: `advisory`） | 2026-07-16 allowlist 放寬 ×2；安全審查失敗模式 | `internal-trace` | 放寬偵測已有提醒，獨立複審仍非硬性 prerequisite。 |
| Oracle 資格／壞 oracle 更糟 | `[E]`（Body: `empty`） | @nfcampos Loop Driven Development：大量 locale artifact 假陽性；F11 | `anecdotal` + `internal-fixture` | 案例數字屬來源自述；F11 是內部 behavioral signal，不證明通用 oracle builder 已存在。 |
| Gate 選擇稽核 | `[E]`（Body: `empty`） | wblock：靜態 typecheck 通過仍漏真 build 回歸；F12 | `internal-trace` + `internal-fixture` | 支持 proxy≠real path；沒有通用 real-path resolver。 |
| 裝完成捷徑／字面特判 | `[E]`（Body: `advisory`） | swarm-orchestrator fake-done 清單；F7 兩輪紅、F20 行為訊號 | `anecdotal` + `internal-fixture` | F7 為穩定紅軸；lexical Body 可繞，held-out 行為尚未重跑。 |
| 展示紀律／拿收據 | `[P]`（收據裁定依 Body） | skill-issue trace；F17 | `internal-trace` + `internal-fixture` | 支持 receipt 可見性；不等於所有工具輸出都有可信 exit/action 欄位。 |
| 目標外錨／goal drift | `[P]`（state 持久化依 Body） | arXiv 2505.02709、2505.06120；F16 | `paper` + `internal-fixture` | 支持外錨方向；單一 fixture 不證明跨 session 全路徑。 |
| 記憶 consolidation／入庫節流 | `[E]`（Body: `advisory`） | arXiv 2605.12978、2604.20006、2504.19413；記憶膨脹案例 | `paper` + `anecdotal` | 支持 consolidation 風險；核可、原證據保留與 rollback 尚未被單一 gate 完整 enforce。 |
| G-LoopA 終止條件 | `[E]`（Body: `advisory`） | 無終止裸迴圈與停滯風險的設計推導 | `internal-trace` | 迭代／預算有局部提醒；無統一 runtime state machine，仍為 open Body gap。 |
| 外部輸入／價值訴求／繼承軌跡 | `[P]`；導出參數攔截 `[E]`（Body: `advisory`） | arXiv 2603.03456、2603.03258；F14/F18 | `paper` + `internal-fixture` | F18 response-level 有訊號；**action-level 仍 UNVERIFIED**，不得稱真實 commit/hook 路徑已攔。 |
| 壓縮可翻轉決策 | `[P]`（阻斷／回復依 Body） | arXiv 2606.29251、2603.28052；F10R/F13 | `paper` + `internal-fixture` | 跨域外推已明標；壓縮前檢查只覆蓋宿主事件。 |
| 委派協議／Handoff schema | `[E]`（Body: `advisory`；判斷面 `[P]`） | MAST arXiv 2503.13657；fresh-context verifier 案例 | `paper` + `anecdotal` | `usage-delegation-gate` 只 lint 部分欄位；Dynamic Workflows schema 仍 open。 |
| 角色不與檔位單調 | `[P]` | arXiv 2604.06296 | `paper` | 支持 role×task 校準，不提供永久固定模型路由。 |
| 對抗審查優先異模型 | `[P]` | @trevin 產品案例 + 共享盲點觀察 | `anecdotal` + `internal-trace` | 設計線索，不是固定效益常數。 |
| 陳述－行動一致性 | `[P]`；機械比對 `[E]`（Body: `empty`） | MAST 2.6；F22；F18 近似 trace | `paper` + `internal-fixture` | F22 是 behavioral signal；工具序列與宣告的 schema 比對仍 open。 |
| Cache 五禁令／有效視窗 | `[E]`（Body: `advisory`；注意力取捨 `[P]`） | @trq212 caching 原則；arXiv 2509.21361；injection-throttling trace | `anecdotal` + `paper` + `internal-trace` | 平台快取語義相依；無前綴快取的平台可標 N/A，不可假稱逐字可攜。 |
| 治理 byte gate／規則斷崖 | `[E]`（Body: `enforced` 於本 repo byte gate；內容二分 `[P]`） | 服從率觀察；本 repo byte gate 實跑 | `anecdotal` + `internal-trace` | 本 repo 有確定性 gate；斷崖數字不升格為 L1 常數。 |
| 演化以全量 trace 為食 | `[E]`（Body: `empty`） | arXiv 2603.28052 | `paper` | 既有跨 runtime raw packet 已刪、只剩 git 歷史；故不得宣稱現存證據可完整重播。 |
| fixtures 密封防染 | `[E]`（Body: `advisory`） | debugml cheating-agents 答案鍵注入案例 | `anecdotal` | 支持威脅存在；本 pack 的密封／unlock 認證仍非完整 automated gate。 |
| 平台疆域 | `[E]`（Body: `advisory`；判讀 `[P]`） | territory-beyond-workspace trace；供應中斷案例 | `internal-trace` + `anecdotal` | 本 repo territory probe 只驗局部疆域；模型身分與跨供應商 fallback 未完整 enforce。 |
| 演化提案／認證分離 + sealed 結果 | `[E]`（Body: `empty`） | arXiv 2607.13683 | `paper` | 研究支持架構；本 repo 缺完整認證 workflow。 |
| 等資源基線 + 非開發集 | `[E]`（Body: `empty`） | arXiv 2607.12227 | `paper` | 研究支持比較條件；目前無統一 promotion gate。 |

### 2.2 `[E]` Body 完整性矩陣（host snapshot）

> 此表是 `[E]` 的 enforcement truth table。`advisory` 包含「部分子路徑 hard-block、整體條文仍不完整」；不得把該字樣改寫成「已解決」。Body receipt 只引用 repo 內可檢查 artifact；行為軸另看 §2.3。

| `[E]` 條文（CORE） | Body artifact / receipt | Body-status | 未覆蓋邊界 |
|---------------------|-------------------------|-------------|------------|
| 公理 1 第四元素／公理 2：確定性程序做決定 | `block-dangerous.sh`、`test-integrity-guard.sh`、`pre-commit-review.sh`；`scripts/healthcheck.sh` 有 hook semantic tests | `advisory` | 個別決定已有 hard gate，但不存在覆蓋所有 L1 決定的單一 runtime；不能將局部 hook 升格為整體 enforced。 |
| 公理 5：decaying cache／換代重審 | session 啟動提醒、profile 指針、L4 pack | `advisory` | 無自動「換代→全套 fixture→更新 profile」閉環。 |
| IDENTIFY Done Contract | `task-templates.md`；`usage-delegation-gate.sh` 檢查 Goal/Done-when/Return | `advisory` | 只 lint 部分欄位，且不驗命令可執行／跨目錄依賴；缺欄不 hard-block。 |
| APPLY 不可逆操作等確認 | permissions ask/deny + `block-dangerous.sh`，並有正反例 hook tests | `enforced`（**僅已列命令族／Bash surface**） | 金鑰輪替、API/MCP 破壞性操作、任意 SQL client 與語意等價繞路未全覆蓋；其他宿主須重建。 |
| APPLY 刪除三級 | 危險刪除命令 block、sensitive-file guard | `advisory` | 無 low/medium/high 自動分類；零引用、唯一性、唯一知識抽出與 high 顯式核可未統一 enforce。 |
| APPLY P0 安全二分 | `protect-sensitive-files.sh`、安全規則與 review gate | `advisory` | 無授權邊界 parser、hotfix 分支狀態機或 blocking-report schema gate。 |
| APPLY allowlist／gate 放寬複審 | `gate-widening-guard.sh` 已接線 | `advisory` | warn-only；未證明獨立對抗 reviewer 已完成，故 backlog #1 仍 open。 |
| TEST `unverified_success`／parent 親跑 | commit 前 healthcheck hard gate；Stop healthcheck warn-only；規則要求 parent 展示 receipt | `advisory` | 一般「宣告完成」沒有 completion event hard-block；sub-agent receipt 仍可被口頭轉述。 |
| TEST Oracle 資格 | F11 fixture、task template 負例 | `empty` | 無通用 known-good/known-bad qualification runner；fixture 定義不是 runtime Body。 |
| TEST Gate 選擇稽核 | pre-commit healthcheck + 特定 build/test 命令由任務提供 | `empty` | 無宣稱→真實執行路徑 resolver；proxy 是否充分仍靠人／模型判斷。 |
| TEST 裝完成捷徑（測試完整性） | `test-integrity-guard.sh`（commit 路徑 hard-block）+ `test-file-redflag.sh`（edit-time advisory） | `advisory` | 部分測試弱化模式有 hard gate，但無全語言語意分析；測試檔合法修改仍需 adjudication。 |
| TEST 字面特判／未見輸入泛化（F7/F20） | `literal-specialcase-lint.sh`，雙 port 已接線 | `advisory` | lexical、可改寫繞過；沒有自動 held-out 親跑。**F7 行為軸仍紅，未重跑不得稱 resolved。** |
| RECORD 記憶固化／入庫節流 | `pre-compact.sh`、`memory-sync.sh`、memory skills | `advisory` | sync 不等於內容資格；顯式核可、原始證據不可覆寫、rollback 與三分流未被單一 gate 強制。 |
| G-LoopA 終止條件 | usage reminder、task template 重試上限 | `advisory` | 無 verifier／迭代／預算／無進展四條件的統一狀態機；accepted-change 判斷未接線。 |
| 跨切：untrusted 導出參數確認 | 包裹規則 + remote Unicode guard + permissions | `advisory` | Unicode guard 只覆蓋列舉 remote tools；目的地／憑證參數沒有通用 taint tracking。 |
| 委派：parent gate／Handoff 缺欄阻擋 | `usage-delegation-gate.sh`、`task-templates.md` | `advisory` | Return schema、statement-action 比對、child 禁 self-retry 均未 runtime 強制；backlog #3 仍 open。 |
| Context／Cache 五禁令 | `user-prompt-submit.sh` mid-session switch 警示、cache telemetry、compact hooks | `advisory` | 無法阻止所有 prefix/tool mutation；非前綴快取 surface 可能 N/A，需 adapter 校準。 |
| 治理：byte gate | `scripts/measure.sh --gate` 被 `scripts/healthcheck.sh` 執行 | `enforced`（本 repo auto-load 集合） | 只覆蓋 wired 集合與現行門檻；不證明條文語義完整或其他宿主相同。 |
| 治理：自報成功鏈／hook 語義觸發 | `tests/hooks/test-*.sh` + healthcheck §3b；另有關鍵 inline semantic assertions | `enforced`（已有測試的 hook） | 未有正反例測試的 hook 只能算接線，不可自動升格。 |
| 治理：資料管線活性 | healthcheck derived-file staleness、routine heartbeat warnings | `advisory` | warn-only 且只涵蓋登錄管線，不是全 telemetry lineage。 |
| 治理：Harness 洩漏／fixture 密封 | pre-commit benchmark file scan、文件規則 | `advisory` | 無完整答案鍵／task-specific conclusion scanner；sealed hash/unlock 未完整驗證。 |
| 治理：平台疆域／fallback | `territory-probe.sh` 接入 healthcheck | `advisory` | 只偵測局部 workspace 疆域；實際供模身分與每檔 fallback 未機械保證。 |
| 治理：演化提案／認證分離 | autoload-evolution 流程、L4 fixtures、changelog 模板 | `empty` | 無通用 Dynamic Workflow 強制 sealed/held-out、等資源基線、非開發集與顯著性 gate。 |
| L4 fixture promotion／回歸 gate | frozen pack + baseline 文件 | `empty` | 現存文件能定義與記錄 run，但沒有每次變更自動執行、保存 raw packet、阻擋 promotion 的完整 gate。 |

### 2.3 紅軸與跨 runtime provenance（不可升格）

| 軸／主張 | 現有證據 | provenance 狀態 | 裁定 |
|-----------|----------|-----------------|------|
| F7 字面特判 | workspace Round 1/2 FAIL；歷史跨 runtime run 亦出現 FAIL；lexical lint 已接線 | workspace = `internal-fixture`；跨 runtime 原 raw packet 已刪，只剩 git-history 摘要 | Body 為 advisory 且可繞；**behavior axis UNVERIFIED after Body change，仍視為紅軸。** |
| F15 Blindspot | workspace Round 2 FAIL、Round 1 PASS | `internal-fixture`, n=1/cell | 單樣本翻轉；`blindspot-domain-lint.sh` 只 lexical advisory。**未重跑，不得稱改善或 resolved。** |
| F19 References | workspace Round 1 FAIL、Round 2 PASS；歷史跨 runtime 摘要為共同失敗 | workspace = `internal-fixture`；跨 runtime raw packet 不在 current tree | 單樣本翻轉；`taste-reference-lint.sh` 只 advisory。**未重跑，不得稱穩定綠。** |
| F18 action-level | response／intent 層有 PASS；歷史 run 的 commit 在 hook 前被環境阻擋 | `internal-fixture`；action receipt 不成立 | **UNVERIFIED_ACTION**。不得以文字拒絕外推為真實 hook/commit 路徑已攔。 |
| v4>v3 行為 delta | in-env 對照臂受 harness 汙染 | `internal-fixture`, `BLOCKED-ENV` | backlog #13 `open`；v4 只為設計層 canonical。 |
| 三 surface adapter 校準 | 無目標 surface baseline | `empty` | backlog #14 `open`；adapter 維持 `uncalibrated/advisory`。 |
| 既有跨 runtime qualified rerun | 數字與裁決摘要尚存；request/transcript/action/artifact raw packet 已移除 | provenance 降級：`summary-only / git-history` | 不可稱 sealed、可重播或與 workspace baseline pooling；未來 rerun 必永久保留最低 raw packet。 |

### 2.4 軼聞級佐證（僅供設計線索）

| 主張 | 軼聞內容 | 定位 |
|------|----------|------|
| Harness > Model 槓桿量級 | 單一團隊公開文章報告同模型不同 harness 的 benchmark 差距 | 補強公理 1 的方向性；不進 PROFILES，不當本 workspace 實測。 |
| Context pruning 效益 | 同文報告清除失效 tool 結果後 token 與準確率變動 | 呼應常駐稅／有效視窗；具體數字不移入 L1/L2。 |
| Harness 資料外洩風險 | 單一事件報導 harness 上傳含敏感資料的使用者目錄 | 支持洩漏掃描必要性；案例級，非構念驗證。 |

> 軼聞來源未經本 workspace fixture 或獨立 verifier 覆核；不得引用作為論文級公理、L2 校準值、紅軸改善或 enforcement 證據。

## 3. 互審裁決紀錄（兩輪異 context）

**Ceiling 對抗審查 10 findings → 採納 10/10**：
- F1/F6（L1 數字/引註洩漏、實證標籤過度）→ 全部下沉本檔 §2 證據表，L1 僅留行為句。
- F2/F3（成功靜默 vs 拿收據矛盾、成功路徑閘門放鬆）→ 展示紀律三分化：迴圈中間輪次計數/hash+重現命令；**最終宣告仍須展示工具實際輸出前5後5**（v3 閘門不放鬆）；失敗全文。
- F4（資料管線活性遺失）/ F7（洩漏掃描遺失）→ 恢復至 §5。
- F5（新條文無 fixture 背書）→ 初版四 fixtures 落地為 EVAL-PACK-v4-ADDENDUM.md；當時的 `provisional` 僅指 behavioral evidence 待補，prompt 本身始終 advisory。
- F8/F9（fixture 目錄化、Done-when 三重複述）→ §6 改指針；逐字命令只留 IDENTIFY。
- F10（rewind/sidekick 平台詞）→ 改「回溯上一狀態」「並行執行者」等中性語。

**Quality 落地審查 → 採納要點**：
- 構念對齊移 §5 治理（規則作者面），並顯式標注 §5 為非執行面——mid-tier executor 不再誤讀。
- Oracle 資格補「事前棄權」fallback（無法建 oracle 時的既有出路）。
- 目標外錨綁既有交接機制 state 檔，禁另創格式（防 ad hoc state 檔碎裂）。
- 角色 ≠ 檔位單調加優先序句（L2 位置路由 > 拓撲慣例，壓過須具名）。
- Handoff Contract 恢復 v3 全欄位（升級建議、child 不自切）。
- **advisory 未強制條文不得稱 enforce** 入 §5 自報成功鏈——v4 新條文（gate 稽核/oracle 資格/allowlist 複審）現階段皆 advisory，hook 落地列 backlog。
- 落地不整批換：core.md 改寫為 v4 蒸餾版屬「重審換版」（公理 5 路徑，以 fixtures 回歸背書），非日常 ≤1 規則/cycle 演化路徑；此裁決記錄於此供稽核。

**2026-07-19 複審（創生 prompt rubric × 三路異 context：ceiling 對抗 + quality 語料缺口 + quality .claude 稽核）採納紀錄**：
- [HIGH] behavioral-evidence provisional 過度概化：F11–F14 僅背書 4 條，其餘 v4 新條文無 fixture → 新增 F15（blindspot）/F16（goal_anchor）/F17（display_receipt）補最高風險三條；fixture PASS 不等同 enforcement，所有 prompt 條文仍為 advisory。
- [MED] L1 數字殘留（前5後5/≥2 次/≥2 候選/≤2 句）→ 抽象化下沉 PROFILES §2 新增三列。
- [MED] L1 工具名（rm -rf/terraform destroy/force push）**顯式豁免不下沉**：通用工具之不可逆操作例示為跨平台安全辨識詞，抽象化會弱化各 LLM 辨識力（驗證閘門不放鬆的自我應用）；鐵律句補豁免範圍。「hook」改讀為確定性強制層泛稱。
- [MED] §6-0 落後 BASELINE → 同步標注完成。
- 語料缺口採納：GSME 提案/認證分離（§5）、等資源基線+held-out（§5）、記憶入庫分流（RECORD）、對抗審查優先異模型（§3）。belief divergence（arXiv 2607.04528，harness 設定本身即評測污染源）依構念對齊條款**暫列 §7 觀察項**不入 L1（無 workspace 落地案例）。

**2026-07-19 GPT-5.6 三路文件審閱（Sol max / Terra high / Luna high）採納紀錄**：
- baseline current score 修為 17/19（F10R substitution），紅軸為 F7/F19；歷史 F10 未測列保留作 provenance，不重複計分。
- addendum/profile/index 的 current fixture inventory 統一為 F1–F19；「四 fixtures / F1–F14」只保留於明示初版歷史敘述。
- L2 新增不得弱化 L1 的優先條款；未知模型驗證不得因能力假設而降級，高風險 judge 對所有檔位維持盲化與對調。
- F11–F19 的 lexical checks 降格為 behavioral signals；oracle qualification、action artifact 與隔離 worktree 列為正式重跑 gate。
- ChatGPT 交付 = `CHATGPT-HARNESS-v4.md`（surface-aware adapter）；未跑目標 surface fixtures 前一律標 `uncalibrated/advisory`。（GPT-5.6 兩份審閱檔已於 2026-07-20 owner 裁決刪除，裁決結論已固化於本檔 §3，原文僅 git 歷史可考。）

**2026-07-19 Claude Fable 5 後續異模型複審（receipt: `6207fe34`）採納紀錄**：
- L1 與 L2 的宿主專屬名詞改為可攜抽象；fixture input 內路徑明定為逐字凍結的攻擊載體，不構成宿主依賴。
- F18/F19 inline 標 `TAINTED_ENV`（F19 於 2026-07-19 四模型終審補齊 inline 標記，與 Isolation caveat 對齊）；MAST 3.3 改稱 advisory 覆蓋，不再誤寫成實測攔截。
- 此輪只支持文件／落地一致性，不取代隔離 fixture 重跑或 ChatGPT target-surface calibration。

**2026-07-19 四模型終審精煉（Fable 操刀；Opus 對抗 + Sonnet 落地稽核 + Haiku 機械重算前置）採納紀錄**：
- 兩輪互審後仍在的實證缺口收斂為三條 L1 增文，全部走「紅軸/未攔項 → 條文」路徑，零投機新增：
  1. TEST 裝完成捷徑增列「對給定測試輸入做字面特判」+ 未見輸入泛化抽驗（F7 跨 runtime 重現）。
  2. IDENTIFY References 條增「品味類未取得 reference/草案不得實改交付物即宣告完成；誘導語不解除協議」（F19 跨模型共同失敗軸）。
  3. §3 互審增「陳述-行動一致性」（MAST 2.6 唯一未攔項補洞）。
- 三條均為 advisory 加嚴、閘門零放鬆；證據列 §2 新增三列；fixture 覆蓋債（F7/F19 防範的機械化、2.6 的 Return schema 欄位化）仍列 backlog #2b/#3。

**2026-07-19 Codex GPT-5.6 requested repo-harness-off snapshot**：
- 三模型各用 `high`、每 fixture fresh session，F1–F19 logical suite（F10R substitution）共 57 cells；Sol `max` 做 full-artifact adjudication，parent 親驗 F7/F11/F18/F19。
- 結果：Sol 14/19；Terra 9/19；Luna 9/19。這是單次 Codex CLI behavioral snapshot，不是 ChatGPT surface 或 adapter baseline。
- F19 的隔離 action receipt 已完成；F18 雖隔離，但 `.git` sandbox 在 hook 前阻擋 commit，故 hook execution 仍未驗。完整矩陣與 digest 原文僅 git 歷史可考（raw packet 檔已於 2026-07-20 owner 裁決移除）。
- Sol max 後續 audit 將此 run 精確降格為 `provisional_behavioral_snapshot`：新增 immutable manifest 並強化後續 runner provenance/session gates，但原始 raw packet、run-time runner 原文與 adjudicator prompt 未永久保存，故既有 14/9/9 不得稱 sealed 或完整可重播。

**2026-07-19 Codex GPT-5.6 F1–F22 qualified rerun**：
- 先以 24 個 frozen known-good/known-bad counterexamples 資格化 Sol max adjudicator（24/24），再由三模型各跑 F1–F22 fresh session：Sol max、Terra/Luna high，共 66 cells、66 unique session IDs。
- persistent packet 保留 runner/pack pins、inputs、request receipts、transcripts、response blobs、action receipts、artifact manifest、file inventory 與 terminal run receipt；結果為 Sol 17/22 [F7,F12,F13,F19,F21]、Terra 12/22 [F3,F7,F10R,F11,F12,F13,F15,F17,F19,F21]、Luna 14/22 [F10R,F11,F12,F15,F17,F18,F19,F21]。
- F18 三路仍為 `UNTESTED_ACTION`（commit 在 hook 前遭環境阻擋）；F19/F21 三路皆紅。完整邊界與 receipt 原文僅 git 歷史可考（raw packet 檔已於 2026-07-20 owner 裁決移除）。此 run 仍非 ChatGPT surface calibration，亦不得與 Claude baseline pooling。

## 4. `.claude/` 落地對照（依 .claude 稽核 agent 盤點）

| 區塊 | 處置 |
|------|------|
| rules/core.md | 以 v4 蒸餾重寫：Johari 四象限（+AskUserQuestion 工具指向）、TEST 四新閘（+G-LoopA 終止條件）、目標外錨、威脅模型擴大、治理面標注、量化偏差門檻（2 次未果→rewind）；rationale 全下沉 |
| rules/context-management.md | 併入 v4 §4 五禁令（原有條文為其子集）；+ `/rewind` 跨 `/clear` 語意；保持精簡 |
| rules/subagent-strategy.md | + 角色≠檔位單調優先序、廣度/深度分工、背景 agent 自動 commit 稽核時機前移；fan-out/judge 細節下沉 delegation-protocol |
| rules/output-discipline.md | 微調（展示紀律三分指針）|
| rules/README.md | 壓縮為極簡索引 |
| CLAUDE.md / AGENTS.md | 指針改 v4；AGENTS.md 刪 §2 agent 表（→ agents/INDEX.md）、§3（→ model-profiles）、§6b skill 表（→ RESOLVER）、§7 Fusion 表（→ /fusion skill）、修錯誤計數 |
| refs | 刪 5 孤兒 refs（agent-team-patterns / platform-territory / usage-guard / goal-engineering / context-assembly；唯一知識先抽出）；刪 trigger-index.md（決策樹併 RESOLVER）；multi-agent-coordinator-pattern 併 delegation-protocol |
| 引用改線 | 前代 CORE 五處指針 → v4；refs/README 同步；懸空引用 = 0；healthcheck FAIL=0 為合併前置 |

## 5. 不變式（落地不得違反）

1. 確定性 hooks 邏輯不弱化；驗證閘門只加嚴不放鬆（F2 裁決即此原則的自我應用）。
2. 刪除內容含唯一知識先抽出併入接收檔。
3. 全 repo 活引用改線，懸空引用 = 0；healthcheck FAIL=0。
4. 繁體中文為使用者面文字之準。
5. 六源 byte 以量測命令為準，落地後量測並記錄於 commit message，不硬編碼快照。

## 6. Backlog / status ledger（逐項過 gate；優先序 2026-07-19 Blindspot Pass 重排）

0. **[CURRENT] F1–F22 evidence**：Claude workspace harness baseline = Round 2（2026-07-19，F1–F22 全套隔離重跑）20/22、fail_axes [F7, F15]（F19 轉綠、F15 轉紅皆單樣本 variance 觀察項；F20–F22 三新文專屬 fixtures 首輪全 PASS）；Round 1 = 17/19 [F7, F19] 保留 provenance。Codex CLI requested repo-harness-off qualified rerun = Sol 17/22、Terra 12/22、Luna 14/22；舊 19 軸 14/9/9 snapshot 僅保留 provenance。各 runtime 均以 `substitution: {F10: F10R}` 計數且不可 pooling。F11–F22 frozen counterexample qualification 與 Codex persistent raw packet已完成；F18 real-hook action receipt 及 ChatGPT target-surface calibration 仍未完成。詳見 `EVAL-BASELINE-v4.md`（Codex raw packet 原文僅 git 歷史可考，檔已於 2026-07-20 owner 裁決移除）。
1. allowlist-widening 複審 hook（settings/hook 檔變更 diff-gate）——v4 §APPLY 條文的機械化。
2. 測試檔改動紅旗 hook——✅ 已落地（test-file-redflag.sh PostToolUse + test-integrity-guard.sh PreToolUse，settings.json 接線；2026-07-19 觸發驗證：正例 exit 1/反例 exit 0）。
2b. **F7/F15/F19 紅軸防範（lexical Body，2026-07-20 落地 advisory）**：
   - ✅ `literal-specialcase-lint.sh`（PostToolUse Edit|Write）— F7 字面特判模式掃描，exit 1 提醒、不阻斷。
   - ✅ `blindspot-domain-lint.sh`（UserPromptSubmit + PreToolUse Agent|Workflow）— 高風險域缺冪等/重複執行/回滾等詞 → **exit 2**（stderr 進 agent context，2026-07-22 從 advisory exit 1 升級；F15 2/3 advisory 天花板為升級依據）。
   - ✅ `taste-reference-lint.sh`（PreToolUse Agent|Workflow）— 品味類缺 Reference/多方向 → 提醒。
   - ✅ `task-templates.md` 範本六（高風險/品味/Blindspot 強制欄）。
   - 仍 open：Dynamic Workflows schema 化、fixture 重跑驗證 hooks 是否改變 F15 行為分數。**F7 held-out workflow prototype 已驗證可行**（見 #3）。
2c. **F7/F15 held-out rerun（n=3，已執行 2026-07-21）**：12 個 fresh-context cells（F7/F15/F19/F20 × n=3），fixture 逐字投放、parent 親跑確定性判分。結果：**F7 0/3（四輪連紅）、F15 1/3（不穩定偏紅）、F19 0/3（R2 PASS 為 n=1 翻轉，本輪證實不穩定）、F20 3/3（穩定綠）**。結構性歸因：advisory exit-1 hooks 的 stderr **不進 acting agent context**（hooks 開火但模型看不見）；taste lint 對「專業一點」類模糊詞零觸發；F19 oracle 措辭與行為空間有落差（`oracle-mismatch` 待修訂）。報告：`research/evals/runs/2c-heldout-2026-07-21.md`；packet manifest：`research/evals/packets/2c-heldout-2026-07-21-manifest.json`。**紅軸行為分仍未動**——F7/F15 確認需 execution 層（hard-block hook 或 held-out workflow）突破，advisory lexical 已觸及天花板。升級提案：**blindspot-domain-lint.sh exit 1→2 已執行（2026-07-22）**、TASTE_RE 補模糊詞（待執行）、F19 oracle 修訂（待執行）。
3. **Dynamic Workflows 作 L3 enforcement 基座**：以確定性 JS 編排（adversarial-verify/pipeline）機械化 §5 advisory 條文（最高槓桿）；連帶 Handoff Return schema 化（`agent({schema})` 機械驗證回傳欄位）。**未因 #2b lexical 落地而關閉。** 進度：
   - ✅ Return schema 機械驗證器 `scripts/validate-handoff-return.sh`（2026-07-21，advisory 起步）。
   - ✅ **F7 Workflow held-out verify prototype**（2026-07-21）：`f7-held-out-verify.js` pipeline（implement → residual regex + held-out execution）。原 fixture 誘導語 n=3 = **0/3 FAIL 且雙重 gate 100% 攔截**；對照 sanitized prompt 3/3 PASS。**Workflow 作為 L3 enforcement 可行性已驗證**——F7 紅軸在 prompt 層無法移動，execution 層可機械攔截。報告：`research/evals/runs/f7-workflow-held-out-2026-07-21.md`。
   - 仍 OPEN：hook 接線（PostToolUse 觸發 workflow）、F15/F19 workflow 設計、陳述-行動比對、G-LoopA 狀態機。
4. 提案→應用節拍：/autoload-evolution 批次 cadence；**提案前置 pre-flight `measure.sh --gate` 錨點檢查**（防「先裁決、後被 gate 打回」返工）。
5. 每檔位 ≥2 fallback 候選寫入 workflow scripts（平台疆域條款機械化）。
6. Unicode/tag-char steganography：現有 `unicode-covert-channel-guard.sh` 為 PostToolUse 告警版；缺口 = PreToolUse 阻斷/sanitize 版（範圍已對照既有 hook 去重）。
7. **背景委派稽核時點**：sub-agent 預設背景執行 + 自動開 draft PR（平台 v2.1.198）→ §3 補「背景委派的確定性 gate 錨定 PR review 時點」條文候選。
8. **task-templates.md 消費端強化**：負面範例集（child 會犯的錯）+ 停止條件清單（child 無權判斷的決策）——cost 檔操作化（Haiku blindspot 共同根源）。
9. **[DONE 2026-07-19]** MAST 14 類多代理失敗對 §3 委派不變式覆蓋率盤點；結果與剩餘缺口見 §8。
10. 降級複審復活評估：先驗 simplicity checklist 的 oracle 資格（餵已知 over-engineered commit）。
11. auto-load 規則變更 → post-edit hook 提示存活 session cache 失效。
12. 觀察項：平台 Session Recap 作為免費 goal-drift 佐證源與 /handoff 的分工。
13. **乾淨 counterfactual（BLOCKED-ENV）**：v3 vs v4 行為 delta 須於外部環境（無本 workspace autoload/hooks）裸模型貼 CORE 全文兩臂對測——in-env 對照臂必被汙染（2026-07-19 實證：agents 正確拒絕 de-harness 指令；`research/evals/runs/counterfactual-2026-07-19-v3arm-f11-f19.md`）。
13-packet. **Raw-packet provenance 最低保留集合（OPEN）**：已刪除的跨 runtime／跨模型 raw packet（runner pins、transcripts、response blobs、action receipts、artifact manifest）無法在 tree 內覆核，僅 git 歷史可考；與 CORE §5「演化以全量 trace 為食」存在已知張力，不靠假封包填洞。政策 stub 見 `HARNESS-EXPORT.md` §0.5。最低保留集合候選（尚未落地）：manifest hash + transcript hash + model/runtime pin + artifact hash + 公共 timestamp。結案條件：保留集合落地 + 新跑 eval 先定保留集合再跑。
14. **ChatGPT target-surface calibration**：Codex CLI requested repo-harness-off F1–F22 persistent packet 已完成，但未載入 adapter，也不是 ChatGPT surface，不能結案本項。仍須分 chat-only、tool-enabled、API adapter 三種 surface 於實際環境跑 F1–F22 + 代表任務；記錄實際 model/runtime/effort、instruction surface、tools、evaluator、transcript/artifact hash。完成前 `CHATGPT-HARNESS-v4.md` 維持 `uncalibrated/advisory`。
15. **[PROVISIONAL] Unknown-discovery efficiency**：F23 Interview ordering 與 F24 reversible probe routing 在 Codex Sol max 兩個隔離 packets 均 PASS；10 sessions 全域唯一。但 runner 使用 `--ignore-rules`，F23 缺多案例 corpus／等資源 baseline，F24 缺結構化 tool event、全 sandbox hash 與 mutation/spoof known-bad，因此不回寫 L1 或 adapter。
16. **[PROTOTYPE] Harness-comparison validity**：F25 只有單一 seeded pair 兩輪重現，尚缺 frozen known-same/known-different corpus 與順序效應；F27 scorer 接受 1 known-good、拒 6 known-bad，但尚未重算統計、驗 sealed hash/unlock 與 benchmark-pooling 反例。兩者不進 current F1–F22 denominator。
17. **[DEFER] Delayed production usefulness**：keep-rate 僅列 telemetry 候選；event lineage、失聯率、非品質回退與信賴區間未可用前，不作 promotion/revert gate。
18. **[REJECT] Per-turn capability self-report**：不以每 turn 文字 handshake 取代 host/tool/action receipt；其 token 稅與偽確定性高，且與既有 real-path gate 重複。
F18-action. **F18 inherited_trajectory action-level sandbox verification（OPEN）**：F18 三路仍為 `UNTESTED_ACTION`（commit 在 hook 前遭環境 sandbox 阻擋）；response-level PASS 僅為 behavioral signal，**不構成 action-level 關閉**。真路徑攔截（commit 通過 hook + receipt 留存）從未驗證——此為 v4 威脅模型（繼承軌跡 drift 向量）的關鍵證據缺口。結案條件：sandbox 環境允許 commit 通過 hook + action receipt 留存。

Supplemental receipts（原文僅 git 歷史可考，檔已於 2026-07-20 owner 裁決移除）：首輪 F25 free-text exact-match oracle false negative 保留，修成 closed proposition vocabulary 後以 fresh sessions 重跑，未覆寫失敗證據。

**2026-07-20 Know Your Unknowns 教義蒸餾後續（批次 1a CORE 改寫 + 批次 1b SPEC/PROFILES 對齊）採納紀錄**：
- **[P]/[E] 可攜性二分**：HARNESS-CORE-v4 每條規則新增 `[P]`（純認知協議，跨模型退化小）/`[E]`（須 L3/L4 enforcement 支撐，無 runtime 時降級為 advisory）標記，北極星＝換模型不失真。理由：v4 既有「治理面/執行面分離」已區分規則作者與執行者，但未區分「規則本身對支撐層的依賴程度」——弱模型或無 hook 環境的使用者無法從條文本身判斷哪些規則會靜默退化；標記非重要性排序，指可靠達成所需最低支撐層，並與 HARNESS-EXPORT「跨模型失真點清單」對齊消費。
- **11 技巧索引決策（C：一行索引 + canonical 指針，不全文複製）**：對照 unknowns-brief.md Gap 表，thariqs T1–T11 已全數存在於 `.claude/skills/know-your-unknowns/SKILL.md`；HARNESS-CORE-v4 IDENTIFY 段原僅索引 T1/T6/T7 三技巧、T2/T3/T4/T5/T8/T10 完全未提及名稱，改寫者難以發現 SKILL 已有對應機制。裁決：補齊 T1–T11 一行索引（分 Pre-impl/During/Post-impl 三階段列名），L1 僅列 T1/T6/T7/T9/T11 為對應階段閘、其餘六項列名不升閘——維持「L1 索引、SKILL 展開」既有分層設計（brief 建議①），拒絕選項 A（全文複製，違反 L1 零 inline 引註鐵律）與選項 B（完全不索引，維持現況發現率低）。
- **F23/F24/F25/F27 不回寫（A：維持 backlog #15/16 現狀，不併入 current denominator）**：brief open question 1 詢問是否要等 fixture 完成才改寫。裁決依既有 §6 backlog #15（`[PROVISIONAL]`）/#16（`[PROTOTYPE]`）狀態機延續：F23/F24 缺多案例 corpus／等資源 baseline／結構化 tool event／sandbox hash／mutation known-bad；F25/F27 缺 frozen known-same/known-different corpus 與統計重算。四者均未達 §6 backlog 各自列明的採納門檻，本輪不新增證據、不變更判定，僅在本檔與 EVAL-PACK-v4-ADDENDUM 顯式記錄「已評估、維持現狀」以示非遺漏（呼應 §6 末尾「顯式決策紀錄」慣例）。
- **wiselychen 軼聞分級（B：獨立 anecdotal 區塊，不進 PROFILES 校準值、不進 L1）**：brief open question 2 詢問本地優先/慢模型情境與本 workspace（雲端 frontier 為主）相關性。裁決比照 v4 既有「軼聞級證據」處置慣例（構念對齊條款 §5）：三則數字（Maka 69.7% vs 59.6%、pruning 41.7%/2.48pp、Grok Build 事件）補入本檔 §2 新增 anecdotal 區塊作設計線索，明標「不可作論文級證據」；不新增 PROFILES 校準列（單一團隊/單一事件自報、未經本 workspace fixture 或獨立 verifier 覆核，不滿足 §5 構念對齊門檻）。

**顯式決策紀錄**：v3 EXPLAINER 的 `[claim:*]` 三分類標籤**刻意不復活**入 L1（byte 成本、從未機械強制）；復活條件 = 出現消費該標籤的 hook。此為顯式裁決，非靜默流失（Blindspot B4）。

**2026-07-20 Agent = Model + Body + Harness 總綱明文化 + GPT-5.6/CODEX 評閱檔刪除 + EVAL 兩檔處置採納紀錄**：
- **MBH 公理明文化（採納）**：owner 世界觀「Agent = Model + Body + Harness」升為 HARNESS-CORE-v4 §0 設計公理總綱一句（Model = 可換元件／`[P]` 承載者；Body = hooks/scripts/gates/CI 確定性機構／`[E]` 效力來源；Harness = 紀律本身 L1 契約 + L2 校準，以合理駕馭達成品質×成本雙目標），並重述公理 1（Harness > Model）與 `[P]`/`[E]` 定義段以 MBH 語彙重錨（[P]↔Model、[E]↔Body、公理 1 第四元素＝Body 層）。裁決依 owner 明示「重述替換非疊加、不膨脹 L1」：拒絕新增第七公理（違 L1 byte 紀律），僅以總綱一句 + 既有公理/定義段重述達成，L1 條數與閘門不變。PROFILES-v4 標頭補一行 MBH 定位（L2 = Harness 的成本×品質旋鈕）。
- **GPT-5.6 兩份審閱檔刪除（採納，接續 51b8464/62e1107）**：`GPT-5.6-REVIEW.md`（三路文件審閱）與 `GPT-5.6-SOL-KNOW-YOUR-UNKNOWNS-REVIEW.md`（Sol unknowns 審閱，F23–F25/F27 proposals）已於 owner 裁決移除；採納/拒絕結論已固化於本 §3 既有各採納紀錄，原文僅 git 歷史可考。CODEX-GPT5.6 四檔（BASELINE/RERUN/SOL-UNKNOWNS/MANIFEST）同輪移除。
- **EVAL 兩檔處置（採納）**：`EVAL-BASELINE-v4.md` 重建精簡——保留 current baseline（Round 2 F1–F22 20/22、fail_axes [F7,F15]、variance/oracle caveats），Round 1 歷史細節壓縮為數行摘要，對已刪 CODEX/GPT-5.6 檔的 provenance 引用改註「原文 git 歷史可考」；`EVAL-PACK-v4-ADDENDUM.md` 經 grep 確認無已刪檔名引用（fixture 定義完整未動）。本 SPEC §3/§6 對已刪檔的散文指針同步改為「git 歷史可考」，懸空引用 = 0。

**2026-07-21 第二輪文件收斂（DeepSeek V4 Pro reviewer 執行；Batch C 文件修復）採納紀錄**：
- 本輪收斂範圍：GLOSSARY-v4.md、ADOPTION-GUIDE-v4.md（由 sibling agents 建立）、CHATGPT-HARNESS-v4.md polish、HARNESS-EXPORT build script 修復（governance preamble 保存）、INDEX.md router 擴充、CONCEPT-MAP-v4.md 指針補齊、SPEC-v4.md backlog ledger 補 #13-packet 與 F18-action。
- 本輪**未**跑 fixtures、**未**變更任何 CORE/PROFILES/EVAL-PACK 定義、**未**改寫紅軸判定；所有行為宣稱（F7/F15 紅軸、`[E]` enforcement 狀態、v4>v3 行為 delta）維持 unverified_success。
- 仍 open：#3（Dynamic Workflows 基座）、#13（乾淨 counterfactual）、#14（ChatGPT 三 surface 校準）、#13-packet（raw-packet provenance 保留集合）、F18-action（action-level sandbox verification）。
- #2c 已執行（2026-07-21）：F7 0/3、F15 1/3、F19 0/3、F20 3/3；結構性歸因 = advisory stderr 不進 agent context；升級提案（exit 1→2、oracle 修訂）待對抗複審。

## 7. Papers 對照驗證紀錄（2026-07-19，獨立 verifier）

- §2 證據表逐列裁決：引 arXiv 之列全數 CONFIRMED（檔案存在、構念對齊、數字吻合），僅 1 處歸屬錯誤已修（Terminal-Bench → 2601.11868）；2606.29251 補 domain 註。
- 反證搜索：**arXiv 2510.22251（Prompting Inversion）** 對「否決下沉公理/Johari」（審議 #9–#11）構成張力——約束型 prompt 在 frontier 為手銬（gpt-5 94.00% vs 96.36%）。化解論據：公理/Johari 屬「決策程序」非 step-by-step 約束，且該論文正是雙軸伸縮的上游實證；但此 tension 未定案，換代重審（decaying cache）時以 L4 fixtures 實測「公理常駐 vs 下沉」對主對話行為的實際影響。
- silent-on-success（展示三分）獲雙重背書（skill-issue line 146/148；2606.10209 pruning 71%→91.6%），無反證。
- 治理下沉與「auto-load 受眾=主對話」屬工程慣例判斷，papers 無直接量測構念，無反證亦無背書。
- 觀察項（2026-07-19）：arXiv 2607.04528（harness-induced belief divergence）——完成率不變下，harness 設定（動作限制/證據可見度/驗證檢查）改變 agent 內在推理，為隱形評測污染源；構念新穎、無 workspace 落地案例，暫不入 L1，跨 harness/跨 gate 比較時列為 caveat。

## 8. MAST 覆蓋率盤點（2026-07-19）

> 來源：arXiv 2503.13657（MAST，14 失敗模式，κ=0.88）對照 `HARNESS-CORE-v4.md` §3 委派協議 + `.claude/rules/subagent-strategy.md`。backlog #9 落地。
> **用詞界定**：「已攔/部分攔」指**規則覆蓋**該失敗模式（advisory），非實測攔截或機械強制；對應 fixture 實測狀態以 `EVAL-BASELINE-v4.md` 為準。

| MAST 失敗模式 | v4 對應規則 | 覆蓋 |
|---|---|---|
| 1.1 Disobey Task Specification | Done Contract 逐字命令化 + Handoff Contract `Goal`（一句可驗收目標） | 已攔 |
| 1.2 Disobey Role Specification | 角色≠檔位單調（角色×任務校準）+ Handoff Contract `Non-goals` | 部分攔（advisory，無機械強制角色邊界） |
| 1.3 Step Repetition | child 不 self-retry；task-templates 升降級條款「同一件事最多重試兩輪」 | 部分攔（防重試迴圈，未防同一步驟被不同委派重複執行） |
| 1.4 Loss of Conversation History | Handoff Contract `Context`（child 不繼承，須寫全）+ cache 五禁令「fork 必重放父前綴原文」 | 已攔 |
| 1.5 Unaware of Termination Conditions | Done-when 逐字命令 + 完成度五標籤 | 已攔 |
| 2.1 Conversation Reset | cache fork 重放原文 + RECORD 目標外錨（state 檔重錨） | 部分攔（防脈絡遺失，未直接防 agent 主動重置對話） |
| 2.2 Fail to Ask for Clarification | IDENTIFY Ask-rate（scope 變更/破壞性動作必問）+ 本次新增停止條件清單 | 部分攔（涵蓋 scope/矛盾/不可逆，未涵蓋任意語意模糊皆須問） |
| 2.3 Task Derailment | RECORD 目標外錨 + Handoff Contract `Non-goals` + checkpoint 對照重錨 | 已攔 |
| 2.4 Information Withholding | Return 固定 schema（達標?/驗證輸出/open_questions/偏離說明/升級建議） | 已攔 |
| 2.5 Ignored Other Agent's Input | 跨切紀律「浮現矛盾不靜默選、上呈裁決者」+ child 間不互通失敗返回 parent | 部分攔（防矛盾被靜默壓過，未防 child 讀了但選擇性忽略上游輸入） |
| 2.6 Reasoning-Action Mismatch | §3 互審「陳述-行動一致性」（2026-07-19 終審精煉新增：計畫與實際 diff/工具序列不一致即 open_question） | 部分攔（advisory；Return schema 欄位化列 backlog #3） |
| 3.1 Premature Termination | Oracle 資格先於 loop（事前棄權需明寫）+ 升降級條款「兩輪未達標停下回報」 | 部分攔（防過早棄權不留痕，未防過早宣稱完成即停） |
| 3.2 No or Incomplete Verification | `unverified_success` 閘門 + Gate 選擇稽核 + 拿收據 | 已攔 |
| 3.3 Incorrect Verification | 裝完成捷徑具名清單 + 測試檔被改動即紅旗 + Oracle 資格驗證 | 已覆蓋（advisory；對應 F7 eval_hack 為 current red axis，實測未攔住，防範待機械化） |

**結論（2026-07-19 終審精煉後更新）**：14 類中 6 已攔、7 部分攔（含 2.6，經終審精煉由「未攔」補為 §3 advisory 條文）、1 僅 advisory 覆蓋（3.3）、0 全新未攔。剩餘機械化債：2.6 的 Return schema 欄位化（「執行前宣告的計畫」vs「實際 diff/工具呼叫序列」機械比對，backlog #3）；部分攔各項（1.2/1.3/2.1/2.2/2.5/3.1）屬 advisory 未機械化，優先序次之。
