// Global flag to prevent duplicate analysis requests
window.isAnalysisInProgress = false;

// Toast notification system
document.addEventListener('DOMContentLoaded', function() {
    window.showToast = function(message, type = 'info', duration = 5000) {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container fixed bottom-4 right-4 z-50';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.setAttribute('x-data', '{ show: true }');
        toast.setAttribute('x-show', 'show');
        toast.setAttribute('x-init', `setTimeout(() => show = false, ${duration})`);
        
        // Set toast styling based on type
        let bgColor, textColor, borderColor, iconSvg;
        switch(type) {
            case 'success':
                bgColor = 'bg-green-50';
                textColor = 'text-green-800';
                borderColor = 'border-green-100';
                iconSvg = '<svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>';
                break;
            case 'error':
                bgColor = 'bg-red-50';
                textColor = 'text-red-800';
                borderColor = 'border-red-100';
                iconSvg = '<svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" /></svg>';
                break;
            case 'warning':
                bgColor = 'bg-yellow-50';
                textColor = 'text-yellow-800';
                borderColor = 'border-yellow-100';
                iconSvg = '<svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>';
                break;
            default:
                bgColor = 'bg-blue-50';
                textColor = 'text-blue-800';
                borderColor = 'border-blue-100';
                iconSvg = '<svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1V9a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>';
        }
        
        // Set toast HTML
        toast.className = `mb-2 p-4 rounded-md shadow-md ${bgColor} ${textColor} border ${borderColor} transform transition-all duration-300 ease-in-out`;
        toast.innerHTML = `
            <div class="flex">
                <div class="flex-shrink-0">
                    ${iconSvg}
                </div>
                <div class="ml-3">
                    <p class="text-sm">${message}</p>
                </div>
                <div class="ml-auto pl-3">
                    <div class="-mx-1.5 -my-1.5">
                        <button @click="show = false" class="inline-flex rounded-md p-1.5 ${textColor} hover:${bgColor} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-${type === 'success' ? 'green' : type === 'error' ? 'red' : type === 'warning' ? 'yellow' : 'blue'}-500">
                            <span class="sr-only">Dismiss</span>
                            <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add to container
        toastContainer.appendChild(toast);
        
        // Initialize Alpine on the new element
        if (window.Alpine) {
            window.Alpine.initTree(toast);
        }
        
        // Remove toast after animation completes
        setTimeout(() => {
            toast.addEventListener('x-collapse:after', () => {
                toast.remove();
            });
        }, duration);
    };

    // Helper functions for common toast types
    window.showSuccessToast = (message, duration = 5000) => window.showToast(message, 'success', duration);
    window.showErrorToast = (message, duration = 5000) => window.showToast(message, 'error', duration);
    window.showWarningToast = (message, duration = 5000) => window.showToast(message, 'warning', duration);
    window.showInfoToast = (message, duration = 5000) => window.showToast(message, 'info', duration);

    // Check for toast headers - this handles toast notifications after redirects or API responses
    const checkToastHeaders = () => {
        // Check for meta tags with toast information
        const message = document.head.querySelector('meta[name="x-toast-message"]')?.getAttribute('content');
        const type = document.head.querySelector('meta[name="x-toast-type"]')?.getAttribute('content') || 'info';
        const duration = document.head.querySelector('meta[name="x-toast-duration"]')?.getAttribute('content') || 5000;

        if (message) {
            window.showToast(message, type, parseInt(duration, 10));
        }
    };

    // Initialize AJAX handlers for toast headers
    const initAjaxToastHandler = () => {
        // Store the original fetch function
        const originalFetch = window.fetch;
        
        // Override the fetch function
        window.fetch = async function(...args) {
            // Call the original fetch function
            const response = await originalFetch(...args);
            
            // Check for toast headers in the response
            const toastMessage = response.headers.get('X-Toast-Message');
            if (toastMessage) {
                const toastType = response.headers.get('X-Toast-Type') || 'info';
                const toastDuration = response.headers.get('X-Toast-Duration') || 5000;
                
                // Show the toast
                window.showToast(toastMessage, toastType, parseInt(toastDuration, 10));
            }
            
            // Return the original response
            return response;
        };

        // Handle XMLHttpRequest for libraries that don't use fetch
        const originalXhrOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function() {
            const xhr = this;
            const originalOnReadyStateChange = xhr.onreadystatechange;
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    const toastMessage = xhr.getResponseHeader('X-Toast-Message');
                    if (toastMessage) {
                        const toastType = xhr.getResponseHeader('X-Toast-Type') || 'info';
                        const toastDuration = xhr.getResponseHeader('X-Toast-Duration') || 5000;
                        
                        // Show the toast
                        window.showToast(toastMessage, toastType, parseInt(toastDuration, 10));
                    }
                }
                
                if (originalOnReadyStateChange) {
                    originalOnReadyStateChange.apply(this, arguments);
                }
            };
            
            originalXhrOpen.apply(this, arguments);
        };
    };

    // Check for toast headers on page load
    checkToastHeaders();
    
    // Initialize AJAX handlers
    initAjaxToastHandler();
});

// Score Resume modal functions
function scoreResume(resumeId) {
    // Set the current resume ID to score
    window.currentResumeId = resumeId;
    
    // Reset the job description field and hide any previous results
    document.getElementById('job-description').value = '';
    
    // Show the modal
    Alpine.store('app').showScoreModal = true;
}

function cancelScoreModal() {
    Alpine.store('app').showScoreModal = false;
    window.currentResumeId = null;
}

async function submitScoreResume() {
    const jobDescription = document.getElementById('job-description').value.trim();
    
    if (!jobDescription) {
        window.showWarningToast('Please enter a job description to score your resume against.');
        return;
    }
    
    if (!window.currentResumeId) {
        window.showErrorToast('No resume selected. Please try again.');
        return;
    }
    
    try {
        // Show loading state
        Alpine.store('app').isScoring = true;
        
        // Call the API to score the resume
        const response = await fetch(`/api/resume/${window.currentResumeId}/score`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                job_description: jobDescription
            })
        });
        
        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }
        
        // Parse the response
        const result = await response.json();
        
        // Update the score results in Alpine store
        Alpine.store('app').scoreResults = {
            ats_score: result.ats_score,
            matching_skills: result.matching_skills || [],
            missing_skills: result.missing_skills || [],
            recommendation: result.recommendation || 'No specific recommendations available.'
        };
        
        // Hide score modal and show results modal
        Alpine.store('app').showScoreModal = false;
        Alpine.store('app').showScoreResultsModal = true;
        
    } catch (error) {
        console.error('Error scoring resume:', error);
        window.showErrorToast('There was a problem scoring your resume. Please try again.');
    } finally {
        Alpine.store('app').isScoring = false;
    }
}

function closeScoreResultsModal() {
    Alpine.store('app').showScoreResultsModal = false;
    window.currentResumeId = null;
}

function optimizeResumeFromScore() {
    if (!window.currentResumeId) {
        window.showErrorToast('Resume ID not found. Please try again.');
        return;
    }
    
    // Close the current modal
    Alpine.store('app').showScoreResultsModal = false;
    
    // Redirect to the optimize page with the resume ID
    window.location.href = `/resume/${window.currentResumeId}/optimize`;
}

// Resume Creator functions
function resumeCreator() {
    return {
        // Initialize and get store reference
        init: function() {
            console.log('resumeCreator initialized');
            this.store = Alpine.store('app');
            window.currentStep = 1;
            
            // Check for master CV from URL parameter
            const urlParams = new URLSearchParams(window.location.search);
            const masterCvId = urlParams.get('master_cv_id');
            
            if (masterCvId) {
                this.loadMasterCV(masterCvId);
            }
        },
        
        // Load master CV details
        loadMasterCV: async function(masterCvId) {
            try {
                const response = await fetch(`/api/resume/master-cv/${masterCvId}`);
                if (response.ok) {
                    const masterCV = await response.json();
                    this.store.isUsingMasterCV = true;
                    this.store.masterCVDetails = masterCV;
                    this.store.resumeFile = masterCV.file_path;
                    this.store.resumeContent = masterCV.master_content || '';
                }
            } catch (error) {
                console.error('Error loading master CV:', error);
            }
        },
        
        // File handling functions
        handleResumeFileChange: function(event) {
            const file = event.target.files[0];
            if (file) {
                this.store.resumeFile = file;
                this.store.isUsingMasterCV = false;
                this.store.masterCVDetails = null;
                
                // Read file content
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.store.resumeContent = e.target.result;
                };
                reader.readAsText(file);
            }
        },
        
        handleResumeDrop: function(event) {
            event.preventDefault();
            this.store.isDraggingResume = false;
            
            const file = event.dataTransfer.files[0];
            if (file) {
                this.store.resumeFile = file;
                this.store.isUsingMasterCV = false;
                this.store.masterCVDetails = null;
                
                // Read file content
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.store.resumeContent = e.target.result;
                };
                reader.readAsText(file);
            }
        },
        
        handleResumeDragOver: function(event) {
            event.preventDefault();
            this.store.isDraggingResume = true;
        },
        
        handleResumeDragLeave: function(event) {
            event.preventDefault();
            this.store.isDraggingResume = false;
        },
        
        // Step management
        nextStep: function() {
            console.log('Moving to next step');
            if (window.currentStep < 5) {
                window.currentStep++;
            }
        },
        
        prevStep: function() {
            console.log('Moving to previous step');
            if (window.currentStep > 1) {
                window.currentStep--;
            }
        },
        
        setStep: function(step) {
            console.log('Setting step to:', step);
            window.currentStep = step;
        },
        
        // Analysis validation
        canProceedToAnalysis: function() {
            return this.store.targetCompany && 
                   this.store.targetRole && 
                   this.store.jobDescription && 
                   (this.store.resumeFile || this.store.isUsingMasterCV);
        },
        
        // Start analysis
        startAnalysis: async function() {
            // Prevent duplicate requests
            if (window.isAnalysisInProgress) {
                console.log('Analysis already in progress, ignoring request');
                return;
            }
            
            window.isAnalysisInProgress = true;
            
            try {
                // Reset analysis state
                this.store.analysisProgress = 0;
                this.store.analysisProgressMessage = 'Starting analysis...';
                this.store.originalScore = 0;
                this.store.matchedSkills = [];
                this.store.missingSkills = [];
                this.store.recommendation = '';
                this.store.matchScore = 0;
                
                // Validate inputs
                if (!this.store.jobDescription || !this.store.resumeContent) {
                    showToast('Please fill in all required fields and upload your resume', 'error');
                    return;
                }
                
                console.log('Starting ATS analysis...');
                
                // Simulate progress
                const progressInterval = setInterval(() => {
                    if (this.store.analysisProgress < 90) {
                        this.store.analysisProgress += 10;
                        if (this.store.analysisProgress <= 25) {
                            this.store.analysisProgressMessage = 'Analyzing resume content...';
                        } else if (this.store.analysisProgress <= 40) {
                            this.store.analysisProgressMessage = 'Matching skills with job description...';
                        } else if (this.store.analysisProgress <= 65) {
                            this.store.analysisProgressMessage = 'Calculating ATS compatibility...';
                        } else if (this.store.analysisProgress <= 85) {
                            this.store.analysisProgressMessage = 'Generating optimization recommendations...';
                        }
                    }
                }, 200);
                
                // Make API call for analysis
                const requestData = {
                    job_description: this.store.jobDescription,
                    resume_text: this.store.resumeContent
                };
                
                const response = await fetch('/api/comprehensive/analyze/ats', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData)
                });
                
                clearInterval(progressInterval);
                this.store.analysisProgress = 100;
                this.store.analysisProgressMessage = 'Analysis complete!';
                
                if (response.ok) {
                    const results = await response.json();
                    console.log('ATS Analysis Results:', results);
                    console.log('Results keys:', Object.keys(results));
                    console.log('Original score:', results.ats_score);
                    console.log('Matched skills:', results.matching_skills);
                    
                    // Map results flexibly since ATS analysis returns different structure
                    this.store.originalScore = results.ats_score || results.score || 0;
                    this.store.matchedSkills = results.matching_skills || results.matched_keywords || results.keywords || [];
                    this.store.missingSkills = results.missing_skills || results.gaps || [];
                    this.store.recommendation = results.recommendation || results.recommendations || '';
                    this.store.matchScore = results.optimized_score || results.ats_score || results.score || 0;
                    
                    console.log('Store updated - Original Score:', this.store.originalScore);
                    console.log('Store updated - Matched Skills:', this.store.matchedSkills);
                    console.log('Store updated - Missing Skills:', this.store.missingSkills);
                    console.log('Store updated - Recommendation:', this.store.recommendation);
                    
                    // Move to results step
                    console.log('Moving to step 3...');
                    setTimeout(() => {
                        // Update Alpine component's currentStep, not window.currentStep
                        const alpineData = document.querySelector('[x-data]').__x.$data;
                        if (alpineData && alpineData.currentStep !== undefined) {
                            alpineData.currentStep = 3;
                        } else {
                            // Fallback to window.currentStep if Alpine data not found
                            window.currentStep = 3;
                        }
                        console.log('Step changed to:', window.currentStep);
                    }, 1000);
                } else {
                    // Get error details from response
                    const errorText = await response.text();
                    console.error('Analysis failed with status:', response.status);
                    console.error('Error response:', errorText);
                    
                    // Handle rate limiting specifically
                    if (response.status === 429) {
                        showToast('Rate limit exceeded. Please wait a moment before trying again.', 'error');
                        return;
                    }
                    
                    throw new Error(`Analysis failed: ${response.status} - ${errorText}`);
                }
            } catch (error) {
                console.error('Analysis error:', error);
                console.error('Error details:', error.message);
                console.error('Error stack:', error.stack);
                
                // Try to get more details from response if available
                if (error.response) {
                    console.error('Response status:', error.response.status);
                    console.error('Response text:', await error.response.text());
                }
                
                showToast('Analysis failed. Please try again.', 'error');
                this.store.analysisProgress = 0;
            } finally {
                // Reset the flag when done
                window.isAnalysisInProgress = false;
            }
        },
        
        // Calculate circumference for score circles
        calculateCircumference: function(score) {
            return Math.round(2 * Math.PI * Math.sqrt(score / 100));
        },
        
        // Getters for all store variables
        get currentStep() { return window.currentStep; },
        get isUsingMasterCV() { return this.store?.isUsingMasterCV || false; },
        get masterCVDetails() { return this.store?.masterCVDetails || null; },
        get resumeFile() { return this.store?.resumeFile || null; },
        get resumeContent() { return this.store?.resumeContent || ''; },
        get isDraggingResume() { return this.store?.isDraggingResume || false; },
        get targetCompany() { return this.store?.targetCompany || ''; },
        get targetRole() { return this.store?.targetRole || ''; },
        get jobDescription() { return this.store?.jobDescription || ''; },
        get analysisProgress() { return this.store?.analysisProgress || 0; },
        get analysisProgressMessage() { return this.store?.analysisProgressMessage || ''; },
        get originalScore() { return this.store?.originalScore || 0; },
        get matchedSkills() { return this.store?.matchedSkills || []; },
        get missingSkills() { return this.store?.missingSkills || []; },
        get recommendation() { return this.store?.recommendation || ''; },
        get matchScore() { return this.store?.matchScore || 0; },
        get selectedTemplate() { return this.store?.selectedTemplate || 'modern'; },
        
        // Setters for store variables
        set targetCompany(value) { if (this.store) this.store.targetCompany = value; },
        set targetRole(value) { if (this.store) this.store.targetRole = value; },
        set jobDescription(value) { if (this.store) this.store.jobDescription = value; },
        set selectedTemplate(value) { if (this.store) this.store.selectedTemplate = value; },
        set resumeContent(value) { if (this.store) this.store.resumeContent = value; }
    };
}

// Analysis functions
function calculateCircumference(score) {
    return Math.round(2 * Math.PI * Math.sqrt(score / 100));
}

// Add Alpine store for managing global state
document.addEventListener('alpine:init', () => {
    // Add global state for preventing duplicate requests
    window.isAnalysisInProgress = false;
    
    Alpine.store('app', {
        // Score modal state
        showScoreModal: false,
        isScoring: false,
        
        // Score results modal state
        showScoreResultsModal: false,
        scoreResults: {
            ats_score: 0,
            matching_skills: [],
            missing_skills: [],
            recommendation: ''
        },
        
        // Resume optimization state
        currentStep: 1,  // Initialize to step 1 (Upload)
        isUsingMasterCV: false,
        masterCVDetails: null,
        
        // File upload state
        resumeFile: null,
        resumeContent: '',
        isDraggingResume: false,
        
        // Analysis state
        targetCompany: '',
        targetRole: '',
        jobDescription: '',
        canProceedToAnalysis: false,
        
        // Analysis progress
        analysisProgress: 0,
        analysisProgressMessage: '',
        
        // Analysis results
        originalScore: 0,
        matchedSkills: [],
        missingSkills: [],
        recommendation: '',
        matchScore: 0,
        
        // Template selection
        selectedTemplate: 'modern'
    });
});
