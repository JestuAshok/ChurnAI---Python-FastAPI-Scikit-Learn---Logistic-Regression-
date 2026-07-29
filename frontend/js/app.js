/**
 * app.js
 * Main frontend logic for Customer Churn Prediction App.
 * Handles sidebar highlighting, interactive forms, dynamic calculations, prediction endpoints, history querying, and database clearing.
 */

document.addEventListener('DOMContentLoaded', () => {
    setupSidebarNavigation();
    
    // Page-specific initializations
    const currentPath = window.location.pathname;
    
    if (currentPath.includes('predict.html')) {
        initPredictForm();
    } else if (currentPath.includes('history.html')) {
        initHistoryTable();
    } else if (currentPath.includes('analytics.html')) {
        if (typeof initAnalyticsCharts === 'function') {
            initAnalyticsCharts();
        }
    } else if (currentPath.includes('index.html') || currentPath === '/' || currentPath.endsWith('Customer-Churn-Prediction/')) {
        initDashboard();
    }
});

/* ========================================================================
SIDEBAR NAVIGATION HIGHLIGHT
======================================================================== */
function setupSidebarNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const currentPath = window.location.pathname;

    navItems.forEach(item => {
        const link = item.querySelector('a');
        if (link) {
            const href = link.getAttribute('href');
            
            // Check if current page matches the link href
            if (currentPath.includes(href) || 
                (href === 'index.html' && (currentPath === '/' || currentPath.endsWith('/') || currentPath.endsWith('index.html')))) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        }
    });
}

