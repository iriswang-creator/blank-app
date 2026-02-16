# 🔧 Streamlit Cloud ModuleNotFoundError 故障排查

## 問題：ModuleNotFoundError 仍然出現

如果仍然看到 `ModuleNotFoundError: This app has encountered an error`，請按照以下步驟排查。

## 📋 第1步：查看詳細的錯誤日誌

### 在Streamlit Cloud上查看日誌
1. 打開您的應用
2. 點擊右下角的 **「Manage app」**
3. 進入 **「Logs」** 選項卡
4. 查找 `ModuleNotFoundError` 的完整錯誤信息
5. 記下具體缺少的模塊名稱

### 運行本地診斷
在本地終端運行：
```bash
cd /workspaces/blank-app
python -c "import streamlit, numpy, pandas, joblib, xgboost, sklearn; print('All OK')"
```

## 📋 第2步：驗證requirements.txt

檢查 `requirements.txt` 包含所有必需的包（不含版本號最靈活）：
```
streamlit
pandas
numpy
joblib
scikit-learn
xgboost
```

❌ 錯誤格式（版本號過於嚴格）：
```
streamlit>=1.28.0
xgboost>=2.0.0
```

在Streamlit Cloud上，寬鬆的版本號更可靠。

## 📋 第3步：檢查.joblib文件

執行以下命令確認所有文件都被Git追蹤：
```bash
git ls-files | grep joblib
```

應該看到：
```
feature_cols.joblib
heloc_medians.joblib
heloc_model.joblib
heloc_threshold.joblib
```

如果沒有顯示，執行：
```bash
git add *.joblib
git commit -m "Add model files"
git push origin main
```

## 📋 第4步：在Streamlit Cloud重新部署

### 方法1：完全重新部署
1. 在應用頁面點擊右下角的 **「Manage app」**
2. 找到 **「Reboot app」** 並點擊
3. 等待應用重新啟動

### 方法2：刪除並重新部署
1. 在 https://share.streamlit.io 
2. 點擊您的應用右側的三個點
3. 選擇 **「Delete app」**
4. 重新部署：New app → 選擇倉庫和streamlit_app.py

## 📋 第5步：驗證部署成功

當應用成功啟動時，您應該看到：
- ✅ 頁面標題：「🏦 HELOC Decision Support System」
- ✅ 側邊欄的模式選擇
- ✅ 應用能夠響應交互

## 🐛 最常見的錯誤原因

### 原因1：XGBoost版本衝突
**症狀**：錯誤信息包含 "xgboost"

**解決方案**：
```
# requirements.txt 中，確保行為：
xgboost
```
不用版本號。

### 原因2：.joblib文件未部署
**症狀**：應用啟動，但顯示「Using demo mode」

**檢查**：
```bash
git ls-files *.joblib
```

如果沒有輸出，執行：
```bash
git add *.joblib
git commit -m "Track joblib files"
git push
```

### 原因3：scikit-learn導入問題
**症狀**：錯誤信息包括 "sklearn"

**解決方案**：
確保 requirements.txt 包含：
```
scikit-learn
```
（不是 sklearn）

## 🔗 如果仍未解決

1. **查看應用日誌**中的完整錯誤信息
2. **複製完整錯誤**（除了敏感信息）
3. 查詢錯誤在 [Streamlit論壇](https://discuss.streamlit.io)
4. 檢查 [Streamlit Cloud文檔](https://docs.streamlit.io/streamlit-cloud/troubleshooting)

## 💡 快速檢查清單

- [ ] Git中追蹤了所有.joblib文件
- [ ] requirements.txt不包含過於嚴格的版本號
- [ ] 本地能夠`python -c "import xgboost, joblib"`
- [ ] Streamlit Cloud的日誌中查看了具體錯誤
- [ ] 嘗試了應用重新啟動（Reboot app）

## 📞 自動重試

如果是暫時性問題，Streamlit Cloud會自動重試部署。等待2-3分鐘後重新檢查。
