// DataWiz AI - Frontend Application

let currentFile = null;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileStats = document.getElementById('fileStats');
const chatSection = document.getElementById('chatSection');
const questionInput = document.getElementById('questionInput');
const askBtn = document.getElementById('askBtn');
const messages = document.getElementById('messages');
const loading = document.getElementById('loading');
const resetBtn = document.getElementById('resetBtn');
const insightsBtn = document.getElementById('insightsBtn');
const insightsSection = document.getElementById('insightsSection');
const insightsLoading = document.getElementById('insightsLoading');
const insightsContainer = document.getElementById('insightsContainer');

// Upload Area Click
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// Drag and Drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--primary)';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = 'var(--border)';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--border)';
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

// File Input Change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

// Upload Button Click
uploadBtn.addEventListener('click', () => {
    fileInput.click();
});

// Ask Button Click
askBtn.addEventListener('click', () => {
    askQuestion();
});

// Question Input Enter Key
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        askQuestion();
    }
});

// Reset Button Click
resetBtn.addEventListener('click', async () => {
    if (confirm('Are you sure you want to reset? This will clear all data and history.')) {
        await resetSession();
    }
});

// Insights Button Click
insightsBtn.addEventListener('click', async () => {
    await getInsights();
});

// Handle File Upload
async function handleFileUpload(file) {
    // Validate file type
    const validTypes = ['.csv', '.xlsx', '.xls'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();

    if (!validTypes.includes(fileExt)) {
        showError('Please upload a CSV or Excel file.');
        return;
    }

    showLoading(true);

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Upload failed');
        }

        currentFile = file.name;
        displayFileInfo(data);
        chatSection.classList.add('show');
        questionInput.focus();

    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// Display File Info
function displayFileInfo(data) {
    fileName.textContent = data.filename;

    const info = data.info;
    fileStats.innerHTML = `
        <div class="stat">
            <div class="stat-label">Rows</div>
            <div class="stat-value">${info.shape[0].toLocaleString()}</div>
        </div>
        <div class="stat">
            <div class="stat-label">Columns</div>
            <div class="stat-value">${info.shape[1]}</div>
        </div>
        <div class="stat">
            <div class="stat-label">Total Cells</div>
            <div class="stat-value">${(info.shape[0] * info.shape[1]).toLocaleString()}</div>
        </div>
    `;

    fileInfo.classList.add('show');
    insightsBtn.style.display = 'inline-flex';
}

// Ask Question
async function askQuestion() {
    const question = questionInput.value.trim();

    if (!question) {
        questionInput.focus();
        return;
    }

    if (!currentFile) {
        showError('Please upload a file first.');
        return;
    }

    // Add user message
    addMessage('user', question);
    questionInput.value = '';
    showLoading(true);

    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Analysis failed');
        }

        // Add AI response
        addMessage('ai', data.answer, data.code, data.visualization);

    } catch (error) {
        showError(error.message);
        addMessage('ai', `Sorry, I encountered an error: ${error.message}`);
    } finally {
        showLoading(false);
        questionInput.focus();
    }
}

// Add Message
function addMessage(type, text, code = null, visualization = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';

    const iconMap = {
        user: '👤',
        ai: '🤖'
    };

    const labelMap = {
        user: 'You',
        ai: 'DataWiz AI'
    };

    let content = `
        <div class="message-header">
            <span class="message-icon">${iconMap[type]}</span>
            <span class="message-label ${type}-message">${labelMap[type]}</span>
        </div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
    `;

    // Add code if present
    if (code) {
        content += `
            <details>
                <summary style="cursor: pointer; color: var(--primary); margin-top: 1rem;">
                    💻 View Generated Code
                </summary>
                <div class="message-code">
                    <pre>${escapeHtml(code)}</pre>
                </div>
            </details>
        `;
    }

    // Add visualization if present
    if (visualization) {
        content += `
            <div class="message-chart">
                <iframe src="${visualization}?t=${Date.now()}"></iframe>
            </div>
        `;
    }

    content += '</div>';
    messageDiv.innerHTML = content;

    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

// Show Loading
function showLoading(show) {
    if (show) {
        loading.classList.add('show');
    } else {
        loading.classList.remove('show');
    }
}

// Show Error
function showError(message) {
    alert(`❌ Error: ${message}`);
}

// Reset Session
async function resetSession() {
    try {
        await fetch('/api/reset', {
            method: 'DELETE'
        });

        // Reset UI
        currentFile = null;
        fileInfo.classList.remove('show');
        chatSection.classList.remove('show');
        insightsSection.classList.remove('show');
        insightsBtn.style.display = 'none';
        messages.innerHTML = '';
        insightsContainer.innerHTML = '';
        questionInput.value = '';
        fileInput.value = '';

        showSuccess('Session reset successfully!');

    } catch (error) {
        showError(error.message);
    }
}

// Show Success
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--success);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    successDiv.textContent = `✓ ${message}`;
    document.body.appendChild(successDiv);

    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Get Insights
async function getInsights() {
    if (!currentFile) {
        showError('Please upload a file first.');
        return;
    }

    // Show insights section and loading
    insightsSection.classList.add('show');
    insightsLoading.classList.add('show');
    insightsContainer.innerHTML = '';

    try {
        const response = await fetch('/api/insights');
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to generate insights');
        }

        // Display insights
        displayInsights(data.insights);

    } catch (error) {
        showError(error.message);
        insightsContainer.innerHTML = `
            <div class="insight-item error">
                <p>❌ Failed to generate insights: ${error.message}</p>
            </div>
        `;
    } finally {
        insightsLoading.classList.remove('show');
    }
}

// Display Insights
function displayInsights(insights) {
    if (!insights || insights.length === 0) {
        insightsContainer.innerHTML = `
            <div class="insight-item">
                <p>No significant insights found.</p>
            </div>
        `;
        return;
    }

    insightsContainer.innerHTML = '';

    insights.forEach(insight => {
        const insightDiv = document.createElement('div');
        insightDiv.className = `insight-item ${insight.category || 'neutral'}`;

        // Icon based on category
        const icons = {
            warning: '⚠️',
            error: '❌',
            success: '✅',
            info: 'ℹ️',
            neutral: '💡'
        };

        const icon = icons[insight.category] || icons.neutral;
        const priority = insight.priority || 'medium';

        insightDiv.innerHTML = `
            <div style="display: flex; align-items: flex-start; gap: 1rem;">
                <span style="font-size: 1.5rem;">${icon}</span>
                <div style="flex: 1;">
                    <p style="margin: 0; line-height: 1.6;">${escapeHtml(insight.text)}</p>
                    ${priority === 'high' ? '<span style="font-size: 0.8rem; color: var(--error); font-weight: 600; text-transform: uppercase;">High Priority</span>' : ''}
                </div>
            </div>
        `;

        insightsContainer.appendChild(insightDiv);
    });
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