/* ========================================================================
DASHBOARD RECENT ACTIVITY LOG
======================================================================== */
function initDashboard() {
    const recentActivityBody = document.getElementById('recent-activity-body');
    if (!recentActivityBody) return;

    fetch('/history')
        .then(res => res.json())
        .then(data => {
            if (!data || data.length === 0) {
                recentActivityBody.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align: center; color: #71717A; padding: 2rem 0;">
                            No recent predictions. Try predicting a customer churn risk first.
                        </td>
                    </tr>
                `;
                return;
            }
            
            // Show only top 5 recent predictions on the dashboard
            const recent = data.slice(0, 5);
            recentActivityBody.innerHTML = recent.map(r => {
                let badgeClass = 'badge-low';
                if (r.risk_level === 'Medium') badgeClass = 'badge-med';
                if (r.risk_level === 'High') badgeClass = 'badge-high';
                
                return `
                    <tr>
                        <td style="font-weight: 600;">${r.customer_id}</td>
                        <td>${r.probability}%</td>
                        <td>
                            <span class="table-badge ${badgeClass}">${r.risk_level} Risk</span>
                        </td>
                        <td>${r.prediction}</td>
                        <td style="color: #71717A;">${r.timestamp}</td>
                    </tr>
                `;
            }).join('');
        })
        .catch(err => {
            console.error('Error loading recent dashboard items:', err);
            recentActivityBody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; color: #EF4444; padding: 2rem 0;">
                        Failed to load recent activity from backend database.
                    </td>
                </tr>
            `;
        });
}

/* ========================================================================
PREDICT CUSTOMER FORM & CALCULATIONS
======================================================================== */
function initPredictForm() {
    const form = document.getElementById('churn-predict-form');
    if (!form) return;

    // Listen to changes in inputs to update calculated features reactively
    const calculatedElements = {
        clv: document.getElementById('calc-clv'),
        avgSpend: document.getElementById('calc-avg-spend'),
        totServices: document.getElementById('calc-services'),
        longTerm: document.getElementById('calc-long-term'),
        monthlyContract: document.getElementById('calc-monthly-contract'),
        internetCount: document.getElementById('calc-internet-count')
    };

    // Helper functions for on-the-fly math
    function runReactiveCalculations() {
        const tenure = parseInt(document.getElementById('tenure').value) || 0;
        const monthlyCharges = parseFloat(document.getElementById('MonthlyCharges').value) || 0.0;
        const phoneService = document.getElementById('PhoneService').value;
        const multipleLines = document.getElementById('MultipleLines').value;
        const internetService = document.getElementById('InternetService').value;
        const onlineSecurity = document.getElementById('OnlineSecurity').value;
        const onlineBackup = document.getElementById('OnlineBackup').value;
        const deviceProtection = document.getElementById('DeviceProtection').value;
        const techSupport = document.getElementById('TechSupport').value;
        const streamingTV = document.getElementById('StreamingTV').value;
        const streamingMovies = document.getElementById('StreamingMovies').value;
        const contract = document.getElementById('Contract').value;

        // 1. Total Charges & CLV
        const clv = monthlyCharges * tenure;
        const totalCharges = tenure > 0 ? (monthlyCharges * tenure) : monthlyCharges;

        // 2. Average Monthly Spend
        const avgMonthlySpend = totalCharges / (tenure + 1);

        // 3. Total Services
        const serviceValues = [phoneService, multipleLines, onlineSecurity, onlineBackup, deviceProtection, techSupport, streamingTV, streamingMovies];
        const totalServices = serviceValues.filter(val => val === 'Yes').length;

        // 4. Internet Service count
        const internetValues = [onlineSecurity, onlineBackup, deviceProtection, techSupport, streamingTV, streamingMovies];
        const internetCount = internetValues.filter(val => val === 'Yes').length;

        // 5. Flags
        const isLongTerm = tenure >= 24 ? 'Yes' : 'No';
        const isMonthlyContract = contract === 'Month-to-month' ? 'Yes' : 'No';

        // Update DOM
        if (calculatedElements.clv) calculatedElements.clv.textContent = `$${clv.toFixed(2)}`;
        if (calculatedElements.avgSpend) calculatedElements.avgSpend.textContent = `$${avgMonthlySpend.toFixed(2)}`;
        if (calculatedElements.totServices) calculatedElements.totServices.textContent = totalServices;
        if (calculatedElements.longTerm) calculatedElements.longTerm.textContent = isLongTerm;
        if (calculatedElements.monthlyContract) calculatedElements.monthlyContract.textContent = isMonthlyContract;
        if (calculatedElements.internetCount) calculatedElements.internetCount.textContent = internetCount;
    }

    // Attach input event listeners
    form.querySelectorAll('input, select').forEach(elem => {
        elem.addEventListener('input', runReactiveCalculations);
    });

    // Setup Demo Customer Loading
    const btnLoadDemo = document.getElementById('btn-load-demo');
    const demoIndexInput = document.getElementById('demo-customer-index');
    const demoStatus = document.getElementById('demo-load-status');

    if (btnLoadDemo && demoIndexInput) {
        btnLoadDemo.addEventListener('click', () => {
            const idx = parseInt(demoIndexInput.value);
            if (isNaN(idx) || idx < 0) {
                showDemoStatus('Please enter a valid positive index.', 'error');
                return;
            }

            showDemoStatus('Loading customer details...', 'info');
            btnLoadDemo.disabled = true;

            fetch(`/api/customer/${idx}`)
                .then(res => {
                    if (!res.ok) {
                        return res.json().then(data => { throw new Error(data.detail || 'Failed to load') });
                    }
                    return res.json();
                })
                .then(data => {
                    const fields = [
                        'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'PhoneService', 
                        'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 
                        'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 
                        'Contract', 'PaperlessBilling', 'PaymentMethod', 'tenure', 'MonthlyCharges'
                    ];

                    fields.forEach(field => {
                        const elem = document.getElementById(field);
                        if (elem) {
                            if (data[field] !== undefined && data[field] !== null) {
                                elem.value = data[field].toString();
                            }
                        }
                    });

                    // Trigger reactive calculations
                    runReactiveCalculations();
                    showDemoStatus(`Successfully loaded customer details at index ${idx}!`, 'success');
                })
                .catch(err => {
                    console.error('Error loading customer:', err);
                    showDemoStatus(`Error: ${err.message}`, 'error');
                })
                .finally(() => {
                    btnLoadDemo.disabled = false;
                });
        });
    }

    function showDemoStatus(msg, type) {
        if (!demoStatus) return;
        demoStatus.style.display = 'block';
        demoStatus.textContent = msg;
        if (type === 'error') {
            demoStatus.style.color = '#EF4444';
        } else if (type === 'success') {
            demoStatus.style.color = '#10B981';
        } else {
            demoStatus.style.color = '#71717A';
        }
    }

    // Run initial calculations
    runReactiveCalculations();

    // Form Submit Handler
    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const submitBtn = form.querySelector('button[type="submit"]');
        const spinner = submitBtn.querySelector('.spinner');
        const btnText = submitBtn.querySelector('.btn-text');
        
        // Results placeholders
        const placeholderCard = document.getElementById('placeholder-result-card');
        const resultCard = document.getElementById('prediction-result-card');
        const recsCard = document.getElementById('recommendations-card');

        // Show spinner, disable button
        if (spinner) spinner.style.display = 'block';
        if (btnText) btnText.style.textContent = 'Analyzing...';
        submitBtn.disabled = true;

        // Collect form data
        const formData = {
            gender: document.getElementById('gender').value,
            SeniorCitizen: parseInt(document.getElementById('SeniorCitizen').value),
            Partner: document.getElementById('Partner').value,
            Dependents: document.getElementById('Dependents').value,
            tenure: parseInt(document.getElementById('tenure').value) || 0,
            PhoneService: document.getElementById('PhoneService').value,
            MultipleLines: document.getElementById('MultipleLines').value,
            InternetService: document.getElementById('InternetService').value,
            OnlineSecurity: document.getElementById('OnlineSecurity').value,
            OnlineBackup: document.getElementById('OnlineBackup').value,
            DeviceProtection: document.getElementById('DeviceProtection').value,
            TechSupport: document.getElementById('TechSupport').value,
            StreamingTV: document.getElementById('StreamingTV').value,
            StreamingMovies: document.getElementById('StreamingMovies').value,
            Contract: document.getElementById('Contract').value,
            PaperlessBilling: document.getElementById('PaperlessBilling').value,
            PaymentMethod: document.getElementById('PaymentMethod').value,
            MonthlyCharges: parseFloat(document.getElementById('MonthlyCharges').value) || 0.0
        };

        fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        .then(res => {
            if (!res.ok) throw new Error('Prediction API failed.');
            return res.json();
        })
        .then(data => {
            // Success: Display results
            if (placeholderCard) placeholderCard.style.display = 'none';
            if (resultCard) {
                resultCard.style.display = 'block';
                
                // Clear risk classes
                resultCard.classList.remove('status-low', 'status-medium', 'status-high');
                
                // Add correct class based on risk
                const probability = data.probability;
                let riskClass = 'status-low';
                if (data.risk_level === 'Medium') riskClass = 'status-medium';
                if (data.risk_level === 'High') riskClass = 'status-high';
                resultCard.classList.add(riskClass);
                
                // Update elements
                document.getElementById('res-customer-id').textContent = data.customer_id;
                document.getElementById('res-probability').textContent = `${probability}%`;
                document.getElementById('res-prediction').textContent = data.prediction;
                document.getElementById('res-badge').textContent = `${data.risk_level} Churn Risk`;
            }

            if (recsCard) {
                recsCard.style.display = 'block';
                const recList = document.getElementById('res-recommendations');
                if (recList) {
                    recList.innerHTML = data.business_recommendations.map(rec => `
                        <li class="recs-item">${rec}</li>
                    `).join('');
                }
            }
        })
        .catch(err => {
            console.error('Error running prediction:', err);
            alert(`Prediction Error: ${err.message}`);
        })
        .finally(() => {
            // Restore button
            if (spinner) spinner.style.display = 'none';
            if (btnText) btnText.textContent = 'Predict Churn Risk';
            submitBtn.disabled = false;
        });
    });
}

