# 🧬 Gene Splice Junction Detector

An advanced DNA splice junction detection application using machine learning to identify exon-intron boundaries in genetic sequences.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Overview

This application uses machine learning to analyze DNA sequences and detect splice junctions - the boundaries between exons (coding regions) and introns (non-coding regions). It's built with Python and Streamlit, providing an intuitive web interface for genetic sequence analysis.

## ✨ Features

- **DNA Sequence Analysis**: Input DNA sequences and get instant splice junction predictions
- **Multiple Junction Types**: Detects donor sites (exon-intron), acceptor sites (intron-exon), and non-junction regions
- **Interactive Visualization**: Visual representation of predictions with confidence scores
- **Batch Processing**: Analyze multiple sequences from CSV files
- **Model Performance Metrics**: View accuracy, precision, recall, and confusion matrix
- **Sequence Statistics**: Get detailed statistics about your DNA sequences
- **Export Results**: Download predictions in CSV format



## 💻 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/ifrahgul/gene-splice-junction.git
cd gene-splice-junction
````
### Dependencies
- streamlit: Web application framework
- scikit-learn: Machine learning models and preprocessing
- pandas: Data manipulation and analysis
- numpy: Numerical computations
- matplotlib/seaborn: Data visualization
- plotly: Interactive plots
- joblib: Model serialization
------
🎯 Usage Guide
Single Sequence Analysis
Enter a DNA sequence in the text input area

Click "Analyze Sequence"

View prediction results and confidence scores

Check visualization of splice sites

Batch Processing
Prepare a CSV file with a 'sequence' column

Upload the file using the file uploader

Click "Process Batch"

Download results as CSV

Example:
DNA Sequencestext
- Donor site (exon-intron):   
AAGGTAAGT
- Acceptor site (intron-exon): 
TTTTCCTAG
- Non-junction:
  ATGCGTACGT
-----
📊 Model Information
The application uses a machine learning model trained on DNA sequences with the following characteristics:

Features: K-mer frequencies, position-specific features

Algorithm: Random Forest Classifier

Classes: Donor site, Acceptor site, Non-junction

Performance: ~95% accuracy on test data
----

🔧 Configuration
Edit config.yaml to customize:

Model parameters

Feature extraction settings

Visualization options

File paths
