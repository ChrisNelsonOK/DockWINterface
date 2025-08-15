// DokWinterface Configuration Wizard JavaScript

// Wizard state
let currentStep = 1;
let totalSteps = 5;
let formData = {};

// Initialize wizard
document.addEventListener('DOMContentLoaded', function() {
    initializeWizard();
    setupFormValidation();
    setupVolumeManagement();
    setupAutoSave();
});

function initializeWizard() {
    updateProgressBar();
    updateStepVisibility();
    updateNavigationButtons();
    
    // Load any saved configuration
    loadSavedConfig();
    
    // Auto-expand textarea on input
    const textarea = document.getElementById('messageInput');
    if (textarea) {
        textarea.addEventListener('input', autoResizeTextarea);
    }
}

function nextStep() {
    if (validateCurrentStep()) {
        saveCurrentStepData();
        
        if (currentStep < totalSteps) {
            currentStep++;
            updateWizard();
            
            // Special handling for review step
            if (currentStep === 5) {
                generateConfigurationReview();
            }
        }
    }
}

function previousStep() {
    if (currentStep > 1) {
        currentStep--;
        updateWizard();
    }
}

function goToStep(step) {
    if (step >= 1 && step <= totalSteps) {
        // Validate all steps up to the target step
        let canProceed = true;
        for (let i = 1; i < step; i++) {
            if (!validateStep(i)) {
                canProceed = false;
                showNotification(`Please complete step ${i} before proceeding`, 'warning');
                break;
            }
        }
        
        if (canProceed) {
            saveCurrentStepData();
            currentStep = step;
            updateWizard();
            
            if (currentStep === 5) {
                generateConfigurationReview();
            }
        }
    }
}

function updateWizard() {
    updateProgressBar();
    updateStepVisibility();
    updateNavigationButtons();
    updateStepIndicators();
}

function updateProgressBar() {
    const progress = (currentStep / totalSteps) * 100;
    const progressBar = document.getElementById('wizardProgress');
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
    }
}

function updateStepVisibility() {
    const steps = document.querySelectorAll('.wizard-step');
    steps.forEach((step, index) => {
        const stepNumber = index + 1;
        if (stepNumber === currentStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

function updateNavigationButtons() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (prevBtn) {
        prevBtn.style.display = currentStep > 1 ? 'inline-block' : 'none';
    }
    
    if (nextBtn) {
        if (currentStep === totalSteps) {
            nextBtn.style.display = 'none';
        } else {
            nextBtn.style.display = 'inline-block';
            nextBtn.innerHTML = currentStep === totalSteps - 1 ? 
                'Review<i class="fas fa-arrow-right ms-1"></i>' : 
                'Next<i class="fas fa-arrow-right ms-1"></i>';
        }
    }
}

function updateStepIndicators() {
    const stepIndicators = document.querySelectorAll('.step');
    stepIndicators.forEach((indicator, index) => {
        const stepNumber = index + 1;
        indicator.classList.remove('active', 'completed');
        
        if (stepNumber === currentStep) {
            indicator.classList.add('active');
        } else if (stepNumber < currentStep) {
            indicator.classList.add('completed');
        }
    });
    
    // Make step indicators clickable
    stepIndicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => goToStep(index + 1));
    });
}

function validateCurrentStep() {
    return validateStep(currentStep);
}

function validateStep(step) {
    const stepElement = document.querySelector(`[data-step="${step}"]`);
    if (!stepElement) return true;
    
    const requiredFields = stepElement.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
            
            // Show error message
            let errorDiv = field.nextElementSibling;
            if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                field.parentNode.insertBefore(errorDiv, field.nextSibling);
            }
            errorDiv.textContent = 'This field is required';
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            
            // Remove error message
            const errorDiv = field.nextElementSibling;
            if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                errorDiv.remove();
            }
        }
    });
    
    // Step-specific validation
    switch (step) {
        case 1:
            isValid = validateBasicInfo() && isValid;
            break;
        case 2:
            isValid = validateSystemConfig() && isValid;
            break;
        case 3:
            isValid = validateNetworkConfig() && isValid;
            break;
        case 4:
            isValid = validateStorageConfig() && isValid;
            break;
    }
    
    if (!isValid) {
        showNotification('Please fix the errors before continuing', 'error');
    }
    
    return isValid;
}

