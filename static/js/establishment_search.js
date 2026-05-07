document.getElementById('restaurant-search-form').addEventListener('submit', async function(event) {
  event.preventDefault();
  const name = document.getElementById('restaurant-name').value;

  try {
    const response = await fetch(`/contrevenants/etablissement?nom=${encodeURIComponent(name)}`);
    const data = await response.json();

    const section = document.getElementById('restaurant-results');
    const resultsContainer = document.getElementById('restaurant-results-body');
    resultsContainer.innerHTML = '';

    if (Array.isArray(data) && data.length > 0) {
      data.forEach(row => {
        const col = document.createElement('div');
        col.className = 'col-md-6';

        col.innerHTML = `
          <div class="card h-100">
            <div class="card-body">
              <h5 class="card-title">${row.etablissement}</h5>
              <p class="card-text"><strong>Catégorie:</strong> ${row.categorie}</p>
              <p class="card-text"><strong>Business ID:</strong> ${row.business_id}</p>
              <p class="card-text"><strong>Propriétaire:</strong> ${row.proprietaire}</p>
              <p class="card-text"><strong>Adresse:</strong> ${row.adresse}</p>
              <p class="card-text"><strong>ID Poursuite:</strong> ${row.id_poursuite}</p>
              <p class="card-text"><strong>Description:</strong><br>${row.description}</p>
              <p class="card-text"><strong>Date:</strong> ${row.date}</p>
              <p class="card-text"><strong>Ville:</strong> ${row.ville}</p>
              <p class="card-text"><strong>Statut:</strong> ${row.statut}</p>
              <p class="card-text"><strong>Date Statut:</strong> ${row.date_statut}</p>
              <p class="card-text"><strong>Montant:</strong> ${row.montant}</p>
              <p class="card-text"><strong>Date Jugement:</strong> ${row.date_jugement}</p>
            </div>
          </div>
        `;

        resultsContainer.appendChild(col);
      });
      section.style.display = 'block';
    } else {
      resultsContainer.innerHTML = '<div class="col-12">Aucune infraction trouvée.</div>';
      section.style.display = 'block';
    }
  } catch (err) {
    console.error('Erreur lors de la requête :', err);
  }
});
