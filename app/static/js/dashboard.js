document.addEventListener('alpine:init', () => {
    Alpine.data('dashboardApp', () => ({
        // State
        resumes: [],
        coverLetters: [],
        coverLetterStats: {
            total_cover_letters: 0,
            average_score: 0,
            last_updated: null
        },
        averageScore: 0,
        lastUpdated: null,
        isLoading: true,
        activeTab: 'resumes',
        viewMode: 'table',
        searchQuery: '',
        sortBy: 'updated_at',
        sortOrder: 'desc',
        showFilters: false,
        filterCompany: '',
        filterPosition: '',
        filterDateFrom: '',
        filterDateTo: '',
        showDeleteModal: false,
        resumeToDelete: null,
        showScoreModal: false,
        resumeToScore: null,
        jobDescription: '',
        isScoring: false,
        showScoreResultsModal: false,
        scoreResults: {},
        showTailorModal: false,
        isTailoring: false,
        showTemplateModal: false,
        downloadResumeId: null,
        template: 'resume_template.tex',
        
        // Computed properties
        get filteredResumes() {
            return this.filterResumes();
        },
        
        // Initialize the dashboard
        async init() {
            await this.loadResumes();
            await this.loadCoverLetters();
            this.isLoading = false;
            
            // Set up auto-refresh every 5 minutes
            setInterval(() => {
                if (this.activeTab === 'resumes') {
                    this.loadResumes();
                } else {
                    this.loadCoverLetters();
                }
            }, 5 * 60 * 1000);
        },
        
        // Load resumes from the API
        async loadResumes() {
            try {
                const response = await fetch('/api/resume/user/local-user');
                if (response.ok) {
                    this.resumes = await response.json();
                    this.updateResumeStats();
                    this.filterResumes();
                }
            } catch (error) {
                console.error('Error loading resumes:', error);
                this.showNotification('Error loading resumes', 'error');
            }
        },
        
        // Update resume statistics
        updateResumeStats() {
            // Update total resumes count
            this.resumeStats.total_resumes = this.resumes.length;
            
            // Calculate average matching score for all resumes
            // Treat missing or null scores as 0 for the average calculation
            if (this.resumes.length > 0) {
                const totalScore = this.resumes.reduce((sum, r) => sum + (r.matching_score || 0), 0);
                this.averageScore = Math.round(totalScore / this.resumes.length);
            } else {
                this.averageScore = 0;
            }
            
            // Update last updated date
            if (this.resumes.length > 0) {
                const latestResume = this.resumes.reduce((latest, resume) => {
                    const resumeDate = new Date(resume.updated_at || resume.created_at);
                    const latestDate = new Date(latest.updated_at || latest.created_at);
                    return resumeDate > latestDate ? resume : latest;
                });
                this.lastUpdated = new Date(latestResume.updated_at || latestResume.created_at).toLocaleDateString();
            } else {
                this.lastUpdated = 'Never';
            }
        },
        
        // Load cover letters from the API
        async loadCoverLetters() {
            try {
                const response = await fetch('/api/cover-letter/user/local-user');
                if (response.ok) {
                    this.coverLetters = await response.json();
                    this.updateCoverLetterStats();
                }
            } catch (error) {
                console.error('Error loading cover letters:', error);
                this.showNotification('Error loading cover letters', 'error');
            }
        },
        
        // Update cover letter statistics
        updateCoverLetterStats() {
            if (this.coverLetters && this.coverLetters.length > 0) {
                // Calculate total cover letters
                this.coverLetterStats.total_cover_letters = this.coverLetters.length;
                
                // Calculate average score
                const totalScore = this.coverLetters.reduce((sum, letter) => {
                    return sum + (letter.score || 0);
                }, 0);
                this.averageScore = Math.round((totalScore / this.coverLetters.length) * 10) / 10;
                this.coverLetterStats.average_score = this.averageScore;
                
                // Find most recent update
                const lastUpdated = this.coverLetters.reduce((latest, letter) => {
                    const updated = new Date(letter.updated_at || 0);
                    return updated > latest ? updated : latest;
                }, new Date(0));
                
                this.lastUpdated = lastUpdated > new Date(0) ? 
                    this.formatDate(lastUpdated) : 'Never';
                this.coverLetterStats.last_updated = lastUpdated > new Date(0) ? 
                    lastUpdated.toISOString() : null;
            } else {
                this.coverLetterStats = {
                    total_cover_letters: 0,
                    average_score: 0,
                    last_updated: null
                };
                this.averageScore = 0;
                this.lastUpdated = 'Never';
            }
        },
        
        // Filter resumes based on search and filter criteria
        filterResumes() {
            this.filteredResumes = this.resumes.filter(resume => {
                const matchesSearch = !this.searchQuery || 
                    resume.title?.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                    resume.target_company?.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                    resume.target_role?.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                    resume.main_job_title?.toLowerCase().includes(this.searchQuery.toLowerCase());
                
                const matchesCompany = !this.filterCompany || 
                    (resume.target_company && resume.target_company.toLowerCase().includes(this.filterCompany.toLowerCase()));
                
                const matchesPosition = !this.filterPosition || 
                    (resume.target_role && resume.target_role.toLowerCase().includes(this.filterPosition.toLowerCase())) ||
                    (resume.main_job_title && resume.main_job_title.toLowerCase().includes(this.filterPosition.toLowerCase()));
                
                const matchesDate = true; // Add date filtering logic if needed
                
                return matchesSearch && matchesCompany && matchesPosition && matchesDate;
            }).sort((a, b) => {
                let comparison = 0;
                
                if (this.sortBy === 'updated_at') {
                    comparison = new Date(b.updated_at) - new Date(a.updated_at);
                } else if (this.sortBy === 'created_at') {
                    comparison = new Date(b.created_at) - new Date(a.created_at);
                } else if (this.sortBy === 'title') {
                    comparison = (a.job_title || '').localeCompare(b.job_title || '');
                } else if (this.sortBy === 'company') {
                    comparison = (a.company || '').localeCompare(b.company || '');
                } else if (this.sortBy === 'score') {
                    comparison = (a.score || 0) - (b.score || 0);
                }
                
                return this.sortOrder === 'asc' ? comparison : -comparison;
            });
        },
        
        // Toggle sort order
        toggleSortOrder(field) {
            if (this.sortBy === field) {
                this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                this.sortBy = field;
                this.sortOrder = 'asc';
            }
        },
        
        // Show delete confirmation modal
        confirmDelete(resumeId) {
            this.resumeToDelete = resumeId;
            this.showDeleteModal = true;
        },
        
        // View a resume
        viewResume(resumeId) {
            if (!resumeId) {
                console.error('No resume ID provided');
                this.showNotification('Error: No resume ID provided', 'error');
                return;
            }
            // Ensure we're using the correct ID field (_id from MongoDB)
            const id = typeof resumeId === 'object' ? resumeId._id || resumeId.id || resumeId : resumeId;
            window.location.href = `/resume/${id}`;
        },
        
        // Download a resume with error handling
        async downloadResume(resumeId, format = 'pdf') {
            if (!resumeId) {
                console.error('No resume ID provided for download');
                this.showNotification('Error: No resume ID provided for download', 'error');
                return;
            }
            
            // Find the resume to check if it has optimized data
            const resume = this.resumes.find(r => r._id === resumeId);
            if (!resume) {
                this.showNotification('Error: Resume not found', 'error');
                return;
            }
            
            if (!resume.optimized_data) {
                this.showNotification('This resume has not been optimized yet. Please optimize it first.', 'error');
                return;
            }
            
            try {
                // Ensure we're using the correct ID field (_id from MongoDB)
                const id = typeof resumeId === 'object' ? resumeId._id || resumeId.id || resumeId : resumeId;
                this.downloadResumeId = id;
                this.showTemplateModal = true;
                
                // Wait for template selection
                const download = await new Promise((resolve) => {
                    const checkDownload = setInterval(() => {
                        if (!this.showTemplateModal) {
                            clearInterval(checkDownload);
                            resolve(true);
                        }
                    }, 100);
                });
                
                if (download) {
                    const url = `/api/resume/${id}/download?format=${format}&template=${encodeURIComponent(this.template)}&use_optimized=true`;
                    const response = await fetch(url);
                    
                    if (!response.ok) {
                        const error = await response.json().catch(() => ({}));
                        throw new Error(error.detail || 'Failed to download resume');
                    }
                    
                    // Get the filename from the Content-Disposition header or use a default
                    let filename = `resume_${id}.${format}`;
                    const contentDisposition = response.headers.get('Content-Disposition');
                    if (contentDisposition) {
                        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
                        if (filenameMatch && filenameMatch[1]) {
                            filename = filenameMatch[1];
                        }
                    }
                    
                    const blob = await response.blob();
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = downloadUrl;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    
                    // Clean up
                    setTimeout(() => {
                        window.URL.revokeObjectURL(downloadUrl);
                        document.body.removeChild(a);
                    }, 100);
                }
            } catch (error) {
                console.error('Download error:', error);
                this.showNotification(`Download failed: ${error.message}`, 'error');
            }
        },
        
        // Delete a resume with confirmation and error handling
        async deleteResume() {
            if (!this.resumeToDelete) {
                console.error('No resume selected for deletion');
                this.showNotification('Error: No resume selected for deletion', 'error');
                return;
            }
            
            try {
                const response = await fetch(`/api/resume/${this.resumeToDelete}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                });
                
                const responseData = await response.json().catch(() => ({}));
                
                if (response.ok) {
                    // Remove the deleted resume from the local state
                    this.resumes = this.resumes.filter(r => r.id !== this.resumeToDelete && r._id !== this.resumeToDelete);
                    this.updateResumeStats();
                    this.showNotification('Resume deleted successfully', 'success');
                } else {
                    console.error('Failed to delete resume:', responseData);
                    this.showNotification(
                        responseData.detail || 'Failed to delete resume. Please try again.',
                        'error'
                    );
                }
            } catch (error) {
                console.error('Error deleting resume:', error);
                this.showNotification(
                    error.message || 'Error connecting to server. Please try again.',
                    'error'
                );
            } finally {
                // Reset state
                this.showDeleteModal = false;
                this.resumeToDelete = null;
            }
        },
        
        // Show score modal
        showResumeScore(resumeId) {
            this.resumeToScore = resumeId;
            this.jobDescription = '';
            this.showScoreModal = true;
        },
        
        // Submit resume for scoring
        async submitResumeScore() {
            if (!this.jobDescription.trim()) return;
            
            this.isScoring = true;
            
            try {
                const response = await fetch(`/api/resume/${this.resumeToScore}/score`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        job_description: this.jobDescription
                    })
                });
                
                if (response.ok) {
                    this.scoreResults = await response.json();
                    this.showScoreModal = false;
                    this.showScoreResultsModal = true;
                    // Reload resumes to get updated ATS score
                    await this.loadResumes();
                } else {
                    console.error('Failed to score resume');
                    this.showNotification('Failed to score resume', 'error');
                }
            } catch (error) {
                console.error('Error scoring resume:', error);
                this.showNotification('Error connecting to server', 'error');
            } finally {
                this.isScoring = false;
            }
        },
        
        // Update resume status
        async updateStatus(resumeId, newStatus) {
            try {
                const response = await fetch(`/api/resume/${resumeId}/status`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        application_status: newStatus
                    })
                });
                
                if (response.ok) {
                    // Update local state
                    const resume = this.resumes.find(r => r.id === resumeId || r._id === resumeId);
                    if (resume) {
                        resume.application_status = newStatus;
                    }
                    this.showNotification('Status updated successfully', 'success');
                } else {
                    this.showNotification('Failed to update status', 'error');
                }
            } catch (error) {
                console.error('Error updating status:', error);
                this.showNotification('Error updating status', 'error');
            }
        },
        
        // Score resume (alias for showResumeScore)
        scoreResume(resumeId) {
            this.showResumeScore(resumeId);
        },
        
        // Download a resume
        downloadResume(resumeId, format = 'pdf') {
            this.downloadResumeId = resumeId;
            this.showTemplateModal = true;
        },
        
        // Confirm download with selected template
        async confirmDownload() {
            if (!this.downloadResumeId || !this.template) return;
            
            const url = `/api/resume/${this.downloadResumeId}/download?format=pdf&template=${encodeURIComponent(this.template)}`;
            window.open(url, '_blank');
            this.showTemplateModal = false;
            this.downloadResumeId = null;
        },
        
        // Show notification
        showNotification(message, type = 'info') {
            // You can implement a notification system here
            console.log(`[${type}] ${message}`);
            // For now, just use the browser's alert
            alert(`[${type.toUpperCase()}] ${message}`);
        },
        
        // Format date
        formatDate(dateString) {
            if (!dateString) return 'N/A';
            const options = { year: 'numeric', month: 'short', day: 'numeric' };
            return new Date(dateString).toLocaleDateString(undefined, options);
        },
        
        // Format file size
        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },
        
        // Toggle resume status
        async toggleResumeStatus(resumeId, status) {
            try {
                const response = await fetch(`/api/resume/${resumeId}/status/${status}`, {
                    method: 'PUT'
                });
                
                if (response.ok) {
                    const data = await response.json();
                    const resume = this.resumes.find(r => r.id === resumeId);
                    if (resume) {
                        resume.is_applied = data.is_applied;
                        resume.applied_date = data.applied_date;
                        resume.is_answered = data.is_answered;
                        resume.answered_date = data.answered_date;
                    }
                    this.showNotification('Status updated successfully', 'success');
                } else {
                    console.error('Failed to update status');
                    this.showNotification('Failed to update status', 'error');
                }
            } catch (error) {
                console.error('Error updating status:', error);
                this.showNotification('Error connecting to server', 'error');
            }
        },
        
        // Mark resume as applied
        async markAsApplied(resumeId) {
            await this.toggleResumeStatus(resumeId, 'applied');
        },
        
        // Mark resume as answered
        async markAsAnswered(resumeId) {
            await this.toggleResumeStatus(resumeId, 'answered');
        },
        
        // Reset resume status
        async resetStatus(resumeId) {
            await this.toggleResumeStatus(resumeId, 'reset');
        },
        
        // Optimize resume from score
        optimizeResumeFromScore() {
            if (this.resumeToScore) {
                window.location.href = `/resume/${this.resumeToScore}/optimize`;
            }
        },
        
        // Close score results modal
        closeScoreResultsModal() {
            this.showScoreResultsModal = false;
            this.scoreResults = {};
            this.resumeToScore = null;
        },
        
        // Get score color class
        getScoreClass(score) {
            if (score >= 80) return 'text-green-600';
            if (score >= 60) return 'text-yellow-600';
            return 'text-red-600';
        },
        
        // Get score badge class
        getScoreBadgeClass(score) {
            if (score >= 80) return 'bg-green-100 text-green-800';
            if (score >= 60) return 'bg-yellow-100 text-yellow-800';
            return 'bg-red-100 text-red-800';
        },
        
        // Get score level
        getScoreLevel(score) {
            if (score >= 80) return 'Excellent';
            if (score >= 60) return 'Good';
            return 'Needs Improvement';
        }
    }));
});