function validateBasicInfo() {
    const containerName = document.getElementById('containerName').value;
    const password = document.getElementById('password').value;
    
    // Validate container name
    if (containerName && !/^[a-zA-Z0-9][a-zA-Z0-9_-]*$/.test(containerName)) {
        showFieldError('containerName', 'Container name must start with a letter/number and contain only letters, numbers, hyphens, and underscores');
        return false;
    }
    
    // Validate password strength
    if (password && password.length < 8) {
        showFieldError('password', 'Password must be at least 8 characters long');
        return false;
    }
    
    return true;
}

function validateSystemConfig() {
    const diskSize = document.getElementById('diskSize').value;
    
    if (diskSize && (parseInt(diskSize) < 20 || parseInt(diskSize) > 1000)) {
        showFieldError('diskSize', 'Disk size must be between 20GB and 1000GB');
        return false;
    }
    
    return true;
}

function validateNetworkConfig() {
    const rdpPort = document.getElementById('rdpPort').value;
    const vncPort = document.getElementById('vncPort').value;
    
    if (rdpPort && (parseInt(rdpPort) < 1024 || parseInt(rdpPort) > 65535)) {
        showFieldError('rdpPort', 'RDP port must be between 1024 and 65535');
        return false;
    }
    
    if (vncPort && (parseInt(vncPort) < 1024 || parseInt(vncPort) > 65535)) {
        showFieldError('vncPort', 'VNC port must be between 1024 and 65535');
        return false;
    }
    
    if (rdpPort && vncPort && rdpPort === vncPort) {
        showFieldError('vncPort', 'VNC port must be different from RDP port');
        return false;
    }
    
    return true;
}

function validateStorageConfig() {
    // Validate volume mounts
    const volumeMounts = document.querySelectorAll('.volume-mount');
    for (let mount of volumeMounts) {
        const hostPath = mount.querySelector('[data-volume-type="host"]').value;
        const containerPath = mount.querySelector('[data-volume-type="container"]').value;
        
        if ((hostPath && !containerPath) || (!hostPath && containerPath)) {
            showNotification('Both host and container paths must be specified for volume mounts', 'error');
            return false;
        }
        
        if (containerPath && !containerPath.startsWith('/')) {
            showNotification('Container paths must be absolute (start with /)', 'error');
            return false;
        }
    }
    
    return true;
}

function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    field.classList.add('is-invalid');
    
    let errorDiv = field.nextElementSibling;
    if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.insertBefore(errorDiv, field.nextSibling);
    }
    errorDiv.textContent = message;
}

function saveCurrentStepData() {
    const currentStepElement = document.querySelector(`[data-step="${currentStep}"]`);
    if (!currentStepElement) return;
    
    const inputs = currentStepElement.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        if (input.type === 'checkbox') {
            formData[input.name] = input.checked;
        } else {
            formData[input.name] = input.value;
        }
    });
    
    // Save volume mounts separately
    if (currentStep === 4) {
        formData.additional_volumes = collectVolumeMounts();
    }
    
    // Auto-save to localStorage
    localStorage.setItem('wizardFormData', JSON.stringify(formData));
}

function loadSavedConfig() {
    const saved = localStorage.getItem('wizardFormData');
    if (saved) {
        try {
            formData = JSON.parse(saved);
            populateFormFromData(formData);
        } catch (e) {
            console.error('Failed to load saved configuration:', e);
        }
    }
}

function populateFormFromData(data) {
    Object.keys(data).forEach(key => {
        const element = document.querySelector(`[name="${key}"]`);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = data[key];
            } else {
                element.value = data[key];
            }
        }
    });
    
    // Populate volume mounts
    if (data.additional_volumes && Array.isArray(data.additional_volumes)) {
        populateVolumeMounts(data.additional_volumes);
    }
}

// Volume Management
function setupVolumeManagement() {
    // Remove default empty volume mount if it exists
    const defaultMount = document.querySelector('.volume-mount');
    if (defaultMount) {
        const hostInput = defaultMount.querySelector('[data-volume-type="host"]');
        const containerInput = defaultMount.querySelector('[data-volume-type="container"]');
        if (!hostInput.value && !containerInput.value) {
            defaultMount.remove();
        }
    }
}

