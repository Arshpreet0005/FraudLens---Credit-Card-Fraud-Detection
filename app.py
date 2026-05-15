import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
import joblib
from datetime import datetime
import hashlib
import warnings
warnings.filterwarnings('ignore')
import os

from huggingface_hub import hf_hub_download

HF_REPO_ID = "Akrodriguez/Fraudlens"

REQUIRED_FILES = [
    "random_forest_model.pkl",
    "scaler.pkl",
    "label_encoders.pkl",
    "feature_names.pkl",
    "xgboost_model.pkl",
    "decision_tree_model.pkl",
    "logistic_regression_model.pkl",
    # add any other .pkl you load in code
]

@st.cache_resource
def ensure_artifacts():
    for f in REQUIRED_FILES:
        if not os.path.exists(f):
            hf_hub_download(
                repo_id=HF_REPO_ID,
                filename=f,
                local_dir=".",                 # put a copy in the app folder
                local_dir_use_symlinks=False   # avoid symlink issues
            )

# ==================== AUTHENTICATION SYSTEM ====================

# Initialize user database in session state (persists during the session)
if 'USER_DATABASE' not in st.session_state:
    st.session_state.USER_DATABASE = {
        "users": {
            "user1": {
                "password": hashlib.sha256("password123".encode()).hexdigest(),
                "name": "Ansh Kumar",
                "role": "user"
            },
            "user2": {
                "password": hashlib.sha256("user456".encode()).hexdigest(),
                "name": "Arshpreet Singh",
                "role": "user"
            }
        },
        "admins": {
            "admin": {
                "password": hashlib.sha256("admin123".encode()).hexdigest(),
                "name": "Admin User",
                "role": "admin"
            },
            "hiritik": {
                "password": hashlib.sha256("hiritik@2024".encode()).hexdigest(),
                "name": "Hiritik",
                "role": "admin"
            },
            "ansh": {
                "password": hashlib.sha256("ansh@2024".encode()).hexdigest(),
                "name": "Ansh",
                "role": "admin"
            },
            "arshpreet": {
                "password": hashlib.sha256("arshpreet@2024".encode()).hexdigest(),
                "name": "Arshpreet",
                "role": "admin"
            }
        }
    }

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_display_name' not in st.session_state:
    st.session_state.user_display_name = None

# ========== Initialize form values in session state (PREVENTS DATETIME RESET) ==========
if 'form_values' not in st.session_state:
    st.session_state.form_values = {
        'trans_date_trans_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'merchant': 'fraud_Kirlin and Sons',
        'category': 'gas_transport',
        'amt': 100.0,
        'first': 'John',
        'last': 'Doe',
        'gender': 'M',
        'street': '123 Main St',
        'city': 'New York',
        'state': 'NY',
        'zip': '10001',
        'lat': 40.7128,
        'long': -74.0060,
        'city_pop': 8000000,
        'job': 'Software Engineer',
        'dob': '1990-01-01',
        'trans_num': 'T123456789',
        'unix_time': int(datetime.now().timestamp()),
        'merch_lat': 40.7589,
        'merch_long': -73.9851
    }


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate(username, password, role):
    """Authenticate user based on role"""
    password_hash = hash_password(password)
    
    user_info = None
    if role == "admin":
        user_info = st.session_state.USER_DATABASE["admins"].get(username)
    else:
        user_info = st.session_state.USER_DATABASE["users"].get(username)
    
    if user_info is not None and user_info["password"] == password_hash:
        # return the WHOLE user info dict
        return True, user_info
    
    return False, None



def signup_user(username, password, name):
    """Register a new regular user"""
    if username in st.session_state.USER_DATABASE["users"]:
        return False, "Username already exists"
    
    if username in st.session_state.USER_DATABASE["admins"]:
        return False, "Username already exists"
    
    # Add new user
    st.session_state.USER_DATABASE["users"][username] = {
        "password": hash_password(password),
        "name": name,
        "role": "user"
    }
    return True, "Signup successful! Please login."


