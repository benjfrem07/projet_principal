import cohere
import json
from flask import Flask, request, jsonify

# Initializing Flask app
app = Flask(__name__)

# Function to extract text from a TXT file
def extraire_texte_txt(fichier_txt):
    with open(fichier_txt, 'r', encoding='utf-8') as fichier:
        texte_complet = fichier.read()
    return texte_complet

# Function to structure data using Cohere API
def structurer_donnees_avec_ia(texte_brut):
    co = cohere.Client("K5wFMFHhipU7zmgokyvQ9wiUm1BiRM4qJCFeP7Cr")
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=f"Prends le texte suivant et divise-le en plusieurs paires 'prompt-completion-solution' au format JSON. Le prompt doit décrire la question ou l'équation, la completion doit fournir une explication de la méthode utilisée, et la solution doit contenir la réponse finale à l'équation. Voici le texte : {texte_brut}",
        max_tokens=800
    )
    
    # Return generated text
    return response.generations[0].text

# Function to save structured data to a JSON file
def sauvegarder_donnees_structurees(donnees, chemin_fichier):
    with open(chemin_fichier, "w") as fichier_json:
        json.dump(donnees, fichier_json, indent=4)

# Function to process the input TXT file and structure it
def traiter_fichier_txt(fichier_txt, chemin_fichier_json):
    # Extract raw text
    texte_brut = extraire_texte_txt(fichier_txt)
    print("Extraction du texte brut terminée.")
    
    # Structure the data using Cohere
    donnees_structurees = structurer_donnees_avec_ia(texte_brut)
    print("Structuration des données avec Cohere terminée.")
    
    try:
        # Validate and save the structured data into a JSON file
        json_data = json.loads(donnees_structurees)
        sauvegarder_donnees_structurees(json_data, chemin_fichier_json)
        print(f"Données structurées sauvegardées dans {chemin_fichier_json}.")
    except json.JSONDecodeError as e:
        print(f"Erreur lors de la conversion en JSON : {e}")
        print("Le texte généré n'est pas un JSON valide.")

# Flask route to handle file uploads and processing
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    # Save uploaded file and process
    file_path = 'uploaded_file.txt'
    file.save(file_path)
    
    output_json_path = 'donnees_structurees.json'
    traiter_fichier_txt(file_path, output_json_path)
    
    return jsonify({"message": "File processed and structured data saved"})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