function addVolumeMount() {
    const container = document.getElementById('volumeContainer');
    const volumeMount = document.createElement('div');
    volumeMount.className = 'volume-mount mb-2';
    volumeMount.innerHTML = `
        <div class="input-group">
            <input type="text" class="form-control bg-dark text-light" placeholder="Host path" data-volume-type="host">
            <span class="input-group-text">:</span>
            <input type="text" class="form-control bg-dark text-light" placeholder="Container path" data-volume-type="container">
            <button class="btn btn-outline-danger" type="button" onclick="removeVolumeMount(this)">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    container.appendChild(volumeMount);
}

function removeVolumeMount(button) {
    const volumeMount = button.closest('.volume-mount');
    volumeMount.remove();
}

function collectVolumeMounts() {
    const volumeMounts = [];
    const mounts = document.querySelectorAll('.volume-mount');
    
    mounts.forEach(mount => {
        const hostPath = mount.querySelector('[data-volume-type="host"]').value;
        const containerPath = mount.querySelector('[data-volume-type="container"]').value;
        
        if (hostPath && containerPath) {
            volumeMounts.push({
                host: hostPath,
                container: containerPath
            });
        }
    });
    
    return volumeMounts;
}

function populateVolumeMounts(volumes) {
    const container = document.getElementById('volumeContainer');
    container.innerHTML = ''; // Clear existing mounts
    
    volumes.forEach(volume => {
        const volumeMount = document.createElement('div');
        volumeMount.className = 'volume-mount mb-2';
        volumeMount.innerHTML = `
            <div class="input-group">
                <input type="text" class="form-control bg-dark text-light" placeholder="Host path" data-volume-type="host" value="${volume.host}">
                <span class="input-group-text">:</span>
                <input type="text" class="form-control bg-dark text-light" placeholder="Container path" data-volume-type="container" value="${volume.container}">
                <button class="btn btn-outline-danger" type="button" onclick="removeVolumeMount(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        container.appendChild(volumeMount);
    });
}

