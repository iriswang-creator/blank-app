# 🏦 HELOC 模型應用 - 故障排除指南

## 如果仍然看到"Using demo mode"訊息

### 1️⃣ **清除Streamlit緩存**
```bash
# 清除所有Streamlit緩存
rm -rf ~/.streamlit
rm -rf .streamlit
```

### 2️⃣ **完全重新啟動應用**
```bash
# 如果在終端運行Streamlit，按 Ctrl+C 停止
# 然後重新運行：
streamlit run streamlit_app.py
```

### 3️⃣ **清除瀏覽器緩存**
- 按 `Ctrl+Shift+Delete` (或 `Cmd+Shift+Delete` on Mac)
- 清除所有緩存和cookie
- 刷新頁面

### 4️⃣ **驗證環境**
```bash
# 運行診斷命令
python -c "import xgboost, joblib, streamlit; print('✅ All modules OK')"
```

## 📋 已驗證的依賴

- ✅ Python 3.11.13
- ✅ streamlit 1.54.0
- ✅ xgboost 3.2.0
- ✅ scikit-learn
- ✅ pandas
- ✅ numpy
- ✅ joblib

## 🔍 模型文件狀態

所有4個joblib文件已驗證：
- ✅ `heloc_model.joblib` (386KB) - XGBoost分類器
- ✅ `feature_cols.joblib` (589B) - 特徵列表
- ✅ `heloc_medians.joblib` (2.9KB) - 中位數數據
- ✅ `heloc_threshold.joblib` (21B) - 決策閾值

## ⚠️ 注意

XGBoost會顯示版本兼容性警告，這是正常的，不影響模型功能。
