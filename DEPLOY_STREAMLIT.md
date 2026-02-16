# 🚀 Streamlit Cloud 部署指南

## 部署步驟

### 1. 準備GitHub倉庫
確保所有文件都在GitHub上：
- ✅ `streamlit_app.py` - 主應用文件
- ✅ `requirements.txt` - Python依賴
- ✅ `heloc_model.joblib` - 模型文件
- ✅ `feature_cols.joblib` - 特徵列表
- ✅ `heloc_medians.joblib` - 中位數數據
- ✅ `heloc_threshold.joblib` - 決策閾值
- ✅ `.streamlit/config.toml` - 配置文件

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2. 在Streamlit Cloud上部署

1. 訪問 https://share.streamlit.io
2. 點擊 "New app"
3. 選擇您的GitHub倉庫
4. 選擇分支: `main`
5. 選擇文件: `streamlit_app.py`
6. 點擊 "Deploy"

### 3. 故障排查

如果看到 `ModuleNotFoundError`：

**步驟 1: 檢查requirements.txt**
```
streamlit>=1.28.0
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
joblib>=1.3.0
xgboost>=2.0.0
```

**步驟 2: 查看應用日誌**
- 在應用右下角點擊 "Manage app"
- 查看 "Logs" 選項卡
- 查找具體的錯誤信息

**步驟 3: 檢查文件位置**
- 確保所有 `.joblib` 文件都在倉庫根目錄
- 文件必須和 `streamlit_app.py` 位於同一目錄

**步驟 4: 重新部署**
- 點擊應用右上角的菜單
- 選擇 "Reboot app"

### 4. 常見錯誤解決方案

#### `ModuleNotFoundError: No module named 'xgboost'`
- ✅ 確認 `xgboost>=2.0.0` 在 requirements.txt 中

#### `ModuleNotFoundError: No module named 'joblib'`
- ✅ 確認 `joblib>=1.3.0` 在 requirements.txt 中

#### 模型檔案找不到
- ✅ 確認 `.joblib` 文件已提交到Git
- ✅ 檢查文件是否被 `.gitignore` 排除
- ✅ 驗證文件位置：應在倉庫根目錄

### 5. 驗證部署成功

應用啟動時應該顯示：
- ✅ 側邊欄上方顯示 "✅ Model loaded successfully" 或 "⚠️ Using demo mode"
- ✅ 主頁面顯示 "🏦 HELOC Decision Support System"
- ✅ 能夠選擇模式和進行預測

## 📊 文件大小

確保文件不超過Streamlit Cloud限制（通常為100MB）：
- `heloc_model.joblib`: 386 KB ✅
- `feature_cols.joblib`: 589 B ✅
- `heloc_medians.joblib`: 2.9 KB ✅
- `heloc_threshold.joblib`: 21 B ✅

## 🔗 有用的連結

- [Streamlit Cloud文檔](https://docs.streamlit.io/streamlit-cloud/get-started)
- [Requirements.txt最佳實踐](https://docs.streamlit.io/streamlit-cloud/deploy-your-app/app-dependencies)
- [故障排查指南](https://docs.streamlit.io/streamlit-cloud/troubleshooting)