/* ========================================================================
PREDICTION HISTORY TABLE & SEARCH
======================================================================== */
let fullHistoryData = [];

function initHistoryTable() {
    const historyBody = document.getElementById('history-table-body');
    const searchInput = document.getElementById('history-search');
    const clearBtn = document.getElementById('clear-history-btn');

    if (!historyBody) return;

    function renderHistoryRows(records) {
        if (!records || records.length === 0) {
            historyBody.innerHTML = `
                <tr>
                    <td colspan="7" class="empty-table-state">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <p>No churn prediction histories recorded.</p>
                    </td>
                </tr>
            `;
            return;
        }

        historyBody.innerHTML = records.map(r => {
            let badgeClass = 'badge-low';
            if (r.risk_level === 'Medium') badgeClass = 'badge-med';
            if (r.risk_level === 'High') badgeClass = 'badge-high';
            
            // Format some key raw details for columns
            const inputs = r.inputs || {};
            const tenure = inputs.tenure !== undefined ? `${inputs.tenure} mo` : 'N/A';
            const charges = inputs.MonthlyCharges !== undefined ? `$${inputs.MonthlyCharges}` : 'N/A';
            const contract = inputs.Contract || 'N/A';

            return `
                <tr>
                    <td style="font-weight: 600;">${r.customer_id}</td>
                    <td>${r.probability}%</td>
                    <td><span class="table-badge ${badgeClass}">${r.risk_level}</span></td>
                    <td style="font-weight: 500;">${r.prediction}</td>
                    <td>${tenure} (${contract})</td>
                    <td>${charges}</td>
                    <td style="color: #71717A; font-size: 0.8rem;">${r.timestamp}</td>
                </tr>
            `;
        }).join('');
    }

    function loadHistoryData() {
        fetch('/history')
            .then(res => res.json())
            .then(data => {
                fullHistoryData = data;
                renderHistoryRows(fullHistoryData);
            })
            .catch(err => {
                console.error('Failed to load history list:', err);
                historyBody.innerHTML = `
                    <tr>
                        <td colspan="7" style="text-align: center; color: #EF4444; padding: 2rem 0;">
                            Error connecting to prediction history backend.
                        </td>
                    </tr>
                `;
            });
    }

    // Attach search filter
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            if (!query) {
                renderHistoryRows(fullHistoryData);
                return;
            }

            const filtered = fullHistoryData.filter(r => {
                const idMatch = r.customer_id.toLowerCase().includes(query);
                const riskMatch = r.risk_level.toLowerCase().includes(query);
                const labelMatch = r.prediction.toLowerCase().includes(query);
                const contractMatch = (r.inputs?.Contract || '').toLowerCase().includes(query);
                return idMatch || riskMatch || labelMatch || contractMatch;
            });
            renderHistoryRows(filtered);
        });
    }

    // Clear history handler
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (confirm('Are you absolutely sure you want to clear all prediction history? This operation is permanent.')) {
                fetch('/history', { method: 'DELETE' })
                    .then(res => res.json())
                    .then(res => {
                        alert(res.message);
                        loadHistoryData();
                    })
                    .catch(err => {
                        console.error('Failed to delete histories:', err);
                        alert('Error clearing histories.');
                    });
            }
        });
    }

    // Fetch on load
    loadHistoryData();
}
