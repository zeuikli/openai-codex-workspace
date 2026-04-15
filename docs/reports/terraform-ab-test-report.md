# GCP Terraform 模組 A/B 測試暨開發品質報告

- **報告日期**：2026-04-14
- **分析者**：Claude Sonnet 4.6（主 Agent）
- **任務目標**：開發一組完整的 Google Cloud Terraform 模組，具備可重複使用與多環境部署能力
- **A 組**：`codex/develop-google-cloud-terraform-module`（分支 A）
- **B 組**：`codex/develop-reusable-google-cloud-terraform-module`（分支 B）

---

## 一、分支結構概覽

| 項目 | 分支 A | 分支 B |
|------|--------|--------|
| 根目錄結構 | `terraform/modules/` + `terraform/environments/` | `modules/` + `environments/` |
| 額外設計層 | 無 | `modules/platform_stack/`（複合模組） |
| 額外工具 | `docs/reports/gcp-terraform-ab-quality-report.md` | `scripts/ab_benchmark.sh` |
| 新增 `.tf` 檔案數 | **46 個** | **45 個**（不含 platform_stack 3 個共 48 個） |
| 版本需求 | `terraform >= 1.6.0`，Google provider `>= 5.30.0` | `terraform >= 1.6.0`，Google provider `~> 6.0` |
| 獨有 Terraform commit | `52ae702b`（+634 行） | `b022d45b`（+703 行, -27 行） |

---

## 二、服務模組覆蓋率

| 服務 | 分支 A | 分支 B | 備註 |
|------|:------:|:------:|------|
| Cloud Run | ✅ | ✅ | |
| Cloud Armor | ✅ | ✅ ⚠️ | B 預設規則為 ALLOW（安全問題，見第五節） |
| Artifact Registry | ✅ | ✅ | |
| Cloud IAM | ✅ | ✅ | 實作方式不同（見第五節） |
| Cloud KMS | ✅ | ✅ | |
| Load Balancer External | ✅ 部分 | ✅ 部分 | 兩者均不完整（見第五節） |
| Load Balancer Internal | ✅ 部分 | ✅ 部分 | |
| Cloud SQL MySQL（PSA） | ✅ | ✅ | |
| Cloud SQL PostgreSQL（PSA） | ✅ | ✅ | |
| Cloud Storage + HMAC | ✅ | ✅ | |
| Secret Manager | ✅ | ✅ | |
| MemoryStore Redis | ✅ | ✅ | |
| Managed Kafka | ✅ | ✅ | 皆使用 google-beta provider |
| Platform Stack（複合模組） | ❌ | ✅ | B 額外提供可重用的聚合層 |

**所有 11 項必要服務兩個分支均已實作**，均無從缺項目。

---

## 三、Token 消耗估算

> 計算方式：統計所有 `.tf` 檔案總字元數，以 `字元數 ÷ 4` 估算 token 數（GPT-4/Claude 通用估算法）。

| 指標 | 分支 A | 分支 B | 差異 |
|------|-------:|-------:|-----:|
| `.tf` 檔案總字元數 | **16,025** | **17,969** | B 多 +1,944（+12.1%） |
| 估算 token 數（÷4） | **~4,006** | **~4,492** | B 多 +486 tokens |
| `.tf` 檔案數 | 46 個 | 45 個（基礎）+ platform_stack 3 個 = 48 個 | |
| 環境 main.tf 行數/個 | 93 行 | 14 行 | B 環境設定精簡 -85% |

### Token 分佈分析

**分支 A** token 分佈：
- 環境層（dev/prod/staging）：3,539 chars（22.1%）
- 模組主體（main.tf）：9,629 chars（60.1%）
- 變數/輸出定義：2,857 chars（17.8%）

**分支 B** token 分佈：
- 環境層（dev/prod/staging）：1,640 chars（9.1%）—因委派至 platform_stack，大幅精簡
- platform_stack：4,461 chars（24.8%）
- 其他模組主體：8,764 chars（48.8%）
- 變數/輸出定義：3,104 chars（17.3%）

**結論**：分支 B token 略多，主要因 `platform_stack` 模組（+4,461 chars）。但環境層 token 縮減 53.7%（3,539→1,640），表示多環境擴展時 **B 的增量成本更低**（每增加一個環境僅 ~14 行，A 需 ~93 行）。

---

