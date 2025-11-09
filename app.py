
# import matplotlib
# matplotlib.use('Agg')

# from flask import Flask, request, jsonify, render_template
# import joblib
# import tensorflow as tf
# load_model = tf.keras.models.load_model

# import numpy as np
# import pandas as pd
# import os
# import seaborn as sns
# import matplotlib.pyplot as plt
# import json
# from sklearn.preprocessing import StandardScaler

# from utils.process import preprocess_data, get_customer_result, get_top_n_churn

# # Initialize app
# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'uploads'

# # Load models
# segmentation_model = joblib.load('kmeans_model.joblib')
# model = load_model('model/churn_ann_model.h5')

# # Global DF for churn
# global_df = pd.DataFrame()

# ### ROUTES ###

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/about')
# def about():
#     return render_template('about.html')

# @app.route('/CustomerSegmentation')
# def customer_segmentation():
#     return render_template('CustomerSegmentation.html')

# @app.route('/CustomerPrediction')
# def customer_prediction():
#     return render_template('CustomerPrediction.html')

# @app.route('/result')
# def result():
#     return render_template('result.html')


# #########################################
# # SEGMENTATION: Upload + Cluster + Plots
# #########################################

# def load_and_clean_data(file_path):
#     retail = pd.read_csv(file_path, sep=",", encoding="ISO-8859-1", header=0)
#     retail['Amount'] = retail['Quantity'] * retail['UnitPrice']
#     retail['InvoiceDate'] = pd.to_datetime(retail['InvoiceDate'], errors='coerce')
#     retail = retail.dropna(subset=['InvoiceDate'])

#     rfm_m = retail.groupby('CustomerID')['Amount'].sum().reset_index()
#     rfm_f = retail.groupby('CustomerID')['InvoiceNo'].count().reset_index()
#     rfm_f.columns = ['CustomerID', 'Frequency']

#     max_date = retail['InvoiceDate'].max()
#     retail['Diff'] = max_date - retail['InvoiceDate']
#     rfm_p = retail.groupby('CustomerID')['Diff'].min().reset_index()
#     rfm_p['Diff'] = rfm_p['Diff'].dt.days

#     rfm = pd.merge(rfm_m, rfm_f, on="CustomerID", how="inner")
#     rfm = pd.merge(rfm, rfm_p, on="CustomerID", how="inner")
#     rfm.columns = ['CustomerID', 'Amount', 'Frequency', 'Recency']

#     Q1 = rfm.quantile(0.05)
#     Q3 = rfm.quantile(0.95)
#     IQR = Q3 - Q1

#     rfm = rfm[(rfm.Amount >= Q1['Amount'] - 1.5 * IQR['Amount']) & (rfm.Amount <= Q3['Amount'] + 1.5 * IQR['Amount'])]
#     rfm = rfm[(rfm.Recency >= Q1['Recency'] - 1.5 * IQR['Recency']) & (rfm.Recency <= Q3['Recency'] + 1.5 * IQR['Recency'])]
#     rfm = rfm[(rfm.Frequency >= Q1['Frequency'] - 1.5 * IQR['Frequency']) & (rfm.Frequency <= Q3['Frequency'] + 1.5 * IQR['Frequency'])]

#     return rfm

# @app.route('/predict', methods=['POST'])
# def predict():
#     file = request.files['file']
#     file_path = os.path.join(os.getcwd(), file.filename)
#     file.save(file_path)

#     rfm_original = load_and_clean_data(file_path)
#     scaler = StandardScaler()
#     rfm_scaled = scaler.fit_transform(rfm_original[['Amount', 'Frequency', 'Recency']])
#     rfm_original['Cluster_Id'] = segmentation_model.predict(rfm_scaled)

#     # Save strip and pie charts
#     cluster_labels = rfm_original['Cluster_Id'].unique()
#     cluster_colors = sns.color_palette("Set3", len(cluster_labels))

#     def save_stripplot(column, path):
#         sns.stripplot(x='Cluster_Id', y=column, data=rfm_original, hue='Cluster_Id')
#         plt.savefig(path)
#         plt.clf()

