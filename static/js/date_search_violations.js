document.getElementById('date-search-form').addEventListener('submit', async function(event) {
  event.preventDefault();
  const du = document.getElementById('du').value;
  const au = document.getElementById('au').value;

  try {
    const response = await fetch(`/contrevenants?du=${du}&au=${au}&sum=true`);
    const data = await response.json();

    const tbody = document.getElementById('summary-table-body');
    tbody.innerHTML = '';

    if (Array.isArray(data) && data.length > 0) {
      data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${row.etablissement}</td><td>${row.total}</td>`;
        tbody.appendChild(tr);
      });
      document.getElementById('summary-table-section').style.display = 'block';
    } else {
      tbody.innerHTML = '<tr><td colspan="2">Aucun résultat trouvé.</td></tr>';
      document.getElementById('summary-table-section').style.display = 'block';
    }

  } catch (err) {
    console.error('Erreur lors de la requête :', err);
  }
});