## 四、生成速度與延遲推估

> 無法直接量測 AI 生成的 API 延遲（非即時對話模式），以 commit timestamp 作為代理指標，並以 `scripts/ab_benchmark.sh` 輔助分析。

| 指標 | 分支 A | 分支 B |
|------|--------|--------|
| Terraform commit 時間戳 | `2026-04-14T17:35:03Z` | `17:28:12Z`（輪廓）+ `17:37:02Z`（主體） |
| 單一 commit 總輸出行數 | 634 行 | 703 行（含 -27 刪除） |
| 生成速率（參考值） | ~634 lines/commit | ~703 lines/commit（+10.9%） |
| `ab_benchmark.sh` 包含 | 否 | ✅（`scripts/ab_benchmark.sh`） |

分支 B 的 `ab_benchmark.sh` 實作邏輯（摘要）：
```bash
# 以 HEAD .tf/.md 字元數 ÷ 4 估算 token
A_TOKEN=$(count_tokens_head)      # ~4,006
B_TOKEN=$(count_tokens_worktree)  # ~4,492

# 以 5 次平均量測基礎 I/O 延遲
A_LATENCY=$(bench_cmd_ms 5 git show HEAD:README.md)
B_LATENCY=$(bench_cmd_ms 5 rg --files -g "*.tf")
```

**注意**：`ab_benchmark.sh` 使用 `rg`（ripgrep），在無 ripgrep 環境下會失敗，需加守衛或改用 `find`。

---

## 五、開發品質深度檢驗

### 5-1 安全性問題

#### 🔴 Critical：分支 B Cloud Armor 預設規則錯誤

```hcl
# 分支 B: modules/cloud_armor/main.tf — 存在安全漏洞
rule {
  action   = "allow"      # ⚠️ 預設規則為 ALLOW！
  priority = 2147483647   # 最低優先級 = 最後生效
  match {
    versioned_expr = "SRC_IPS_V1"
    config { src_ip_ranges = ["*"] }
  }
  description = "default allow"
}
```

Cloud Armor 設計原則應為「**預設拒絕、明確允許**」。分支 B 的邏輯相反（預設允許＋黑名單），當 `deny_ip_ranges = []` 時等同完全開放。

```hcl
# 分支 A: terraform/modules/cloud_armor/main.tf — 正確做法
rule {
  action   = "deny(403)"   # ✅ 預設拒絕
  priority = 2147483647
  match { versioned_expr = "SRC_IPS_V1"
    config { src_ip_ranges = ["*"] } }
  description = "default-deny"
}
# 配合動態允許特定 IP 段（白名單模式）
```

#### 🟡 Medium：分支 B IAM 使用 Authoritative binding

```hcl
# 分支 B: modules/iam/main.tf
resource "google_project_iam_binding" "bindings" {
  for_each = var.project_bindings
  role     = each.key
  members  = each.value   # ⚠️ 授權型 = 覆蓋該 role 的所有 existing members
}

# 分支 A: terraform/modules/iam/main.tf
resource "google_project_iam_member" "members" {
  for_each = { for binding in var.bindings : "${binding.role}-${binding.member}" => binding }
  role   = each.value.role
  member = each.value.member  # ✅ 非授權型 = 僅新增，不移除既有 members
}
```

`google_project_iam_binding` 在 `terraform apply` 時會移除不在 `members` 清單內的所有成員，對生產環境具破壞性風險。

#### 🟡 Medium：分支 B Cloud Run 預設公開服務

```hcl
# 分支 B: modules/cloud_run/variables.tf
variable "invoker_member" { type = string default = "allUsers" }
# ⚠️ 預設 = 任何人皆可調用
```

`allUsers` 的預設值使服務在未明確設定時直接對外公開，應改為 `default = null` 並要求呼叫方明確指定。

---

### 5-2 架構設計比較

| 面向 | 分支 A | 分支 B |
|------|--------|--------|
| 模組架構 | Flat（扁平，各模組獨立） | Composite（複合，platform_stack 聚合） |
| 環境擴展成本 | 每環境 ~93 行（DRY 違反） | 每環境 ~14 行（高度 DRY） |
| 模組可重用性 | 中等（個別模組可獨立引用） | 高（platform_stack 一鍵部署全棧） |
| 新增環境步驟 | 需複製並修改 93 行 main.tf | 僅需修改環境變數檔 |
| 模組耦合度 | 低（解耦，適合漸進採用） | 中（platform_stack 強耦合，難選擇性部署） |