#     def save_pie(column, path, agg_func='sum'):
#         if agg_func == 'sum':
#             data = rfm_original.groupby('Cluster_Id')[column].sum()
#         else:
#             data = rfm_original.groupby('Cluster_Id')[column].mean()
#         plt.pie(data, labels=[f'Cluster {i}' for i in data.index], autopct='%1.1f%%', colors=cluster_colors)
#         plt.title(f'{column} Distribution by Cluster')
#         plt.savefig(path)
#         plt.clf()

#     paths = {
#         'amount_img': 'static/ClusterId_Amount.png',
#         'freq_img': 'static/ClusterId_Frequency.png',
#         'recency_img': 'static/ClusterId_Recency.png',
#         'amount_pie': 'static/Amount_Pie_Chart.png',
#         'freq_pie': 'static/Frequency_Pie_Chart.png',
#         'recency_pie': 'static/Recency_Pie_Chart.png'
#     }

#     save_stripplot('Amount', paths['amount_img'])
#     save_stripplot('Frequency', paths['freq_img'])
#     save_stripplot('Recency', paths['recency_img'])
#     save_pie('Amount', paths['amount_pie'])
#     save_pie('Frequency', paths['freq_pie'])
#     save_pie('Recency', paths['recency_pie'], agg_func='mean')

#     return json.dumps(paths)


# #########################################
# # CHURN PREDICTION ROUTES
# #########################################

# @app.route('/upload_churn', methods=['POST'])
# def upload_churn_file():
#     global global_df

#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part in request'}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No file selected'}), 400

#     filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#     file.save(filepath)

#     churn_model = tf.keras.models.load_model("model/churn_ann_model.h5")

#     df = pd.read_csv(filepath)
#     df = preprocess_data(df)
#     df['churn_probability'] = churn_model.predict(df[['Recency', 'Frequency', 'Monetary']]).flatten()
#     df['churn'] = (df['churn_probability'] > 0.5).astype(int)
#     df['rank'] = df['churn_probability'].rank(method='first', ascending=False).astype(int)

#     global_df = df.copy()
#     return jsonify({'message': 'Churn predictions processed successfully'})


# @app.route('/customer/<customer_id>', methods=['GET'])
# def get_customer(customer_id):
#     if global_df.empty:
#         return jsonify({'error': 'No churn data uploaded'}), 400

#     result = get_customer_result(global_df, customer_id)
#     if result is None:
#         return jsonify({'error': 'Customer ID not found'}), 404

#     return jsonify(result)


# @app.route('/top_churn/<int:n>', methods=['GET'])
# def top_churn(n):
#     if global_df.empty:
#         return jsonify({'error': 'No churn data uploaded'}), 400

#     result = get_top_n_churn(global_df, n)
#     return jsonify(result)


# if __name__ == '__main__':
#     app.run(debug=True, use_reloader=False)






# ye login register wala hai

# import matplotlib
# matplotlib.use('Agg')

# from flask import Flask, request, jsonify, render_template, redirect, session, flash
# import joblib
# import tensorflow as tf
# import numpy as np
# import pandas as pd
# import os
# import seaborn as sns
# import matplotlib.pyplot as plt
# import json
# from sklearn.preprocessing import StandardScaler
# from flask_pymongo import PyMongo

# from utils.process import preprocess_data, get_customer_result, get_top_n_churn

# # Initialize Flask app
# app = Flask(__name__)
# app.secret_key = 'your_secret_key'
# app.config['UPLOAD_FOLDER'] = 'uploads'
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/customerApp'
# mongo = PyMongo(app)

# # Load models
# segmentation_model = joblib.load('kmeans_model.joblib')
# model = tf.keras.models.load_model('model/churn_ann_model.h5')

# global_df = pd.DataFrame()

# #########################################
# # AUTH: Register & Login (Index page)
# #########################################

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         action = request.form['action']
#         email = request.form['email']
#         password = request.form['password']
#         users = mongo.db.users

#         if action == 'register':
#             if users.find_one({'email': email}):
#                 flash('Email already exists.', 'danger')
#             else:
#                 users.insert_one({'email': email, 'password': password})
#                 flash('Registration successful. Please log in.', 'success')

#         elif action == 'login':
#             user = users.find_one({'email': email, 'password': password})
#             if user:
#                 session['email'] = email
#                 flash('Login successful.', 'success')
#                 return redirect('/CustomerSegmentation')
#             else:
#                 flash('Invalid credentials.', 'danger')

