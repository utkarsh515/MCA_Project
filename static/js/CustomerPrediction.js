 
        // File input handling
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const fileName = e.target.files[0] ? e.target.files[0].name : 'No file chosen';
            document.getElementById('fileName').textContent = fileName;
        });

        // Drag and drop functionality
        const dropZone = document.getElementById('dropZone');
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.borderColor = '#4e73df';
            this.style.backgroundColor = 'rgba(78, 115, 223, 0.1)';
        });

        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.style.borderColor = '#d1d3e2';
            this.style.backgroundColor = '#f8f9fc';
        });

        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.borderColor = '#d1d3e2';
            this.style.backgroundColor = '#f8f9fc';
            
            if (e.dataTransfer.files.length) {
                document.getElementById('fileInput').files = e.dataTransfer.files;
                document.getElementById('fileName').textContent = e.dataTransfer.files[0].name;
            }
        });

        // Upload form submission
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const uploadLoading = document.getElementById('uploadLoading');
            const uploadStatus = document.getElementById('uploadStatus');
            
            uploadLoading.style.display = 'block';
            uploadStatus.style.display = 'none';
            
            try {
                const formData = new FormData(this);
                const res = await fetch('/upload_churn', { method: 'POST', body: formData });
                const data = await res.json();
                
                uploadLoading.style.display = 'none';
                uploadStatus.style.display = 'block';
                uploadStatus.innerText = data.message || data.error || 'Upload completed successfully';
                
                if (data.message && data.message.includes('successfully')) {
                    uploadStatus.className = 'mt-3 alert alert-success';
                } else {
                    uploadStatus.className = 'mt-3 alert alert-danger';
                }
            } catch (error) {
                uploadLoading.style.display = 'none';
                uploadStatus.style.display = 'block';
                uploadStatus.className = 'mt-3 alert alert-danger';
                uploadStatus.innerText = 'An error occurred during upload. Please try again.';
            }
        });

        // Customer form submission
        document.getElementById('customerForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const customerLoading = document.getElementById('customerLoading');
            const customerResult = document.getElementById('customerResult');
            
            customerLoading.style.display = 'block';
            customerResult.innerHTML = '';
            
            try {
                const id = document.getElementById('customerId').value;
                const res = await fetch(`/customer/${id}`);
                const data = await res.json();
                
                customerLoading.style.display = 'none';
                
                if (data.error) {
                    customerResult.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                } else {
                    const isChurn = data.Churn === 1;
                    const churnClass = isChurn ? 'churn' : 'no-churn';
                    const churnText = isChurn ? 'Likely to Churn' : 'Not Likely';
                    const churnBadgeClass = isChurn ? 'badge-danger' : 'badge-success';
                    const progressBarClass = isChurn ? 'bg-danger' : 'bg-success';
                    const probability = (data.ChurnProbability * 100).toFixed(2);
                    
                    customerResult.innerHTML = `
                        <div class="result-card ${churnClass}">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h4>Customer ID: ${data.CustomerID}</h4>
                                <span class="status-badge ${churnBadgeClass}">${churnText}</span>
                            </div>
                            <div class="mb-3">
                                <div class="d-flex justify-content-between">
                                    <span>Churn Probability:</span>
                                    <strong>${probability}%</strong>
                                </div>
                                <div class="progress">
                                    <div class="progress-bar ${progressBarClass}" role="progressbar" style="width: ${probability}%" 
                                         aria-valuenow="${probability}" aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                            </div>
                            <div class="d-flex justify-content-between">
                                <span>Rank:</span>
                                <strong>#${data.Rank}</strong>
                            </div>
                        </div>`;
                }
            } catch (error) {
                customerLoading.style.display = 'none';
                customerResult.innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
            }
        });

        // Top N form submission
        document.getElementById('topNForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const topNLoading = document.getElementById('topNLoading');
            const topNResult = document.getElementById('topNResult');
            
            topNLoading.style.display = 'block';
            topNResult.innerHTML = '';
            
            try {
                const n = document.getElementById('topN').value;
                const res = await fetch(`/top_churn/${n}`);
                const data = await res.json();
                
                topNLoading.style.display = 'none';
                
                if (data.error) {
                    topNResult.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                } else {
                    let html = `
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Rank</th>
                                        <th>Customer ID</th>
                                        <th>Churn Probability</th>
                                        <th>Risk Level</th>
                                    </tr>
                                </thead>
                                <tbody>`;
                    
                    data.forEach((c, index) => {
                        const rankClass = index < 3 ? `rank-${index+1}` : '';
                        const probability = (c.churn_probability * 100).toFixed(2);
                        let riskLevel = 'Low';
                        let riskClass = 'success';
                        
                        if (probability >= 80) {
                            riskLevel = 'Very High';
                            riskClass = 'danger';
                        } else if (probability >= 60) {
                            riskLevel = 'High';
                            riskClass = 'warning';
                        } else if (probability >= 40) {
                            riskLevel = 'Medium';
                            riskClass = 'info';
                        }
                        
                        html += `
                            <tr>
                                <td><span class="rank-badge ${rankClass}">${c.rank}</span></td>
                                <td>${c.CustomerID}</td>
                                <td>
                                    <div class="progress" style="height: 8px;">
                                        <div class="progress-bar bg-${riskClass}" role="progressbar" style="width: ${probability}%" 
                                             aria-valuenow="${probability}" aria-valuemin="0" aria-valuemax="100"></div>
                                    </div>
                                    <small>${probability}%</small>
                                </td>
                                <td><span class="badge badge-${riskClass}">${riskLevel}</span></td>
                            </tr>`;
                    });
                    
                    html += `</tbody></table></div>`;
                    topNResult.innerHTML = html;
                }
            } catch (error) {
                topNLoading.style.display = 'none';
                topNResult.innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
            }
        });

