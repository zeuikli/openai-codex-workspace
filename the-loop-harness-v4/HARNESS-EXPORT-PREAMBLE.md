## 0. 採用者必讀：可攜分層 × 效力誠實（治理自應用）

> 本節是 **EXPORT 治理層**（採用者防誤用），不是 L1 契約正文。L1 正文見下方嵌入 CORE（零模型名、零可調校數字）。本節允許寫宿主名、fixture 軸名、backlog 編號——因為防誤用本身需要可稽核的疆域標示。

### 0.1 三層可攜地圖（禁止把 Claude 專屬當模型無關）

| 層 | 內容 | 可攜性 | 無對應 runtime 時 |
|---|---|---|---|
| **L1 契約**（下方嵌入 CORE） | 六階段、公理、`[P]`/`[E]` 條文、降級條款 | **模型無關**（model-agnostic cognitive protocol） | `[P]` 仍可作 prompt；`[E]` **一律 advisory** |
| **L2 校準**（下方嵌入 PROFILES） | 檔位旋鈕、接入程序、數字來源 | 跨模型可攜**結構**；數字須在目標 surface **重校** | 沿用保守預設 + 標 `未校準` |
| **L3/L4 Body**（hooks/CI/fixtures/workflows） | 確定性 gate、lexical lint、eval pack 執行 | **宿主專屬**（本 workspace 的 Claude Code hooks / settings 不隨 EXPORT 旅行） | 整層不存在；不得宣稱已 enforce |

**鐵律（自我應用）**：EXPORT 把 L1/L2 打包給外部採用者，**不**把任一宿主的 hook 二進位或 settings 配線假裝成可攜保證。讀過本檔 ≠ 目標環境有 Body。

### 0.2 Advisory vs Hard-block 邊界（必須尖銳；治理套用到自己）

| 效力等級 | 定義 | 可被繞過？ | 可宣稱什麼 | 不可宣稱什麼 |
|---|---|---|---|---|
| **Prompt / `[P]`** | 模型讀了可能遵守 | 是（服從率無保證） | 「契約要求 X」 | 「系統會擋住 X」 |
| **Advisory Body** | hook/CI **可見提醒**（告警、exit 非阻斷、lint 提示） | **是**（換寫法、換路徑、忽略告警即可繞） | 「有機械訊號提醒 X」 | 「X 已 enforce / 紅軸已解」 |
| **Hard-block Body** | 確定性攔截使違規動作**無法完成**（或 CI 必紅且合併路徑關閉） | 設計上否（仍須防 allowlist 放寬攻擊面） | 「Y 路徑已 enforce」——且僅限通過語義級觸發測試的路徑 | 「全 L1 已 enforce」 |
| **Behavioral evidence（fixture）** | 獨立 context 跑 fixture 的通過/失敗 | N/A（證據不是機制） | 「軸 Z 本輪 PASS/FAIL（附 n、環境）」 | 「PASS = 已 enforce」 |

**自報成功鏈（對 EXPORT 自身）**：
1. 落地 advisory hook **≠** 紅軸行為分數移動。
2. fixture PASS **≠** enforcement。
3. 本檔寫了「方向列／補償層」**≠** 補償層已在讀者環境存在。
4. 只有「機制存在 + 語義級會觸發 +（若宣稱解紅軸）held-out 行為分移動」三者齊備，才可升級措辭。
5. **本 EXPORT 若違反上表措辭，即治理自腐蝕**——審閱者應記 finding，不給「文件寫了就算 enforce」過關。

### 0.3 紅軸與 Body 現況（行為分 UNVERIFIED）

| 軸 | 契約位置 | Body 訊號（典型 Claude Code 宿主，2026-07-20） | 效力 | 行為軸狀態 |
|---|---|---|---|---|
| F7 eval_hack（字面特判） | CORE TEST 裝完成捷徑 | `literal-specialcase-lint` 類 lexical 掃描 | **advisory** | **UNVERIFIED**（未因 hooks 重跑證明移動；baseline 仍列紅軸 fail） |
| F15 blindspot_pass | CORE IDENTIFY Blindspot | 高風險域關鍵字 lint | **advisory** | **UNVERIFIED** |
| F19 references_over_spec | CORE IDENTIFY 品味/reference | 品味缺 reference lint | **advisory** | 曾單樣本轉綠；**不得**歸因 hooks；n=1 |
| F18 inherited_trajectory | CORE §2 繼承軌跡 | 多為 response-level 證據 | response ≠ action | **action-level OPEN**（真擋違規 commit 等路徑未閉） |