#     return render_template('index.html', email=session.get('email'))

# @app.route('/logout')
# def logout():
#     session.clear()
#     flash('Logged out successfully.', 'info')
#     return redirect('/')

# #########################################
# # PAGES: About, Segmentation, Prediction
# #########################################

# @app.route('/about')
# def about():
#     return render_template('about.html')

# @app.route('/CustomerSegmentation')
# def customer_segmentation():
#     if 'email' not in session:
#         flash("You must be logged in to view this page.", "warning")
#         return redirect('/')
#     return render_template('CustomerSegmentation.html')

# @app.route('/CustomerPrediction')
# def customer_prediction():
#     if 'email' not in session:
#         flash("You must be logged in to view this page.", "warning")
#         return redirect('/')
#     return render_template('CustomerPrediction.html')

# @app.route('/result')
# def result():
#     if 'email' not in session:
#         flash("You must be logged in to view this page.", "warning")
#         return redirect('/')
#     return render_template('result.html')

# #########################################
# # SEGMENTATION: Upload + Cluster + Plots
# #########################################

# def load_and_clean_data(file_path):
#     # Load dataset
#     retail = pd.read_csv(file_path, sep=",", encoding="ISO-8859-1", header=0)

#     # Calculate Amount
#     retail['Amount'] = retail['Quantity'] * retail['UnitPrice']

#     # Parse dates
#     retail['InvoiceDate'] = pd.to_datetime(retail['InvoiceDate'], errors='coerce')
#     retail.dropna(subset=['InvoiceDate'], inplace=True)

#     # Aggregate RFM metrics
#     rfm_m = retail.groupby('CustomerID')['Amount'].sum().reset_index()
#     rfm_f = retail.groupby('CustomerID')['InvoiceNo'].nunique().reset_index()
#     rfm_f.columns = ['CustomerID', 'Frequency']

#     max_date = retail['InvoiceDate'].max()
#     retail['Diff'] = (max_date - retail['InvoiceDate']).dt.days
#     rfm_r = retail.groupby('CustomerID')['Diff'].min().reset_index()
#     rfm_r.columns = ['CustomerID', 'Recency']

#     # Merge RFM components
#     rfm = pd.merge(rfm_m, rfm_f, on='CustomerID')
#     rfm = pd.merge(rfm, rfm_r, on='CustomerID')

#     # Remove outliers using IQR
#     Q1 = rfm.quantile(0.05)
#     Q3 = rfm.quantile(0.95)
#     IQR = Q3 - Q1

#     rfm = rfm[
#         (rfm['Amount'] >= Q1['Amount'] - 1.5 * IQR['Amount']) & (rfm['Amount'] <= Q3['Amount'] + 1.5 * IQR['Amount']) &
#         (rfm['Frequency'] >= Q1['Frequency'] - 1.5 * IQR['Frequency']) & (rfm['Frequency'] <= Q3['Frequency'] + 1.5 * IQR['Frequency']) &
#         (rfm['Recency'] >= Q1['Recency'] - 1.5 * IQR['Recency']) & (rfm['Recency'] <= Q3['Recency'] + 1.5 * IQR['Recency'])
#     ]

#     return rfm


# @app.route('/predict', methods=['POST'])
# def predict():
#     # User authentication check
#     if 'email' not in session:
#         flash("Login required.", "danger")
#         return redirect('/')

#     # File upload handling
#     file = request.files['file']
#     file_path = os.path.join(os.getcwd(), file.filename)
#     file.save(file_path)

#     # Load and preprocess data
#     rfm = load_and_clean_data(file_path)
#     scaler = StandardScaler()
#     rfm_scaled = scaler.fit_transform(rfm[['Amount', 'Frequency', 'Recency']])
#     rfm['Cluster_Id'] = segmentation_model.predict(rfm_scaled)

#     # Get unique clusters
#     cluster_labels = sorted(rfm['Cluster_Id'].unique())
#     cluster_colors = sns.color_palette("Set3", len(cluster_labels))

#     # Plot helper functions
#     def save_stripplot(column, path):
#         sns.stripplot(x='Cluster_Id', y=column, data=rfm, hue='Cluster_Id', palette=cluster_colors, dodge=True)
#         plt.title(f'{column} by Cluster')
#         plt.legend().remove()
#         plt.tight_layout()
#         plt.savefig(path)
#         plt.clf()

