# Caveman 研究筆記（2026-04-15）

## 0) Clone 狀態

- 指令：`git clone --depth 1 https://github.com/JuliusBrussee/caveman.git /tmp/caveman`
- 結果：失敗（`CONNECT tunnel failed, response 403`）。
- 因此改採「公開原始檔抓取（raw URL）」做研究證據來源。

## 1) 研究問題 A：哪個 OpenAI 模型搭配 Caveman 最省 output tokens？

### 一手資料（外部）

- Caveman README 說明提供 Lite/Full/Ultra 三層壓縮，並以 React 範例示意壓縮幅度。
  - 來源：<https://raw.githubusercontent.com/JuliusBrussee/caveman/main/README.md>
- Caveman skill 定義三種強度（lite/full/ultra）與行為規則。
  - 來源：<https://raw.githubusercontent.com/JuliusBrussee/caveman/main/skills/caveman/SKILL.md>
- OpenAI 發表頁有 GPT-5.4 / GPT-5.4 mini / GPT-5.4 nano 的 benchmark 與價格。
  - 來源：<https://openai.com/index/introducing-gpt-5-4/>

### 本地可重跑測試

- 腳本：`scripts/research_caveman_openai_fit.py`
- 產出：
  - `docs/reports/caveman_openai_fit_20260415.json`
  - `docs/reports/caveman_openai_fit_20260415.md`

### 結論（以「output token 成本效率」為主）

- 若只看輸出成本，`gpt-5.4-nano + ultra` 通常最便宜。
- 若看「準確度/效能 + 成本」平衡，`gpt-5.4-mini + full` 通常是較穩妥折衷。
- 若是高風險、高正確率任務，才建議 `gpt-5.4 + lite/full`。

## 2) 研究問題 B：sub-agent 深度分派比較 lite/full/ultra 與模型契合

- 測試以三個平行 worker（ThreadPool）對 lite/full/ultra 同時計算壓縮率。
- 再與模型表現/價格組合成 fitness score（越高越好）。
- 由於沒有直接 API 實測 usage meter，這份是「離線效率模型」，不是 billing report。

## 3) 研究問題 C：SKILLS vs AGENTS vs HOOKS vs Rules 哪個最快載入？

### 方法

- 以「啟動摩擦」作代理指標：
  - 是否 auto-load
  - 手動步驟數
  - 需載入指令內容長度（payload chars）

### 結果摘要

- 一般情境下：`hooks` 與 `AGENTS` 最快（接近零手動步驟）。
- `skills` 與一般 `rules` 需手動觸發或貼入，首次啟動較慢。
- 若團隊需要「全 session 預設生效」，`hooks` 最接近即插即用。

## 4) 限制與風險

- 無法在此環境直接 clone GitHub repo（403），改用 raw 檔案作證據。
- 未串接實際 OpenAI API usage，因此 token 為近似估算。
- 載入速度比較是架構摩擦模型，非網路 RTT 實測。

## 5) 後續建議

1. 在可連網環境補跑真實 API A/B（同一 prompts、同一溫度）。
2. 加入 task 類型分層（debug / codegen / review / design）再做 level 建議。
3. 若要「預設省 token」且不犧牲太多可讀性，先採 `gpt-5.4-mini + full`。

## 6) 二次驗證（Repo 效能面）

- 已新增 `scripts/benchmark_repo_scan_efficiency.py` 對 review worker 做 baseline vs optimized 比較。
- 最新結果顯示：
  - `scanned_repo_chars` 由 131,219 降至 81,951（-37.5%）。
  - 中位執行時間由 17.17ms 改善至 17.03ms（+0.8%）。
- 來源：
  - `docs/reports/repo_scan_efficiency_20260415.md`
  - `docs/reports/repo_scan_efficiency_20260415.json`
