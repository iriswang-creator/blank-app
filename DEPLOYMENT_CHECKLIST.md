# ✅ Streamlit Cloud 部署檢查清單

## 📋 部署前檢查

### 文件狀態
- ✅ `streamlit_app.py` - 已更新並簡化
- ✅ `requirements.txt` - 包含所有必需依賴及版本號
- ✅ `.streamlit/config.toml` - 配置完成
- ✅ 所有 `.joblib` 文件 - 已Git追蹤

### 模型文件驗證
- ✅ `heloc_model.joblib` (386 KB)
- ✅ `feature_cols.joblib` (589 B)
- ✅ `heloc_medians.joblib` (2.9 KB)
- ✅ `heloc_threshold.joblib` (21 B)

## 🚀 部署步驟

### 1️⃣ 提交更改到GitHub
```bash
cd /workspaces/blank-app
git add .
git commit -m "Optimize for Streamlit Cloud deployment"
git push origin main
```

### 2️⃣ 在Streamlit Cloud上部署
1. 訪問 https://share.streamlit.io
2. 登錄您的GitHub帳戶
3. 點擊 "New app"
4. 選擇：
   - Repository: `iriswang-creator/blank-app`
   - Branch: `main`
   - File: `streamlit_app.py`
5. 點擊 "Deploy"

### 3️⃣ 驗證部署
應用啟動時檢查：
- ✅ 側邊欄顯示狀態（"✅ Model loaded" 或 "⚠️ Using demo mode"）
- ✅ 主頁面顯示 "🏦 HELOC Decision Support System"
- ✅ 能夠選擇模式（Applicant View / Internal Testing）

## 🔍 如果出現ModuleNotFoundError

### 原因1: requirements.txt缺少依賴
✅ 已驗證，包含：
```
streamlit>=1.28.0
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
joblib>=1.3.0
xgboost>=2.0.0
```

### 原因2: XGBoost版本不兼容
✅ 已更新為 `xgboost>=2.0.0`
注意：XGBoost會顯示版本兼容性警告，這是正常的

### 原因3: .joblib文件未部署
✅ 已驗證所有文件在Git中被追蹤：
```
feature_cols.joblib
heloc_medians.joblib
heloc_model.joblib
heloc_threshold.joblib
```

## 📊 最後驗證

在終端運行以下命令確認一切正常：
```bash
# 驗證所有imports
python -c "import streamlit, xgboost, joblib, sklearn, pandas, numpy; print('✅ All OK')"

# 驗證模型加載
python -c "import joblib; m = joblib.load('heloc_model.joblib'); print('✅ Model OK')"

# 驗證Git追蹤
git ls-files | grep joblib
```

## 💡 故障排查

### 看到"Using demo mode"
- ✅ 這是正常的，如果模型加載失敗，會自動使用演示模式
- 檢查應用日誌（右下角 "Manage app" > "Logs"）

### 應用加載很慢
- ✅ XGBoost模型加載需要時間，請耐心等待

### 仍然看到ModuleNotFoundError
- 複製應用日誌中的完整錯誤訊息
- 檢查 [Streamlit文檔](https://docs.streamlit.io/streamlit-cloud/troubleshooting)