#     def save_pie(column, path, agg_func='sum'):
#         data = rfm.groupby('Cluster_Id')[column].sum() if agg_func == 'sum' else rfm.groupby('Cluster_Id')[column].mean()
#         plt.pie(data, labels=[f'Cluster {i}' for i in data.index], autopct='%1.1f%%', colors=cluster_colors)
#         plt.title(f'{column} Distribution by Cluster')
#         plt.tight_layout()
#         plt.savefig(path)
#         plt.clf()

#     # Paths to images
#     paths = {
#         'amount_img': 'static/ClusterId_Amount.png',
#         'freq_img': 'static/ClusterId_Frequency.png',
#         'recency_img': 'static/ClusterId_Recency.png',
#         'amount_pie': 'static/Amount_Pie_Chart.png',
#         'freq_pie': 'static/Frequency_Pie_Chart.png',
#         'recency_pie': 'static/Recency_Pie_Chart.png'
#     }

#     # Generate and save plots
#     save_stripplot('Amount', paths['amount_img'])
#     save_stripplot('Frequency', paths['freq_img'])
#     save_stripplot('Recency', paths['recency_img'])
#     save_pie('Amount', paths['amount_pie'])
#     save_pie('Frequency', paths['freq_pie'])
#     save_pie('Recency', paths['recency_pie'], agg_func='mean')

#     return json.dumps(paths)
# #########################################
# # CHURN PREDICTION ROUTES
# #########################################

# @app.route('/upload_churn', methods=['POST'])
# def upload_churn_file():
#     if 'email' not in session:
#         return jsonify({'error': 'Authentication required'}), 401

#     global global_df

#     file = request.files.get('file')
#     if not file or file.filename == '':
#         return jsonify({'error': 'No file uploaded'}), 400

#     filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#     file.save(filepath)

#     churn_model = tf.keras.models.load_model("model/churn_ann_model.h5")

#     df = pd.read_csv(filepath)
#     df = preprocess_data(df)
#     df['churn_probability'] = churn_model.predict(df[['Recency', 'Frequency', 'Monetary']]).flatten()
#     df['churn'] = (df['churn_probability'] > 0.5).astype(int)
#     df['rank'] = df['churn_probability'].rank(method='first', ascending=False).astype(int)

#     global_df = df.copy()
#     return jsonify({'message': 'Churn predictions processed successfully'})

# @app.route('/customer/<customer_id>', methods=['GET'])
# def get_customer(customer_id):
#     if 'email' not in session:
#         return jsonify({'error': 'Login required'}), 401

#     if global_df.empty:
#         return jsonify({'error': 'No churn data uploaded'}), 400

#     result = get_customer_result(global_df, customer_id)
#     if result is None:
#         return jsonify({'error': 'Customer ID not found'}), 404

#     return jsonify(result)

# @app.route('/top_churn/<int:n>', methods=['GET'])
# def top_churn(n):
#     if 'email' not in session:
#         return jsonify({'error': 'Login required'}), 401

#     if global_df.empty:
#         return jsonify({'error': 'No churn data uploaded'}), 400

#     result = get_top_n_churn(global_df, n)
#     return jsonify(result)

# #########################################
# # Run the app
# #########################################

# if __name__ == '__main__':
#     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#     app.run(debug=True, use_reloader=False)











import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, jsonify, render_template, redirect, session, flash
import joblib
import tensorflow as tf
import numpy as np
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import json
import base64
from io import BytesIO
from sklearn.preprocessing import StandardScaler
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from utils.process import preprocess_data, get_customer_result, get_top_n_churn

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/customerApp'
mongo = PyMongo(app)

segmentation_model = joblib.load('kmeans_model.joblib')
model = tf.keras.models.load_model('model/churn_ann_model.h5')

# global_df = pd.DataFrame()

