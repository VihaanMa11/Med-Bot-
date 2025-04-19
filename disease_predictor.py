import logging
import pandas as pd
import numpy as np
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DiseasePredictor:
    def __init__(self):
        """Initialize the disease predictor."""
        self.data_dir = "data"
        self.symptom_severity = None
        self.symptom_description = None
        self.training_data = None
        self.symptom_encoder = None
        self.all_symptoms = None
        self.disease_descriptions = None
        self.precautions = None
        self.load_data()
        
    def load_data(self):
        """Load necessary datasets for prediction."""
        try:
            # Load symptom severity data
            self.symptom_severity = pd.read_csv(f"attached_assets/Symptom-severity.csv")
            
            # Load training data
            self.training_data = pd.read_csv(f"attached_assets/Training.csv")
            
            # Get disease descriptions
            self.disease_descriptions = pd.read_csv(f"attached_assets/description.csv")
            
            # Get precautions
            self.precautions = pd.read_csv(f"attached_assets/precautions_df.csv")
            
            # Extract all unique symptoms from the training data
            # First, get the column names that contain symptoms
            symptom_cols = [col for col in self.training_data.columns if col != 'prognosis']
            
            # Create a set of all symptoms
            all_symptoms = set()
            for col in symptom_cols:
                # Add non-NaN symptoms to the set
                symptoms = self.training_data[col].dropna().unique()
                all_symptoms.update(symptoms)
            
            # Remove any empty strings
            self.all_symptoms = sorted([s for s in all_symptoms if isinstance(s, str) and s.strip()])
            
            # Create a symptom encoder (mapping symptoms to indices)
            self.symptom_encoder = {symptom: i for i, symptom in enumerate(self.all_symptoms)}
            
            logger.info(f"Disease predictor data loaded successfully. Found {len(self.all_symptoms)} unique symptoms.")
            return True
        except Exception as e:
            logger.error(f"Error loading disease predictor data: {str(e)}")
            return False
    
    def get_symptom_categories(self):
        """Get symptom categories for the diagnostic questionnaire."""
        categories = {
            "Skin and Hair": [
                "itching", "skin_rash", "nodal_skin_eruptions", "dischromic _patches",
                "red_spots_over_body", "pus_filled_pimples", "blackheads", "scurring",
                "skin_peeling", "silver_like_dusting", "small_dents_in_nails", "inflammatory_nails"
            ],
            "Respiratory System": [
                "continuous_sneezing", "shivering", "chills", "cough", "high_fever",
                "breathlessness", "phlegm", "throat_irritation", "runny_nose", "congestion"
            ],
            "Digestive System": [
                "stomach_pain", "acidity", "ulcers_on_tongue", "vomiting", "diarrhoea",
                "constipation", "abdominal_pain", "belly_pain", "loss_of_appetite", "indigestion"
            ],
            "Cardiovascular System": [
                "chest_pain", "fast_heart_rate", "palpitations"
            ],
            "Musculoskeletal System": [
                "joint_pain", "muscle_weakness", "muscle_pain", "stiff_neck", "swelling_joints",
                "movement_stiffness", "painful_walking", "knee_pain", "hip_joint_pain", "neck_pain", "back_pain"
            ],
            "General Symptoms": [
                "fatigue", "weight_loss", "weight_gain", "restlessness", "lethargy", "malaise",
                "swelling_of_stomach", "weakness_of_one_body_side", "patches_in_throat"
            ],
            "Neurological Symptoms": [
                "headache", "dizziness", "loss_of_balance", "unsteadiness", "spinning_movements",
                "slurred_speech", "altered_sensorium"
            ],
            "Psychological Symptoms": [
                "mood_swings", "anxiety", "irritability", "depression", "lack_of_concentration"
            ],
            "Urinary Symptoms": [
                "bladder_discomfort", "foul_smell_of urine", "continuous_feel_of_urine", "burning_micturition"
            ],
            "Vision-Related Symptoms": [
                "blurred_and_distorted_vision", "redness_of_eyes", "sinus_pressure", 
                "puffy_face_and_eyes", "visual_disturbances", "watering_from_eyes"
            ],
            "Other Symptoms": [
                "yellow_urine", "dark_urine", "yellowing_of_eyes", "yellowish_skin", "sunken_eyes",
                "dehydration", "nausea", "pain_behind_the_eyes", "sweating", "cold_hands_and_feets"
            ]
        }
        
        return categories
        
    def predict_disease(self, symptoms):
        """
        Predict diseases based on provided symptoms.
        
        Args:
            symptoms (list): List of symptom strings
            
        Returns:
            list: Top predicted diseases with probabilities
        """
        try:
            # Ensure symptoms are standardized
            symptoms = [s.lower().strip().replace(' ', '_') for s in symptoms]
            
            # Count disease occurrences in the training data
            disease_counts = self.training_data['prognosis'].value_counts().to_dict()
            
            # Calculate disease probabilities based on symptoms
            disease_scores = defaultdict(float)
            total_symptoms = len(symptoms)
            
            # Go through all rows in the training data
            for _, row in self.training_data.iterrows():
                disease = row['prognosis']
                matching_symptoms = 0
                
                # Check each symptom column
                for col in self.training_data.columns:
                    if col == 'prognosis':
                        continue
                    
                    # If the symptom exists in this disease case, and is in user's symptoms
                    if pd.notna(row[col]) and row[col] in symptoms:
                        matching_symptoms += 1
                
                # Calculate score for this disease based on matching symptoms ratio
                if matching_symptoms > 0:
                    # Score = (matching symptoms / total symptoms) * disease prior probability
                    score = (matching_symptoms / total_symptoms) * (disease_counts[disease] / len(self.training_data))
                    disease_scores[disease] += score
            
            # Get top 3 diseases with highest scores
            top_diseases = sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # For each disease, get its description and precautions
            results = []
            for disease, score in top_diseases:
                # Get description
                description = "No description available."
                try:
                    description_row = self.disease_descriptions[self.disease_descriptions['Disease'] == disease]
                    if not description_row.empty:
                        description = description_row['Description'].values[0]
                except Exception as e:
                    logger.error(f"Error getting description for {disease}: {str(e)}")
                
                # Get precautions
                precautions = []
                try:
                    precaution_row = self.precautions[self.precautions['Disease'] == disease]
                    if not precaution_row.empty:
                        for i in range(1, 5):
                            col = f'Precaution_{i}'
                            if col in precaution_row.columns and pd.notna(precaution_row[col].values[0]):
                                precautions.append(precaution_row[col].values[0])
                except Exception as e:
                    logger.error(f"Error getting precautions for {disease}: {str(e)}")
                
                results.append({
                    'disease': disease,
                    'score': score,
                    'description': description,
                    'precautions': precautions
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error predicting disease: {str(e)}")
            return []
    
    def get_disease_info(self, disease_name):
        """Get detailed information about a specific disease."""
        try:
            # Get description
            description = "No description available."
            try:
                description_row = self.disease_descriptions[self.disease_descriptions['Disease'] == disease_name]
                if not description_row.empty:
                    description = description_row['Description'].values[0]
            except Exception as e:
                logger.error(f"Error getting description for {disease_name}: {str(e)}")
            
            # Get precautions
            precautions = []
            try:
                precaution_row = self.precautions[self.precautions['Disease'] == disease_name]
                if not precaution_row.empty:
                    for i in range(1, 5):
                        col = f'Precaution_{i}'
                        if col in precaution_row.columns and pd.notna(precaution_row[col].values[0]):
                            precautions.append(precaution_row[col].values[0])
            except Exception as e:
                logger.error(f"Error getting precautions for {disease_name}: {str(e)}")
            
            return {
                'disease': disease_name,
                'description': description,
                'precautions': precautions
            }
        except Exception as e:
            logger.error(f"Error getting disease info: {str(e)}")
            return {'disease': disease_name, 'description': 'Information not available', 'precautions': []}
    
    def get_symptoms_by_disease(self, disease_name):
        """Get common symptoms for a specific disease."""
        try:
            # Filter the training data for the specified disease
            disease_rows = self.training_data[self.training_data['prognosis'] == disease_name]
            
            if disease_rows.empty:
                return []
            
            # Collect symptoms from all matching rows
            all_symptoms = set()
            for _, row in disease_rows.iterrows():
                for col in self.training_data.columns:
                    if col == 'prognosis':
                        continue
                    
                    if pd.notna(row[col]) and row[col].strip():
                        all_symptoms.add(row[col])
            
            # Convert symptoms to more readable format (replace underscores with spaces)
            readable_symptoms = [s.replace('_', ' ').strip() for s in all_symptoms]
            
            return sorted(readable_symptoms)
        except Exception as e:
            logger.error(f"Error getting symptoms for {disease_name}: {str(e)}")
            return []

# Create a predictor instance for testing
if __name__ == "__main__":
    predictor = DiseasePredictor()
    
    # Test prediction with some symptoms
    test_symptoms = ["cough", "fever", "fatigue"]
    results = predictor.predict_disease(test_symptoms)
    
    print(f"Prediction results for {test_symptoms}:")
    for result in results:
        print(f"- {result['disease']} (score: {result['score']:.4f})")
        print(f"  Description: {result['description'][:100]}...")
        if result['precautions']:
            print(f"  Precautions: {', '.join(result['precautions'])}")