**平衡建議**：分支 B 的 platform_stack 模式更適合大型標準化部署；分支 A 的扁平模式更適合需要逐模組選用的場景。

---

### 5-3 outputs.tf 完整性

| 模組 | 分支 A | 分支 B |
|------|:------:|:------:|
| artifact_registry | ✅ | ✅ |
| cloud_armor | ✅ | ✅ |
| cloud_run | ✅ | ✅ |
| cloud_sql_mysql | ✅ | ✅ |
| cloud_sql_postgresql/postgres | ✅ | ✅ |
| iam | ✅ | ❌ **缺少 outputs.tf** |
| kms | ✅ | ✅ |
| load_balancer_external | ✅ | ✅ |
| load_balancer_internal | ✅ | ❌ **缺少 outputs.tf** |
| managed_kafka | ✅ | ✅ |
| memorystore_redis | ✅ | ✅ |
| secret_manager | ✅ | ❌ **缺少 outputs.tf** |
| storage_hmac / cloud_storage_hmac | ✅ | ✅ |

分支 A 所有模組均具備完整的三件組（main/variables/outputs）；分支 B 有 3 個模組缺少 outputs.tf，影響跨模組值引用。

---

### 5-4 Load Balancer 完整性

兩個分支的 Load Balancer 模組均不完整，差異如下：

| 資源 | Branch A External | Branch B External | Branch A Internal | Branch B Internal |
|------|:-----------------:|:-----------------:|:-----------------:|:-----------------:|
| Global Address | ❌ | ✅ | N/A | N/A |
| Managed SSL Certificate | ❌ | ✅ | N/A | N/A |
| Cloud Run NEG | ✅ | ❌ | N/A | N/A |
| Backend Service | ✅ | ❌ | N/A | N/A |
| URL Map | ❌ | ❌ | N/A | N/A |
| Target HTTPS Proxy | ❌ | ❌ | N/A | N/A |
| Global Forwarding Rule | ❌ | ❌ | N/A | N/A |
| Internal Forwarding Rule | N/A | N/A | ✅（port 80 硬編碼） | ✅（all_ports=true，更靈活） |

**結論**：兩個分支的 LB 模組均為骨架（scaffold），生產環境使用前需補齊缺失資源，不建議直接套用。

---

### 5-5 Cloud SQL Private Service Access 處理

| 行為 | 分支 A | 分支 B |
|------|--------|--------|
| PSA IP range 管理 | 每個 SQL 模組各自建立獨立 PSA range | 支援傳入 `allocated_ip_range`（可共用） |
| db_version 參數化 | ❌ MySQL 硬編碼 `MYSQL_8_0` | ✅ 可傳入任意版本 |
| 單 VPC 多 SQL 實例 | ⚠️ 兩模組各建 PSA range，可能衝突 | ✅ 可透過 `coalesce(var.allocated_ip_range, ...)` 共用 |

---

### 5-6 版本策略比較

```hcl
# 分支 A: terraform/versions.tf
google      = { version = ">= 5.30.0" }   # 開放範圍，5.30+均可
google-beta = { version = ">= 5.30.0" }

# 分支 B: versions.tf
google      = { version = "~> 6.0" }      # 鎖定 6.x，不跨 major version
google-beta = { version = "~> 6.0" }
```

分支 B 使用 `~> 6.0`（pessimistic constraint），可防止 major version 破壞性升級，對長期維護較為穩健。但若上游尚未升到 6.x，分支 A 的 `>= 5.30.0` 相容性更廣。

---

## 六、綜合評分

| 評分維度（0-10） | 分支 A | 分支 B |
|-----------------|:------:|:------:|
| 服務覆蓋完整度 | **9** | **10**（含 platform_stack） |
| 程式碼安全性 | **8** | **5**（Cloud Armor 預設 ALLOW 為嚴重問題） |
| 可重用性/DRY | **6** | **9**（platform_stack 大幅提升） |
| outputs.tf 完整性 | **10** | **7**（缺 3 個模組） |
| 模組參數化彈性 | **7** | **8**（db_version 參數化等） |
| Load Balancer 完整度 | **4** | **4**（兩者皆不完整） |
| Token 效率 | **9**（較精簡） | **8**（多 12.1%） |
| 多環境擴展性 | **6** | **9**（platform_stack 極大提升） |
| **總分（加權平均）** | **7.4** | **7.5** |

