import os
import pandas as pd
import logging
import ast

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class HealthDataProcessor:
    def __init__(self):
        """Initialize the health data processor."""
        self.data_dir = "data"
        self.descriptions = None
        self.diets = None
        self.medications = None
        self.medicines = None
        self.precautions = None
        self.symptoms = None
        self.symptom_severity = None
        self.training_data = None
        self.workouts = None
        self.diseases = None
        self.knowledge_base = {}
        
    def load_data(self):
        """Load all health datasets from CSV files."""
        try:
            # Load all CSV files
            self.descriptions = pd.read_csv(os.path.join(self.data_dir, "description.csv"))
            self.diets = pd.read_csv(os.path.join(self.data_dir, "diets.csv"))
            self.medications = pd.read_csv(os.path.join(self.data_dir, "medications.csv"))
            self.medicines = pd.read_csv(os.path.join(self.data_dir, "medicines.csv"))
            self.precautions = pd.read_csv(os.path.join(self.data_dir, "precautions_df.csv"))
            self.symptoms = pd.read_csv(os.path.join(self.data_dir, "symptoms_df.csv"))
            self.symptom_severity = pd.read_csv(os.path.join(self.data_dir, "Symptom-severity.csv"))
            self.workouts = pd.read_csv(os.path.join(self.data_dir, "workout_df.csv"))
            
            # Get unique diseases
            self.diseases = self.descriptions['Disease'].unique()
            
            logger.info(f"Successfully loaded all datasets. Found {len(self.diseases)} unique diseases.")
            return True
        except Exception as e:
            logger.error(f"Error loading health data: {str(e)}")
            return False
    
    def process_data(self):
        """Process the loaded data and create a knowledge base."""
        try:
            for disease in self.diseases:
                # Create entry for each disease
                self.knowledge_base[disease] = {
                    "description": self._get_description(disease),
                    "symptoms": self._get_symptoms(disease),
                    "precautions": self._get_precautions(disease),
                    "diets": self._get_diets(disease),
                    "medications": self._get_medications(disease),
                    "medicines": self._get_medicines(disease),
                    "workouts": self._get_workouts(disease),
                    "keywords": self._generate_keywords(disease)
                }
            
            logger.info(f"Successfully processed data for {len(self.knowledge_base)} diseases.")
            return True
        except Exception as e:
            logger.error(f"Error processing health data: {str(e)}")
            return False
    
    def _get_description(self, disease):
        """Get description for a specific disease."""
        try:
            desc = self.descriptions[self.descriptions['Disease'] == disease]['Description'].values[0]
            return desc
        except (IndexError, KeyError):
            return f"No description available for {disease}"
    
    def _get_symptoms(self, disease):
        """Get symptoms for a specific disease."""
        try:
            disease_symptoms = self.symptoms[self.symptoms['Disease'] == disease]
            symptom_list = []
            
            for _, row in disease_symptoms.iterrows():
                for col in ['Symptom_1', 'Symptom_2', 'Symptom_3', 'Symptom_4']:
                    if pd.notna(row[col]) and row[col] != '':
                        symptom_list.append(row[col].strip())
            
            return list(set(symptom_list))  # Remove duplicates
        except (IndexError, KeyError):
            return []
    
    def _get_precautions(self, disease):
        """Get precautions for a specific disease."""
        try:
            precaution_row = self.precautions[self.precautions['Disease'] == disease]
            if not precaution_row.empty:
                precautions = []
                for col in ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']:
                    if pd.notna(precaution_row[col].values[0]) and precaution_row[col].values[0] != '':
                        precautions.append(precaution_row[col].values[0])
                return precautions
            return []
        except (IndexError, KeyError):
            return []
    
    def _get_diets(self, disease):
        """Get recommended diets for a specific disease."""
        try:
            diet_str = self.diets[self.diets['Disease'] == disease]['Diet'].values[0]
            # The diet string is in the format of a Python list, so we need to evaluate it
            return ast.literal_eval(diet_str)
        except (IndexError, KeyError, SyntaxError, ValueError):
            return []
    
    def _get_medications(self, disease):
        """Get medications for a specific disease."""
        try:
            medication_str = self.medications[self.medications['Disease'] == disease]['Medication'].values[0]
            return ast.literal_eval(medication_str)
        except (IndexError, KeyError, SyntaxError, ValueError):
            return []
    
    def _get_medicines(self, disease):
        """Get specific medicines for a specific disease."""
        try:
            medicine_str = self.medicines[self.medicines['Disease'] == disease]['Medicine'].values[0]
            return ast.literal_eval(medicine_str)
        except (IndexError, KeyError, SyntaxError, ValueError):
            return []
    
    def _get_workouts(self, disease):
        """Get recommended workouts/exercises for a specific disease."""
        try:
            disease_workouts = self.workouts[self.workouts['disease'] == disease]['workout'].tolist()
            return disease_workouts
        except (IndexError, KeyError):
            return []
    
    def _generate_keywords(self, disease):
        """Generate keywords for a disease based on its name, symptoms, and other data."""
        keywords = [disease.lower()]
        
        # Add disease name words as individual keywords
        for word in disease.lower().split():
            if len(word) > 2:  # Only add words longer than 2 characters
                keywords.append(word)
        
        # Add symptoms as keywords
        symptoms = self._get_symptoms(disease)
        for symptom in symptoms:
            keywords.append(symptom.lower())
            # Add individual words from multi-word symptoms
            if '_' in symptom:
                for word in symptom.split('_'):
                    if len(word) > 2:
                        keywords.append(word.lower())
        
        # Remove duplicates and return
        return list(set(keywords))
    
    def initialize_knowledge_base(self):
        """Load and process data to create the knowledge base."""
        if self.load_data() and self.process_data():
            return self.knowledge_base
        return {}

def initialize_health_data():
    """Initialize health knowledge base from the CSV datasets."""
    processor = HealthDataProcessor()
    health_knowledge_base = processor.initialize_knowledge_base()
    logger.info(f"Health knowledge base initialized with {len(health_knowledge_base)} diseases")
    return health_knowledge_base

if __name__ == "__main__":
    # Test the data processing
    kb = initialize_health_data()
    print(f"Initialized knowledge base with {len(kb)} diseases")
    
    # Print a sample disease entry
    if kb:
        sample_disease = list(kb.keys())[0]
        print(f"\nSample entry for {sample_disease}:")
        for key, value in kb[sample_disease].items():
            if key == "keywords":
                print(f"Keywords: {value[:10]}...")  # Print first 10 keywords
            elif isinstance(value, list):
                print(f"{key.capitalize()}: {value[:3]}...")  # Print first 3 items
            else:
                print(f"{key.capitalize()}: {value}")