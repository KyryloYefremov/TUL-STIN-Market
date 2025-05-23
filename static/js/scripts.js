// Toggle log panel visibility
const logPanelWrapper = document.getElementById('log-panel-wrapper');
const toggleLogBtn = document.getElementById('toggle-log-btn');

let hidden = true; // Initial state of the log panel (default hidden)
logPanelWrapper.style.transform = 'translateX(100%)'; // Hide it initially
toggleLogBtn.innerText = 'Show Logs';

toggleLogBtn.addEventListener('click', () => {
    hidden = !hidden;
    logPanelWrapper.style.transform = hidden ? 'translateX(100%)' : 'translateX(0)';
    toggleLogBtn.innerText = hidden ? 'Show Logs' : 'Hide Logs';
});

// Handle stock search
document.getElementById('search-form').addEventListener('submit', function (e) {
    e.preventDefault(); // Prevent form submission for AJAX-like behavior

    const query = document.querySelector('input[name="query"]').value;

    fetch(`/search_stock?query=${query}`)
        .then(response => response.json())
        .then(data => {
            const modalList = document.getElementById('modal-result-list');
            modalList.innerHTML = '';

            if (data.length === 0) {
                modalList.innerHTML = '<li class="list-group-item">No results found.</li>';
            } else {
                data.forEach(company => {
                    const listItem = document.createElement('li');
                    listItem.classList.add('list-group-item');
                    listItem.innerHTML = `${company[1]} - ${company[0]} 
                    <form action="${addFavouriteStockUrl}" method="POST" class="d-inline">
                        <input type="hidden" name="ticker" value="${company[1]}">
                        <input type="hidden" name="name" value="${company[0]}">
                        <button class="btn btn-success btn-sm float-end" type="submit">Save</button>
                    </form>`;
                    modalList.appendChild(listItem);
                });
            }

            const myModal = new bootstrap.Modal(document.getElementById('resultModal'));
            myModal.show();
        })
        .catch(error => console.error('Error:', error));
});

// Logging helper
function logEvent(message) {
    const logPanel = document.getElementById('log-panel');
    logPanel.textContent += `\n\n${message}`;
    logPanel.scrollIntoView(false); // Scroll to bottom when panel is shown
}

// Connect to SSE for server logs
const eventSource = new EventSource('/logs');
eventSource.onmessage = function (event) {
    logEvent(event.data);
};