> **明確禁止**：不得寫「F7/F15 已機械化解決」「hooks 落地後紅軸已綠」。正確句式：「F7/F15/F19 已有 **advisory lexical** 方向與（若宿主有）接線；**行為軸 UNVERIFIED**，須 SPEC §6 #2c held-out rerun（每 cell n≥3）後才能更新行為宣稱。」

### 0.4 Open backlog（誠實開帳；結案前不作對應宣稱）

| ID | 主題 | 狀態 | 結案前禁止的宣稱 |
|---|---|---|---|
| **#2c** | F7/F15/F19/F20 held-out rerun（n≥3）驗證 #2b hooks 是否移動紅軸 | **OPEN** | 「紅軸已解／hooks 已證實有效」 |
| **#3** | Dynamic Workflows 作 L3 基座；Handoff Return schema 機械驗證；陳述-行動機械比對 | **OPEN** | 「Handoff/statement-action 已 enforce」 |
| **#13** | 乾淨 counterfactual（v3 vs v4 行為 delta；BLOCKED-ENV） | **OPEN** | 「v4 行為層優於 v3」 |
| **#14** | ChatGPT 三 surface（chat-only / tool-enabled / API）實測校準 | **OPEN** | 「ChatGPT adapter 已校準／可生產 enforce」 |
| **F18 action** | 繼承軌跡 action-level（真路徑攔截，非只 response） | **OPEN** | 「繼承軌跡威脅已在 action 層關閉」 |
| **#13-packet** | Raw-packet 永久保留／可覆核 provenance（見 §0.5） | **OPEN（政策 stub）** | 「跨模型數字可獨立覆核 raw packet」（目前多僅 git 歷史／散文） |

完整 ledger 與 DONE 項（如 #2 測試檔紅旗、#2b advisory lexical 三件、#9 MAST）→ `SPEC-v4.md` §6。本表只列 **仍會造成跨模型誤讀** 的開帳。

### 0.5 Raw-packet provenance 政策 stub（#13-packet；不偽造封包）

**現況（誠實）**：部分跨 runtime／跨模型 baseline 的 persistent raw packet（runner pins、transcripts、response blobs、action receipts、artifact manifest）已於 owner 裁決移除；數字與結論的 **原文封包不可在 tree 內覆核**，僅 git 歷史／散文摘要可考。此與 CORE §5「演化以全量 trace 為食」存在已知張力——**承認張力，不靠假封包填洞**。

**政策 stub（未結案前的最低紀律）**：
1. **不偽造、不「還原」已刪封包**。無 blob 就標 `packet_absent`。
2. 引用已刪證據時強制措辭：`原文僅 git 歷史可考；tree 內不可獨立覆核`。
3. 未來最低保留集合（結案 #13-packet 的候選，尚未落地）：`manifest hash + transcript hash + model/runtime pin + artifact hash + 公共 timestamp`；可 sealed 存證，不必全文進主 tree。
4. 無 packet 的跨模型數字：**不得**當 sealed/held-out 演化認證輸入；最多當 anecdotal／historical point estimate。
5. 新跑 eval **先**定保留集合再跑，避免再造「跑完即刪、只剩摘要」的 reward-hacking 形狀。

### 0.6 外部採用最短路徑（防整檔誤貼）

1. 讀本節 §0.1–0.4 → 接受「無 Body = 全 `[E]` advisory」。
2. 取 **CORE 全文**（或 adapter 蒸餾）+ **一個** profile 欄；不要整份 EXPORT 當 system prompt。
3. 目標 surface 跑 fixtures（邏輯 suite 見 PROFILES §4）前，可攜性結論只能是 `uncalibrated/advisory`。
4. ChatGPT → 只用 `CHATGPT-HARNESS-v4.md`，且維持 uncalibrated 至 #14 結案。
5. 完成上限：無親跑確定性 gate → 最高 `unverified_success`。

---

## 跨模型失真點清單（adapter 選型必讀）