// Configuration Generation and Review
function generateConfigurationReview() {
    saveCurrentStepData();
    
    const reviewContainer = document.getElementById('configReview');
    if (!reviewContainer) return;
    
    const config = {
        ...formData,
        additional_volumes: collectVolumeMounts()
    };
    
    const reviewHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6><i class="fas fa-info-circle me-2"></i>Basic Configuration</h6>
                <table class="table table-dark table-sm">
                    <tr><td>Container Name:</td><td><strong>${config.name || 'Not specified'}</strong></td></tr>
                    <tr><td>Windows Version:</td><td><strong>${config.version || 'Not specified'}</strong></td></tr>
                    <tr><td>Username:</td><td><strong>${config.username || 'Not specified'}</strong></td></tr>
                    <tr><td>Language:</td><td>${config.language || 'en-US'}</td></tr>
                    <tr><td>Keyboard:</td><td>${config.keyboard || 'us'}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6><i class="fas fa-cogs me-2"></i>System Resources</h6>
                <table class="table table-dark table-sm">
                    <tr><td>CPU Cores:</td><td>${config.cpu_cores || '4'}</td></tr>
                    <tr><td>RAM:</td><td>${config.ram_size || '4'} GB</td></tr>
                    <tr><td>Disk Size:</td><td>${config.disk_size || '40'} GB</td></tr>
                    <tr><td>Hardware Acceleration:</td><td>${config.enable_kvm ? 'Enabled' : 'Disabled'}</td></tr>
                    <tr><td>Debug Mode:</td><td>${config.debug ? 'Enabled' : 'Disabled'}</td></tr>
                </table>
            </div>
        </div>
        <div class="row mt-3">
            <div class="col-md-6">
                <h6><i class="fas fa-network-wired me-2"></i>Network Configuration</h6>
                <table class="table table-dark table-sm">
                    <tr><td>RDP Port:</td><td>${config.rdp_port || '3389'}</td></tr>
                    <tr><td>VNC Port:</td><td>${config.vnc_port || '8006'}</td></tr>
                    <tr><td>Network Mode:</td><td>${config.network_mode || 'Default (Bridge)'}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6><i class="fas fa-hdd me-2"></i>Storage Configuration</h6>
                <table class="table table-dark table-sm">
                    <tr><td>Data Volume:</td><td>${config.data_volume || 'None'}</td></tr>
                    <tr><td>Additional Volumes:</td><td>${config.additional_volumes ? config.additional_volumes.length : 0} mount(s)</td></tr>
                </table>
                ${config.additional_volumes && config.additional_volumes.length > 0 ? `
                    <div class="mt-2">
                        <small class="text-muted">Volume Mounts:</small>
                        <ul class="list-unstyled small">
                            ${config.additional_volumes.map(vol => `<li><code>${vol.host}:${vol.container}</code></li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
    
    reviewContainer.innerHTML = reviewHTML;
}

async function generateConfig() {
    saveCurrentStepData();
    
    const config = {
        ...formData,
        additional_volumes: collectVolumeMounts()
    };
    
    // Validate configuration before generating
    const validationResult = await validateConfiguration(config);
    if (!validationResult.valid) {
        showNotification('Configuration validation failed: ' + validationResult.errors.join(', '), 'error');
        return;
    }
    
    if (validationResult.warnings && validationResult.warnings.length > 0) {
        const proceed = confirm('Configuration has warnings:\n' + validationResult.warnings.join('\n') + '\n\nProceed anyway?');
        if (!proceed) return;
    }
    
    setLoading('generateConfigBtn', true);
    
    try {
        const response = await fetch('/api/generate-config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            displayGeneratedFiles(result);
            showNotification('Configuration files generated successfully', 'success');
            
            // Update statistics
            incrementStat('totalConfigs');
        } else {
            throw new Error(result.error || 'Unknown error occurred');
        }
    } catch (error) {
        console.error('Error generating configuration:', error);
        showNotification('Failed to generate configuration: ' + error.message, 'error');
    } finally {
        setLoading('generateConfigBtn', false);
    }
}

async function validateConfiguration(config) {
    try {
        const response = await fetch('/api/validate-config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error validating configuration:', error);
        return {
            valid: false,
            errors: ['Failed to validate configuration: ' + error.message]
        };
    }
}

function displayGeneratedFiles(result) {
    const filesContainer = document.getElementById('generatedFiles');
    const dockerComposeCode = document.getElementById('dockerComposeCode');
    const envFileCode = document.getElementById('envFileCode');
    
    if (filesContainer && dockerComposeCode && envFileCode) {
        dockerComposeCode.textContent = result.docker_compose;
        envFileCode.textContent = result.env_file;
        filesContainer.style.display = 'block';
        
        // Scroll to generated files
        filesContainer.scrollIntoView({ behavior: 'smooth' });
    }
}

async function validateWithAI() {
    saveCurrentStepData();
    
    const config = {
        ...formData,
        additional_volumes: collectVolumeMounts()
    };
    
    const modal = new bootstrap.Modal(document.getElementById('aiValidationModal'));
    modal.show();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: `Please analyze this Windows container configuration and provide recommendations:

Configuration:
${JSON.stringify(config, null, 2)}

Please provide analysis with recommendations, security notes, performance tips, and any warnings.`
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            displayAIAnalysis(result.response);
            incrementStat('aiQueries');
        } else {
            throw new Error(result.error || 'AI analysis failed');
        }
    } catch (error) {
        console.error('Error with AI validation:', error);
        document.getElementById('aiAnalysisContent').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                Failed to get AI analysis: ${error.message}
            </div>
        `;
    }
}

function displayAIAnalysis(analysis) {
    const content = document.getElementById('aiAnalysisContent');
    content.innerHTML = `
        <div class="ai-analysis">
            <div class="mb-3">
                <h6><i class="fas fa-robot me-2"></i>AI Analysis Results</h6>
                <div class="bg-dark p-3 rounded">
                    <pre class="text-light mb-0" style="white-space: pre-wrap;">${analysis}</pre>
                </div>
            </div>
        </div>
    `;
}

async function downloadConfig() {
    saveCurrentStepData();
    
    const config = {
        ...formData,
        additional_volumes: collectVolumeMounts()
    };
    
    try {
        const response = await fetch('/api/download-config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Configuration files saved to server', 'success');
        } else {
            throw new Error(result.error || 'Download failed');
        }
    } catch (error) {
        console.error('Error downloading configuration:', error);
        showNotification('Failed to save configuration files: ' + error.message, 'error');
    }
}

// Form setup and utilities
function setupFormValidation() {
    const form = document.getElementById('wizardForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            nextStep();
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.hasAttribute('required') && !this.value.trim()) {
                    this.classList.add('is-invalid');
                } else {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid') && this.value.trim()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
        });
    }
}

function setupAutoSave() {
    // Auto-save form data every 30 seconds
    setInterval(() => {
        saveCurrentStepData();
    }, 30000);
}

function autoResizeTextarea(event) {
    const textarea = event.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

// Clear wizard data
function clearWizardData() {
    if (confirm('Are you sure you want to clear all configuration data?')) {
        localStorage.removeItem('wizardFormData');
        formData = {};
        location.reload();
    }
}

// Export wizard functions to global scope
window.nextStep = nextStep;
window.previousStep = previousStep;
window.goToStep = goToStep;
window.addVolumeMount = addVolumeMount;
window.removeVolumeMount = removeVolumeMount;
window.generateConfig = generateConfig;
window.validateWithAI = validateWithAI;
window.downloadConfig = downloadConfig;
window.clearWizardData = clearWizardData;
