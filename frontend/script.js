// E-Consult Vector Search Frontend JavaScript

const API_BASE_URL = 'http://localhost:8000';

/**
 * Load settings from the API
 */
async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/settings`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.success && data.settings) {
            document.getElementById('defaultSystemPrompts').value = data.settings.default_system_prompts || '';
        }
    } catch (error) {
        console.error('Failed to load settings:', error);
        showMessage('Kon instellingen niet laden', 'error');
    }
}

/**
 * Save settings to the API
 */
async function saveSettings() {
    const defaultSystemPrompts = document.getElementById('defaultSystemPrompts').value.trim();
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/settings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                default_system_prompts: defaultSystemPrompts
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.success) {
            showMessage('Instellingen succesvol opgeslagen!', 'success');
        } else {
            throw new Error(data.message || 'Onbekende fout opgetreden');
        }

    } catch (error) {
        console.error('Settings save error:', error);
        showMessage(`Fout bij opslaan instellingen: ${error.message}`, 'error');
    }
}

/**
 * Reset settings to defaults
 */
async function resetSettings() {
    if (!confirm('Weet je zeker dat je alle instellingen wilt resetten naar standaardwaarden?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/settings`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.success) {
            document.getElementById('defaultSystemPrompts').value = '';
            showMessage('Instellingen gereset naar standaardwaarden!', 'success');
        } else {
            throw new Error(data.message || 'Onbekende fout opgetreden');
        }

    } catch (error) {
        console.error('Settings reset error:', error);
        showMessage(`Fout bij resetten instellingen: ${error.message}`, 'error');
    }
}

/**
 * Perform vector search with the provided query and doctor instructions
 */
async function performSearch() {
    const question = document.getElementById('question').value.trim();
    const doctorInstructions = document.getElementById('doctorInstructions').value.trim();

    if (!question) {
        showMessage('Vul eerst een vraag in.', 'error');
        return;
    }

    // Show loading state
    showLoading(true);
    hideMessage();
    hideAnswerSection();

    try {
        const response = await fetch(`${API_BASE_URL}/api/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: question,
                doctor_instructions: doctorInstructions
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
            showMessage('Zoekopdracht succesvol voltooid!', 'success');
        } else {
            // Handle error response with new structure
            const errorMessage = data.error_message || 'Onbekende fout opgetreden';
            if (data.llm_output && data.llm_output.summary) {
                // Show error message but still display any available content
                displayResults(data);
                showMessage(`Waarschuwing: ${errorMessage}`, 'warning');
            } else {
                throw new Error(errorMessage);
            }
        }

    } catch (error) {
        console.error('Search error:', error);
        showMessage(`Fout bij zoeken: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Display search results in the answer section
 */
function displayResults(data) {
    const answerContent = document.getElementById('answerContent');
    const referencesContent = document.getElementById('referencesContent');
    
    // Display the AI-generated summary/answer (editable)
    answerContent.innerHTML = data.llm_output.summary || 'Geen samenvatting beschikbaar.';
    
    // Display references (read-only)
    if (data.llm_output.sources_used && data.llm_output.sources_used.length > 0) {
        let referencesHTML = '<h4>Gebruikte bronnen:</h4><ul>';
        data.llm_output.sources_used.forEach(result => {
            referencesHTML += `<li><a href="${result.url}" target="_blank" rel="noopener noreferrer">${result.title}</a></li>`;
        });
        referencesHTML += '</ul>';
        referencesContent.innerHTML = referencesHTML;
    } else {
        referencesContent.innerHTML = '<p>Geen bronnen gevonden.</p>';
    }
    
    showAnswerSection();
}

/**
 * Save the current answer (placeholder for future database integration)
 */
function saveAnswer() {
    const answerContent = document.getElementById('answerContent');
    const content = answerContent.innerText;
    
    // In a real application, you would save this to a database
    // For now, we'll just show a success message
    showMessage('Antwoord opgeslagen! (In een echte app zou dit naar een database gaan)', 'success');
}

/**
 * Copy the current answer to clipboard (only the answer, not references)
 */
function copyAnswer() {
    const answerContent = document.getElementById('answerContent');
    const content = answerContent.innerText;
    
    if (!content.trim()) {
        showMessage('Geen antwoord om te kopiëren', 'warning');
        return;
    }
    
    navigator.clipboard.writeText(content).then(() => {
        showMessage('Antwoord gekopieerd naar klembord!', 'success');
    }).catch(err => {
        showMessage('Fout bij kopiëren naar klembord', 'error');
    });
}

/**
 * Clear the current answer and hide the answer section
 */
function clearAnswer() {
    document.getElementById('answerContent').innerHTML = '';
    document.getElementById('referencesContent').innerHTML = ''; // Clear references
    hideAnswerSection();
    showMessage('Antwoord gewist!', 'success');
}

/**
 * Show or hide the loading spinner
 */
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
    document.getElementById('searchBtn').disabled = show;
}

/**
 * Display a message to the user
 */
function showMessage(message, type) {
    const messageArea = document.getElementById('messageArea');
    messageArea.innerHTML = `<div class="${type}">${message}</div>`;
}

/**
 * Hide all messages
 */
function hideMessage() {
    document.getElementById('messageArea').innerHTML = '';
}

/**
 * Show the answer section
 */
function showAnswerSection() {
    document.getElementById('answerSection').style.display = 'block';
}

/**
 * Hide the answer section
 */
function hideAnswerSection() {
    document.getElementById('answerSection').style.display = 'none';
}

/**
 * Auto-resize textarea based on content
 */
function setupTextareaAutoResize() {
    const questionTextarea = document.getElementById('question');
    
    questionTextarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    const questionTextarea = document.getElementById('question');
    
    // Enter key in question field triggers search
    questionTextarea.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            e.preventDefault();
            performSearch();
        }
    });
}

/**
 * Initialize the frontend when the page loads
 */
function initializeFrontend() {
    setupTextareaAutoResize();
    setupKeyboardShortcuts();
    setupEventListeners();
    
    // Load settings from API
    loadSettings();
    
    // Focus on the question textarea for better UX
    document.getElementById('question').focus();
}

/**
 * Setup event listeners for all buttons
 */
function setupEventListeners() {
    const saveSettingsBtn = document.getElementById('saveSettingsBtn');
    const resetSettingsBtn = document.getElementById('resetSettingsBtn');
    const searchBtn = document.getElementById('searchBtn');
    const saveAnswerBtn = document.getElementById('saveAnswerBtn');
    const copyAnswerBtn = document.getElementById('copyAnswerBtn');
    const clearAnswerBtn = document.getElementById('clearAnswerBtn');
    
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', saveSettings);
    }
    
    if (resetSettingsBtn) {
        resetSettingsBtn.addEventListener('click', resetSettings);
    }
    
    if (searchBtn) {
        searchBtn.addEventListener('click', performSearch);
    }
    
    if (saveAnswerBtn) {
        saveAnswerBtn.addEventListener('click', saveAnswer);
    }
    
    if (copyAnswerBtn) {
        copyAnswerBtn.addEventListener('click', copyAnswer);
    }
    
    if (clearAnswerBtn) {
        clearAnswerBtn.addEventListener('click', clearAnswer);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeFrontend);