> 依 CORE 的 `[P]`/`[E]` 二分列出：換弱模型／非原宿主 surface／無 enforcement runtime 時最易失真的 `[E]` 條文，及應補的支撐層（L3=hook/CI/gate，L4=fixture）。`[P]` 條文跨模型退化小（靠 prompt 位置與 effort，不靠新 enforcement）。整體無 runtime 降級見 CORE §7。
>
> **讀表規則**：補償層欄是「應有」不是「讀者環境已有」。標 **advisory** 的補償 = 可見提醒、可繞過；標 **hard-block** 才是動作攔截。紅軸列行為分一律 **UNVERIFIED** 直至 #2c。

| `[E]` 條文（CORE 段） | 換弱模型／無 runtime 退化模式 | 補償層（應有） | 效力／狀態 |
|---|---|---|---|
| unverified_success 閘門（TEST） | 自報成功不親跑 gate，口頭「已通過」冒充 verified | L3 CI/PreToolUse 強制 healthcheck；parent 親跑不跨 agent | 無 Body → advisory；有語義測試之 gate → 可稱該路徑 enforced |
| 不可逆操作等確認（APPLY） | 受「直接做」誘導略過確認，執行 DROP/rm -rf/force push/destroy | L3 PreToolUse 攔截 + 本次人核可 | 應 hard-block；未接線 = advisory |
| 刪除三級 + P0 安全二分（APPLY） | 漏零引用／唯一性檢查；「先記著之後修」 | L3 gate + high 級人核可 | 應 hard-block；未接線 = advisory |
| Gate 選擇稽核／裝完成捷徑（TEST） | 改測試檔配合實作、proxy gate 冒充真實路徑、字面特判 | L4 fixture（測試檔 diff 即紅旗）+ held-out 未見輸入抽驗；測試檔紅旗 hook（#2 DONE 於部分宿主） | 測試檔路徑：宿主或有 hard-block；字面特判見下行 |
| **F7/F15/F19 紅軸 advisory-hook 方向（TEST/IDENTIFY）** | 字面特判（F7）、高風險域 Blindspot 漏點名（F15）、品味類缺 reference 即宣告完成（F19）——prompt 加嚴邊際效益已遞減，紅軸跨 runtime 重現 | L3 **advisory lexical** hooks（字面特判 lint／高風險域 Blindspot 關鍵字 lint／品味缺 reference lint）= **可見提醒，非硬阻斷**，換寫法可繞；**必須**搭配 L4 held-out rerun（#2c，n≥3 per cell）才得更新行為分；升 hard-block 僅在 #2c 證明有效或可接受誤報後 | **行為軸 UNVERIFIED**；不得宣稱已解（SPEC §6 #2b/#2c） |
| Done Contract 逐字命令（IDENTIFY） | 以描述性條件冒充可機械驗證命令 | L3 要求驗證命令可執行落地 | 無 schema 強制 → advisory（#3 連動） |
| 委派確定性 gate parent 親跑（§3） | 無 sub-agent runtime 則整條 N/A；有則弱 parent 中介失真 | runtime 委派框架 + parent/CI gate | N/A 或 advisory／hard-block 視宿主 |
| Handoff Return／陳述-行動一致性（§3） | 缺欄仍開工；宣告計畫與 diff/工具序列不一致仍通過 | L3 Dynamic Workflows + schema 機械驗證（**#3 OPEN**） | **OPEN**；僅有 advisory 條文與部分 behavioral signal |
| Cache 五禁令（§4） | 非原宿主平台快取語義不同或無前綴快取 | 依目標平台快取機制校準，不適用即標 N/A | 靜默 drop = adapter 缺陷；須顯式 N/A 或替代 |
| 治理 byte gate／演化認證（§5） | 無 CI 則 byte gate／changelog／sealed-set 不 enforce | L3 byte gate + L4 sealed/held-out 認證 | 治理自應用：無機制不得稱 harness 已防自腐蝕 |
| 繼承軌跡 action（§2 / F18） | 只「說會拒」卻在工具層沿用前手違規慣例 | L4 action-level fixture + 真路徑 hook | **F18 action OPEN**；response PASS ≠ action 關閉 |
| 跨模型 packet 覆核（證據層） | 摘要數字當可覆核證據 | §0.5 保留集合；不造假包 | **#13-packet OPEN**；`packet_absent` 時降級引用 |

> 逐字可攜性未在目標 surface 跑 fixtures 前不得宣稱「不需改寫」（見 PROFILES §4 接入程序）。
> T1–T11 完整機制若 canonical 綁定某宿主 skill 路徑，非該宿主 surface 只得名稱＋adapter 一句定義；**不可**假設 skill 全文可攜。