# ---------- [Unchanged: Login/Register/Logout Routes] ----------

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form['action']
        email = request.form['email']
        password = request.form['password']
        users = mongo.db.users

        if action == 'register':
            if users.find_one({'email': email}):
                flash('Email already exists.', 'danger')
            else:
                users.insert_one({'email': email, 'password': password})
                flash('Registration successful. Please log in.', 'success')

        elif action == 'login':
            user = users.find_one({'email': email, 'password': password})
            if user:
                session['email'] = email
                session['user_id'] = str(user['_id'])
                flash('Login successful.', 'success')
                return redirect('/CustomerSegmentation')
            else:
                flash('Invalid credentials.', 'danger')

    return render_template('index.html', email=session.get('email'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/CustomerSegmentation')
def customer_segmentation():
    if 'email' not in session:
        flash("You must be logged in to view this page.", "warning")
        return redirect('/')
    return render_template('CustomerSegmentation.html')

@app.route('/CustomerPrediction')
def customer_prediction():
    if 'email' not in session:
        flash("You must be logged in to view this page.", "warning")
        return redirect('/')
    return render_template('CustomerPrediction.html')

@app.route('/result')
def result():
    if 'email' not in session:
        flash("You must be logged in to view this page.", "warning")
        return redirect('/')

    segmentation = mongo.db.segmentations.find_one({'user_id': session['user_id']}, sort=[('_id', -1)])
    if segmentation:
        return render_template('result.html', images=segmentation['images'])
    else:
        flash("No segmentation data found.", "warning")
        return redirect('/CustomerSegmentation')

def load_and_clean_data(file_path):
    retail = pd.read_csv(file_path, sep=",", encoding="ISO-8859-1", header=0)
    retail['Amount'] = retail['Quantity'] * retail['UnitPrice']
    retail['InvoiceDate'] = pd.to_datetime(retail['InvoiceDate'], errors='coerce')
    retail.dropna(subset=['InvoiceDate'], inplace=True)
    rfm_m = retail.groupby('CustomerID')['Amount'].sum().reset_index()
    rfm_f = retail.groupby('CustomerID')['InvoiceNo'].nunique().reset_index()
    rfm_f.columns = ['CustomerID', 'Frequency']
    max_date = retail['InvoiceDate'].max()
    retail['Diff'] = (max_date - retail['InvoiceDate']).dt.days
    rfm_r = retail.groupby('CustomerID')['Diff'].min().reset_index()
    rfm_r.columns = ['CustomerID', 'Recency']
    rfm = pd.merge(rfm_m, rfm_f, on='CustomerID')
    rfm = pd.merge(rfm, rfm_r, on='CustomerID')
    Q1 = rfm.quantile(0.05)
    Q3 = rfm.quantile(0.95)
    IQR = Q3 - Q1
    rfm = rfm[
        (rfm['Amount'] >= Q1['Amount'] - 1.5 * IQR['Amount']) & (rfm['Amount'] <= Q3['Amount'] + 1.5 * IQR['Amount']) &
        (rfm['Frequency'] >= Q1['Frequency'] - 1.5 * IQR['Frequency']) & (rfm['Frequency'] <= Q3['Frequency'] + 1.5 * IQR['Frequency']) &
        (rfm['Recency'] >= Q1['Recency'] - 1.5 * IQR['Recency']) & (rfm['Recency'] <= Q3['Recency'] + 1.5 * IQR['Recency'])
    ]
    return rfm

@app.route('/predict', methods=['POST'])
def predict():
    if 'email' not in session:
        flash("Login required.", "danger")
        return redirect('/')

    file = request.files['file']
    file_path = os.path.join(os.getcwd(), file.filename)
    file.save(file_path)

    rfm = load_and_clean_data(file_path)
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm[['Amount', 'Frequency', 'Recency']])
    rfm['Cluster_Id'] = segmentation_model.predict(rfm_scaled)

    cluster_labels = sorted(rfm['Cluster_Id'].unique())
    cluster_colors = sns.color_palette("Set3", len(cluster_labels))

    def fig_to_base64(fig):
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    def strip_plot(column):
        fig, ax = plt.subplots()
        sns.stripplot(x='Cluster_Id', y=column, data=rfm, hue='Cluster_Id', palette=cluster_colors, dodge=True, ax=ax)
        ax.set_title(f'{column} by Cluster')
        ax.legend_.remove()
        plt.tight_layout()
        img_str = fig_to_base64(fig)
        plt.close(fig)
        return img_str

    def pie_plot(column, agg_func='sum'):
        fig, ax = plt.subplots()
        data = rfm.groupby('Cluster_Id')[column].sum() if agg_func == 'sum' else rfm.groupby('Cluster_Id')[column].mean()
        ax.pie(data, labels=[f'Cluster {i}' for i in data.index], autopct='%1.1f%%', colors=cluster_colors)
        ax.set_title(f'{column} Distribution by Cluster')
        plt.tight_layout()
        img_str = fig_to_base64(fig)
        plt.close(fig)
        return img_str

    # Encode all plots to base64
    images = {
        'amount_img': "data:image/png;base64," + strip_plot('Amount'),
        'freq_img': "data:image/png;base64," + strip_plot('Frequency'),
        'recency_img': "data:image/png;base64," + strip_plot('Recency'),
        'amount_pie': "data:image/png;base64," + pie_plot('Amount'),
        'freq_pie': "data:image/png;base64," + pie_plot('Frequency'),
        'recency_pie': "data:image/png;base64," + pie_plot('Recency', agg_func='mean')

    }

    # Save to MongoDB
    mongo.db.segmentations.insert_one({
        'user_id': session['user_id'],
        'email': session['email'],
        'images': images
    })

    flash("Segmentation completed and saved!", "success")
    return jsonify(images)

# ----------------- Churn Upload Route ----------------
@app.route('/upload_churn', methods=['POST'])
def upload_churn_file():
    if 'email' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file uploaded'}), 400

    # Save uploaded file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(filepath)

    # Preprocess
    df = pd.read_csv(filepath)
    df = preprocess_data(df)

    # Predict
    df['churn_probability'] = model.predict(df[['Recency', 'Frequency', 'Monetary']]).flatten()
    df['churn'] = (df['churn_probability'] > 0.5).astype(int)
    df['rank'] = df['churn_probability'].rank(method='first', ascending=False).astype(int)

    # Save to MongoDB
    mongo.db.predictions.insert_one({
        'email': session['email'],
        'timestamp': datetime.now(),
        'data': df.to_dict(orient='records')
    })

    return jsonify({'message': 'Churn predictions processed successfully'})


# ---------------- Get Specific Customer ----------------
@app.route('/customer/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    if 'email' not in session:
        return jsonify({'error': 'Login required'}), 401

    entry = mongo.db.predictions.find_one(
        {'email': session['email']},
        sort=[('timestamp', -1)]
    )

    if not entry:
        return jsonify({'error': 'No churn data uploaded'}), 400

    df = pd.DataFrame(entry['data'])
    result = get_customer_result(df, customer_id)

    if result is None:
        return jsonify({'error': 'Customer ID not found'}), 404

    return jsonify(result)


# ---------------- Get Top N Customers ----------------
@app.route('/top_churn/<int:n>', methods=['GET'])
def top_churn(n):
    if 'email' not in session:
        return jsonify({'error': 'Login required'}), 401

    entry = mongo.db.predictions.find_one(
        {'email': session['email']},
        sort=[('timestamp', -1)]
    )

    if not entry:
        return jsonify({'error': 'No churn data uploaded'}), 400

    df = pd.DataFrame(entry['data'])
    result = get_top_n_churn(df, n)
    return jsonify(result)


# this is api for result page
@app.route('/check_segmentation')
def check_segmentation():
    """Check if segmentation data exists for the current user"""
    if 'email' not in session:
        return jsonify({'exists': False})
    
    segmentation = mongo.db.segmentations.find_one(
        {'user_id': session['user_id']}, 
        sort=[('_id', -1)]
    )
    
    if segmentation:
        return jsonify({'exists': True, 'images': segmentation['images']})
    else:
        return jsonify({'exists': False})

@app.route('/check_prediction')
def check_prediction():
    """Check if prediction data exists for the current user"""
    if 'email' not in session:
        return jsonify({'exists': False})
    
    prediction = mongo.db.predictions.find_one(
        {'email': session['email']},
        sort=[('timestamp', -1)]
    )
    
    if prediction:
        df = pd.DataFrame(prediction['data'])
        
        # Calculate metrics
        customer_count = len(df)
        churn_count = df['churn'].sum() if 'churn' in df.columns else 0
        churn_rate = round((churn_count / customer_count) * 100, 2) if customer_count > 0 else 0
        
        return jsonify({
            'exists': True,
            'customer_count': customer_count,
            'churn_rate': churn_rate,
            'upload_time': prediction['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        return jsonify({'exists': False})

# ---------------- Run App ----------------
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)




