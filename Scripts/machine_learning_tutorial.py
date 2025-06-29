#!/usr/bin/env python
# coding: utf-8

# # **Welcome to the MRInference machine learning tutorial!**
# by Sandra Vieira
# 
# ---
# This webpage contains a brief step-by-step tutorial on the implementation of a standard supervised machine learning pipeline using Python programming language. Before this tutorial make sure to go through the pre-recorded lectures:  
# 
# *   Introduction to Machine Learning
# *   The Machine Learning Pipeline
# 
# ---
# ##Machine Learning: Methods and Applications to Brain Disorders
# This tutorial and both pre-recorded lectures above are based on the book [Machine Learning: Methods and Applications to Brain Disorders](https://www.amazon.co.uk/Machine-Learning-Methods-Applications-Disorders/dp/0128157399). The pre-recorded lectures are based on chapters 1-3 and this tutorial is a shorter version of Chapter 19. You can access the full tutorial of Chapter 19 [here](https://github.com/MLMH-Lab/How-To-Build-A-Machine-Learning-Model).
# 
# ---  
# ## Aim and structure of the tutorial
# For this tutorial you will use a toy dataset containing the grey matter volume and thickness from different brain regions extracted with FreeSurfer to classify patients with schizophrenia and healthy controls using a Support Vector Machine (SVM). The script and data for the tutorial are stored [here](https://github.com/sandramv/MRInference_ML_Tutorial). The main steps of the tutrial will follow the pipeline presented in the lecture The Machine Learning Pipeline and are shown in the figure below.
# 
# ![workflow](https://raw.githubusercontent.com/sandramv/MRInference_ML_Tutorial/master/Figures/pipeline.png)
# 
# 

# ## Import libraries

# Python language is organised in libraries. Each library contains a set of functions for a specific purpose. For example, numpy is a popular library for manipulating numerical data, while pandas is most commonly used to handle tabular data. There are several libraries for machine learning analysis; in this tutorial we will use scikitlearn. 

# In[ ]:


# SNIPPET 1: import libraries

# Manipulate data
import numpy as np
import pandas as pd

# Plots
import seaborn as sns
import matplotlib.pyplot as plt

# Statistical tests
import scipy.stats as stats

# Machine learning
from sklearn.svm import LinearSVC
import joblib
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold, StratifiedKFold

# Ignore WARNING
import warnings
warnings.filterwarnings('ignore')


# ## Set random seed
# Some steps in our analysis will be subjected to randomness.  We should set the  seed value to a fixed number to guarantee that we get the same results every time we run the code. 

# In[ ]:


# SNIPPET 2: set random seed
random_seed = 1
np.random.seed(random_seed)


# ## 1. Problem formulation
# 
#  In this tutorial, our machine learning problem is: 
# 
# > *Classify patients with schizophrenia and healthy controls using structural MRI data.*
# 
# From this formulation we can derive the main elements of our machine learning problem:
# 
# *   **Features**: Structural MRI data
# *   **Task**: Binary classification
# *   **Target**: Patients with schizophrenia and healthy controls
# 
# 
# 
# ---
# 
# 

# ## 2. Data preparation
# 
# The aim of this step is to perform a series of statistical analyses to get the data ready for the machine learning model. In this tutorial, we will assume the data is ready to be analysed. However, in a real project we would want to pay close attention to several things including class imbalance (N HC vs N SZ), missing data (data imputation?), confounding variables (age, sex?), dimensionality (N features vs N participants).

# ### Load data

# In[ ]:


# SNIPPET 3: load data
dataset_url = 'https://raw.githubusercontent.com/sandramv/ML_tutorial/main/Data/ml_tutorial_data.csv'
dataset_df = pd.read_csv(dataset_url, index_col='ID')


# In[ ]:


# SNIPPET 4: preview data
dataset_df[0:6]


# In[ ]:


# SNIPPET 5: sample size and number of features
print('Number of features = %d' % dataset_df.shape[1])
print('Number of participants = %d' % dataset_df.shape[0])


# In[ ]:


# SNIPPET 6: number of healthy controls (HC=0) and patients (SZ=1)
dataset_df['Diagnosis'].value_counts()


# ### Feature set and target
# 
# Our next step is to retrieve the target and features from the dataset.

# In[ ]:


# SNIPPET 7: get target and input features
targets_df = dataset_df['Diagnosis']

features_names = dataset_df.columns[3:]
features_df = dataset_df[features_names]


# In[ ]:


# SNIPPET 8: see features
features_df


# ## 3. Feature engineering
# 
# 
# 

# ### Feature extraction
# In our example, we want to use neuroanatomical data to classify SZ and HC. This requires the extraction of brain morphometric information from the raw MRI images. This step has already been done, i.e. the csv file already contains these data.
# 

# ## 4. Model training  
# The first thing we need to do at this step is to setup the **cross-validation (CV) scheme**. Then we iterate over each CV fold and train and test the model at each one. The snippets below:  
# * Setup de CV scheme 
# * Change data type of features and target variables   
# * Create structure to hold the results from each CV fold  
# * Iterate over each cv fold (snippet 22) and: 
#   * Split all data into train and test sets  
#   * Normalize data
#   * Define machine learning algorithm
#   * Fit algorithm to the train set
#   * Make predictions in the test set
#   * Compute performance metrics in the test set
# 

