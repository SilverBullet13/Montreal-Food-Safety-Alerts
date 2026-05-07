const form = document.getElementById("plainte-form");
form.addEventListener("submit", async function (e) {
  e.preventDefault();

  const data = {
    etablissement: form.etablissement.value,
    adresse: form.adresse.value,
    ville: form.ville.value,
    date_visite: form.date_visite.value,
    nom_client: form.nom_client.value,
    prenom_client: form.prenom_client.value,
    description: form.description.value
  };

  try {
    const response = await fetch("/demand-inspection", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    if (response.status === 201) {
      document.getElementById("confirmation").textContent = "Votre plainte a été envoyée avec succès.";
      document.getElementById("erreur").textContent = "";
      form.reset();
    } else {
      const error = await response.json();
      document.getElementById("erreur").textContent = "Erreur: " + (error.details || "Requête invalide.");
      document.getElementById("confirmation").textContent = "";
    }
  } catch (err) {
    document.getElementById("erreur").textContent = "Erreur de connexion au serveur.";
    document.getElementById("confirmation").textContent = "";
  }
});
