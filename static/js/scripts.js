// Toggle log panel visibility
const logPanelWrapper = document.getElementById('log-panel-wrapper');
const toggleLogBtn = document.getElementById('toggle-log-btn');

let hidden = true; // Initial state of the log panel

toggleLogBtn.addEventListener('click', () => {
    hidden = !hidden;
    logPanelWrapper.style.transform = hidden ? 'translateX(100%)' : 'translateX(0)';
    toggleLogBtn.innerText = hidden ? 'Show Logs' : 'Hide Logs';
});


// Handle stock search
document.getElementById('search-form').addEventListener('submit', function (e) {
    e.preventDefault(); // Prevent form submission for AJAX-like behavior

    // Get the search query value
    const query = document.querySelector('input[name="query"]').value;

    // Send the search query to the server using fetch
    fetch(`/search_stock?query=${query}`)
        .then(response => response.json())  // Parse JSON response
        .then(data => {
            // Populate the modal with the results
            const modalList = document.getElementById('modal-result-list');
            modalList.innerHTML = '';  // Clear previous results

            if (data.length === 0) {
                modalList.innerHTML = '<li class="list-group-item">No results found.</li>';
            } else {
                data.forEach(company => {
                    const listItem = document.createElement('li');
                    listItem.classList.add('list-group-item');
                    listItem.innerHTML = `${company.ticker} - ${company.name} 
                    <form action="${addFavoriteStockUrl}" method="POST" class="d-inline">
                        <input type="hidden" name="ticker" value="${company.ticker}">
                        <input type="hidden" name="name" value="${company.name}">
                        <button class="btn btn-success btn-sm float-end" type="submit">Save</button>
                    </form>`;
                    modalList.appendChild(listItem);
                });
            }

            // Show the modal
            const myModal = new bootstrap.Modal(document.getElementById('resultModal'));
            myModal.show();
        })
        .catch(error => console.error('Error:', error));
});


// Logging helper
function logEvent(message) {
    const now = new Date();
    const time = now.toLocaleTimeString();
    const date = now.toLocaleDateString();
    const logPanel = document.getElementById('log-panel');
    logPanel.textContent += `\n[${time}] - ${message} [${date}]`;
}