# In[ ]:


# SNIPPET 9: setup cross-validation (cv) scheme
n_folds = 10
skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_seed)


# ![alt text](https://raw.githubusercontent.com/sandramv/MRInference_ML_Tutorial/master/Figures/crossvalidation.png)

# In[ ]:


# SNIPPET 10: change data type 
targets = targets_df.values.astype('int')
features = features_df.values.astype('float32')


# In[ ]:


# SNIPPET 11: create structure to hold the results from each cross-validaiton fold
acc_cv = np.zeros((n_folds, 1))
bac_cv = np.zeros((n_folds, 1))
sens_cv = np.zeros((n_folds, 1))
spec_cv = np.zeros((n_folds, 1))


# In[ ]:


# SNIPPET 12: iterate over each cv fold
for i_fold, (train_idx, test_idx) in enumerate(skf.split(features, targets)):

    # SNIPPET 13: split data into train and test sets
    features_train, features_test = features[train_idx], features[test_idx]
    targets_train, targets_test = targets[train_idx], targets[test_idx]

    print('CV iteration: %d' % (i_fold + 1))
    print('Training set size: %d' % len(targets_train))
    print('Test set size: %d' % len(targets_test))

    # --------------------------------------------------------------------------
    # SNIPPET 14: normalize data
    scaler = StandardScaler()

    scaler.fit(features_train)

    features_train_norm = scaler.transform(features_train)
    features_test_norm = scaler.transform(features_test)

    # --------------------------------------------------------------------------
    # SNIPPET 15: define and train the classifier (SVM)
    clf = LinearSVC(loss='hinge')
    clf.fit(features_train_norm, targets_train)

    # --------------------------------------------------------------------------
    # SNIPPET 16: make predictions in the test set
    target_test_predicted = clf.predict(features_test_norm)

    # --------------------------------------------------------------------------
    # SNIPPET 17: compute performance metrics in the test set
    print('Confusion matrix')
    cm = confusion_matrix(targets_test, target_test_predicted)
    print(cm)

    tn, fp, fn, tp = cm.ravel()

    acc_test = accuracy_score(targets_test, target_test_predicted)
    bac_test = balanced_accuracy_score(targets_test, target_test_predicted)
    sens_test = tp / (tp + fn)
    spec_test = tn / (tn + fp)

    print('Accuracy: %.3f ' % acc_test)
    print('Balanced accuracy: %.3f ' % bac_test)
    print('Sensitivity: %.3f ' % sens_test)
    print('Specificity: %.3f ' % spec_test)

    acc_cv[i_fold, :] = acc_test
    bac_cv[i_fold, :] = bac_test
    sens_cv[i_fold, :] = sens_test
    spec_cv[i_fold, :] = spec_test
    print('--------------------------------------------------------------------------')


# ## 5. Model evaluation  
# Once the model training and testing in the CV scheme is finished, we compute the overall performace of the model by taking the mean performance across the CV folds.

# In[ ]:


# SNIPPET 18
print('CV results')
print('Acc: Mean(SD) = %.3f(%.3f)' % (acc_cv.mean(), acc_cv.std()))
print('Bac: Mean(SD) = %.3f(%.3f)' % (bac_cv.mean(), bac_cv.std()))
print('Sens: Mean(SD) = %.3f(%.3f)' % (sens_cv.mean(), sens_cv.std()))
print('Spec: Mean(SD) = %.3f(%.3f)' % (spec_cv.mean(), spec_cv.std()))


# ## 6. Post-hoc analysis
# 
# Once we have our final model, we can run several additional analyses. This tutotial does not include these analysis, but we could look at the following:
# 
# *   Test balanced accuracy, sensitivity and specificity for statistical significance via permutation testing
# *   Identify the features that provided the greatest contribution to the task 

# ## Exercises
# 
# ### Exercise 1
# Review the pipeline above and answer the questions below.  
# 1.1. What are the features, target variable and task? What does features, target variable and task mean?  
# 1.2. Is this a classification or regression problem? Why?  
# 1.3. What cross-validation scheme used? Explain in your own words how it works.  
# 1.4. What machine learning algorithm was used?  
# 1.5. How was the data normalized (hint: google the method used and click on the sklearn website)  
# 1.6. Why should the data be normalized? Why was the train and test data normalized separately?  
# 1.7. What is the value inside the parenthesis for each performance metric and what does it mean in this context?    
# 1.8. What is Snippet 2 doing and why do we need it?  
# 
# ### Exercise 2
# 2.1. What is the difference between accuracy and balanced accuracy? Are they different or the same in this exercise? If they are different, explain why this is the case.  
# 2.2. What does 75% sensitivity mean?  
# 2.3. Run the snippet below and explain what it shows. Would you have any concerns about the results above with this information? If you do, how would you address them?  
# 
# 

# In[ ]:


# SNIPPET 19
sns.countplot(x='Diagnosis', hue='Sex', data=dataset_df, palette=['#839098', '#f7d842'])
plt.legend(['Male', 'Female'])
plt.show()


# 2.4. Can you think of any confounding variables that may be influencing the result?  
