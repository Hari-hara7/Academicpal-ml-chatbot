from flask import Flask, request, render_template, jsonify
import pickle
from spellchecker import SpellChecker
import textdistance
import logging
import pandas as pd
import os
import re
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Define file paths - update these to match your directory structure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
KEYWORDS_PATH = os.path.join(BASE_DIR, "keywords.pkl")
DATASET_PATH = os.path.join(BASE_DIR, "Academicpal chatbot1styear - Sheet1.csv")

# Load the model, vectorizer, and keywords
def load_resources():
    try:
        # Load vectorizer
        with open(VECTORIZER_PATH, "rb") as vectorizer_file:
            vectorizer = pickle.load(vectorizer_file)
            logger.info("Vectorizer loaded successfully")
            
        # Load model
        with open(MODEL_PATH, "rb") as model_file:
            model = pickle.load(model_file)
            logger.info("Model loaded successfully")
            
        # Load keywords
        with open(KEYWORDS_PATH, "rb") as keywords_file:
            keywords = pickle.load(keywords_file)
            logger.info("Keywords loaded successfully")
            
        # Load dataset
        data = pd.read_csv(DATASET_PATH)
        logger.info("Dataset loaded successfully")
        
        return vectorizer, model, keywords, data
    except Exception as e:
        logger.error(f"Error loading resources: {e}")
        return None, None, None, None

# Load all resources
vectorizer, model, keywords, data = load_resources()

# Extract unique cycles and subjects for better query processing
def extract_metadata():
    try:
        if data is not None:
            cycles = data['Cycle'].unique().tolist()
            subjects = data['Subject'].unique().tolist()
            return cycles, subjects
        return [], []
    except Exception as e:
        logger.error(f"Error extracting metadata: {e}")
        return [], []

cycles, subjects = extract_metadata()

# Identify cycle and subject in query
def extract_query_elements(query, cycles, subjects):
    query_lower = query.lower()
    
    # Extract cycle
    extracted_cycle = None
    for cycle in cycles:
        if cycle.lower() in query_lower:
            extracted_cycle = cycle
            break
    
    # Extract subject
    extracted_subject = None
    for subject in subjects:
        if subject.lower() in query_lower:
            extracted_subject = subject
            break
    
    return extracted_cycle, extracted_subject

# Spell correction function - Fixed to handle array issues
def correct_spelling(query, keywords):
    try:
        spell = SpellChecker()
        # Add domain-specific terms to the spell checker
        spell.word_frequency.load_words(keywords)
        words = query.lower().split()
        corrected_words = []
        
        for word in words:
            if word in spell:
                corrected_words.append(word)
            else:
                # Use a safer approach to find closest match
                min_distance = float('inf')
                closest_word = word  # Default to original word
                
                for keyword in keywords:
                    try:
                        # Calculate Levenshtein distance safely
                        distance = textdistance.levenshtein.distance(word, keyword)
                        
                        # Handle case where distance might be an array
                        if isinstance(distance, (list, np.ndarray)):
                            distance = float(distance[0]) if len(distance) > 0 else float('inf')
                        
                        # Update closest word if we found a better match
                        if distance < min_distance:
                            min_distance = distance
                            closest_word = keyword
                    except Exception as e:
                        logger.error(f"Error calculating distance between '{word}' and '{keyword}': {e}")
                        continue
                
                corrected_words.append(closest_word)
                
        corrected_query = " ".join(corrected_words)
        logger.info(f"Original query: {query}")
        logger.info(f"Corrected query: {corrected_query}")
        return corrected_query
    except Exception as e:
        logger.error(f"Error in spell correction: {e}")
        return query  # Return original query if correction fails

# Reformat query to match training data format
def reformat_query(query, cycles, subjects):
    # Try to extract cycle and subject from query
    extracted_cycle, extracted_subject = extract_query_elements(query, cycles, subjects)
    
    # If both were found, reformat query to match training data format
    if extracted_cycle and extracted_subject:
        reformatted = f"{extracted_cycle} {extracted_subject} {query}"
        logger.info(f"Reformatted query: {reformatted}")
        return reformatted
    
    # If cycle or subject not found, use original query
    return query

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# API route for predictions
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if all resources are loaded
        if None in (vectorizer, model, keywords, data):
            logger.error("Required resources not loaded")
            return jsonify({'error': 'Server resources not loaded properly'}), 500
            
        # Get query from request
        query = request.form.get('query')
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return jsonify({'error': 'Please provide a query'}), 400
        
        # Reformat query to match training data format
        reformatted_query = reformat_query(query, cycles, subjects)
            
        # Correct spelling
        corrected_query = correct_spelling(reformatted_query, keywords)
        
        # Transform the query using the vectorizer
        query_vector = vectorizer.transform([corrected_query])
        
        # Predict the notes link
        predicted_link = model.predict(query_vector)[0]
        logger.info(f"Predicted link: {predicted_link}")
        
        # Find the matching row from the dataset
        matching_rows = data[data['Notes Link'] == predicted_link]
        
        # If no direct match, try a more flexible approach
        if matching_rows.empty:
            # Try to find a match based on extracted cycle and subject
            extracted_cycle, extracted_subject = extract_query_elements(query, cycles, subjects)
            filter_conditions = []
            
            if extracted_cycle:
                filter_conditions.append(data['Cycle'] == extracted_cycle)
            
            if extracted_subject:
                filter_conditions.append(data['Subject'] == extracted_subject)
            
            if filter_conditions:
                # Combine conditions with AND
                combined_filter = filter_conditions[0]
                for condition in filter_conditions[1:]:
                    combined_filter = combined_filter & condition
                
                matching_rows = data[combined_filter]
        
        if matching_rows.empty:
            logger.warning(f"No matching notes found for: {query}")
            return jsonify({
                'query': query,
                'corrected_query': corrected_query,
                'error': 'No matching notes found'
            }), 404
            
        # Get the first matching row
        matched_row = matching_rows.iloc[0]
        
        # Prepare response data
        response_data = {
            'query': query,
            'corrected_query': corrected_query,
            'subject': matched_row['Subject'],
            'cycle': matched_row['Cycle'],
            'notes_link': matched_row['Notes Link'],
            'keywords': matched_row['Keywords']
        }
            
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({'error': f'An error occurred while processing your request: {str(e)}'}), 500

# Add a health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    if None in (vectorizer, model, keywords, data):
        status = "Some resources failed to load"
        status_code = 500
    else:
        status = "All resources loaded successfully"
        status_code = 200
        
    return jsonify({
        'status': status,
        'vectorizer': vectorizer is not None,
        'model': model is not None,
        'keywords': keywords is not None,
        'dataset': data is not None,
        'cycles': cycles,
        'subjects': subjects
    }), status_code

if __name__ == '__main__':
    app.run(debug=True)