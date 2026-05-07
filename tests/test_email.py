from utils.email_utils import notify_by_email

# Create mock violation data
mock_violations = [
    {
        "etablissement": "BOULANGERIE LA TUNISIENNE",
        "adresse": "123 Rue Sainte-Catherine, Montréal",
        "date": "2025-04-20",
        "description": "Manque d'hygiène dans la cuisine.",
        "montant": 1000
    },
    {
        "etablissement": "RESTAURANT XYZ",
        "adresse": "456 Boulevard Saint-Laurent, Montréal",
        "date": "2025-04-19",
        "description": "Température inadéquate des aliments.",
        "montant": 1500
    }
]

# Call the notification function
notify_by_email(mock_violations)
