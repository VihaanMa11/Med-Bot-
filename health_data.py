import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def initialize_health_data():
    """
    Initialize health knowledge base with key topics and information
    Each topic includes:
    - keywords: list of keywords related to the topic
    - information: detailed information about the topic
    """
    health_knowledge_base = {
        "nutrition": {
            "keywords": ["nutrition", "food", "diet", "eat", "eating", "meal", "meals", 
                        "vitamin", "vitamins", "mineral", "minerals", "nutrient", "nutrients",
                        "fruit", "fruits", "vegetable", "vegetables", "protein", "carbohydrate", "fat"],
            "information": """
<h3>Nutrition</h3>
<p>A balanced diet is essential for good health. Key components include:</p>
<ul>
    <li><strong>Proteins:</strong> Build and repair tissues. Sources include meat, fish, eggs, dairy, beans, and nuts.</li>
    <li><strong>Carbohydrates:</strong> Provide energy. Choose complex carbs like whole grains, fruits, and vegetables.</li>
    <li><strong>Fats:</strong> Essential for vitamin absorption and cell function. Focus on healthy fats from olive oil, avocados, and nuts.</li>
    <li><strong>Vitamins and minerals:</strong> Vital for various bodily functions. Eat a colorful variety of fruits and vegetables.</li>
    <li><strong>Water:</strong> Aim for 8 glasses daily to maintain hydration.</li>
</ul>
<p>Try to limit processed foods, excessive sugar, and salt intake for optimal health.</p>
"""
        },
        "exercise": {
            "keywords": ["exercise", "workout", "fitness", "physical activity", "training",
                        "cardio", "aerobic", "strength", "flexibility", "run", "running", 
                        "walk", "walking", "jog", "jogging", "swim", "swimming", "gym"],
            "information": """
<h3>Exercise and Physical Activity</h3>
<p>Regular physical activity is crucial for maintaining good health and preventing diseases.</p>
<ul>
    <li><strong>Aerobic exercise:</strong> Aim for at least 150 minutes of moderate-intensity activity per week (like brisk walking, swimming, or cycling).</li>
    <li><strong>Strength training:</strong> Include muscle-strengthening activities at least twice per week.</li>
    <li><strong>Flexibility:</strong> Regular stretching helps maintain range of motion and prevents injuries.</li>
    <li><strong>Balance exercises:</strong> Particularly important as you age to prevent falls.</li>
</ul>
<p>Start slowly if you're new to exercise and gradually increase intensity and duration. Always consult with a healthcare provider before beginning a new exercise program, especially if you have pre-existing health conditions.</p>
"""
        },
        "mental_health": {
            "keywords": ["mental health", "depression", "anxiety", "stress", "mindfulness",
                        "meditation", "therapy", "counseling", "emotion", "emotions", "emotional",
                        "psychological", "psychologist", "psychiatrist", "mind", "relax", "relaxation"],
            "information": """
<h3>Mental Health</h3>
<p>Mental well-being is just as important as physical health. Here are some key aspects:</p>
<ul>
    <li><strong>Stress management:</strong> Practice relaxation techniques like deep breathing, meditation, or yoga.</li>
    <li><strong>Sleep:</strong> Aim for 7-9 hours of quality sleep per night.</li>
    <li><strong>Social connections:</strong> Maintain relationships with family and friends to prevent isolation.</li>
    <li><strong>Professional help:</strong> Don't hesitate to seek help from therapists or counselors when needed.</li>
    <li><strong>Self-care:</strong> Make time for activities you enjoy and that help you relax.</li>
</ul>
<p>Remember that mental health conditions are medical conditions, just like physical illnesses, and deserve proper treatment and attention.</p>
"""
        },
        "sleep": {
            "keywords": ["sleep", "insomnia", "rest", "fatigue", "tired", "drowsy", 
                        "snoring", "apnea", "bed", "nap", "slumber", "drowsiness"],
            "information": """
<h3>Sleep and Rest</h3>
<p>Quality sleep is essential for physical and mental health. Most adults need 7-9 hours of sleep per night.</p>
<ul>
    <li><strong>Sleep hygiene:</strong> Maintain a regular sleep schedule, even on weekends.</li>
    <li><strong>Sleep environment:</strong> Keep your bedroom cool, quiet, and dark.</li>
    <li><strong>Pre-sleep routine:</strong> Avoid screens (TV, phone, computer) at least 1 hour before bed.</li>
    <li><strong>Diet impact:</strong> Limit caffeine and alcohol, especially later in the day.</li>
    <li><strong>Exercise:</strong> Regular physical activity promotes better sleep, but avoid vigorous exercise close to bedtime.</li>
</ul>
<p>If you consistently have trouble sleeping, talk to a healthcare provider, as it could indicate an underlying sleep disorder or health condition.</p>
"""
        },
        "common_illnesses": {
            "keywords": ["cold", "flu", "fever", "headache", "migraine", "allergy", "allergies",
                        "cough", "sore throat", "infection", "virus", "bacteria", "illness",
                        "symptom", "symptoms", "disease", "sick", "nausea", "pain"],
            "information": """
<h3>Common Illnesses</h3>
<p>Understanding common illnesses can help you recognize symptoms and seek appropriate treatment:</p>
<ul>
    <li><strong>Common cold:</strong> Symptoms include runny/stuffy nose, sore throat, and cough. Rest, fluids, and over-the-counter remedies can help.</li>
    <li><strong>Influenza (flu):</strong> More severe than a cold, with fever, body aches, fatigue, and respiratory symptoms. Annual vaccination is recommended.</li>
    <li><strong>Allergies:</strong> Can cause sneezing, itching, rashes, or more serious reactions. Identify and avoid triggers.</li>
    <li><strong>Gastroenteritis:</strong> Often called "stomach flu," causes nausea, vomiting, and diarrhea. Stay hydrated and seek care if symptoms are severe.</li>
</ul>
<p>Always consult a healthcare provider for proper diagnosis and treatment, especially for persistent or severe symptoms.</p>
"""
        },
        "preventive_care": {
            "keywords": ["prevention", "preventive", "vaccine", "vaccination", "immunization",
                        "screening", "checkup", "check-up", "examination", "preventative",
                        "protect", "protection", "hygiene", "wash"],
            "information": """
<h3>Preventive Care</h3>
<p>Preventive care focuses on maintaining health and early detection of problems:</p>
<ul>
    <li><strong>Regular check-ups:</strong> Schedule routine visits with your healthcare provider, even when you feel well.</li>
    <li><strong>Screenings:</strong> Age-appropriate health screenings can detect issues before symptoms appear (like blood pressure, cholesterol, cancer screenings).</li>
    <li><strong>Vaccinations:</strong> Stay up-to-date with recommended immunizations for your age and risk factors.</li>
    <li><strong>Dental care:</strong> Regular dental check-ups help prevent oral health problems.</li>
    <li><strong>Hand hygiene:</strong> Regular handwashing is one of the best ways to prevent the spread of infections.</li>
</ul>
<p>Prevention is always better than treatment. Many conditions are easier to manage when caught early.</p>
"""
        },
        "heart_health": {
            "keywords": ["heart", "cardiac", "cardiovascular", "blood pressure", "hypertension",
                        "cholesterol", "stroke", "circulation", "artery", "arteries", "vein", "veins"],
            "information": """
<h3>Heart Health</h3>
<p>Maintaining heart health is crucial for overall well-being and longevity:</p>
<ul>
    <li><strong>Diet:</strong> Eat a heart-healthy diet low in saturated fats, trans fats, and sodium, and rich in fruits, vegetables, and whole grains.</li>
    <li><strong>Exercise:</strong> Regular physical activity strengthens your heart and improves circulation.</li>
    <li><strong>Blood pressure:</strong> Maintain healthy levels (typically below 120/80 mmHg).</li>
    <li><strong>Cholesterol:</strong> Keep your cholesterol levels in check through diet, exercise, and sometimes medication.</li>
    <li><strong>Avoid smoking:</strong> Smoking damages blood vessels and can lead to heart disease.</li>
</ul>
<p>Know your risk factors and work with your healthcare provider to develop a personalized heart health plan.</p>
"""
        },
        "diabetes": {
            "keywords": ["diabetes", "blood sugar", "glucose", "insulin", "diabetic", 
                        "hyperglycemia", "hypoglycemia", "sugar", "type 1", "type 2"],
            "information": """
<h3>Diabetes</h3>
<p>Diabetes is a chronic condition that affects how your body processes blood sugar (glucose):</p>
<ul>
    <li><strong>Type 1 diabetes:</strong> The body doesn't produce insulin and requires insulin therapy.</li>
    <li><strong>Type 2 diabetes:</strong> The body doesn't use insulin properly. Often related to lifestyle factors.</li>
    <li><strong>Prediabetes:</strong> Blood sugar is elevated but not high enough to be diagnosed as diabetes.</li>
    <li><strong>Gestational diabetes:</strong> Occurs during pregnancy and usually resolves after delivery.</li>
</ul>
<p>Management typically includes monitoring blood sugar, maintaining a healthy diet and weight, regular physical activity, and sometimes medication or insulin. Regular check-ups are essential for monitoring and preventing complications.</p>
"""
        },
        "weight_management": {
            "keywords": ["weight", "obesity", "overweight", "bmi", "body mass index", "diet", 
                        "calorie", "calories", "fat", "slim", "thin", "heavy", "lose weight", "gain weight"],
            "information": """
<h3>Weight Management</h3>
<p>Maintaining a healthy weight is important for overall health and reducing risk of chronic diseases:</p>
<ul>
    <li><strong>Healthy eating:</strong> Focus on a balanced diet with appropriate portion sizes.</li>
    <li><strong>Regular physical activity:</strong> Aim for at least 150 minutes of moderate-intensity exercise per week.</li>
    <li><strong>Behavior changes:</strong> Identify triggers for unhealthy eating and develop coping strategies.</li>
    <li><strong>Realistic goals:</strong> Aim for gradual, sustainable weight changes (1-2 pounds per week).</li>
    <li><strong>Monitor progress:</strong> Track your food intake, physical activity, and weight regularly.</li>
</ul>
<p>Remember that healthy weight ranges vary by individual. Consult with healthcare providers to determine what's appropriate for you and to develop a personalized plan.</p>
"""
        }
    }
    
    logger.info(f"Health knowledge base initialized with {len(health_knowledge_base)} topics")
    return health_knowledge_base
