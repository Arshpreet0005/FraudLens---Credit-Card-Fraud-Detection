# FraudLens – Credit Card Fraud Detection

End‑to‑end credit card fraud detection system with a full ML pipeline (EDA, feature engineering, SMOTE, model training/evaluation) and a Streamlit web app for real‑time and batch predictions, built on the Kaggle credit card transactions dataset.

---

## Features

- Data cleaning, exploratory data analysis, and visualization of class imbalance.
- Feature engineering: datetime features (hour, day, month, day‑of‑week), customer age, and categorical encodings for merchant, category, gender, state, and job.
- Class imbalance handling using SMOTE on the training set.[file:1]
- Multiple ML models trained and compared (Logistic Regression, Random Forest, XGBoost, Decision Tree) with metrics such as Accuracy, Precision, Recall, F1‑Score, and ROC‑AUC.
- Streamlit UI with:
  - Login / signup and admin roles.
  - Single‑transaction fraud prediction with probability, risk level, and gauge chart.
  - Batch prediction from CSV upload with downloadable results and summary statistics.
  - Admin analytics dashboard, user management, and system stats.

---

## Tech Stack

- Python, pandas, NumPy
- scikit‑learn, XGBoost, imbalanced‑learn (SMOTE)
- Matplotlib, Seaborn, Plotly
- Streamlit
- joblib for model persistence

---

## Getting Started

<<<<<<< HEAD
1. **Clone the repo**
2. **Create a virtual environment (optional)**
3. **Install dependencies**
4. **Train models (first time)**
- Open `real_code.ipynb` in Jupyter / VS Code.
=======
1. *Clone the repo*
2. *Create a virtual environment (optional)*
3. *Install dependencies (requirements.txt)---> pip install requirements.txt*
4. *Train models (first time)*
- Open real_code.ipynb in Jupyter / VS Code.
>>>>>>> fd3332f358b452fe329b51b89b01e6d814a2bf88
- Run all cells to:
  - Load the Kaggle credit card fraud dataset.
  - Run preprocessing, feature engineering, SMOTE.
  - Train models and save:
<<<<<<< HEAD
    - `randomforestmodel.pkl`
    - `scaler.pkl`
    - `labelencoders.pkl`
    - `featurenames.pkl`
- Place these files where  `app.py` expects them (e.g., a `models/` folder).

5. **Run the Streamlit app**
   
## Dataset

This project uses the public *Credit Card Transactions Fraud Detection* dataset from Kaggle.  
Download it from Kaggle and place it in the project directory before running the training notebook.
=======
    - randomforestmodel.pkl
    - scaler.pkl
    - labelencoders.pkl
    - featurenames.pkl
- Place these files where  app.py expects them (e.g., a models/ folder).

5. *Run the Streamlit app*
   
## Dataset

This project uses the public Credit Card Transactions Fraud Detection dataset from Kaggle.  
Download it from Kaggle and place it in the project directory before running the training notebook.
https://www.kaggle.com/datasets/kartik2112/fraud-detection
>>>>>>> fd3332f358b452fe329b51b89b01e6d814a2bf88
