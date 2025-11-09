// result.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the page with empty data
    initPage();
    
    // Load data from the server
    loadData();
    
    // Customer search form handler
    $('#customer-search-form').on('submit', function(e) {
        e.preventDefault();
        const customerId = $('#customer-id-input').val();
        if (customerId) {
            searchCustomer(customerId);
        }
    });
});

function initPage() {
    // Set initial values to zero or empty
    $('#total-customers').text('0');
    $('#churn-rate').text('0%');
    $('#segment-count').text('0');
}

function loadData() {
    // Load segmentation data if available
    loadSegmentationData();
    
    // Load prediction data if available
    loadPredictionData();
}

function loadSegmentationData() {
    // Check if segmentation data exists in the database
    $.ajax({
        url: '/check_segmentation',
        method: 'GET',
        success: function(data) {
            if (data.exists) {
                updateSegmentationUI(data.images);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error checking segmentation data:', error);
        }
    });
}

function loadPredictionData() {
    // Check if prediction data exists in the database
    $.ajax({
        url: '/check_prediction',
        method: 'GET',
        success: function(data) {
            if (data.exists) {
                updatePredictionUI(data);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error checking prediction data:', error);
        }
    });
}

function updateSegmentationUI(images) {
    // Show segmentation images
    $('#segmentation-placeholder').hide();
    $('#segmentation-results').show();
    
    // Set image sources
    $('#amount-img').attr('src', images.amount_img);
    $('#freq-img').attr('src', images.freq_img);
    $('#recency-img').attr('src', images.recency_img);
    $('#amount-pie').attr('src', images.amount_pie);
    $('#freq-pie').attr('src', images.freq_pie);
    $('#recency-pie').attr('src', images.recency_pie);
    
    // Update segment count (assuming 4 clusters from your model)
    $('#segment-count').text('4');
}

function updatePredictionUI(data) {
    // Update metrics
    if (data.customer_count) {
        $('#total-customers').text(data.customer_count.toLocaleString());
    }
    
    if (data.churn_rate) {
        $('#churn-rate').text(data.churn_rate + '%');
    }
    
    if (data.upload_time) {
        $('#upload-time').text(data.upload_time);
    }
    
    // Load high risk customers
    loadHighRiskCustomers(10);
}

function searchCustomer(customerId) {
    $.ajax({
        url: `/customer/${customerId}`,
        method: 'GET',
        success: function(data) {
            const resultDiv = $('#customer-details');
            if (data.error) {
                resultDiv.html(`
                    <div class="alert alert-danger">
                        ${data.error}
                    </div>
                `);
            } else {
                resultDiv.html(`
                    <div class="alert alert-${data.Churn ? 'danger' : 'success'}">
                        <strong>Customer ID:</strong> ${data.CustomerID}<br>
                        <strong>Churn Prediction:</strong> ${data.Churn ? "Likely to Churn" : "Not Likely"}<br>
                        <strong>Probability:</strong> ${(data.ChurnProbability * 100).toFixed(2)}%<br>
                        <strong>Rank:</strong> ${data.Rank}
                    </div>
                `);
            }
        },
        error: function(xhr, status, error) {
            $('#customer-details').html(`
                <div class="alert alert-danger">
                    Error fetching customer data: ${error}
                </div>
            `);
        }
    });
}

function loadHighRiskCustomers(n) {
    $.ajax({
        url: `/top_churn/${n}`,
        method: 'GET',
        success: function(data) {
            if (data.error) {
                $('#high-risk-table').html(`
                    <tr>
                        <td colspan="4" class="text-center">${data.error}</td>
                    </tr>
                `);
            } else {
                updateHighRiskTable(data);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading high risk customers:', error);
            $('#high-risk-table').html(`
                <tr>
                    <td colspan="4" class="text-center">Error loading data</td>
                </tr>
            `);
        }
    });
}

function updateHighRiskTable(customers) {
    const tableBody = $('#high-risk-table');
    tableBody.empty();
    
    if (customers.length === 0) {
        tableBody.append(`
            <tr>
                <td colspan="4" class="text-center">No high-risk customers found.</td>
            </tr>
        `);
        return;
    }
    
    customers.forEach(customer => {
        let riskClass = 'risk-medium';
        if (customer.churn_probability >= 0.7) riskClass = 'risk-high';
        if (customer.churn_probability <= 0.3) riskClass = 'risk-low';
        
        tableBody.append(`
            <tr>
                <td>${customer.CustomerID}</td>
                <td class="${riskClass}">${(customer.churn_probability * 100).toFixed(2)}%</td>
                <td><span class="badge badge-${riskClass.replace('risk-', '')}">${riskClass.replace('risk-', '')}</span></td>
                <td><button class="btn btn-sm btn-outline-primary view-details" data-id="${customer.CustomerID}">View Details</button></td>
            </tr>
        `);
    });
    
    // Add click handlers for view details buttons
    $('.view-details').on('click', function() {
        const customerId = $(this).data('id');
        $('#customer-id-input').val(customerId);
        searchCustomer(customerId);
    });
}