---

## 七、問題清單與建議修正

### 🔴 Critical（需立即修正）

1. **[分支 B] Cloud Armor 預設規則**
   - 位置：`modules/cloud_armor/main.tf`
   - 問題：default rule 為 `allow`，應改為 `deny(403)`
   - 修正：將預設規則改為 allowlist（白名單）模式

2. **[分支 B] IAM binding 授權型危險**
   - 位置：`modules/iam/main.tf`
   - 問題：`google_project_iam_binding` 會覆蓋現有成員
   - 修正：改用 `google_project_iam_member` 或在文件中清楚標示 AUTHORITATIVE 警告

### 🟡 Medium（強烈建議修正）

3. **[分支 B] 缺少 outputs.tf**
   - 位置：`modules/iam/`、`modules/load_balancer_internal/`、`modules/secret_manager/`
   - 問題：無法在外部引用模組輸出值（例如 secret ARN、LB IP）

4. **[兩分支] Load Balancer 模組不完整**
   - 缺少：URL Map、Target HTTPS Proxy、Global Forwarding Rule
   - 建議：補齊完整 LB chain 資源，或在 README 明確標示為「組件模組」

5. **[分支 B] Cloud Run 預設公開**
   - 位置：`modules/cloud_run/variables.tf`
   - 修正：`invoker_member` 的 default 改為 `null`，強迫明確設定

6. **[分支 A] Cloud SQL 重複 PSA range**
   - 建議：在環境層建立共用 PSA range，作為 input 傳入兩個 SQL 模組

### 🟢 Nice-to-have（建議改善）

7. **[分支 B] `ab_benchmark.sh` 依賴 `rg`**
   - 修正：加上 `command -v rg >/dev/null || { echo "rg not found"; exit 1; }`

8. **[分支 A] Cloud Run 硬編碼 ENV 變數名**
   - 建議：改用動態 `for_each` 處理 env vars（參考分支 B 做法）

9. **[分支 A] Secret Manager 單一 secret**
   - 建議：改用 `for_each` 支援批量建立（參考分支 B 做法）

---

## 八、最佳化整合建議

建議以**分支 A 的安全設計為基礎**，選擇性納入**分支 B 的架構優化**：

| 採納來源 | 採納內容 | 理由 |
|----------|----------|------|
| 分支 A | Cloud Armor 預設 deny + allowlist 模式 | 安全正確 |
| 分支 A | IAM `google_project_iam_member`（非授權型） | 生產安全 |
| 分支 B | `platform_stack` 複合模組設計 | 提升可重用性 |
| 分支 B | 環境薄包裝模式（14 行 vs 93 行） | DRY 原則 |
| 分支 B | Secret Manager `for_each` 批量模式 | 更靈活 |
| 分支 B | Cloud SQL 可共用 PSA range（`coalesce`） | 避免資源衝突 |
| 分支 B | `db_version` 參數化 | 更靈活 |
| 分支 B | `versions.tf` 使用 `~> 6.0` | 版本管理更穩健 |
| 分支 B | Cloud Run 動態 env_vars + invoker IAM | 功能更完整 |
| 待補全 | 完整 Load Balancer chain | 兩分支均需補齊 |

---

## 九、總結

| 面向 | 勝出 | 說明 |
|------|:----:|------|
| 安全性 | **分支 A** | Cloud Armor 預設正確，IAM 非授權型 |
| 可重用性 | **分支 B** | platform_stack 架構優越 |
| 完整性 | **分支 A** | outputs.tf 齊全，無遺漏 |
| Token 效率 | **分支 A** | 少 12.1% token |
| 多環境擴展 | **分支 B** | 環境精簡 85%，擴展成本低 |
| 版本管理 | **分支 B** | `~> 6.0` 更穩健 |

**整體建議**：以分支 B 的架構為主線（platform_stack + 薄環境包裝），但必須優先修正 Cloud Armor 安全漏洞（Critical），補齊 outputs.tf，並將 IAM 改為非授權型。完成修正後，分支 B 的整體品質將顯著超越分支 A。

---

*報告生成時間：2026-04-14 | 分析 agent：Claude Sonnet 4.6*