def login_page():
    """Display login and sign-up page"""
    st.markdown("""
<style>
body {
    min-height: 100vh;
    /* Animated gradient */
    background: linear-gradient(-45deg, #6a82fb, #fc5c7d, #40c9ff, #ffde7d);
    background-size: 400% 400%;
    animation: gradientBG 16s ease infinite;
    background-attachment: fixed;
}
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.login-container {
    max-width: 500px;
    margin: auto;
    padding: 2.5rem;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 25px;
    box-shadow: 0 10px 40px rgba(56,56,56,0.20), 0 1.5px 36px 0px rgba(53, 75, 150, 0.10);
    backdrop-filter: blur(8px);
    /* glassmorphism border */
    border: 2px solid rgba(255,255,255,0.17);
}

.login-title {
    color: #ffffff;
    text-align: center;
    font-size: 2.8rem;
    font-weight: bold;
    margin-bottom: 2rem;
    letter-spacing: 2px;
    text-shadow: 0 4px 16px rgba(80,80,120,0.10);
}

.login-subtitle {
    color: #eef2fb;
    text-align: center;
    font-size: 1.25rem;
    margin-bottom: 1rem;
    text-shadow: 0 2px 10px rgba(80,80,120,0.10);
}

/* Round and modern tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.23) !important;
    border-radius: 27px 27px 0 0;
}
.stTabs [data-testid="stTab"] {
    color: #4a6fa5 !important;
    font-weight: bold;
}

footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class='login-container'>
                <div class='login-title'>💳 FraudLens</div>
                <div class='login-subtitle'>Secure Login Portal</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Login type selection
        user_type = st.radio(
            "Login As:",
            ["👤 User", "🔐 Admin"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        user_type_value = "user" if user_type == "👤 User" else "admin"
        
        st.markdown("---")
        
        # For Users: Show Login and Sign-Up tabs
        if user_type_value == "user":
            tab1, tab2 = st.tabs(["🔓 Login", "➕ Sign Up"])
            
            with tab1:
                # Login form
                with st.form("login_form", clear_on_submit=False):
                    username = st.text_input(
                        "Username",
                        placeholder="Enter your username",
                        key="login_username"
                    )
                    
                    password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter your password",
                        key="login_password"
                    )
                    
                    col_a, col_b, col_c = st.columns([1, 2, 1])
                    with col_b:
                        submit_button = st.form_submit_button(
                            "🔓 Login",
                            use_container_width=True,
                            type="primary"
                        )
                    
                    if submit_button:
                        if not username or not password:
                            st.error("⚠️ Please fill in all fields")
                        else:
                            is_valid, user_data = authenticate(username, password, user_type_value)
                            
                            if is_valid:
                                # Store user info in session state
                                st.session_state.authenticated = True
                                st.session_state.username = username
                                st.session_state.user_role = user_data["role"]
                                st.session_state.user_name = user_data["name"]
                                st.session_state.user_display_name = user_data["name"]
                                st.session_state.page = 'Dashboard'
                                
                                st.success(f"✅ Welcome, {user_data['name']}!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Invalid username or password")
            
            with tab2:
                # Sign-up form
                with st.form("signup_form", clear_on_submit=True):
                    new_username = st.text_input(
                        "Username",
                        placeholder="Choose a username",
                        key="signup_username"
                    )
                    new_name = st.text_input(
                        "Full Name",
                        placeholder="Enter your full name",
                        key="signup_name"
                    )
                    new_password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Choose a password (min 6 characters)",
                        key="signup_password"
                    )
                    confirm_password = st.text_input(
                        "Confirm Password",
                        type="password",
                        placeholder="Re-enter your password",
                        key="signup_confirm_password"
                    )
                    
                    col_a, col_b, col_c = st.columns([1, 2, 1])
                    with col_b:
                        signup_button = st.form_submit_button(
                            "➕ Create Account",
                            use_container_width=True,
                            type="primary"
                        )
                    
                    if signup_button:
                        if not new_username or not new_password or not new_name or not confirm_password:
                            st.error("⚠️ Please fill in all fields")
                        elif new_password != confirm_password:
                            st.error("❌ Passwords do not match")
                        else:
                            success, message = signup_user(new_username, new_password, new_name)
                            if success:
                                st.success(f"✅ {message} You can now login.")
                                st.info("💡 Switch to the Login tab to sign in")
                            else:
                                st.error(f"❌ {message}")
        
        # For Admins: Show only Login (no sign-up)
        else:
            # Login form for admin
            with st.form("admin_login_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    placeholder="Enter admin username",
                    key="admin_login_username"
                )
                
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter admin password",
                    key="admin_login_password"
                )
                
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    submit_button = st.form_submit_button(
                        "🔓 Login as Admin",
                        use_container_width=True,
                        type="primary"
                    )
                
                if submit_button:
                    if not username or not password:
                        st.error("⚠️ Please fill in all fields")
                    else:
                        is_valid, user_data = authenticate(username, password, user_type_value)
                        
                        if is_valid:
                            # Store user info in session state
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.session_state.user_role = user_data["role"]
                            st.session_state.user_name = user_data["name"]
                            st.session_state.user_display_name = user_data["name"]
                            st.session_state.page = 'Dashboard'
                            
                            st.success(f"✅ Welcome, {user_data['name']}!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Invalid admin credentials")
        
        st.markdown("---")


def logout():
    """Logout function"""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.session_state.user_display_name = None
    st.rerun()


# ==================== FEATURE ENGINEERING FUNCTIONS ====================


def engineer_features(df):
    """
    Apply EXACT SAME feature engineering as training notebook
    This is CRITICAL for correct predictions
    """
    df = df.copy()
    
    # 1. Extract date/time features
    print("Extracting datetime features...")

    # SAFE datetime conversion
    if 'trans_date_trans_time' in df.columns:
        df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
    else:
        st.error("Missing 'trans_date_trans_time'; check file or input data.")
        return None

    if 'dob' in df.columns:
        df['dob'] = pd.to_datetime(df['dob'])
    else:
        st.error("Missing 'dob'; check file or input data.")
        return None

    df['trans_hour'] = df['trans_date_trans_time'].dt.hour
    df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
    df['dob'] = pd.to_datetime(df['dob'])
    
    df['trans_hour'] = df['trans_date_trans_time'].dt.hour
    df['trans_day'] = df['trans_date_trans_time'].dt.day
    df['trans_month'] = df['trans_date_trans_time'].dt.month
    df['trans_dow'] = df['trans_date_trans_time'].dt.dayofweek
    df['age'] = (df['trans_date_trans_time'] - df['dob']).dt.days / 365.25
    
    print(f"✓ Extracted: hour, day, month, day_of_week, age")
    
    # 2. Encode categorical variables (using pre-saved encoders)
    print("Encoding categorical variables...")
    categorical_features = ['merchant', 'category', 'gender', 'state', 'job']
    
    try:
        # Load label encoders
        le_dict = joblib.load('label_encoders.pkl')
        
        for col in categorical_features:
            if col in df.columns and col in le_dict:
                # Handle unseen labels
                le = le_dict[col]
                df[col] = df[col].astype(str)
                
                # Map unseen values to a default category (most common)
                valid_classes = set(le.classes_)
                df[col] = df[col].apply(lambda x: x if x in valid_classes else le.classes_[0])
                
                df[col] = le.transform(df[col])
                print(f"  ✓ {col}: encoded")
    except FileNotFoundError:
        st.error("⚠️ label_encoders.pkl not found! Please train models first.")
        return None
    
    # 3. Drop unnecessary columns (SAME AS TRAINING)
    print("Removing unnecessary columns...")
    cols_to_drop = ['Unnamed: 0', 'trans_num', 'first', 'last', 'street', 'zip', 
                    'lat', 'long', 'city', 'trans_date_trans_time', 'dob']
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')
    
    print(f"✓ Final shape after feature engineering: {df.shape}")
    
    return df


def preprocess_for_prediction(df):
    """
    Complete preprocessing pipeline for prediction
    """
    print("\n=== PREPROCESSING FOR PREDICTION ===")
    
    # 1. Feature engineering
    df_processed = engineer_features(df)
    if df_processed is None:
        return None, None
    
    # 2. Separate target if present
    if 'is_fraud' in df_processed.columns:
        X = df_processed.drop('is_fraud', axis=1)
        y = df_processed['is_fraud']
    else:
        X = df_processed
        y = None


    # -- DROP cc_num here for compatibility!
    if 'cc_num' in X.columns:
        print("Dropping cc_num from prediction features (to match training)...")
        X = X.drop(columns=['cc_num'])


    # 3. Load scaler and scale numerical features
    print("\nScaling numerical features...")
    try:
        scaler = joblib.load('scaler.pkl')
        numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
        X[numeric_features] = scaler.transform(X[numeric_features])
        print(f"✓ Scaled {len(numeric_features)} numerical features")
    except FileNotFoundError:
        st.error("⚠️ scaler.pkl not found! Please train models first.")
        return None, None


    # 4. Ensure column order matches training
    try:
        feature_names = joblib.load('feature_names.pkl')
        # Reorder columns to match training
        missing_cols = set(feature_names) - set(X.columns)
        extra_cols = set(X.columns) - set(feature_names)
        
        if missing_cols:
            print(f"⚠️ Missing columns: {missing_cols}")
            for col in missing_cols:
                X[col] = 0  # Add missing columns with default value
        
        if extra_cols:
            print(f"⚠️ Extra columns (removing): {extra_cols}")
            X = X.drop(columns=list(extra_cols))
        
        X = X[feature_names]  # Reorder to match training
        print(f"✓ Column order matched: {X.shape[1]} features")
        
    except FileNotFoundError:
        st.warning("⚠️ feature_names.pkl not found - using current column order")


    print(f"\n✓ Preprocessing complete! Shape: {X.shape}")
    return X, y



# ==================== MODEL LOADING ====================


@st.cache_resource
def load_models():
    """Load ONLY Random Forest model for user display"""
    models = {}
    
    model_files = {
        'Random Forest': 'random_forest_model.pkl',
    }
    
    for name, file in model_files.items():
        try:
            models[name] = joblib.load(file)
            print(f"✓ Loaded {name}")
        except FileNotFoundError:
            st.warning(f"⚠️ {file} not found")
    
    return models


# ==================== PREDICTION FUNCTION ====================


def make_predictions(input_df, models):
    """Make predictions using Random Forest only"""
    # Preprocess input
    X_processed, _ = preprocess_for_prediction(input_df)
    
    if X_processed is None:
        st.error("Preprocessing failed!")
        return None, None
    
    predictions = {}
    probabilities = {}
    
    for name, model in models.items():
        try:
            # Get prediction
            pred = model.predict(X_processed)
            predictions[name] = pred[0]
            
            # Get probability if available
            if hasattr(model, 'predict_proba'):
                prob = model.predict_proba(X_processed)
                probabilities[name] = prob[0][1]  # Probability of fraud
            else:
                probabilities[name] = pred[0]  # For models without predict_proba
                
        except Exception as e:
            st.error(f"Error with {name}: {str(e)}")
            predictions[name] = None
            probabilities[name] = None
    
    return predictions, probabilities


# ==================== MAIN APPLICATION ====================


def main():
    """Main application"""
    
    # Check authentication
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Sidebar for navigation and logout
    with st.sidebar:
        st.title("🏦 Navigation")
        st.write(f"👤 **{st.session_state.user_display_name}**")
        st.write(f"🔑 Role: **{st.session_state.user_role.upper()}**")
        st.divider()
        
        if st.session_state.user_role == "admin":
            page = st.radio("Select Page", 
                          ["🏠 Home", "🔍 Single Transaction", "📊 Batch Prediction", "📈 Analytics", "⚙️Authorizer Panel"])
        else:
            page = st.radio("Select Page", 
                          ["🏠 Home", "🔍 Single Transaction", "📊 Batch Prediction"])
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    
    # Load models
    models = load_models()
    
    if not models:
        st.error("⚠️ No models found! Please train models first using real_code.ipynb")
        st.stop()
    
    # Page routing
    if page == "🏠 Home":
        home_page()
    elif page == "🔍 Single Transaction":
        single_transaction_page(models)
    elif page == "📊 Batch Prediction":
        batch_prediction_page(models)
    elif page == "📈 Analytics" and st.session_state.user_role == "admin":
        analytics_page()
    elif page == "⚙️Authorizer Panel" and st.session_state.user_role == "admin":
        authorizer_panel()


def home_page():
    """Home page"""
    st.title("🏦 FRAUDLENS")
    st.markdown("### Welcome to the Advanced Fraud Detection Platform")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🎯 Model Accuracy", "99.2%", "+0.5%")
    with col2:
        st.metric("🔍 Fraud Detected", "7,506", "+22")
    with col3:
        st.metric("✅ Valid Transactions", "1,289,169", "+234")
    
    st.markdown("---")
    
    st.markdown("""
    ## 🔐 System Features
    
    ### For All Users:
    - **🔍 Single Transaction Analysis**: Check individual transactions for fraud
    - **📊 Real-time Predictions**: Get instant fraud detection results
    - **🎯 Random Forest ML Model**: Highly accurate ensemble algorithm(For batch process)
    
    ### For Admins:
    - **📈 Advanced Analytics**: Comprehensive fraud statistics
    - **📊 Batch Processing**: Upload and analyze multiple transactions for different models
    - **⚙️ Authorizer Panel**: Manage Users, See System stats, Change Settings
    
    ## 🤖 Detection Model
    
    **Random Forest** - Ensemble decision tree model with 99%+ accuracy
    
    ---
    
    ### 📝 How to Use:
    1. Navigate to **Single Transaction** to check a transaction
    2. Fill in transaction details
    3. Get instant fraud prediction
    4. Upload CSV files for batch processing
    
    """)
    
    st.info("💡 **Tip**: The model is trained on real credit card transaction data with advanced feature engineering!")


def single_transaction_page(models):
    """Single transaction prediction page - SHOWS ONLY RANDOM FOREST"""
    st.title("🔍 Single Transaction Fraud Detection")
    st.markdown("Enter transaction details below to check for potential fraud")
    
    # Create input form with session state values
    with st.form("transaction_form"):
        st.subheader("📋 Transaction Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            trans_date_trans_time = st.text_input(
                "Transaction DateTime", 
                value=st.session_state.form_values['trans_date_trans_time'],
                help="Format: YYYY-MM-DD HH:MM:SS"
            )
            merchant = st.text_input("Merchant Name", value=st.session_state.form_values['merchant'])
            category = st.selectbox("Category", 
                                   ['gas_transport', 'grocery_pos', 'home', 'shopping_pos', 
                                    'misc_pos', 'shopping_net', 'grocery_net', 'entertainment',
                                    'food_dining', 'personal_care', 'health_fitness', 'misc_net',
                                    'travel', 'kids_pets'],
                                   index=['gas_transport', 'grocery_pos', 'home', 'shopping_pos', 
                                          'misc_pos', 'shopping_net', 'grocery_net', 'entertainment',
                                          'food_dining', 'personal_care', 'health_fitness', 'misc_net',
                                          'travel', 'kids_pets'].index(st.session_state.form_values['category']))
            amt = st.number_input("Amount ($)", min_value=0.0, value=st.session_state.form_values['amt'], step=0.01)
        
        with col2:
            first = st.text_input("First Name", value=st.session_state.form_values['first'])
            last = st.text_input("Last Name", value=st.session_state.form_values['last'])
            gender = st.selectbox("Gender", ['M', 'F'],
                                 index=['M', 'F'].index(st.session_state.form_values['gender']))
            street = st.text_input("Street", value=st.session_state.form_values['street'])
            city = st.text_input("City", value=st.session_state.form_values['city'])
        
        with col3:
            state = st.selectbox("State", ['NY', 'CA', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI'],
                               index=['NY', 'CA', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI'].index(st.session_state.form_values['state']))
            zip_code = st.text_input("ZIP Code", value=st.session_state.form_values['zip'])
            lat = st.number_input("Latitude", value=st.session_state.form_values['lat'], format="%.4f")
            long = st.number_input("Longitude", value=st.session_state.form_values['long'], format="%.4f")
            city_pop = st.number_input("City Population", value=st.session_state.form_values['city_pop'], step=1000)
        
        st.subheader("👤 Cardholder Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            job = st.text_input("Job", value=st.session_state.form_values['job'])
            dob = st.text_input("Date of Birth", 
                               value=st.session_state.form_values['dob'],
                               help="Format: YYYY-MM-DD")
        
        with col2:
            trans_num = st.text_input("Transaction Number", value=st.session_state.form_values['trans_num'])
            unix_time = st.number_input("Unix Time", value=st.session_state.form_values['unix_time'])
        
        with col3:
            merch_lat = st.number_input("Merchant Latitude", value=st.session_state.form_values['merch_lat'], format="%.4f")
            merch_long = st.number_input("Merchant Longitude", value=st.session_state.form_values['merch_long'], format="%.4f")
        
        submit = st.form_submit_button("🔍 Check for Fraud", use_container_width=True)
    
    if submit:
        # Update session state
        st.session_state.form_values.update({
            'trans_date_trans_time': trans_date_trans_time,
            'merchant': merchant,
            'category': category,
            'amt': amt,
            'first': first,
            'last': last,
            'gender': gender,
            'street': street,
            'city': city,
            'state': state,
            'zip': zip_code,
            'lat': lat,
            'long': long,
            'city_pop': city_pop,
            'job': job,
            'dob': dob,
            'trans_num': trans_num,
            'unix_time': unix_time,
            'merch_lat': merch_lat,
            'merch_long': merch_long
        })
        
        # Create DataFrame from inputs
        input_data = {
            'trans_date_trans_time': [trans_date_trans_time],
            'merchant': [merchant],
            'category': [category],
            'amt': [amt],
            'first': [first],
            'last': [last],
            'gender': [gender],
            'street': [street],
            'city': [city],
            'state': [state],
            'zip': [zip_code],
            'lat': [lat],
            'long': [long],
            'city_pop': [city_pop],
            'job': [job],
            'dob': [dob],
            'trans_num': [trans_num],
            'unix_time': [unix_time],
            'merch_lat': [merch_lat],
            'merch_long': [merch_long]
        }
        
        input_df = pd.DataFrame(input_data)
        
        # Show processing
        with st.spinner("🔄 Analyzing transaction..."):
            predictions, probabilities = make_predictions(input_df, models)
        
        if predictions:
            st.success("✅ Analysis Complete!")
            
            # Display results - ONLY RANDOM FOREST
            st.markdown("---")
            st.subheader("📊 Prediction Result")
            
            # Get Random Forest result
            rf_prediction = predictions['Random Forest']
            rf_probability = probabilities['Random Forest']
            
            # Large display of result
            if rf_prediction == 1:
                st.error("### 🚨 FRAUD DETECTED")
                st.metric("Fraud Probability", f"{rf_probability*100:.2f}%")
                st.warning("**Recommendation**: Block transaction and verify with cardholder")
            else:
                st.success("### ✅ TRANSACTION VALID")
                st.metric("Fraud Probability", f"{rf_probability*100:.2f}%")
                st.info("**Recommendation**: Proceed with transaction")
            
                        # Progress bar for probability
            st.markdown("### Fraud Probability Indicator")
            st.progress(rf_probability)

            # Gauge/Semi-circular Meter Visualization
            st.markdown("### Fraud Score")
            import plotly.graph_objects as go  

            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = rf_probability * 100,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': ""},
                delta = {'reference': 50, 'increasing': {'color': "red"}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "red" if rf_probability > 0.5 else "lightgreen"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 20], 'color': '#28a745'},
                        {'range': [20, 40], 'color': '#90ee90'},
                        {'range': [40, 60], 'color': '#ffeb3b'},
                        {'range': [60, 80], 'color': '#ff9800'},
                        {'range': [80, 100], 'color': '#f44336'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={'color': "gray", 'family': "Arial"},
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
            
                        # Feature Importance Chart
            st.markdown("---")
            st.subheader("📊 Key Features Influencing This Prediction")

            # Get feature importances from Random Forest model
            rf_model = models['Random Forest']

            try:
                # Load feature names 
                feature_names = joblib.load('feature_names.pkl')

                # Get feature importances
                importances = rf_model.feature_importances_

                # Create dataframe for top 10 features
                feature_importance_df = pd.DataFrame({
                    'Feature': feature_names,
                    'Importance': importances
                }).sort_values('Importance', ascending=False).head(10)

                # Create horizontal bar chart using Plotly
                fig_feat = go.Figure(go.Bar(
                    x=feature_importance_df['Importance'][::-1],
                    y=feature_importance_df['Feature'][::-1],
                    orientation='h',
                    marker=dict(
                        color=feature_importance_df['Importance'][::-1],
                        colorscale='Viridis'
                    ),
                    text=[f"{val:.3f}" for val in feature_importance_df['Importance'][::-1]],
                    textposition='auto'
                ))
                fig_feat.update_layout(
                    title="Top 10 Most Important Features",
                    xaxis_title="Importance Score",
                    yaxis_title="",
                    margin=dict(l=120, r=20, t=50, b=30),
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_feat, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not show feature importance: {e}")
            
            # Detailed breakdown
            with st.expander("📋 View Detailed Analysis"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Model**: Random Forest")
                    st.write(f"**Prediction**: {'🚨 FRAUD' if rf_prediction == 1 else '✅ VALID'}")
                with col2:
                    st.write(f"**Confidence**: {abs(rf_probability - 0.5) * 200:.1f}%")
                    st.write(f"**Risk Level**: {'High' if rf_probability > 0.7 else 'Medium' if rf_probability > 0.3 else 'Low'}")


def batch_prediction_page(models):
    """Batch prediction page - Now available for all users and admins"""
    st.title("📊 Batch Fraud Detection")
    st.markdown("Upload a CSV file with multiple transactions for batch analysis")
    st.info("ℹ️ Upload a CSV file containing transaction data. The file should have the same columns as your training data.")

    uploaded_file = st.file_uploader("📁 Choose a CSV file", type=['csv'])

    # ---- Probability threshold slider for admin and user
    if st.session_state.user_role == "admin":
        PROB_THRESHOLD = st.slider(
            "Fraud Threshold (applies to all models)", min_value=0.05, max_value=0.9, value=0.3, step=0.01, key="admin_fraud_threshold"
        )
    else:
        PROB_THRESHOLD = st.slider(
            'Fraud Threshold', min_value=0.05, max_value=0.9, value=0.3, step=0.01, key="user_fraud_threshold"
        )

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("📋 Uploaded Data Preview")
        st.dataframe(df.head(), use_container_width=True)
        st.info(f"📊 Total transactions: {len(df)}")

        if st.button("🔍 Analyze All Transactions", use_container_width=True):
            with st.spinner("🔄 Processing batch..."):
                X_processed, y_true = preprocess_for_prediction(df)
                if X_processed is not None:
                    if st.session_state.user_role == "admin":
                        # ---- Admin: show all models with the common threshold
                        all_models = {
                            'Logistic Regression': joblib.load('logistic_regression_model.pkl'),
                            'Random Forest': joblib.load('random_forest_model.pkl'),
                            'XGBoost': joblib.load('xgboost_model.pkl'),
                            'Decision Tree': joblib.load('decision_tree_model.pkl'),
                        }
                        results = {}
                        for name, model in all_models.items():
                            try:
                                if hasattr(model, 'predict_proba'):
                                    probabilities = model.predict_proba(X_processed)[:, 1]
                                else:
                                    probabilities = model.predict(X_processed)
                                predictions = (probabilities >= PROB_THRESHOLD).astype(int)
                                results[name] = {
                                    'predictions': predictions,
                                    'probabilities': probabilities
                                }
                            except Exception as e:
                                st.error(f"Error with {name}: {str(e)}")
                        st.success("✅ Batch analysis complete!")
                        st.markdown("### 📊 Summary Statistics")
                        summary_data = []
                        for name, result in results.items():
                            fraud_count = sum(result['predictions'])
                            fraud_rate = fraud_count / len(result['predictions']) * 100
                            summary_data.append({
                                'Model': name,
                                'Total Transactions': len(result['predictions']),
                                'Fraud Detected': fraud_count,
                                'Fraud Rate (%)': f"{fraud_rate:.2f}%"
                            })
                        summary_df = pd.DataFrame(summary_data)
                        st.dataframe(summary_df, use_container_width=True, hide_index=True)
                        st.markdown("### 📈 Fraud Detection Comparison")
                        fig = go.Figure()
                        for name in results.keys():
                            fraud_count = sum(results[name]['predictions'])
                            fig.add_trace(go.Bar(
                                name=name,
                                x=[name],
                                y=[fraud_count],
                                text=[fraud_count],
                                textposition='outside'
                            ))
                        fig.update_layout(
                            title="Fraud Cases Detected by Each Model",
                            xaxis_title="Model",
                            yaxis_title="Number of Fraud Cases",
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # ---- Regular user: only Random Forest, threshold applied
                        try:
                            st.success("✅ Batch analysis complete!")
                            rf_model = models['Random Forest']
                            if hasattr(rf_model, 'predict_proba'):
                                probabilities = rf_model.predict_proba(X_processed)[:, 1]
                            else:
                                probabilities = rf_model.predict(X_processed)
                            predictions = (probabilities >= PROB_THRESHOLD).astype(int)
                            results_df = df.copy()
                            results_df['Fraud_Probability'] = [f"{prob*100:.2f}%" for prob in probabilities]
                            results_df['Prediction'] = [
                                'FRAUD' if prob >= PROB_THRESHOLD else 'VALID' for prob in probabilities
                            ]
                            fraud_count = (results_df['Prediction'] == "FRAUD").sum()
                            valid_count = (results_df['Prediction'] == "VALID").sum()
                            fraud_rate = fraud_count / len(results_df) * 100
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Transactions", len(results_df))
                            with col2:
                                st.metric("🚨 Fraud Detected", fraud_count)
                            with col3:
                                st.metric("✅ Valid Transactions", valid_count)
                            st.markdown(f"**Fraud Rate**: {fraud_rate:.2f}%")
                            st.markdown("### 📈 Fraud Distribution (Random Forest)")
                            fig_pie = go.Figure(data=[go.Pie(
                                labels=['FRAUD', 'VALID'],
                                values=[fraud_count, valid_count],
                                marker=dict(colors=['#dc3545', '#28a745'])
                            )])
                            fig_pie.update_layout(title="Transaction Distribution")
                            st.plotly_chart(fig_pie, use_container_width=True)
                            with st.expander("📋 View Detailed Results"):
                                st.dataframe(results_df, use_container_width=True)
                            st.markdown("### 📥 Download Results")
                            csv = results_df.to_csv(index=False)
                            st.download_button(
                                label="Download Predictions as CSV",
                                data=csv,
                                file_name="fraud_predictions.csv",
                                mime="text/csv"
                            )
                        except Exception as e:
                            st.error(f"Batch prediction error: {e}")



def analytics_page():
    """Analytics page (admin only)"""
    st.title("📈 Fraud Detection Analytics")
    st.markdown("Comprehensive analytics and model performance metrics")
    
    st.info("📊 Analytics dashboard...")
    
    # Placeholder metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Transactions", "1,296,675", "+1.2%")
    with col2:
        st.metric("Fraud Detected", "7,506", "+5.4%")
    with col3:
        st.metric("Detection Rate", "99.28%", "+0.3%")
    with col4:
        st.metric("False Positives", "1,686", "-2.1%")

        # Model Comparison
    st.markdown("<div class='subheader'>Model Performance Comparison</div>", unsafe_allow_html=True)

    model_data = {
        'Model': ['Logistic Regression', 'Decision Tree', 'Random Forest', 'XGBoost','TunedXGBoost'],
        'Accuracy': [94.27, 99.01, 99.28, 84.53, 98.48],
        'Precision': [7.35, 35.92, 44.12, 3.57, 27.08],
        'Recall': [76.55, 90.34, 88.67, 99.00, 95.94],
        'F1-Score': [13.41, 51.40, 58.92, 6.90, 42.23],
        'ROC-AUC': [86.32, 95.62, 99.14, 99.29, 99.43]
    }

    df_models = pd.DataFrame(model_data)

    col1, col2 = st.columns(2)

    # First row: Accuracy and ROC-AUC
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(df_models, x='Model', y='Accuracy', 
                    title='Accuracy Comparison', 
                    color='Accuracy',
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(df_models, x='Model', y='ROC-AUC',
                    title='ROC-AUC Score Comparison',
                    color='ROC-AUC',
                    color_continuous_scale='Plasma')
        st.plotly_chart(fig, use_container_width=True)

    # Second row: Precision and Recall
    col3, col4 = st.columns(2)
    with col3:
        fig = px.bar(df_models, x='Model', y='Precision',
                    title='Precision Comparison',
                    color='Precision',
                    color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = px.bar(df_models, x='Model', y='Recall',
                    title='Recall Comparison',
                    color='Recall',
                    color_continuous_scale='Greens')
        st.plotly_chart(fig, use_container_width=True)

    # Third row: F1-Score (full width)
    st.markdown("### F1-Score Comparison")
    fig = px.bar(df_models, x='Model', y='F1-Score',
                color='F1-Score',
                title='F1-Score Comparison',
                color_continuous_scale='Oranges')
    st.plotly_chart(fig, use_container_width=True)
    

def authorizer_panel():
    """Admin/Authorizer Panel with User Management, System Stats, and Settings."""

    if st.session_state.user_role != "admin":
        st.error("⛔ Access Denied: Authorizer privileges required")
        st.stop()
    
    st.markdown("<div class='subheader'>⚙️ Authorizer Control Panel</div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👥 User Management", "📊 System Stats", "🔧 Settings"])
    
    # ---------- User Management Tab ----------
    with tab1:
        st.markdown("### Registered Users")
        all_users = []
        for username, data in st.session_state.USER_DATABASE["users"].items():
            all_users.append({
                "Username": username,
                "Name": data["name"],
                "Role": data["role"],
                "Type": "User"
            })
        for username, data in st.session_state.USER_DATABASE["admins"].items():
            all_users.append({
                "Username": username,
                "Name": data["name"],
                "Role": data["role"],
                "Type": "Authorizer"
            })
        users_df = pd.DataFrame(all_users)
        st.dataframe(users_df, use_container_width=True)
        st.markdown("---")
        st.markdown("### Add New User")
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username", key="add_user_username")
                new_password = st.text_input("Password", type="password", key="add_user_password")
            with col2:
                new_name = st.text_input("Full Name", key="add_user_name")
                new_role = st.selectbox("Role", ["user", "admin"], key="add_user_role")
            if st.form_submit_button("➕ Add User", type="primary"):
                if new_role == "user":
                    if new_username not in st.session_state.USER_DATABASE["users"]:
                        st.session_state.USER_DATABASE["users"][new_username] = {
                            "password": hash_password(new_password),
                            "name": new_name,
                            "role": "user"
                        }
                        st.success(f"✅ User '{new_username}' added successfully!")
                    else:
                        st.error("❌ Username already exists!")
                else:
                    if new_username not in st.session_state.USER_DATABASE["admins"]:
                        st.session_state.USER_DATABASE["admins"][new_username] = {
                            "password": hash_password(new_password),
                            "name": new_name,
                            "role": "admin"
                        }
                        st.success(f"✅ Authorizer '{new_username}' added successfully!")
                    else:
                        st.error("❌ Username already exists!")
    
    # ---------- System Stats Tab ----------
    with tab2:
        st.markdown("### System Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", len(st.session_state.USER_DATABASE["users"]))
        with col2:
            st.metric("Total Authorizers", len(st.session_state.USER_DATABASE["admins"]))
        with col3:
            st.metric("Active Sessions", 1)
        with col4:
            st.metric("System Uptime", "99.9%")
        st.markdown("---")
        st.markdown("### Recent Activity Log")
        activity_data = {
            "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 5,
            "User": [st.session_state.username, "user1", "user2", st.session_state.username, "user1"],
            "Action": ["Login", "Prediction", "Batch Upload", "View Dashboard", "Logout"],
            "Status": ["Success", "Success", "Success", "Success", "Success"]
        }
        activity_df = pd.DataFrame(activity_data)
        st.dataframe(activity_df, use_container_width=True)
    
    # ---------- System Settings Tab ----------
    with tab3:
        st.markdown("### System Configuration")
        st.checkbox("Enable User Registration", value=False)
        st.checkbox("Require Email Verification", value=True)
        st.checkbox("Enable Two-Factor Authentication", value=False)
        st.selectbox("Session Timeout (minutes)", [15, 30, 60, 120])
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Settings", use_container_width=True, type="primary"):
                st.success("✅ Settings saved successfully!")
        with col2:
            if st.button("🔄 Reset to Default", use_container_width=True):
                st.info("Settings reset to default values")



if __name__ == "__main__":
    st.set_page_config(
        page_title="Fraud Detection System",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    main()