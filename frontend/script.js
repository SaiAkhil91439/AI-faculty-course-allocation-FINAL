document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const numSectionsInput = document.getElementById('numSections');
    const numSubjectsInput = document.getElementById('numSubjects');
    const sectionsPerFacultyInput = document.getElementById('sectionsPerFaculty');
    const maxSubjectsInput = document.getElementById('maxSubjectsPerFaculty');
    const deanMaxSectionsInput = document.getElementById('deanMaxSections');
    const hodMaxSectionsInput = document.getElementById('hodMaxSections');
    const highExpThresholdInput = document.getElementById('highExpThreshold');
    const lblExpThreshold = document.getElementById('lblExpThreshold');

    if (highExpThresholdInput && lblExpThreshold) {
        highExpThresholdInput.addEventListener('input', () => {
            lblExpThreshold.textContent = highExpThresholdInput.value;
        });
    }

    const calcFacultyRequired = document.getElementById('calcFacultyRequired');
    const calcFormula = document.getElementById('calcFormula');
    const divisibilityBadge = document.getElementById('divisibilityBadge');

    const weightPref = document.getElementById('weightPref');
    const weightExp = document.getElementById('weightExp');
    const weightSkill = document.getElementById('weightSkill');
    const weightQual = document.getElementById('weightQual');
    const weightsTotal = document.getElementById('weightsTotal');

    const valPref = document.getElementById('valPref');
    const valExp = document.getElementById('valExp');
    const valSkill = document.getElementById('valSkill');
    const valQual = document.getElementById('valQual');

    const fileCourse = document.getElementById('fileCourse');
    const fileFaculty = document.getElementById('fileFaculty');
    const filePref = document.getElementById('filePref');
    const fileExp = document.getElementById('fileExp');
    const nameCourse = document.getElementById('nameCourse');
    const nameFaculty = document.getElementById('nameFaculty');
    const namePref = document.getElementById('namePref');
    const nameExp = document.getElementById('nameExp');
    const dropzoneCourse = document.getElementById('dropzoneCourse');
    const dropzoneFaculty = document.getElementById('dropzoneFaculty');
    const dropzonePref = document.getElementById('dropzonePref');
    const dropzoneExp = document.getElementById('dropzoneExp');

    // Upload Mode Elements & Dropzone Controls
    const btnModeCombined = document.getElementById('btnModeCombined');
    const btnModeSplit = document.getElementById('btnModeSplit');
    const containerModeCombined = document.getElementById('containerModeCombined');
    const containerModeSplit = document.getElementById('containerModeSplit');

    const btnClearFacultyFile = document.getElementById('btnClearFacultyFile');
    const btnClearPrefFile = document.getElementById('btnClearPrefFile');
    const btnClearExpFile = document.getElementById('btnClearExpFile');
    const btnClearCourseFile = document.getElementById('btnClearCourseFile');

    const btnViewFacultyFile = document.getElementById('btnViewFacultyFile');
    const btnViewCourseFile = document.getElementById('btnViewCourseFile');
    const btnHeaderViewData = document.getElementById('btnHeaderViewData');
    const btnHeaderChat = document.getElementById('btnHeaderChat');
    const btnBannerViewCharts = document.getElementById('btnBannerViewCharts');

    let currentUploadMode = 'combined'; // 'combined' | 'split'

    if (btnModeCombined && btnModeSplit) {
        btnModeCombined.addEventListener('click', () => {
            currentUploadMode = 'combined';
            btnModeCombined.classList.add('active');
            btnModeSplit.classList.remove('active');
            if (containerModeCombined) containerModeCombined.classList.remove('hidden');
            if (containerModeSplit) containerModeSplit.classList.add('hidden');
            cachedPreviewData = null;
        });

        btnModeSplit.addEventListener('click', () => {
            currentUploadMode = 'split';
            btnModeSplit.classList.add('active');
            btnModeCombined.classList.remove('active');
            if (containerModeSplit) containerModeSplit.classList.remove('hidden');
            if (containerModeCombined) containerModeCombined.classList.add('hidden');
            cachedPreviewData = null;
        });
    }

    const btnValidate = document.getElementById('btnValidate');
    const btnDownloadSample = document.getElementById('btnDownloadSample');
    const btnLogout = document.getElementById('btnLogout');

    if (btnLogout) {
        btnLogout.addEventListener('click', async () => {
            try { await fetch('/api/logout', { method: 'POST' }); }
            finally { window.location.href = '/login'; }
        });
    }

    const allocationForm = document.getElementById('allocationForm');

    const emptyState = document.getElementById('emptyState');
    const loadingState = document.getElementById('loadingState');
    const errorBox = document.getElementById('errorBox');
    const errorMessage = document.getElementById('errorMessage');
    const errorDetails = document.getElementById('errorDetails');
    const resultsContent = document.getElementById('resultsContent');

    // Metrics Display
    const resSections = document.getElementById('resSections');
    const resSubjects = document.getElementById('resSubjects');
    const resFacReq = document.getElementById('resFacReq');
    const resAvgScore = document.getElementById('resAvgScore');

    // Tab Containers
    const matrixTableContainer = document.getElementById('matrixTableContainer');
    const facultyTableContainer = document.getElementById('facultyTableContainer');
    const aiExplanationContent = document.getElementById('aiExplanationContent');
    const traceTimeline = document.getElementById('traceTimeline');

    // 1. Live Calculation of Required Faculty
    function updateCalculatedMetrics() {
        const sections = parseInt(numSectionsInput.value) || 0;
        const perFaculty = parseInt(sectionsPerFacultyInput.value) || 0;

        if (perFaculty > 0 && sections > 0) {
            const required = sections / perFaculty;
            calcFacultyRequired.textContent = `${required} faculty per subject`;
            calcFormula.textContent = `Formula: ${sections} sections / ${perFaculty} sections per faculty`;

            const remainder = sections % perFaculty;
            if (remainder === 0) {
                divisibilityBadge.className = 'divisibility-badge valid';
                divisibilityBadge.innerHTML = '<i class="fa-solid fa-check-circle"></i> Valid Division';
            } else {
                divisibilityBadge.className = 'divisibility-badge invalid';
                divisibilityBadge.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Remainder: ${remainder}`;
            }
        } else {
            calcFacultyRequired.textContent = 'Invalid configuration';
            calcFormula.textContent = 'Sections per faculty must be > 0';
            divisibilityBadge.className = 'divisibility-badge invalid';
            divisibilityBadge.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> Invalid';
        }
    }

    numSectionsInput.addEventListener('input', updateCalculatedMetrics);
    sectionsPerFacultyInput.addEventListener('input', updateCalculatedMetrics);
    updateCalculatedMetrics();

    // 2. Weight Sliders Sync
    function updateWeightDisplays() {
        valPref.textContent = `${weightPref.value}%`;
        valExp.textContent = `${weightExp.value}%`;
        valSkill.textContent = `${weightSkill.value}%`;
        valQual.textContent = `${weightQual.value}%`;

        const total = parseInt(weightPref.value) + parseInt(weightExp.value) + parseInt(weightSkill.value) + parseInt(weightQual.value);
        weightsTotal.textContent = `Total: ${total}%`;
        weightsTotal.style.color = total === 100 ? 'var(--accent)' : 'var(--warning)';
    }

    [weightPref, weightExp, weightSkill, weightQual].forEach(slider => {
        slider.addEventListener('input', updateWeightDisplays);
    });
    updateWeightDisplays();

    function formatFileSize(bytes) {
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    // 3. Dropzone File Pickers & Drag-Drop with File Size and Reset
    function setupDropzone(dropzone, input, nameLabel, clearBtn, defaultText) {
        if (!dropzone || !input) return;

        function setFileSelected(file) {
            if (!file) return;
            nameLabel.innerHTML = `<strong style="color:#f8fafc;">${file.name}</strong> <span style="color:#94a3b8; font-size:11px;">(${formatFileSize(file.size)})</span>`;
            nameLabel.style.color = '#34d399';
            dropzone.classList.add('has-file');
            if (clearBtn) clearBtn.classList.remove('hidden');
            cachedPreviewData = null;
        }

        function resetDropzoneFile() {
            input.value = '';
            nameLabel.textContent = defaultText;
            nameLabel.style.color = '';
            dropzone.classList.remove('has-file');
            if (clearBtn) clearBtn.classList.add('hidden');
            cachedPreviewData = null;
        }

        dropzone.addEventListener('click', (e) => {
            if (e.target.closest('button') || e.target.closest('a')) return;
            input.click();
        });

        input.addEventListener('change', () => {
            if (input.files.length > 0) {
                setFileSelected(input.files[0]);
            } else {
                resetDropzoneFile();
            }
        });

        if (clearBtn) {
            clearBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                resetDropzoneFile();
            });
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                input.files = files;
                setFileSelected(files[0]);
            }
        });
    }

    setupDropzone(dropzoneFaculty, fileFaculty, nameFaculty, btnClearFacultyFile, 'Default: faculty_sample_combined.xlsx');
    setupDropzone(dropzoneCourse, fileCourse, nameCourse, btnClearCourseFile, 'Default: course_details.xlsx');
    if (dropzonePref) setupDropzone(dropzonePref, filePref, namePref, btnClearPrefFile, 'Default: faculty_preferences.xlsx');
    if (dropzoneExp) setupDropzone(dropzoneExp, fileExp, nameExp, btnClearExpFile, 'Default: faculty_experience.xlsx');

    function appendFacultyFilesToForm(formData) {
        if (currentUploadMode === 'combined') {
            if (fileFaculty && fileFaculty.files && fileFaculty.files.length > 0) {
                formData.append('faculty_file', fileFaculty.files[0]);
                formData.append('pref_file', fileFaculty.files[0]);
            }
        } else {
            if (filePref && filePref.files && filePref.files.length > 0) {
                formData.append('pref_file', filePref.files[0]);
            }
            if (fileExp && fileExp.files && fileExp.files.length > 0) {
                formData.append('exp_file', fileExp.files[0]);
            }
        }
        if (fileCourse && fileCourse.files && fileCourse.files.length > 0) {
            formData.append('course_file', fileCourse.files[0]);
        }
    }

    // 4. Download Sample Excel
    btnDownloadSample.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/sample-data', { method: 'POST' });
            if (response.ok) {
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = 'faculty_sample_excel_files.zip';
                document.body.appendChild(a);
                a.click();
                a.remove();
            }
        } catch (err) {
            alert('Failed to download sample data package.');
        }
    });

    // Helper: Show UI States
    function showState(stateName) {
        emptyState.classList.add('hidden');
        loadingState.classList.add('hidden');
        errorBox.classList.add('hidden');
        resultsContent.classList.add('hidden');

        if (stateName === 'loading') loadingState.classList.remove('hidden');
        if (stateName === 'error') errorBox.classList.remove('hidden');
        if (stateName === 'results') resultsContent.classList.remove('hidden');
        if (stateName === 'empty') emptyState.classList.remove('hidden');
    }

    // Helper: Render Error Message
    function showError(title, message, details = []) {
        showState('error');
        document.getElementById('errorTitle').textContent = title;
        errorMessage.textContent = message;
        errorDetails.innerHTML = '';
        if (details && details.length > 0) {
            details.forEach(d => {
                const li = document.createElement('li');
                li.textContent = d;
                errorDetails.appendChild(li);
            });
        }
    }

    // 5. Data Validation Trigger
    btnValidate.addEventListener('click', async () => {
        showState('loading');
        document.getElementById('loadingTitle').textContent = 'Validating Excel Files & Designation Rules...';
        document.getElementById('loadingMessage').textContent = 'Checking Dean (4-6 hrs) & HOD (10-12 hrs) workload constraints and High-Exp (2+1 split) requirements.';

        const formData = new FormData();
        formData.append('num_sections', numSectionsInput.value);
        formData.append('num_subjects', numSubjectsInput.value);
        formData.append('sections_per_faculty', sectionsPerFacultyInput.value);
        formData.append('max_subjects_per_faculty', maxSubjectsInput.value);
        formData.append('dean_max_sections', deanMaxSectionsInput.value);
        formData.append('hod_max_sections', hodMaxSectionsInput.value);
        if (highExpThresholdInput) formData.append('high_exp_threshold', highExpThresholdInput.value);

        // Attach faculty & course files based on active mode
        appendFacultyFilesToForm(formData);

        try {
            const response = await fetch('/api/validate', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (data.success) {
                alert(`Validation Passed!\n\nDeans Found: ${data.summary.deans_count} (Cap: ${data.summary.dean_max_sections} sections)\nHODs Found: ${data.summary.hods_count} (Cap: ${data.summary.hod_max_sections} sections)\nHigh-Exp Faculty (>= ${data.summary.high_exp_threshold} yrs): ${data.summary.high_exp_count}\nCourses Loaded: ${data.summary.courses_loaded}\nTotal Available Faculty: ${data.summary.total_faculty_count}`);
                showState('empty');
            } else {
                showError(data.error_type || 'Validation Failed', data.message, data.details);
            }
        } catch (err) {
            showError('Network / System Error', err.message);
        }
    });

    // 6. Form Submission - Run Allocation Pipeline
    allocationForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        showState('loading');
        document.getElementById('loadingTitle').textContent = 'Running Optimization Engine...';
        document.getElementById('loadingMessage').textContent = 'Solving CP-SAT Model for L-T-P-C contact hours, designation workload limits, and Experienced Faculty 2+1 Section Split.';

        const formData = new FormData();
        formData.append('num_sections', numSectionsInput.value);
        formData.append('num_subjects', numSubjectsInput.value);
        formData.append('sections_per_faculty', sectionsPerFacultyInput.value);
        formData.append('max_subjects_per_faculty', maxSubjectsInput.value);
        formData.append('dean_max_sections', deanMaxSectionsInput.value);
        formData.append('hod_max_sections', hodMaxSectionsInput.value);
        if (highExpThresholdInput) formData.append('high_exp_threshold', highExpThresholdInput.value);

        const totalW = parseInt(weightPref.value) + parseInt(weightExp.value) + parseInt(weightSkill.value) + parseInt(weightQual.value);
        formData.append('weight_pref', parseFloat(weightPref.value) / (totalW || 100));
        formData.append('weight_exp', parseFloat(weightExp.value) / (totalW || 100));
        formData.append('weight_skill', parseFloat(weightSkill.value) / (totalW || 100));
        formData.append('weight_qual', parseFloat(weightQual.value) / (totalW || 100));

        // Attach faculty & course files based on active mode
        appendFacultyFilesToForm(formData);

        try {
            const response = await fetch('/api/allocate', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (data.success) {
                showState('results');
                renderResults(data);
            } else {
                showError(data.error_type || 'Allocation Error', data.message, data.details);
            }
        } catch (err) {
            showError('Allocation Execution Error', err.message);
        }
    });

    // Render Full Allocation Result Views
    function renderResults(data) {
        const summary = data.summary;
        const allocData = data.allocation_data;

        resSections.textContent = summary.num_sections;
        resSubjects.textContent = summary.num_subjects;
        resFacReq.textContent = summary.faculty_required_per_subject;
        resAvgScore.textContent = `${summary.average_score} / 100`;

        // Render Visual Analytics & Charts
        renderAnalyticsCharts(allocData);

        // Render LTPC Workload Analysis Tab
        if (allocData.workload_analysis) {
            currentWorkloadData = allocData.workload_analysis;
            renderWorkloadTab(allocData.workload_analysis);
        } else {
            fetchAndRenderWorkload({ num_sections: summary.num_sections });
        }

        // Dynamically update AI Chat suggestion chips based on real allocation results
        if (allocData.faculty_allocations && allocData.faculty_allocations.length > 0) {
            const fAllocs = allocData.faculty_allocations;
            const f1 = fAllocs[0].Lecture_Faculty_Name;
            const f2 = fAllocs.length > 1 ? fAllocs[1].Lecture_Faculty_Name : null;
            const s1 = fAllocs[0].Subject;
            const smartQuestions = [
                `Tell details of ${f1} allocation`,
                f2 ? `Tell details of ${f2} allocation` : null,
                `Details of ${s1} course allocation`,
                `Show timetable for Section A`,
                `What is the workload pattern across designations?`,
                `Show L-T-P workload component split`
            ].filter(Boolean);
            if (typeof updateSuggestionChips === 'function') {
                updateSuggestionChips(smartQuestions);
            }
        }

        // 1. Matrix View Table with Role Badges & Color Coding
        const subjects = allocData.subjects;
        const sectionNames = allocData.section_names;
        const matrix = allocData.final_allocation_matrix;
        const facAllocs = allocData.faculty_allocations;

        // Build role lookup for faculty
        const roleMap = {};
        facAllocs.forEach(a => {
            roleMap[a.Lecture_Faculty_Name] = a.Lecture_Role || 'Faculty';
        });

        function getRoleBadge(facName) {
            if (!facName) return '';
            const role = roleMap[facName] || '';
            if (role === 'Dean') return '<span class="role-badge-dean">Dean</span>';
            if (role === 'HOD') return '<span class="role-badge-hod">HOD</span>';
            if (role.includes('Professor') && !role.includes('Assistant')) return '<span class="role-badge-prof">Prof</span>';
            if (role.includes('Assistant')) return '<span class="role-badge-asst">Asst Prof</span>';
            return '';
        }

        let matrixHtml = '<table><thead><tr><th>Section</th>';
        subjects.forEach(s => {
            const ltpc = allocData.course_details && allocData.course_details[s] ? allocData.course_details[s]['L-T-P-C'] : '';
            const hrs = allocData.course_details && allocData.course_details[s] ? allocData.course_details[s]['Total_Hours'] : 5;
            matrixHtml += `<th>${s}<br/><small style="color:#38bdf8; font-weight:600;">[${ltpc}] (${hrs}h)</small></th>`;
        });
        matrixHtml += '</tr></thead><tbody>';

        sectionNames.forEach(sec => {
            matrixHtml += `<tr><td class="td-bold">${sec}</td>`;
            subjects.forEach(s => {
                const cellObj = matrix[sec] ? matrix[sec][s] : null;
                if (typeof cellObj === 'object' && cellObj !== null) {
                    const lBadge = getRoleBadge(cellObj.Lecture_Faculty);
                    matrixHtml += `<td class="td-highlight">
                        <strong style="color:#f8fafc;"><i class="fa-solid fa-chalkboard-user" style="color:#38bdf8;"></i> L:</strong> ${cellObj.Lecture_Faculty} ${lBadge}<br/>
                        <small style="color: #94a3b8;">T/P 1: ${cellObj.TP_Faculty_1}</small><br/>
                        <small style="color: #94a3b8;">T/P 2: ${cellObj.TP_Faculty_2}</small>
                    </td>`;
                } else {
                    matrixHtml += `<td class="td-highlight">${cellObj || 'N/A'}</td>`;
                }
            });
            matrixHtml += '</tr>';
        });
        matrixHtml += '</tbody></table>';
        matrixTableContainer.innerHTML = matrixHtml;

        // 2. Faculty Detail View Table
        let facHtml = `<table>
            <thead>
                <tr>
                    <th>Subject & L-T-P-C</th>
                    <th>Sections</th>
                    <th>Lecture (L) Faculty</th>
                    <th>Designation & Role</th>
                    <th>Course Teaching Exp</th>
                    <th>Teaching Workload (hrs/wk)</th>
                    <th>T/P Faculty 1</th>
                    <th>T/P Faculty 2</th>
                    <th>Pref Rank</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>`;

        facAllocs.forEach(row => {
            const isDeanOrHod = row.Lecture_Role === 'Dean' || row.Lecture_Role === 'HOD';
            const isHighExp = row.Is_High_Experience_Split;
            const roleBadge = isDeanOrHod ? `<span class="badge badge-info" style="background:#059669; color:white;">${row.Lecture_Role}</span>` : `<span class="badge badge-info">${row.Lecture_Role}</span>`;
            const expBadge = isHighExp ? `<br/><small style="color: #f59e0b; font-weight: bold;"><i class="fa-solid fa-star"></i> High-Exp Split (${row.Num_Sections} Secs)</small>` : '';

            facHtml += `<tr ${isHighExp ? 'style="background: rgba(245, 158, 11, 0.08);"' : (isDeanOrHod ? 'style="background: rgba(16, 185, 129, 0.08);"' : '')}>
                <td>
                    <span class="badge badge-info">${row.Subject}</span><br/>
                    <small style="color:#38bdf8; font-weight:600;">L-T-P-C: ${row['L-T-P-C'] || '3-0-2-4'} (${row.Total_Course_Hours || 5} hrs/sec)</small>
                </td>
                <td class="td-bold" style="color: #38bdf8;">${row.Sections}</td>
                <td class="td-bold">${row.Lecture_Faculty_Name} ${expBadge}</td>
                <td>${row.Lecture_Designation} ${roleBadge}</td>
                <td><strong style="color: #60a5fa;">${row.Experience_Years || 0} yrs</strong></td>
                <td>
                    <strong style="color: #34d399;">${row.Assigned_Weekly_Hours} hrs/wk</strong><br/>
                    <small style="color: #94a3b8;">Target: ${row.Target_Hours_Range}</small>
                </td>
                <td>${row.TP_Faculty_1_Name}</td>
                <td>${row.TP_Faculty_2_Name}</td>
                <td><span class="badge-rank">Rank ${row.Preference_Rank}</span></td>
                <td><span class="badge-score">${row.Score}</span></td>
            </tr>`;
        });
        facHtml += '</tbody></table>';
        facultyTableContainer.innerHTML = facHtml;

        // 3. AI Explanation
        aiExplanationContent.innerHTML = data.ai_explanation;

        // 4. Execution Trace Steps
        let traceHtml = '';
        data.agent_steps.forEach(step => {
            traceHtml += `<div class="trace-step">
                <div class="step-num"><i class="fa-solid fa-check"></i></div>
                <div class="step-info">
                    <span class="step-title">Step ${step.step}: ${step.action}</span>
                    <span class="step-desc">${step.details}</span>
                </div>
            </div>`;
        });
        traceTimeline.innerHTML = traceHtml;
    }

    // =========================================================================
    // CHART.JS VISUAL ANALYTICS ENGINE & DATA VISUALIZATION
    // =========================================================================
    let latestAllocData = null;
    let chartFacultyLoadInstance = null;
    let chartPreferenceSatInstance = null;
    let chartRoleWorkloadInstance = null;
    let chartSubjectCoverageInstance = null;

    function renderAnalyticsCharts(allocData) {
        if (!allocData) return;
        latestAllocData = allocData;
        if (typeof Chart === 'undefined') return;

        const facAllocs = allocData.faculty_allocations || [];

        // 0. Update Visual Analytics KPI Cards
        const facultySectionsMap = {};
        let rank1Count = 0;
        let highExpCount = 0;

        facAllocs.forEach(a => {
            const name = a.Lecture_Faculty_Name || 'Faculty';
            const numSecs = a.Num_Sections || 0;
            facultySectionsMap[name] = (facultySectionsMap[name] || 0) + numSecs;
            if (a.Preference_Rank === 1) rank1Count++;
            if (a.Is_High_Experience_Split) highExpCount++;
        });

        const facNames = Object.keys(facultySectionsMap);
        const facSections = Object.values(facultySectionsMap);

        const elAllocFac = document.getElementById('analyticsAllocFacultyCount');
        if (elAllocFac) elAllocFac.textContent = `${facNames.length} Faculty`;
        const elAllocSub = document.getElementById('analyticsAllocFacultySub');
        if (elAllocSub) elAllocSub.textContent = `Assigned to ${facAllocs.length} course blocks`;

        const elRank1 = document.getElementById('analyticsRank1Pct');
        const rank1Pct = facAllocs.length > 0 ? Math.round((rank1Count / facAllocs.length) * 1000) / 10 : 0;
        if (elRank1) elRank1.textContent = `${rank1Pct}%`;
        const elRank1Sub = document.getElementById('analyticsRank1Sub');
        if (elRank1Sub) elRank1Sub.textContent = `${rank1Count} of ${facAllocs.length} received 1st choice`;

        const elHighExp = document.getElementById('analyticsHighExpCount');
        if (elHighExp) elHighExp.textContent = `${highExpCount} Faculty`;

        const elAvgScore = document.getElementById('analyticsAvgScoreVal');
        if (elAvgScore) elAvgScore.textContent = `${allocData.average_score || 0} / 100`;

        // 1. Faculty Load Distribution Bar Chart
        const ctxLoad = document.getElementById('chartFacultyLoad');
        if (ctxLoad) {
            if (chartFacultyLoadInstance) chartFacultyLoadInstance.destroy();
            chartFacultyLoadInstance = new Chart(ctxLoad, {
                type: 'bar',
                data: {
                    labels: facNames,
                    datasets: [{
                        label: 'Assigned Sections',
                        data: facSections,
                        backgroundColor: 'rgba(56, 189, 248, 0.75)',
                        borderColor: '#38bdf8',
                        borderWidth: 1.5,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => ` ${ctx.raw} Sections assigned`
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#94a3b8', stepSize: 1 },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        },
                        y: {
                            ticks: { color: '#e2e8f0', font: { size: 11 } },
                            grid: { display: false }
                        }
                    }
                }
            });
        }

        // 2. Preference Satisfaction Doughnut Chart
        const rankCounts = { 'Rank 1': 0, 'Rank 2': 0, 'Rank 3': 0, 'Rank 4+': 0 };
        facAllocs.forEach(a => {
            const r = a.Preference_Rank;
            if (r === 1) rankCounts['Rank 1']++;
            else if (r === 2) rankCounts['Rank 2']++;
            else if (r === 3) rankCounts['Rank 3']++;
            else rankCounts['Rank 4+']++;
        });

        const ctxSat = document.getElementById('chartPreferenceSat');
        if (ctxSat) {
            if (chartPreferenceSatInstance) chartPreferenceSatInstance.destroy();
            chartPreferenceSatInstance = new Chart(ctxSat, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(rankCounts),
                    datasets: [{
                        data: Object.values(rankCounts),
                        backgroundColor: [
                            'rgba(16, 185, 129, 0.85)',
                            'rgba(59, 130, 246, 0.85)',
                            'rgba(245, 158, 11, 0.85)',
                            'rgba(239, 68, 68, 0.85)'
                        ],
                        borderColor: 'rgba(15, 23, 42, 0.9)',
                        borderWidth: 2,
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#cbd5e1', padding: 14, font: { size: 12, weight: '600' } }
                        }
                    }
                }
            });
        }

        // 3. Designation Workload Breakdown Data
        const roleWorkload = {
            'Dean': { totalHrs: 0, count: 0, target: '4-6 hrs' },
            'HOD': { totalHrs: 0, count: 0, target: '10-12 hrs' },
            'Associate Professor': { totalHrs: 0, count: 0, target: '14-16 hrs' },
            'Assistant Professor': { totalHrs: 0, count: 0, target: '16-18 hrs' },
            'Professor': { totalHrs: 0, count: 0, target: '14-16 hrs' }
        };

        facAllocs.forEach(a => {
            const role = a.Lecture_Role || 'Faculty';
            const hrs = a.Assigned_Weekly_Hours || 0;
            if (!roleWorkload[role]) {
                roleWorkload[role] = { totalHrs: 0, count: 0, target: '14-16 hrs' };
            }
            roleWorkload[role].totalHrs += hrs;
            roleWorkload[role].count += 1;
        });

        const activeRoles = Object.keys(roleWorkload).filter(r => roleWorkload[r].count > 0);
        const avgHoursData = activeRoles.map(r => Math.round((roleWorkload[r].totalHrs / roleWorkload[r].count) * 10) / 10);

        const ctxRole = document.getElementById('chartRoleWorkload');
        if (ctxRole) {
            if (chartRoleWorkloadInstance) chartRoleWorkloadInstance.destroy();
            chartRoleWorkloadInstance = new Chart(ctxRole, {
                type: 'bar',
                data: {
                    labels: activeRoles,
                    datasets: [{
                        label: 'Average Weekly Hours',
                        data: avgHoursData,
                        backgroundColor: [
                            'rgba(16, 185, 129, 0.75)',
                            'rgba(139, 92, 246, 0.75)',
                            'rgba(59, 130, 246, 0.75)',
                            'rgba(6, 182, 212, 0.75)',
                            'rgba(245, 158, 11, 0.75)'
                        ],
                        borderColor: [
                            '#10b981', '#8b5cf6', '#3b82f6', '#06b6d4', '#f59e0b'
                        ],
                        borderWidth: 1.5,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => {
                                    const role = ctx.label;
                                    const target = roleWorkload[role] ? roleWorkload[role].target : 'N/A';
                                    return ` Avg Hours: ${ctx.raw} hrs/wk (Target: ${target})`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#e2e8f0', font: { size: 11, weight: '600' } },
                            grid: { display: false }
                        },
                        y: {
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        }
                    }
                }
            });
        }

        // 4. Subject Allocation & Coverage Chart
        const ctxSubject = document.getElementById('chartSubjectCoverage');
        if (ctxSubject) {
            if (chartSubjectCoverageInstance) chartSubjectCoverageInstance.destroy();
            const subjects = allocData.subjects || [];
            const secPerFac = allocData.sections_per_faculty || 3;
            const numSecs = allocData.num_sections || 12;
            const facPerSub = Math.round(numSecs / secPerFac);

            const subHours = subjects.map(s => {
                const cDet = (allocData.course_details && allocData.course_details[s]) || {};
                const hrs = cDet.Total_Hours || 5;
                return hrs * numSecs;
            });
            const facCounts = subjects.map(() => facPerSub);

            chartSubjectCoverageInstance = new Chart(ctxSubject, {
                type: 'bar',
                data: {
                    labels: subjects,
                    datasets: [
                        {
                            label: 'Assigned Faculty Count',
                            data: facCounts,
                            backgroundColor: 'rgba(99, 102, 241, 0.75)',
                            borderColor: '#6366f1',
                            borderWidth: 1.5,
                            borderRadius: 6,
                            yAxisID: 'y'
                        },
                        {
                            type: 'line',
                            label: 'Total Weekly Contact Hours (Dept)',
                            data: subHours,
                            borderColor: '#38bdf8',
                            backgroundColor: 'rgba(56, 189, 248, 0.15)',
                            borderWidth: 2.5,
                            pointRadius: 4,
                            fill: true,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: { color: '#cbd5e1', font: { size: 11 } }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#cbd5e1', font: { size: 11 } },
                            grid: { display: false }
                        },
                        y: {
                            type: 'linear',
                            position: 'left',
                            ticks: { color: '#6366f1', stepSize: 1 },
                            title: { display: true, text: 'Faculty Count', color: '#6366f1' },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        },
                        y1: {
                            type: 'linear',
                            position: 'right',
                            ticks: { color: '#38bdf8' },
                            title: { display: true, text: 'Dept Weekly Hours', color: '#38bdf8' },
                            grid: { display: false }
                        }
                    }
                }
            });
        }
    }

    // =========================================================================
    // LIVE DATA EXPLORER & EXCEL PREVIEW CONTROLLER
    // =========================================================================
    const btnPreviewExcel = document.getElementById('btnPreviewExcel');
    const previewModal = document.getElementById('previewModal');
    const modalCloseBtn = document.getElementById('modalCloseBtn');
    const previewCloseFooterBtn = document.getElementById('previewCloseFooterBtn');
    const previewTabs = document.querySelectorAll('.preview-tab-btn');
    const previewPanes = document.querySelectorAll('.preview-pane');
    const previewSearchInput = document.getElementById('previewSearchInput');
    const previewRoleFilter = document.getElementById('previewRoleFilter');

    let cachedPreviewData = null;
    let chartPreviewRolesInstance = null;
    let chartPreviewCoursesInstance = null;

    async function openDataExplorer(targetTabId = 'previewFaculty') {
        if (!previewModal) return;
        previewModal.classList.remove('hidden');

        // Switch to target preview tab
        if (targetTabId) {
            previewTabs.forEach(t => t.classList.toggle('active', t.getAttribute('data-preview') === targetTabId));
            previewPanes.forEach(p => p.classList.toggle('active', p.id === targetTabId));
        }

        const facContainer = document.getElementById('previewFacultyContainer');
        const courseContainer = document.getElementById('previewCourseContainer');

        if (cachedPreviewData) {
            renderDataExplorer(cachedPreviewData);
            renderPreviewModalCharts(cachedPreviewData);
            return;
        }

        if (facContainer) facContainer.innerHTML = '<p class="preview-placeholder"><i class="fa-solid fa-spinner fa-spin"></i> Loading faculty roster & preferences preview...</p>';
        if (courseContainer) courseContainer.innerHTML = '<p class="preview-placeholder"><i class="fa-solid fa-spinner fa-spin"></i> Loading course curriculum preview...</p>';

        try {
            const formData = new FormData();
            appendFacultyFilesToForm(formData);

            const resp = await fetch('/api/preview-data', {
                method: 'POST',
                body: formData
            });
            const resJson = await resp.json();
            if (resJson.success) {
                cachedPreviewData = resJson;
                renderDataExplorer(resJson);
                renderPreviewModalCharts(resJson);
                return;
            }
        } catch (e) {
            console.warn('Backend preview failed, falling back to local file parse:', e);
        }

        // Fallback to local SheetJS if network failed
        const targetFacultyInput = currentUploadMode === 'combined' ? 'fileFaculty' : 'filePref';
        await loadExcelPreview(targetFacultyInput, 'previewFacultyContainer', 'Faculty Input');
        await loadExcelPreview('fileCourse', 'previewCourseContainer', 'Course Details');
    }

    function renderDataExplorer(data) {
        if (!data) return;
        const query = (previewSearchInput ? previewSearchInput.value : '').toLowerCase().trim();
        const roleFilter = (previewRoleFilter ? previewRoleFilter.value : '').trim();
        const facContainer = document.getElementById('previewFacultyContainer');
        const courseContainer = document.getElementById('previewCourseContainer');
        const statsBar = document.getElementById('previewStatsBar');

        // Render Stats Bar
        if (statsBar && data.faculty && data.courses) {
            const f = data.faculty;
            const c = data.courses;
            statsBar.innerHTML = `
                <div class="preview-stat-chip"><i class="fa-solid fa-users" style="color:#38bdf8;"></i> Total Faculty: <strong>${f.total_count}</strong></div>
                <div class="preview-stat-chip"><i class="fa-solid fa-user-tie" style="color:#10b981;"></i> Deans: <strong>${f.role_counts['Dean'] || 0}</strong></div>
                <div class="preview-stat-chip"><i class="fa-solid fa-user-shield" style="color:#a855f7;"></i> HODs: <strong>${f.role_counts['HOD'] || 0}</strong></div>
                <div class="preview-stat-chip"><i class="fa-solid fa-graduation-cap" style="color:#3b82f6;"></i> Professors: <strong>${(f.role_counts['Professor'] || 0) + (f.role_counts['Associate Professor'] || 0) + (f.role_counts['Assistant Professor'] || 0)}</strong></div>
                <div class="preview-stat-chip"><i class="fa-solid fa-book-bookmark" style="color:#f59e0b;"></i> Total Courses: <strong>${c.total_count}</strong></div>
                <div class="preview-stat-chip"><i class="fa-solid fa-clock" style="color:#10b981;"></i> Total Contact Hours: <strong>${c.total_contact_hours}h</strong></div>
                <div class="preview-stat-chip"><i class="fa-solid fa-award" style="color:#eab308;"></i> Total Credits: <strong>${c.total_c}</strong></div>
            `;
        }

        // Render Faculty Table
        if (facContainer && data.faculty) {
            let filteredRecords = data.faculty.records || [];
            if (roleFilter) {
                filteredRecords = filteredRecords.filter(r =>
                    (r.Role && r.Role.toLowerCase() === roleFilter.toLowerCase()) ||
                    (r.Designation && r.Designation.toLowerCase().includes(roleFilter.toLowerCase()))
                );
            }
            if (query) {
                filteredRecords = filteredRecords.filter(r => 
                    (r.Faculty_Name && r.Faculty_Name.toLowerCase().includes(query)) ||
                    (r.Designation && r.Designation.toLowerCase().includes(query)) ||
                    (r.Role && r.Role.toLowerCase().includes(query)) ||
                    (r.Qualification && r.Qualification.toLowerCase().includes(query)) ||
                    (r.Preferences && r.Preferences.toLowerCase().includes(query)) ||
                    (r.Experience && r.Experience.toLowerCase().includes(query))
                );
            }

            let html = `<table>
                <thead>
                    <tr>
                        <th style="width: 45px;">#</th>
                        <th>Faculty Name</th>
                        <th>Designation</th>
                        <th>Role</th>
                        <th>Qualification</th>
                        <th>Course Preferences</th>
                        <th>Teaching Experience Summary</th>
                    </tr>
                </thead>
                <tbody>`;

            filteredRecords.forEach((r, idx) => {
                const roleBadge = r.Role === 'Dean' ? '<span class="role-badge-dean">Dean</span>' :
                                 (r.Role === 'HOD' ? '<span class="role-badge-hod">HOD</span>' :
                                 (r.Role.includes('Associate') ? '<span class="role-badge-prof">Assoc Prof</span>' :
                                 (r.Role.includes('Assistant') ? '<span class="role-badge-asst">Asst Prof</span>' :
                                 '<span class="role-badge-prof">Prof</span>')));

                html += `<tr>
                    <td style="color:#94a3b8; text-align:center;">${idx + 1}</td>
                    <td class="td-bold">${r.Faculty_Name}</td>
                    <td>${r.Designation}</td>
                    <td>${roleBadge}</td>
                    <td><span class="badge badge-info">${r.Qualification}</span></td>
                    <td style="font-size:12px; color:#cbd5e1;">${r.Preferences}</td>
                    <td style="font-size:12px; color:#38bdf8;">${r.Experience}</td>
                </tr>`;
            });

            if (filteredRecords.length === 0) {
                html += `<tr><td colspan="7" style="text-align:center; padding:20px; color:#94a3b8;">No faculty members match the selected criteria.</td></tr>`;
            }

            html += `</tbody></table>`;
            facContainer.innerHTML = html;
        }

        // Render Course Curriculum Table
        if (courseContainer && data.courses) {
            let filteredCourses = data.courses.records || [];
            if (query) {
                filteredCourses = filteredCourses.filter(c => 
                    (c.Subject && c.Subject.toLowerCase().includes(query)) ||
                    (c['L-T-P-C'] && c['L-T-P-C'].toLowerCase().includes(query))
                );
            }

            let html = `<table>
                <thead>
                    <tr>
                        <th style="width: 45px;">#</th>
                        <th>Course Title</th>
                        <th style="text-align:center;">L</th>
                        <th style="text-align:center;">T</th>
                        <th style="text-align:center;">P</th>
                        <th style="text-align:center;">C</th>
                        <th style="text-align:center;">L-T-P-C</th>
                        <th style="text-align:center;">Contact Hours</th>
                    </tr>
                </thead>
                <tbody>`;

            filteredCourses.forEach((c, idx) => {
                html += `<tr>
                    <td style="color:#94a3b8; text-align:center;">${idx + 1}</td>
                    <td class="td-bold" style="color:#f8fafc;">${c.Subject}</td>
                    <td style="text-align:center; color:#38bdf8; font-weight:600;">${c.L}</td>
                    <td style="text-align:center; color:#f59e0b; font-weight:600;">${c.T}</td>
                    <td style="text-align:center; color:#10b981; font-weight:600;">${c.P}</td>
                    <td style="text-align:center; font-weight:600;">${c.C}</td>
                    <td style="text-align:center;"><span class="badge badge-info">${c['L-T-P-C']}</span></td>
                    <td style="text-align:center; font-weight:700; color:#38bdf8;">${c.Total_Hours} hrs/wk</td>
                </tr>`;
            });

            if (filteredCourses.length === 0) {
                html += `<tr><td colspan="8" style="text-align:center; padding:20px; color:#94a3b8;">No courses match "${query}".</td></tr>`;
            }

            html += `</tbody></table>`;
            courseContainer.innerHTML = html;
        }
    }

    function renderPreviewModalCharts(data) {
        if (!data || typeof Chart === 'undefined') return;

        // 1. Roles & Designation Distribution Chart
        const ctxRoles = document.getElementById('chartPreviewRoles');
        if (ctxRoles && data.faculty && data.faculty.role_counts) {
            if (chartPreviewRolesInstance) chartPreviewRolesInstance.destroy();

            const roles = ['Dean', 'HOD', 'Professor', 'Associate Professor', 'Assistant Professor'];
            const counts = roles.map(r => data.faculty.role_counts[r] || 0);

            chartPreviewRolesInstance = new Chart(ctxRoles, {
                type: 'doughnut',
                data: {
                    labels: roles,
                    datasets: [{
                        data: counts,
                        backgroundColor: [
                            'rgba(16, 185, 129, 0.85)',
                            'rgba(168, 85, 247, 0.85)',
                            'rgba(59, 130, 246, 0.85)',
                            'rgba(56, 189, 248, 0.85)',
                            'rgba(245, 158, 11, 0.85)'
                        ],
                        borderColor: 'rgba(15, 23, 42, 0.9)',
                        borderWidth: 2,
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: { color: '#cbd5e1', padding: 12, font: { size: 11, weight: '600' } }
                        },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => ` ${ctx.label}: ${ctx.raw} Faculty`
                            }
                        }
                    }
                }
            });
        }

        // 2. Course Contact Hours Stacked Bar Chart
        const ctxCourses = document.getElementById('chartPreviewCourses');
        if (ctxCourses && data.courses && data.courses.records) {
            if (chartPreviewCoursesInstance) chartPreviewCoursesInstance.destroy();

            const courses = data.courses.records;
            const labels = courses.map(c => c.Subject.length > 20 ? c.Subject.substring(0, 18) + '...' : c.Subject);
            const lData = courses.map(c => c.L || 0);
            const tData = courses.map(c => c.T || 0);
            const pData = courses.map(c => c.P || 0);

            chartPreviewCoursesInstance = new Chart(ctxCourses, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        { label: 'Lecture (L)', data: lData, backgroundColor: 'rgba(56, 189, 248, 0.85)', borderRadius: 4 },
                        { label: 'Tutorial (T)', data: tData, backgroundColor: 'rgba(245, 158, 11, 0.85)', borderRadius: 4 },
                        { label: 'Practical (P)', data: pData, backgroundColor: 'rgba(16, 185, 129, 0.85)', borderRadius: 4 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            stacked: true,
                            ticks: { color: '#94a3b8', font: { size: 10 } },
                            grid: { display: false }
                        },
                        y: {
                            stacked: true,
                            ticks: { color: '#94a3b8', stepSize: 1 },
                            title: { display: true, text: 'Hours / Week', color: '#64748b' },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: { color: '#cbd5e1', font: { size: 11 } }
                        },
                        tooltip: {
                            callbacks: {
                                afterBody: (items) => {
                                    const idx = items[0].dataIndex;
                                    const c = courses[idx];
                                    return `Total: ${c.Total_Hours} hrs/wk | Credits: ${c.C}`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    if (btnPreviewExcel && previewModal) {
        btnPreviewExcel.addEventListener('click', () => openDataExplorer('previewFaculty'));
        modalCloseBtn.addEventListener('click', () => previewModal.classList.add('hidden'));
        if (previewCloseFooterBtn) {
            previewCloseFooterBtn.addEventListener('click', () => previewModal.classList.add('hidden'));
        }
    }

    if (btnHeaderViewData) {
        btnHeaderViewData.addEventListener('click', () => openDataExplorer('previewFaculty'));
    }

    if (btnViewFacultyFile) {
        btnViewFacultyFile.addEventListener('click', (e) => {
            e.stopPropagation();
            openDataExplorer('previewFaculty');
        });
    }

    if (btnViewCourseFile) {
        btnViewCourseFile.addEventListener('click', (e) => {
            e.stopPropagation();
            openDataExplorer('previewCourse');
        });
    }

    if (previewSearchInput) {
        previewSearchInput.addEventListener('input', () => {
            if (cachedPreviewData) {
                renderDataExplorer(cachedPreviewData);
            }
        });
    }

    if (previewRoleFilter) {
        previewRoleFilter.addEventListener('change', () => {
            if (cachedPreviewData) {
                renderDataExplorer(cachedPreviewData);
            }
        });
    }

    previewTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            previewTabs.forEach(t => t.classList.remove('active'));
            previewPanes.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            const targetId = tab.getAttribute('data-preview');
            const targetPane = document.getElementById(targetId);
            if (targetPane) targetPane.classList.add('active');

            if (targetId === 'previewCharts' && cachedPreviewData) {
                setTimeout(() => {
                    renderPreviewModalCharts(cachedPreviewData);
                    if (chartPreviewRolesInstance) chartPreviewRolesInstance.resize();
                    if (chartPreviewCoursesInstance) chartPreviewCoursesInstance.resize();
                }, 50);
            }
        });
    });

    async function loadExcelPreview(fileInputId, containerId, label) {
        const fileInput = document.getElementById(fileInputId);
        const container = document.getElementById(containerId);
        if (!container) return;

        if (fileInput && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            try {
                const buffer = await file.arrayBuffer();
                if (typeof XLSX !== 'undefined') {
                    const workbook = XLSX.read(buffer, { type: 'array' });
                    const firstSheetName = workbook.SheetNames[0];
                    const worksheet = workbook.Sheets[firstSheetName];
                    const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

                    if (jsonData.length > 0) {
                        let html = `<div style="margin-bottom:10px; color:#34d399; font-size:12px; font-weight:600;"><i class="fa-solid fa-file-excel"></i> File: ${file.name} (${jsonData.length - 1} rows)</div><table><thead><tr>`;
                        const headers = jsonData[0];
                        headers.forEach(h => {
                            html += `<th>${h || ''}</th>`;
                        });
                        html += '</tr></thead><tbody>';

                        for (let i = 1; i < Math.min(jsonData.length, 50); i++) {
                            const row = jsonData[i];
                            html += '<tr>';
                            headers.forEach((_, colIdx) => {
                                const val = row[colIdx] !== undefined ? row[colIdx] : '';
                                html += `<td>${val}</td>`;
                            });
                            html += '</tr>';
                        }
                        html += '</tbody></table>';
                        if (jsonData.length > 50) {
                            html += `<p style="text-align:center; margin-top:8px; font-size:11px; color:#94a3b8;">Showing first 50 rows of ${jsonData.length - 1} total rows.</p>`;
                        }
                        container.innerHTML = html;
                        return;
                    }
                }
            } catch (err) {
                container.innerHTML = `<p class="preview-placeholder" style="color:var(--error);">Failed to parse Excel file: ${err.message}</p>`;
                return;
            }
        }
        container.innerHTML = `<p class="preview-placeholder">No custom ${label} file selected. Click "PREVIEW & VISUALIZE DATA" to load compliant system data.</p>`;
    }

    // Tab Switching with Immediate Chart Sizing & Redraw
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            const targetPane = document.getElementById(tabId);
            if (targetPane) targetPane.classList.add('active');

            if (tabId === 'tabWorkload' && currentWorkloadData) {
                setTimeout(() => renderWorkloadCharts(currentWorkloadData), 60);
            }
            if (tabId === 'tabAnalytics' && latestAllocData) {
                setTimeout(() => renderAnalyticsCharts(latestAllocData), 60);
            }
        });
    });

    if (btnBannerViewCharts) {
        btnBannerViewCharts.addEventListener('click', () => {
            const tabAnalyticsBtn = document.querySelector('[data-tab="tabAnalytics"]');
            if (tabAnalyticsBtn) {
                tabAnalyticsBtn.click();
                const tabPane = document.getElementById('tabAnalytics');
                if (tabPane) tabPane.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    // Window Resize Chart Adaptability
    window.addEventListener('resize', () => {
        if (chartFacultyLoadInstance) chartFacultyLoadInstance.resize();
        if (chartPreferenceSatInstance) chartPreferenceSatInstance.resize();
        if (chartRoleWorkloadInstance) chartRoleWorkloadInstance.resize();
        if (chartSubjectCoverageInstance) chartSubjectCoverageInstance.resize();
        if (chartWorkloadShareInstance) chartWorkloadShareInstance.resize();
        if (chartCourseStackedLoadInstance) chartCourseStackedLoadInstance.resize();
        if (chartSectionLoadDistributionInstance) chartSectionLoadDistributionInstance.resize();
        if (chartPreviewRolesInstance) chartPreviewRolesInstance.resize();
        if (chartPreviewCoursesInstance) chartPreviewCoursesInstance.resize();
    });

    // =========================================================================
    // AI CHATBOT ASSISTANT (FLOATING WIDGET & IN-PAGE CONSOLE)
    // =========================================================================
    const chatWidgetContainer = document.getElementById('chatWidgetContainer');
    const chatTriggerBtn = document.getElementById('chatTriggerBtn');
    const chatDrawer = document.getElementById('chatDrawer');
    const chatCloseBtn = document.getElementById('chatCloseBtn');
    const chatBody = document.getElementById('chatBody');
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');
    const chatSuggestions = document.getElementById('chatSuggestions');

    const inpageChatBody = document.getElementById('inpageChatBody');
    const inpageChatInput = document.getElementById('inpageChatInput');
    const inpageChatSendBtn = document.getElementById('inpageChatSendBtn');
    const inpageChatSuggestions = document.getElementById('inpageChatSuggestions');

    if (chatTriggerBtn && chatDrawer) {
        chatTriggerBtn.addEventListener('click', () => {
            chatDrawer.classList.toggle('hidden');
            if (!chatDrawer.classList.contains('hidden') && chatInput) {
                chatInput.focus();
            }
        });

        chatCloseBtn.addEventListener('click', () => {
            chatDrawer.classList.add('hidden');
        });
    }

    if (btnHeaderChat) {
        btnHeaderChat.addEventListener('click', () => {
            if (chatDrawer) {
                chatDrawer.classList.remove('hidden');
                if (chatInput) chatInput.focus();
            }
        });
    }

    function formatMarkdown(text) {
        if (!text) return '';
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code style="background:rgba(30,41,59,0.8); padding:2px 6px; border-radius:4px; font-family:monospace; color:#38bdf8;">$1</code>')
            .replace(/^### (.*$)/gim, '<h4 style="margin:8px 0 4px 0; color:#38bdf8; font-size:14px; font-weight:700;">$1</h4>')
            .replace(/^## (.*$)/gim, '<h3 style="margin:10px 0 6px 0; color:#38bdf8; font-size:15px; font-weight:700;">$1</h3>')
            .replace(/^# (.*$)/gim, '<h2 style="margin:12px 0 6px 0; color:#38bdf8; font-size:16px; font-weight:700;">$1</h2>')
            .replace(/^\> (.*$)/gim, '<blockquote style="border-left:3px solid #38bdf8; padding-left:10px; margin:6px 0; color:#94a3b8; font-style:italic;">$1</blockquote>')
            .replace(/^\- (.*$)/gim, '<li style="margin-left:16px; margin-bottom:3px;">$1</li>')
            .replace(/^\d+\.\s(.*$)/gim, '<li style="margin-left:16px; list-style-type:decimal; margin-bottom:3px;">$1</li>');

        // Markdown Table parsing
        if (formatted.includes('|')) {
            const lines = formatted.split('\n');
            let inTable = false;
            let isHeader = true;
            let tableHtml = '<div style="overflow-x:auto; margin:8px 0;"><table style="width:100%; border-collapse:collapse; font-size:12px; background:rgba(15,23,42,0.6); border-radius:6px; overflow:hidden;">';
            let newLines = [];
            lines.forEach(line => {
                const trimmed = line.trim();
                if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
                    if (trimmed.includes('---')) {
                        isHeader = false;
                        return; // separator row
                    }
                    if (!inTable) {
                        inTable = true;
                        isHeader = true;
                    }
                    const cols = trimmed.slice(1, -1).split('|').map(c => c.trim());
                    if (isHeader) {
                        tableHtml += '<thead style="background:rgba(30,41,59,0.9);"><tr style="border-bottom:1px solid rgba(255,255,255,0.1);">';
                        cols.forEach(c => { tableHtml += `<th style="padding:6px 8px; text-align:left; color:#38bdf8;">${c}</th>`; });
                        tableHtml += '</tr></thead><tbody>';
                        isHeader = false;
                    } else {
                        tableHtml += '<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">';
                        cols.forEach(c => { tableHtml += `<td style="padding:5px 8px; color:#e2e8f0;">${c}</td>`; });
                        tableHtml += '</tr>';
                    }
                } else {
                    if (inTable) {
                        tableHtml += '</tbody></table></div>';
                        newLines.push(tableHtml);
                        tableHtml = '<div style="overflow-x:auto; margin:8px 0;"><table style="width:100%; border-collapse:collapse; font-size:12px; background:rgba(15,23,42,0.6); border-radius:6px; overflow:hidden;">';
                        inTable = false;
                        isHeader = true;
                    }
                    newLines.push(line);
                }
            });
            if (inTable) {
                tableHtml += '</tbody></table></div>';
                newLines.push(tableHtml);
            }
            formatted = newLines.join('<br/>');
        }

        return formatted.replace(/\n/g, '<br/>');
    }

    function appendChatMessage(sender, text) {
        const createMsgEl = () => {
            const msgDiv = document.createElement('div');
            msgDiv.className = `chat-message ${sender === 'user' ? 'user-msg' : 'assistant-msg'}`;

            const avatar = document.createElement('div');
            avatar.className = 'msg-avatar';
            avatar.innerHTML = sender === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';

            const bubble = document.createElement('div');
            bubble.className = 'msg-bubble';
            bubble.innerHTML = sender === 'user' ? text : formatMarkdown(text);

            msgDiv.appendChild(avatar);
            msgDiv.appendChild(bubble);
            return msgDiv;
        };

        if (chatBody) {
            chatBody.appendChild(createMsgEl());
            chatBody.scrollTop = chatBody.scrollHeight;
        }

        if (inpageChatBody) {
            inpageChatBody.appendChild(createMsgEl());
            inpageChatBody.scrollTop = inpageChatBody.scrollHeight;
        }
    }

    function updateSuggestionChips(questions) {
        if (!questions || !Array.isArray(questions)) return;

        const populateContainer = (container) => {
            if (!container) return;
            container.innerHTML = '';
            questions.forEach(sq => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'chip-btn';
                btn.setAttribute('data-query', sq);
                btn.textContent = sq;
                container.appendChild(btn);
            });
        };

        populateContainer(chatSuggestions);
        populateContainer(inpageChatSuggestions);
    }

    async function sendUserChatMessage(questionText, source = 'floating') {
        let query = (questionText || '').trim();
        if (!query) {
            query = source === 'inpage' 
                ? (inpageChatInput ? inpageChatInput.value.trim() : '')
                : (chatInput ? chatInput.value.trim() : '');
        }

        if (!query) return;

        appendChatMessage('user', query);
        if (chatInput) chatInput.value = '';
        if (inpageChatInput) inpageChatInput.value = '';

        // Add typing indicators
        const addIndicator = (container, id) => {
            if (!container) return;
            const typingDiv = document.createElement('div');
            typingDiv.className = 'chat-message assistant-msg';
            typingDiv.id = id;
            typingDiv.innerHTML = `<div class="msg-avatar"><i class="fa-solid fa-robot"></i></div><div class="msg-bubble"><em><i class="fa-solid fa-spinner fa-spin"></i> Analyzing allocation data...</em></div>`;
            container.appendChild(typingDiv);
            container.scrollTop = container.scrollHeight;
        };

        addIndicator(chatBody, 'typingIndicatorFloating');
        addIndicator(inpageChatBody, 'typingIndicatorInpage');

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: query })
            });
            const data = await res.json();

            const ind1 = document.getElementById('typingIndicatorFloating');
            if (ind1) ind1.remove();
            const ind2 = document.getElementById('typingIndicatorInpage');
            if (ind2) ind2.remove();

            if (data.answer) {
                appendChatMessage('assistant', data.answer);
            } else {
                appendChatMessage('assistant', '⚠️ Unable to process chat request.');
            }

            if (data.suggested_questions && data.suggested_questions.length > 0) {
                updateSuggestionChips(data.suggested_questions);
            }
        } catch (err) {
            const ind1 = document.getElementById('typingIndicatorFloating');
            if (ind1) ind1.remove();
            const ind2 = document.getElementById('typingIndicatorInpage');
            if (ind2) ind2.remove();
            appendChatMessage('assistant', '❌ Network error connecting to chat assistant.');
        }
    }

    // Floating Chat Listeners
    if (chatSendBtn) {
        chatSendBtn.addEventListener('click', () => sendUserChatMessage('', 'floating'));
    }

    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendUserChatMessage('', 'floating');
        });
    }

    // In-Page Chat Listeners
    if (inpageChatSendBtn) {
        inpageChatSendBtn.addEventListener('click', () => sendUserChatMessage('', 'inpage'));
    }

    if (inpageChatInput) {
        inpageChatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendUserChatMessage('', 'inpage');
        });
    }

    // Suggestion Chips Click Delegation
    function setupChipDelegation(container) {
        if (!container) return;
        container.addEventListener('click', (e) => {
            const btn = e.target.closest('.chip-btn');
            if (btn) {
                const q = btn.getAttribute('data-query') || btn.textContent.trim();
                if (q) sendUserChatMessage(q);
            }
        });
    }
    setupChipDelegation(chatSuggestions);
    setupChipDelegation(inpageChatSuggestions);

    // =========================================================================
    // LTPC WORKLOAD CALCULATION & DASHBOARD CONTROLLER
    // =========================================================================

    const DEFAULT_PROMPT_COURSES = [
        { course_title: "Advanced Linear Algebra and Optimization", l: 2, t: 2, p: 2, c: 4, ltpc: "2-2-2-4" },
        { course_title: "Full Stack AI Application Development", l: 0, t: 2, p: 2, c: 3, ltpc: "0-2-2-3" },
        { course_title: "Open Elective - 1", l: 2, t: 2, p: 0, c: 3, ltpc: "2-2-0-3" },
        { course_title: "Algorithm Design and Analysis", l: 2, t: 2, p: 2, c: 4, ltpc: "2-2-2-4" },
        { course_title: "Machine Learning", l: 3, t: 0, p: 2, c: 4, ltpc: "3-0-2-4" },
        { course_title: "Operating Systems", l: 2, t: 0, p: 2, c: 3, ltpc: "2-0-2-3" },
        { course_title: "Digital Logic and Computer Organization", l: 2, t: 0, p: 2, c: 3, ltpc: "2-0-2-3" }
    ];

    let currentWorkloadData = null;
    let modalCoursesList = JSON.parse(JSON.stringify(DEFAULT_PROMPT_COURSES));

    let chartWorkloadShareInstance = null;
    let chartCourseStackedLoadInstance = null;
    let chartSectionLoadDistributionInstance = null;

    // Elements in Tab
    const displayFormulaSection = document.getElementById('displayFormulaSection');
    const displayFormulaDept = document.getElementById('displayFormulaDept');
    const displayNumSectionsLabel = document.getElementById('displayNumSectionsLabel');
    const wlInputSections = document.getElementById('wlInputSections');
    const wlInputLFac = document.getElementById('wlInputLFac');
    const wlInputTFac = document.getElementById('wlInputTFac');
    const wlInputPFac = document.getElementById('wlInputPFac');
    const wlInputFacultyCap = document.getElementById('wlInputFacultyCap');
    const btnRecalculateWorkload = document.getElementById('btnRecalculateWorkload');
    const btnResetToPromptCourses = document.getElementById('btnResetToPromptCourses');
    const btnQuickCalcWorkload = document.getElementById('btnQuickCalcWorkload');
    const btnOpenWorkloadCalculator = document.getElementById('btnOpenWorkloadCalculator');

    // Efficiency Dashboard & Interactive Sliders
    const wlSliderSections = document.getElementById('wlSliderSections');
    const lblValSections = document.getElementById('lblValSections');
    const wlSliderLFac = document.getElementById('wlSliderLFac');
    const lblValLFac = document.getElementById('lblValLFac');
    const wlSliderTFac = document.getElementById('wlSliderTFac');
    const lblValTFac = document.getElementById('lblValTFac');
    const wlSliderPFac = document.getElementById('wlSliderPFac');
    const lblValPFac = document.getElementById('lblValPFac');
    const wlSliderAvailFaculty = document.getElementById('wlSliderAvailFaculty');
    const wlInputAvailFaculty = document.getElementById('wlInputAvailFaculty');
    const lblValAvailFac = document.getElementById('lblValAvailFac');
    const wlSliderFacultyCap = document.getElementById('wlSliderFacultyCap');
    const lblValCap = document.getElementById('lblValCap');

    const btnPresetBaseline = document.getElementById('btnPresetBaseline');
    const btnPresetDualBatch = document.getElementById('btnPresetDualBatch');
    const btnPresetBlended = document.getElementById('btnPresetBlended');
    const btnPresetAICTE = document.getElementById('btnPresetAICTE');

    const effStatusPill = document.getElementById('effStatusPill');
    const effStatusText = document.getElementById('effStatusText');
    const effScoreVal = document.getElementById('effScoreVal');
    const effScoreBadge = document.getElementById('effScoreBadge');
    const effScoreBar = document.getElementById('effScoreBar');
    const effUtilVal = document.getElementById('effUtilVal');
    const effUtilDetails = document.getElementById('effUtilDetails');
    const effUtilBar = document.getElementById('effUtilBar');
    const effBalanceVal = document.getElementById('effBalanceVal');
    const effBalanceSub = document.getElementById('effBalanceSub');
    const effDeltaTag = document.getElementById('effDeltaTag');
    const effRatioVal = document.getElementById('effRatioVal');
    const effRatioDetails = document.getElementById('effRatioDetails');
    const scenariosGrid = document.getElementById('scenariosGrid');

    const btnWlAddCourse = document.getElementById('btnWlAddCourse');
    const btnWlResetPrompt = document.getElementById('btnWlResetPrompt');

    const wlTotalL = document.getElementById('wlTotalL');
    const wlDeptL = document.getElementById('wlDeptL');
    const wlTotalT = document.getElementById('wlTotalT');
    const wlDeptT = document.getElementById('wlDeptT');
    const wlTotalP = document.getElementById('wlTotalP');
    const wlDeptP = document.getElementById('wlDeptP');
    const wlTotalC = document.getElementById('wlTotalC');
    const wlTotalCoursesCount = document.getElementById('wlTotalCoursesCount');
    const wlSectionTotal = document.getElementById('wlSectionTotal');
    const wlDeptTotal = document.getElementById('wlDeptTotal');
    const wlEstimatedFaculty = document.getElementById('wlEstimatedFaculty');
    const lblLastSection = document.getElementById('lblLastSection');

    const workloadCourseTableContainer = document.getElementById('workloadCourseTableContainer');
    const workloadSectionTableContainer = document.getElementById('workloadSectionTableContainer');

    // Modal Elements
    const workloadCalculatorModal = document.getElementById('workloadCalculatorModal');
    const modalCloseWorkloadBtn = document.getElementById('modalCloseWorkloadBtn');
    const mBtnCloseFooter = document.getElementById('mBtnCloseFooter');
    const mBtnAddCourse = document.getElementById('mBtnAddCourse');
    const mBtnResetCourses = document.getElementById('mBtnResetCourses');
    const mBtnDownloadExcel = document.getElementById('mBtnDownloadExcel');
    const mBtnApplyToAllocation = document.getElementById('mBtnApplyToAllocation');
    const modalCoursesTbody = document.getElementById('modalCoursesTbody');
    const mInputSections = document.getElementById('mInputSections');
    const mInputLFac = document.getElementById('mInputLFac');
    const mInputTFac = document.getElementById('mInputTFac');
    const mInputPFac = document.getElementById('mInputPFac');
    const mFormulaSec = document.getElementById('mFormulaSec');
    const mFormulaDept = document.getElementById('mFormulaDept');
    const mKpiL = document.getElementById('mKpiL');
    const mKpiT = document.getElementById('mKpiT');
    const mKpiP = document.getElementById('mKpiP');
    const mKpiSec = document.getElementById('mKpiSec');
    const mKpiDept = document.getElementById('mKpiDept');
    const mKpiFac = document.getElementById('mKpiFac');

    // Helper: Calculate Local Workload Object from Array of Courses with Efficiency Metrics
    function calculateLocalWorkload(courses, numSecs, lFac, tFac, pFac, capHours, availFac) {
        numSecs = Math.max(1, parseInt(numSecs) || 12);
        lFac = Math.max(1, parseInt(lFac) || 1);
        tFac = Math.max(1, parseInt(tFac) || 3);
        pFac = Math.max(1, parseInt(pFac) || 3);
        capHours = Math.max(1, parseFloat(capHours) || 15);
        availFac = Math.max(1, parseInt(availFac) || 34);

        let totL = 0, totT = 0, totP = 0, totC = 0;
        const processed = courses.map((c, idx) => {
            const l = Math.max(0, parseInt(c.l) || 0);
            const t = Math.max(0, parseInt(c.t) || 0);
            const p = Math.max(0, parseInt(c.p) || 0);
            const cred = Math.max(0, parseInt(c.c) || 0);

            totL += l;
            totT += t;
            totP += p;
            totC += cred;

            const secL = l * lFac;
            const secT = t * tFac;
            const secP = p * pFac;
            const secTot = secL + secT + secP;

            return {
                sl_no: idx + 1,
                course_title: c.course_title || `Course ${idx + 1}`,
                l, t, p, c: cred,
                contact_hours: l + t + p,
                l_faculty: lFac,
                t_faculty: tFac,
                p_faculty: pFac,
                sec_l_load: secL,
                sec_t_load: secT,
                sec_p_load: secP,
                sec_total_workload: secTot,
                dept_l_load: secL * numSecs,
                dept_t_load: secT * numSecs,
                dept_p_load: secP * numSecs,
                dept_total_workload: secTot * numSecs
            };
        });

        const secL = totL * lFac;
        const secT = totT * tFac;
        const secP = totP * pFac;
        const secTot = secL + secT + secP;
        const deptL = secL * numSecs;
        const deptT = secT * numSecs;
        const deptP = secP * numSecs;
        const deptTot = secTot * numSecs;

        processed.forEach(c => {
            c.dept_share_pct = deptTot > 0 ? Math.round((c.dept_total_workload / deptTot) * 1000) / 10 : 0;
        });

        const sections = [];
        let cum = 0;
        for (let i = 0; i < numSecs; i++) {
            cum += secTot;
            sections.push({
                section_name: `Section ${getSectionName(i)}`,
                num_courses: processed.length,
                l_hours: secL,
                t_hours: secT,
                p_hours: secP,
                section_total_workload: secTot,
                cumulative_dept_workload: cum
            });
        }

        const estFac = Math.round((deptTot / capHours) * 10) / 10;
        const availCapHours = Math.round(availFac * capHours * 10) / 10;
        const utilPct = availCapHours > 0 ? Math.round((deptTot / availCapHours) * 1000) / 10 : 0;

        let effScore = 100;
        if (utilPct <= 100) {
            effScore = Math.max(30, Math.round((100 - (100 - utilPct) * 0.35) * 10) / 10);
        } else {
            effScore = Math.max(25, Math.round((100 - (utilPct - 100) * 0.40) * 10) / 10);
        }

        let effStatus = "Optimal Workload Balance";
        let effStatusBadge = "status-success";
        if (utilPct <= 80) {
            effStatus = "Underutilized (Surplus Staff)";
            effStatusBadge = "status-info";
        } else if (utilPct <= 105) {
            effStatus = "Optimal Workload Balance";
            effStatusBadge = "status-success";
        } else if (utilPct <= 130) {
            effStatus = "High Contact Demand";
            effStatusBadge = "status-warning";
        } else {
            effStatus = "Critical Overload (Faculty Deficit)";
            effStatusBadge = "status-danger";
        }

        const facDeficit = Math.max(0, Math.round((estFac - availFac) * 10) / 10);
        const facSurplus = Math.max(0, Math.round((availFac - estFac) * 10) / 10);
        const contactRatio = Math.round((totL / Math.max(1, (totT + totP))) * 100) / 100;

        // Optimization Scenarios
        const scenarioDefs = [
            { name: "Institutional Model", code: "1-3-3", desc: "1 L, 3 T, 3 P fac/sec (Current Prompt)", l_fac: 1, t_fac: 3, p_fac: 3 },
            { name: "Dual-Batch Optimized", code: "1-2-2", desc: "1 L, 2 T, 2 P fac/sec (Balanced Lab Coverage)", l_fac: 1, t_fac: 2, p_fac: 2 },
            { name: "Blended Core", code: "1-1-2", desc: "1 L, 1 T, 2 P fac/sec (Lecture + Dual Lab)", l_fac: 1, t_fac: 1, p_fac: 2 },
            { name: "Compact AICTE Norm", code: "1-1-1", desc: "1 L, 1 T, 1 P fac/sec (Single Faculty Baseline)", l_fac: 1, t_fac: 1, p_fac: 1 }
        ];

        const scenarios = scenarioDefs.map(sc => {
            const scSec = (totL * sc.l_fac) + (totT * sc.t_fac) + (totP * sc.p_fac);
            const scDept = scSec * numSecs;
            const scFac = Math.round((scDept / capHours) * 10) / 10;
            const scSaved = Math.max(0, deptTot - scDept);
            const scSavedPct = deptTot > 0 ? Math.round((scSaved / deptTot) * 1000) / 10 : 0;
            const isActive = (sc.l_fac === lFac && sc.t_fac === tFac && sc.p_fac === pFac);
            return {
                ...sc,
                section_workload: scSec,
                dept_workload: scDept,
                faculty_required: scFac,
                hours_saved: scSaved,
                savings_percent: scSavedPct,
                is_active: isActive
            };
        });

        return {
            num_sections: numSecs,
            l_faculty_multiplier: lFac,
            t_faculty_multiplier: tFac,
            p_faculty_multiplier: pFac,
            avg_faculty_capacity_hours: capHours,
            num_available_faculty: availFac,
            available_capacity_hours: availCapHours,
            capacity_utilization_pct: utilPct,
            workload_efficiency_score: effScore,
            efficiency_status: effStatus,
            efficiency_status_badge: effStatusBadge,
            faculty_deficit: facDeficit,
            faculty_surplus: facSurplus,
            theory_to_practical_ratio: contactRatio,
            efficiency_scenarios: scenarios,
            total_courses: processed.length,
            total_l_hours: totL,
            total_t_hours: totT,
            total_p_hours: totP,
            total_credits: totC,
            total_contact_hours: totL + totT + totP,
            section_l_load: secL,
            section_t_load: secT,
            section_p_load: secP,
            section_total_workload: secTot,
            dept_l_load: deptL,
            dept_t_load: deptT,
            dept_p_load: deptP,
            dept_total_workload: deptTot,
            estimated_faculty_required: estFac,
            courses: processed,
            sections
        };
    }

    function getSectionName(index) {
        let label = "";
        while (index >= 0) {
            label = String.fromCharCode(65 + (index % 26)) + label;
            index = Math.floor(index / 26) - 1;
        }
        return label;
    }

    // Live fast recalculator that can run without network latency
    function executeLiveWorkloadRecalc() {
        const numSecs = parseInt(wlSliderSections ? wlSliderSections.value : (wlInputSections ? wlInputSections.value : 12)) || 12;
        const lFac = parseInt(wlSliderLFac ? wlSliderLFac.value : (wlInputLFac ? wlInputLFac.value : 1)) || 1;
        const tFac = parseInt(wlSliderTFac ? wlSliderTFac.value : (wlInputTFac ? wlInputTFac.value : 3)) || 3;
        const pFac = parseInt(wlSliderPFac ? wlSliderPFac.value : (wlInputPFac ? wlInputPFac.value : 3)) || 3;
        const cap = parseFloat(wlSliderFacultyCap ? wlSliderFacultyCap.value : (wlInputFacultyCap ? wlInputFacultyCap.value : 15)) || 15;
        const availFac = parseInt(wlSliderAvailFaculty ? wlSliderAvailFaculty.value : (wlInputAvailFaculty ? wlInputAvailFaculty.value : 34)) || 34;
        const courses = modalCoursesList && modalCoursesList.length ? modalCoursesList : DEFAULT_PROMPT_COURSES;

        const data = calculateLocalWorkload(courses, numSecs, lFac, tFac, pFac, cap, availFac);
        currentWorkloadData = data;
        renderWorkloadTab(data);
    }

    // Fetch and render workload from backend API with local instant fallback
    async function fetchAndRenderWorkload(customParams = {}) {
        const numSecs = parseInt(customParams.num_sections || (wlSliderSections ? wlSliderSections.value : 12)) || 12;
        const lFac = parseInt(customParams.l_faculty_multiplier || (wlSliderLFac ? wlSliderLFac.value : 1)) || 1;
        const tFac = parseInt(customParams.t_faculty_multiplier || (wlSliderTFac ? wlSliderTFac.value : 3)) || 3;
        const pFac = parseInt(customParams.p_faculty_multiplier || (wlSliderPFac ? wlSliderPFac.value : 3)) || 3;
        const cap = parseFloat(customParams.avg_faculty_capacity_hours || (wlSliderFacultyCap ? wlSliderFacultyCap.value : 15)) || 15;
        const availFac = parseInt(customParams.num_available_faculty || (wlSliderAvailFaculty ? wlSliderAvailFaculty.value : 34)) || 34;
        const courses = customParams.courses || modalCoursesList || DEFAULT_PROMPT_COURSES;

        // Run local calculation instantly first for zero UI lag
        const localData = calculateLocalWorkload(courses, numSecs, lFac, tFac, pFac, cap, availFac);
        currentWorkloadData = localData;
        renderWorkloadTab(localData);

        // Async sync with backend for Excel pre-generation
        try {
            const resp = await fetch('/api/calculate-ltpc-workload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    num_sections: numSecs,
                    l_faculty_multiplier: lFac,
                    t_faculty_multiplier: tFac,
                    p_faculty_multiplier: pFac,
                    avg_faculty_capacity_hours: cap,
                    num_available_faculty: availFac,
                    courses: courses
                })
            });

            const resJson = await resp.json();
            if (resJson.success && resJson.data) {
                currentWorkloadData = resJson.data;
                renderWorkloadTab(resJson.data);
                return resJson.data;
            }
        } catch (e) {
            console.warn('API workload call fallback to local calculation:', e);
        }
        return localData;
    }

    // Render Workload Tab UI with Efficiency Metrics and Inline Editable Table
    function renderWorkloadTab(wl) {
        if (!wl) return;

        // Sync inputs & labels
        if (wlInputSections) wlInputSections.value = wl.num_sections;
        if (wlSliderSections) wlSliderSections.value = wl.num_sections;
        if (lblValSections) lblValSections.textContent = wl.num_sections;

        if (wlInputLFac) wlInputLFac.value = wl.l_faculty_multiplier;
        if (wlSliderLFac) wlSliderLFac.value = wl.l_faculty_multiplier;
        if (lblValLFac) lblValLFac.textContent = wl.l_faculty_multiplier;

        if (wlInputTFac) wlInputTFac.value = wl.t_faculty_multiplier;
        if (wlSliderTFac) wlSliderTFac.value = wl.t_faculty_multiplier;
        if (lblValTFac) lblValTFac.textContent = wl.t_faculty_multiplier;

        if (wlInputPFac) wlInputPFac.value = wl.p_faculty_multiplier;
        if (wlSliderPFac) wlSliderPFac.value = wl.p_faculty_multiplier;
        if (lblValPFac) lblValPFac.textContent = wl.p_faculty_multiplier;

        if (wlInputAvailFaculty) wlInputAvailFaculty.value = wl.num_available_faculty || 34;
        if (wlSliderAvailFaculty) wlSliderAvailFaculty.value = wl.num_available_faculty || 34;
        if (lblValAvailFac) lblValAvailFac.textContent = wl.num_available_faculty || 34;

        if (wlInputFacultyCap) wlInputFacultyCap.value = wl.avg_faculty_capacity_hours || 15;
        if (wlSliderFacultyCap) wlSliderFacultyCap.value = wl.avg_faculty_capacity_hours || 15;
        if (lblValCap) lblValCap.textContent = `${wl.avg_faculty_capacity_hours || 15}h`;

        if (displayNumSectionsLabel) displayNumSectionsLabel.textContent = wl.num_sections;

        // Efficiency Status Pill
        if (effStatusPill) {
            effStatusPill.className = `eff-status-pill ${wl.efficiency_status_badge || 'status-info'}`;
            if (effStatusText) effStatusText.textContent = wl.efficiency_status || 'Optimal Workload Balance';
        }

        // Efficiency KPI Cards
        if (effScoreVal) effScoreVal.textContent = `${wl.workload_efficiency_score || 100}%`;
        if (effScoreBadge) {
            effScoreBadge.textContent = wl.capacity_utilization_pct > 120 ? 'High Demand' : (wl.capacity_utilization_pct < 85 ? 'Surplus' : 'Balanced');
            effScoreBadge.className = wl.capacity_utilization_pct > 120 ? 'badge badge-warning' : 'badge badge-success';
        }
        if (effScoreBar) effScoreBar.style.width = `${Math.min(100, wl.workload_efficiency_score || 100)}%`;

        if (effUtilVal) effUtilVal.textContent = `${wl.capacity_utilization_pct || 0}%`;
        if (effUtilDetails) effUtilDetails.textContent = `${wl.available_capacity_hours || 510}h avail vs ${wl.dept_total_workload}h need`;
        if (effUtilBar) {
            effUtilBar.style.width = `${Math.min(100, (wl.capacity_utilization_pct || 100) * 0.7)}%`;
            effUtilBar.className = wl.capacity_utilization_pct > 120 ? 'eff-bar-fill fill-warn' : 'eff-bar-fill';
        }

        if (effBalanceVal) {
            if (wl.faculty_deficit > 0) {
                effBalanceVal.textContent = `-${wl.faculty_deficit} Faculty`;
                effBalanceVal.style.color = '#f87171';
            } else if (wl.faculty_surplus > 0) {
                effBalanceVal.textContent = `+${wl.faculty_surplus} Faculty`;
                effBalanceVal.style.color = '#34d399';
            } else {
                effBalanceVal.textContent = `Balanced (0)`;
                effBalanceVal.style.color = '#38bdf8';
            }
        }
        if (effBalanceSub) effBalanceSub.textContent = `Need ${wl.estimated_faculty_required} / Have ${wl.num_available_faculty || 34}`;
        if (effDeltaTag) {
            effDeltaTag.textContent = wl.faculty_deficit > 0 ? 'Staffing Deficit Detected' : (wl.faculty_surplus > 0 ? 'Capacity Surplus Available' : 'Optimal Capacity Match');
            effDeltaTag.style.color = wl.faculty_deficit > 0 ? '#f87171' : '#34d399';
        }

        if (effRatioVal) effRatioVal.textContent = `${wl.theory_to_practical_ratio || 0.65} : 1`;
        if (effRatioDetails) effRatioDetails.textContent = `${wl.total_l_hours} L vs ${wl.total_t_hours + wl.total_p_hours} T+P Contact Hrs`;

        // Render Efficiency Scenarios
        if (scenariosGrid && wl.efficiency_scenarios) {
            let scHtml = '';
            wl.efficiency_scenarios.forEach((sc, sIdx) => {
                const activeClass = sc.is_active ? 'active-model' : '';
                const savingsHtml = sc.hours_saved > 0 ? `<span class="scenario-savings"><i class="fa-solid fa-arrow-down"></i> Saves ${sc.hours_saved}h (${sc.savings_percent}%)</span>` : `<span style="color:#94a3b8; font-size:11px;">Current Baseline</span>`;
                scHtml += `
                    <div class="scenario-card ${activeClass}" data-sc-idx="${sIdx}">
                        <div class="scenario-top">
                            <span class="scenario-title">${sc.name}</span>
                            <span class="scenario-desc">${sc.description}</span>
                        </div>
                        <div class="scenario-metrics">
                            <span class="scenario-load">${sc.section_workload}h/sec (${sc.dept_workload}h dept)</span>
                            ${savingsHtml}
                        </div>
                        <button type="button" class="scenario-apply-btn">
                            ${sc.is_active ? '✓ Current Active Model' : 'Apply This Model'}
                        </button>
                    </div>
                `;
            });
            scenariosGrid.innerHTML = scHtml;

            // Scenario click handlers
            scenariosGrid.querySelectorAll('.scenario-card').forEach(card => {
                card.addEventListener('click', () => {
                    const idx = parseInt(card.getAttribute('data-sc-idx'));
                    const targetSc = wl.efficiency_scenarios[idx];
                    if (!targetSc) return;
                    if (wlSliderLFac) wlSliderLFac.value = targetSc.l_faculty;
                    if (wlInputLFac) wlInputLFac.value = targetSc.l_faculty;
                    if (wlSliderTFac) wlSliderTFac.value = targetSc.t_faculty;
                    if (wlInputTFac) wlInputTFac.value = targetSc.t_faculty;
                    if (wlSliderPFac) wlSliderPFac.value = targetSc.p_faculty;
                    if (wlInputPFac) wlInputPFac.value = targetSc.p_faculty;
                    updatePresetButtonStates(targetSc.code);
                    executeLiveWorkloadRecalc();
                });
            });
        }

        // Formula expressions
        if (displayFormulaSection) {
            displayFormulaSection.innerHTML = `
                ${wl.total_l_hours} × ${wl.l_faculty_multiplier} <small>(L hrs × ${wl.l_faculty_multiplier} fac)</small> + 
                ${wl.total_t_hours} × ${wl.t_faculty_multiplier} <small>(T hrs × ${wl.t_faculty_multiplier} fac)</small> + 
                ${wl.total_p_hours} × ${wl.p_faculty_multiplier} <small>(P hrs × ${wl.p_faculty_multiplier} fac)</small> = 
                <strong class="glow-accent">${wl.section_total_workload} hrs / section</strong>
            `;
        }

        if (displayFormulaDept) {
            displayFormulaDept.innerHTML = `
                ${wl.total_l_hours}×${wl.l_faculty_multiplier}×${wl.num_sections} + 
                ${wl.total_t_hours}×${wl.t_faculty_multiplier}×${wl.num_sections} + 
                ${wl.total_p_hours}×${wl.p_faculty_multiplier}×${wl.num_sections} = 
                ${wl.dept_l_load} + ${wl.dept_t_load} + ${wl.dept_p_load} = 
                <strong class="glow-green">${wl.dept_total_workload} faculty-hours</strong>
            `;
        }

        // KPI cards
        if (wlTotalL) wlTotalL.textContent = `${wl.total_l_hours} hrs`;
        if (wlDeptL) wlDeptL.textContent = `Dept Load: ${wl.dept_l_load} faculty-hrs`;
        if (wlTotalT) wlTotalT.textContent = `${wl.total_t_hours} hrs`;
        if (wlDeptT) wlDeptT.textContent = `Dept Load: ${wl.dept_t_load} faculty-hrs`;
        if (wlTotalP) wlTotalP.textContent = `${wl.total_p_hours} hrs`;
        if (wlDeptP) wlDeptP.textContent = `Dept Load: ${wl.dept_p_load} faculty-hrs`;
        if (wlTotalC) wlTotalC.textContent = `${wl.total_credits} Credits`;
        if (wlTotalCoursesCount) wlTotalCoursesCount.textContent = `Across ${wl.total_courses} courses`;
        if (wlSectionTotal) wlSectionTotal.textContent = `${wl.section_total_workload} hrs`;
        if (wlDeptTotal) wlDeptTotal.textContent = `${wl.dept_total_workload} hrs`;
        if (wlEstimatedFaculty) wlEstimatedFaculty.textContent = `~${wl.estimated_faculty_required} Faculty`;

        if (lblLastSection && wl.sections && wl.sections.length > 0) {
            lblLastSection.textContent = getSectionName(wl.sections.length - 1);
        }

        // Render INLINE EDITABLE Course Table directly on dashboard
        let cTableHtml = `<table class="wl-editable-table">
            <thead>
                <tr>
                    <th style="width: 45px;">#</th>
                    <th>Course Title (Editable)</th>
                    <th style="width: 60px;">L</th>
                    <th style="width: 60px;">T</th>
                    <th style="width: 60px;">P</th>
                    <th style="width: 60px;">C</th>
                    <th style="width: 85px;">Contact</th>
                    <th style="width: 90px;">L Load</th>
                    <th style="width: 90px;">T Load</th>
                    <th style="width: 90px;">P Load</th>
                    <th>Section Workload</th>
                    <th>Dept Workload</th>
                    <th style="width: 75px;">% Share</th>
                    <th style="width: 50px;">Action</th>
                </tr>
            </thead>
            <tbody>`;

        wl.courses.forEach((c, cIdx) => {
            cTableHtml += `<tr>
                <td style="text-align: center; color: #94a3b8;">${c.sl_no}</td>
                <td>
                    <input type="text" class="wl-in-title" data-idx="${cIdx}" value="${c.course_title}">
                </td>
                <td style="text-align: center;"><input type="number" class="wl-in-num wl-in-l" min="0" max="20" data-idx="${cIdx}" value="${c.l}"></td>
                <td style="text-align: center;"><input type="number" class="wl-in-num wl-in-t" min="0" max="20" data-idx="${cIdx}" value="${c.t}"></td>
                <td style="text-align: center;"><input type="number" class="wl-in-num wl-in-p" min="0" max="20" data-idx="${cIdx}" value="${c.p}"></td>
                <td style="text-align: center;"><input type="number" class="wl-in-num wl-in-c" min="0" max="20" data-idx="${cIdx}" value="${c.c}"></td>
                <td style="text-align: center; font-weight: 600;">${c.contact_hours}h</td>
                <td style="text-align: center; color: #38bdf8;">${c.sec_l_load}h</td>
                <td style="text-align: center; color: #f59e0b;">${c.sec_t_load}h</td>
                <td style="text-align: center; color: #10b981;">${c.sec_p_load}h</td>
                <td style="text-align: center; font-weight: 700; color: #38bdf8;">${c.sec_total_workload} hrs</td>
                <td style="text-align: center; font-weight: 700; color: #34d399;">${c.dept_total_workload} hrs</td>
                <td style="text-align: center; font-weight: 600;">${c.dept_share_pct || 0}%</td>
                <td style="text-align: center;">
                    <button type="button" class="btn-icon-del wl-del-btn" data-idx="${cIdx}" title="Delete Course">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </td>
            </tr>`;
        });

        // Summary Total Row
        cTableHtml += `<tr class="tr-total-row">
            <td colspan="2" style="text-align: left; padding-left: 14px;">TOTAL CURRICULUM WORKLOAD</td>
            <td style="text-align: center;"><span class="badge-l">${wl.total_l_hours}</span></td>
            <td style="text-align: center;"><span class="badge-t">${wl.total_t_hours}</span></td>
            <td style="text-align: center;"><span class="badge-p">${wl.total_p_hours}</span></td>
            <td style="text-align: center;"><span class="badge-c">${wl.total_credits}</span></td>
            <td style="text-align: center;">${wl.total_contact_hours}h</td>
            <td style="text-align: center; color: #38bdf8;">${wl.section_l_load}h</td>
            <td style="text-align: center; color: #f59e0b;">${wl.section_t_load}h</td>
            <td style="text-align: center; color: #10b981;">${wl.section_p_load}h</td>
            <td style="text-align: center; font-size: 15px; color: #38bdf8;">${wl.section_total_workload} hrs</td>
            <td style="text-align: center; font-size: 15px; color: #34d399;">${wl.dept_total_workload} hrs</td>
            <td style="text-align: center;">100%</td>
            <td></td>
        </tr></tbody></table>`;

        if (workloadCourseTableContainer) {
            workloadCourseTableContainer.innerHTML = cTableHtml;

            // Bind inline editing input listeners
            workloadCourseTableContainer.querySelectorAll('.wl-in-title, .wl-in-num').forEach(input => {
                input.addEventListener('input', (e) => {
                    const idx = parseInt(e.target.getAttribute('data-idx'));
                    if (!modalCoursesList[idx]) return;
                    if (e.target.classList.contains('wl-in-title')) {
                        modalCoursesList[idx].course_title = e.target.value;
                    } else if (e.target.classList.contains('wl-in-l')) {
                        modalCoursesList[idx].l = parseInt(e.target.value) || 0;
                    } else if (e.target.classList.contains('wl-in-t')) {
                        modalCoursesList[idx].t = parseInt(e.target.value) || 0;
                    } else if (e.target.classList.contains('wl-in-p')) {
                        modalCoursesList[idx].p = parseInt(e.target.value) || 0;
                    } else if (e.target.classList.contains('wl-in-c')) {
                        modalCoursesList[idx].c = parseInt(e.target.value) || 0;
                    }
                    executeLiveWorkloadRecalc();
                });
            });

            // Bind inline delete button listeners
            workloadCourseTableContainer.querySelectorAll('.wl-del-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const idx = parseInt(btn.getAttribute('data-idx'));
                    if (modalCoursesList.length <= 1) {
                        alert('At least one course must remain in the curriculum.');
                        return;
                    }
                    modalCoursesList.splice(idx, 1);
                    executeLiveWorkloadRecalc();
                });
            });
        }

        // Render Section Matrix Table
        let sTableHtml = `<table>
            <thead>
                <tr>
                    <th style="width: 50px;">#</th>
                    <th>Section Name</th>
                    <th>Number of Courses</th>
                    <th>Section Lecture (L) Hours</th>
                    <th>Section Tutorial (T) Hours</th>
                    <th>Section Practical (P) Hours</th>
                    <th>Weekly Section Load</th>
                    <th>Cumulative Department Load</th>
                </tr>
            </thead>
            <tbody>`;

        wl.sections.forEach((s, idx) => {
            sTableHtml += `<tr>
                <td style="text-align: center; color: #94a3b8;">${idx + 1}</td>
                <td><strong style="color: #38bdf8;">${s.section_name}</strong></td>
                <td style="text-align: center;">${s.num_courses} Courses</td>
                <td style="text-align: center; color: #38bdf8;">${s.l_hours} hrs</td>
                <td style="text-align: center; color: #f59e0b;">${s.t_hours} hrs</td>
                <td style="text-align: center; color: #10b981;">${s.p_hours} hrs</td>
                <td style="text-align: center;"><strong style="color: #f8fafc;">${s.section_total_workload} hrs/wk</strong></td>
                <td style="text-align: center;"><strong style="color: #34d399;">${s.cumulative_dept_workload} hrs</strong></td>
            </tr>`;
        });

        sTableHtml += `</tbody></table>`;
        if (workloadSectionTableContainer) {
            workloadSectionTableContainer.innerHTML = sTableHtml;
        }

        // Render Chart Visualizations
        renderWorkloadCharts(wl);
    }

    // Render 3 Rich Chart.js Visualizations for Workload
    function renderWorkloadCharts(wl) {
        if (typeof Chart === 'undefined' || !wl) return;

        // 1. LTPC Share Doughnut Chart
        const ctxShare = document.getElementById('chartWorkloadShare');
        if (ctxShare) {
            if (chartWorkloadShareInstance) chartWorkloadShareInstance.destroy();
            chartWorkloadShareInstance = new Chart(ctxShare, {
                type: 'doughnut',
                data: {
                    labels: [
                        `Lecture (L) - ${wl.dept_l_load} hrs`,
                        `Tutorial (T) - ${wl.dept_t_load} hrs`,
                        `Practical (P) - ${wl.dept_p_load} hrs`
                    ],
                    datasets: [{
                        data: [wl.dept_l_load, wl.dept_t_load, wl.dept_p_load],
                        backgroundColor: [
                            'rgba(56, 189, 248, 0.85)',
                            'rgba(245, 158, 11, 0.85)',
                            'rgba(16, 185, 129, 0.85)'
                        ],
                        borderColor: 'rgba(15, 23, 42, 0.9)',
                        borderWidth: 2,
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#cbd5e1', padding: 14, font: { size: 12, weight: '600' } }
                        },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => {
                                    const val = ctx.raw;
                                    const pct = wl.dept_total_workload > 0 ? Math.round((val / wl.dept_total_workload) * 1000) / 10 : 0;
                                    return ` ${ctx.label}: ${val} faculty-hours (${pct}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }

        // 2. Course-wise Stacked Bar Chart
        const ctxCourse = document.getElementById('chartCourseStackedLoad');
        if (ctxCourse) {
            if (chartCourseStackedLoadInstance) chartCourseStackedLoadInstance.destroy();
            const courseLabels = wl.courses.map(c => c.course_title.length > 20 ? c.course_title.substring(0, 18) + '...' : c.course_title);
            const dataL = wl.courses.map(c => c.sec_l_load);
            const dataT = wl.courses.map(c => c.sec_t_load);
            const dataP = wl.courses.map(c => c.sec_p_load);

            chartCourseStackedLoadInstance = new Chart(ctxCourse, {
                type: 'bar',
                data: {
                    labels: courseLabels,
                    datasets: [
                        {
                            label: `Lecture Load (×${wl.l_faculty_multiplier} fac)`,
                            data: dataL,
                            backgroundColor: 'rgba(56, 189, 248, 0.75)',
                            borderColor: '#38bdf8',
                            borderWidth: 1,
                            borderRadius: 4
                        },
                        {
                            label: `Tutorial Load (×${wl.t_faculty_multiplier} fac)`,
                            data: dataT,
                            backgroundColor: 'rgba(245, 158, 11, 0.75)',
                            borderColor: '#f59e0b',
                            borderWidth: 1,
                            borderRadius: 4
                        },
                        {
                            label: `Practical Load (×${wl.p_faculty_multiplier} fac)`,
                            data: dataP,
                            backgroundColor: 'rgba(16, 185, 129, 0.75)',
                            borderColor: '#10b981',
                            borderWidth: 1,
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: { color: '#cbd5e1', font: { size: 11 } }
                        },
                        tooltip: {
                            callbacks: {
                                footer: (items) => {
                                    const total = items.reduce((sum, item) => sum + item.parsed.y, 0);
                                    return ` Total Course Section Load: ${total} hrs`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            stacked: true,
                            ticks: { color: '#cbd5e1', font: { size: 10 } },
                            grid: { display: false }
                        },
                        y: {
                            stacked: true,
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        }
                    }
                }
            });
        }

        // 3. Section Load Distribution Chart
        const ctxSec = document.getElementById('chartSectionLoadDistribution');
        if (ctxSec) {
            if (chartSectionLoadDistributionInstance) chartSectionLoadDistributionInstance.destroy();
            const secLabels = wl.sections.map(s => s.section_name);
            const secLoads = wl.sections.map(s => s.section_total_workload);
            const cumLoads = wl.sections.map(s => s.cumulative_dept_workload);

            chartSectionLoadDistributionInstance = new Chart(ctxSec, {
                type: 'bar',
                data: {
                    labels: secLabels,
                    datasets: [
                        {
                            type: 'bar',
                            label: 'Per-Section Weekly Workload (hrs)',
                            data: secLoads,
                            backgroundColor: 'rgba(56, 189, 248, 0.65)',
                            borderColor: '#38bdf8',
                            borderWidth: 1,
                            borderRadius: 6,
                            yAxisID: 'y'
                        },
                        {
                            type: 'line',
                            label: 'Cumulative Department Demand (hrs)',
                            data: cumLoads,
                            borderColor: '#34d399',
                            backgroundColor: 'rgba(52, 211, 153, 0.1)',
                            borderWidth: 2.5,
                            pointBackgroundColor: '#34d399',
                            pointRadius: 4,
                            fill: true,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: { color: '#cbd5e1', font: { size: 12 } }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#cbd5e1', font: { size: 11 } },
                            grid: { display: false }
                        },
                        y: {
                            type: 'linear',
                            position: 'left',
                            ticks: { color: '#38bdf8' },
                            title: { display: true, text: 'Section Load (hrs)', color: '#38bdf8' },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        },
                        y1: {
                            type: 'linear',
                            position: 'right',
                            ticks: { color: '#34d399' },
                            title: { display: true, text: 'Cumulative Dept Load (hrs)', color: '#34d399' },
                            grid: { display: false }
                        }
                    }
                }
            });
        }
    }

    function updatePresetButtonStates(code) {
        [btnPresetBaseline, btnPresetDualBatch, btnPresetBlended, btnPresetAICTE].forEach(btn => {
            if (btn) btn.classList.remove('active-preset');
        });
        if (code === '1-3-3' && btnPresetBaseline) btnPresetBaseline.classList.add('active-preset');
        else if (code === '1-2-2' && btnPresetDualBatch) btnPresetDualBatch.classList.add('active-preset');
        else if (code === '1-1-2' && btnPresetBlended) btnPresetBlended.classList.add('active-preset');
        else if (code === '1-1-1' && btnPresetAICTE) btnPresetAICTE.classList.add('active-preset');
    }

    // Workload Adjusters Listeners
    if (btnRecalculateWorkload) {
        btnRecalculateWorkload.addEventListener('click', () => {
            fetchAndRenderWorkload();
        });
    }

    if (btnResetToPromptCourses) {
        btnResetToPromptCourses.addEventListener('click', () => {
            modalCoursesList = JSON.parse(JSON.stringify(DEFAULT_PROMPT_COURSES));
            if (wlSliderSections) wlSliderSections.value = 12;
            if (wlSliderLFac) wlSliderLFac.value = 1;
            if (wlSliderTFac) wlSliderTFac.value = 3;
            if (wlSliderPFac) wlSliderPFac.value = 3;
            updatePresetButtonStates('1-3-3');
            executeLiveWorkloadRecalc();
        });
    }

    // Interactive Range Sliders Live Zero-Lag Listeners
    if (wlSliderSections) {
        wlSliderSections.addEventListener('input', (e) => {
            if (lblValSections) lblValSections.textContent = e.target.value;
            if (wlInputSections) wlInputSections.value = e.target.value;
            executeLiveWorkloadRecalc();
        });
    }
    if (wlSliderLFac) {
        wlSliderLFac.addEventListener('input', (e) => {
            if (lblValLFac) lblValLFac.textContent = e.target.value;
            if (wlInputLFac) wlInputLFac.value = e.target.value;
            executeLiveWorkloadRecalc();
        });
    }
    if (wlSliderTFac) {
        wlSliderTFac.addEventListener('input', (e) => {
            if (lblValTFac) lblValTFac.textContent = e.target.value;
            if (wlInputTFac) wlInputTFac.value = e.target.value;
            executeLiveWorkloadRecalc();
        });
    }
    if (wlSliderPFac) {
        wlSliderPFac.addEventListener('input', (e) => {
            if (lblValPFac) lblValPFac.textContent = e.target.value;
            if (wlInputPFac) wlInputPFac.value = e.target.value;
            executeLiveWorkloadRecalc();
        });
    }
    if (wlSliderAvailFaculty) {
        wlSliderAvailFaculty.addEventListener('input', (e) => {
            if (lblValAvailFac) lblValAvailFac.textContent = e.target.value;
            if (wlInputAvailFaculty) wlInputAvailFaculty.value = e.target.value;
            executeLiveWorkloadRecalc();
        });
    }
    if (wlSliderFacultyCap) {
        wlSliderFacultyCap.addEventListener('input', (e) => {
            if (lblValCap) lblValCap.textContent = `${e.target.value}h`;
            if (wlInputFacultyCap) wlInputFacultyCap.value = e.target.value;
            executeLiveWorkloadRecalc();
        });
    }

    // Quick Staffing Efficiency Preset Buttons
    if (btnPresetBaseline) {
        btnPresetBaseline.addEventListener('click', () => {
            if (wlSliderLFac) wlSliderLFac.value = 1;
            if (wlSliderTFac) wlSliderTFac.value = 3;
            if (wlSliderPFac) wlSliderPFac.value = 3;
            updatePresetButtonStates('1-3-3');
            executeLiveWorkloadRecalc();
        });
    }
    if (btnPresetDualBatch) {
        btnPresetDualBatch.addEventListener('click', () => {
            if (wlSliderLFac) wlSliderLFac.value = 1;
            if (wlSliderTFac) wlSliderTFac.value = 2;
            if (wlSliderPFac) wlSliderPFac.value = 2;
            updatePresetButtonStates('1-2-2');
            executeLiveWorkloadRecalc();
        });
    }
    if (btnPresetBlended) {
        btnPresetBlended.addEventListener('click', () => {
            if (wlSliderLFac) wlSliderLFac.value = 1;
            if (wlSliderTFac) wlSliderTFac.value = 1;
            if (wlSliderPFac) wlSliderPFac.value = 2;
            updatePresetButtonStates('1-1-2');
            executeLiveWorkloadRecalc();
        });
    }
    if (btnPresetAICTE) {
        btnPresetAICTE.addEventListener('click', () => {
            if (wlSliderLFac) wlSliderLFac.value = 1;
            if (wlSliderTFac) wlSliderTFac.value = 1;
            if (wlSliderPFac) wlSliderPFac.value = 1;
            updatePresetButtonStates('1-1-1');
            executeLiveWorkloadRecalc();
        });
    }

    // Dashboard Table Action Buttons (Add Course & Reset)
    if (btnWlAddCourse) {
        btnWlAddCourse.addEventListener('click', () => {
            const nextIdx = modalCoursesList.length + 1;
            modalCoursesList.push({
                course_title: `New Course ${nextIdx}`,
                l: 3, t: 0, p: 2, c: 4, ltpc: "3-0-2-4"
            });
            executeLiveWorkloadRecalc();
        });
    }
    if (btnWlResetPrompt) {
        btnWlResetPrompt.addEventListener('click', () => {
            modalCoursesList = JSON.parse(JSON.stringify(DEFAULT_PROMPT_COURSES));
            executeLiveWorkloadRecalc();
        });
    }

    // Quick Action button in Left Panel to calculate Workload
    if (btnQuickCalcWorkload) {
        btnQuickCalcWorkload.addEventListener('click', async () => {
            showState('results');
            const successBanner = document.getElementById('resultsSuccessBanner');
            if (successBanner && !latestAllocData) {
                successBanner.style.display = 'none';
            } else if (successBanner) {
                successBanner.style.display = 'flex';
            }

            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

            const tabWlBtn = document.querySelector('[data-tab="tabWorkload"]');
            if (tabWlBtn) tabWlBtn.classList.add('active');
            const tabWlPane = document.getElementById('tabWorkload');
            if (tabWlPane) tabWlPane.classList.add('active');

            const numSecs = parseInt(wlSliderSections ? wlSliderSections.value : (numSectionsInput ? numSectionsInput.value : 12)) || 12;
            const lFac = parseInt(wlSliderLFac ? wlSliderLFac.value : 1) || 1;
            const tFac = parseInt(wlSliderTFac ? wlSliderTFac.value : 3) || 3;
            const pFac = parseInt(wlSliderPFac ? wlSliderPFac.value : 3) || 3;

            const data = await fetchAndRenderWorkload({
                num_sections: numSecs,
                l_faculty_multiplier: lFac,
                t_faculty_multiplier: tFac,
                p_faculty_multiplier: pFac
            });

            setTimeout(() => {
                if (data || currentWorkloadData) renderWorkloadCharts(data || currentWorkloadData);
            }, 60);

            tabWlPane.scrollIntoView({ behavior: 'smooth' });
        });
    }

    // =========================================================================
    // INTERACTIVE WORKLOAD MODAL LOGIC
    // =========================================================================

    function openWorkloadModal() {
        if (!workloadCalculatorModal) return;
        workloadCalculatorModal.classList.remove('hidden');

        const numSecs = parseInt(wlSliderSections ? wlSliderSections.value : (numSectionsInput ? numSectionsInput.value : 12)) || 12;
        const lFac = parseInt(wlSliderLFac ? wlSliderLFac.value : 1) || 1;
        const tFac = parseInt(wlSliderTFac ? wlSliderTFac.value : 3) || 3;
        const pFac = parseInt(wlSliderPFac ? wlSliderPFac.value : 3) || 3;

        if (mInputSections) mInputSections.value = numSecs;
        if (mInputLFac) mInputLFac.value = lFac;
        if (mInputTFac) mInputTFac.value = tFac;
        if (mInputPFac) mInputPFac.value = pFac;

        renderModalCoursesTable();
        recalculateModalWorkload();
    }

    function closeWorkloadModal() {
        if (!workloadCalculatorModal) return;
        workloadCalculatorModal.classList.add('hidden');
    }

    if (btnOpenWorkloadCalculator) {
        btnOpenWorkloadCalculator.addEventListener('click', openWorkloadModal);
    }
    if (modalCloseWorkloadBtn) {
        modalCloseWorkloadBtn.addEventListener('click', closeWorkloadModal);
    }
    if (mBtnCloseFooter) {
        mBtnCloseFooter.addEventListener('click', closeWorkloadModal);
    }

    function renderModalCoursesTable() {
        if (!modalCoursesTbody) return;
        let html = '';
        modalCoursesList.forEach((c, idx) => {
            html += `<tr>
                <td style="text-align: center; color: #94a3b8;">${idx + 1}</td>
                <td>
                    <input type="text" class="m-cell-input m-course-title" data-idx="${idx}" value="${c.course_title}">
                </td>
                <td><input type="number" min="0" max="20" class="m-cell-input num m-course-l" data-idx="${idx}" value="${c.l}"></td>
                <td><input type="number" min="0" max="20" class="m-cell-input num m-course-t" data-idx="${idx}" value="${c.t}"></td>
                <td><input type="number" min="0" max="20" class="m-cell-input num m-course-p" data-idx="${idx}" value="${c.p}"></td>
                <td><input type="number" min="0" max="20" class="m-cell-input num m-course-c" data-idx="${idx}" value="${c.c}"></td>
                <td style="text-align: center; font-weight: 600; color: #38bdf8;" class="m-sec-load-${idx}">-</td>
                <td style="text-align: center; font-weight: 700; color: #34d399;" class="m-dept-load-${idx}">-</td>
                <td style="text-align: center;">
                    <button type="button" class="btn-icon-del m-del-btn" data-idx="${idx}" title="Delete Course">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </td>
            </tr>`;
        });
        modalCoursesTbody.innerHTML = html;

        // Attach input change listeners
        modalCoursesTbody.querySelectorAll('.m-cell-input').forEach(inp => {
            inp.addEventListener('input', (e) => {
                const idx = parseInt(e.target.getAttribute('data-idx'));
                if (e.target.classList.contains('m-course-title')) {
                    modalCoursesList[idx].course_title = e.target.value;
                } else if (e.target.classList.contains('m-course-l')) {
                    modalCoursesList[idx].l = parseInt(e.target.value) || 0;
                } else if (e.target.classList.contains('m-course-t')) {
                    modalCoursesList[idx].t = parseInt(e.target.value) || 0;
                } else if (e.target.classList.contains('m-course-p')) {
                    modalCoursesList[idx].p = parseInt(e.target.value) || 0;
                } else if (e.target.classList.contains('m-course-c')) {
                    modalCoursesList[idx].c = parseInt(e.target.value) || 0;
                }
                recalculateModalWorkload();
            });
        });

        // Attach delete listeners
        modalCoursesTbody.querySelectorAll('.m-del-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = parseInt(btn.getAttribute('data-idx'));
                if (modalCoursesList.length <= 1) {
                    alert('At least one course must remain in the curriculum.');
                    return;
                }
                modalCoursesList.splice(idx, 1);
                renderModalCoursesTable();
                recalculateModalWorkload();
            });
        });
    }

    function recalculateModalWorkload() {
        const numSecs = parseInt(mInputSections ? mInputSections.value : 12) || 12;
        const lFac = parseInt(mInputLFac ? mInputLFac.value : 1) || 1;
        const tFac = parseInt(mInputTFac ? mInputTFac.value : 3) || 3;
        const pFac = parseInt(mInputPFac ? mInputPFac.value : 3) || 3;

        const res = calculateLocalWorkload(modalCoursesList, numSecs, lFac, tFac, pFac, 15);

        // Update table row values
        res.courses.forEach((c, idx) => {
            const secCell = document.querySelector(`.m-sec-load-${idx}`);
            const deptCell = document.querySelector(`.m-dept-load-${idx}`);
            if (secCell) secCell.textContent = `${c.sec_total_workload}h`;
            if (deptCell) deptCell.textContent = `${c.dept_total_workload}h`;
        });

        // Update modal KPI strip
        if (mKpiL) mKpiL.textContent = `${res.total_l_hours}h (${res.dept_l_load}h dept)`;
        if (mKpiT) mKpiT.textContent = `${res.total_t_hours}h (${res.dept_t_load}h dept)`;
        if (mKpiP) mKpiP.textContent = `${res.total_p_hours}h (${res.dept_p_load}h dept)`;
        if (mKpiSec) mKpiSec.textContent = `${res.section_total_workload} hrs/sec`;
        if (mKpiDept) mKpiDept.textContent = `${res.dept_total_workload} hrs`;
        if (mKpiFac) mKpiFac.textContent = `~${res.estimated_faculty_required} Faculty`;

        // Update modal formula
        if (mFormulaSec) {
            mFormulaSec.textContent = `${res.total_l_hours}*${lFac} + ${res.total_t_hours}*${tFac} + ${res.total_p_hours}*${pFac} = ${res.section_total_workload} hrs`;
        }
        if (mFormulaDept) {
            mFormulaDept.textContent = `${res.section_total_workload} × ${numSecs} = ${res.dept_total_workload} hrs`;
        }
    }

    // Modal controls event listeners
    [mInputSections, mInputLFac, mInputTFac, mInputPFac].forEach(inp => {
        if (inp) inp.addEventListener('input', recalculateModalWorkload);
    });

    if (mBtnAddCourse) {
        mBtnAddCourse.addEventListener('click', () => {
            const newIdx = modalCoursesList.length + 1;
            modalCoursesList.push({
                course_title: `New Course ${newIdx}`,
                l: 3, t: 0, p: 2, c: 4, ltpc: "3-0-2-4"
            });
            renderModalCoursesTable();
            recalculateModalWorkload();
        });
    }

    if (mBtnResetCourses) {
        mBtnResetCourses.addEventListener('click', () => {
            modalCoursesList = JSON.parse(JSON.stringify(DEFAULT_PROMPT_COURSES));
            renderModalCoursesTable();
            recalculateModalWorkload();
        });
    }

    if (mBtnDownloadExcel) {
        mBtnDownloadExcel.addEventListener('click', async () => {
            const numSecs = parseInt(mInputSections ? mInputSections.value : 12) || 12;
            const lFac = parseInt(mInputLFac ? mInputLFac.value : 1) || 1;
            const tFac = parseInt(mInputTFac ? mInputTFac.value : 3) || 3;
            const pFac = parseInt(mInputPFac ? mInputPFac.value : 3) || 3;

            try {
                const response = await fetch('/api/download/ltpc-workload.xlsx', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        num_sections: numSecs,
                        l_faculty_multiplier: lFac,
                        t_faculty_multiplier: tFac,
                        p_faculty_multiplier: pFac,
                        courses: modalCoursesList
                    })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'ltpc_workload_calculation.xlsx';
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);
                } else {
                    window.location.href = '/api/download/ltpc-workload.xlsx';
                }
            } catch (e) {
                window.location.href = '/api/download/ltpc-workload.xlsx';
            }
        });
    }

    if (mBtnApplyToAllocation) {
        mBtnApplyToAllocation.addEventListener('click', async () => {
            closeWorkloadModal();
            showState('results');
            const successBanner = document.getElementById('resultsSuccessBanner');
            if (successBanner && !latestAllocData) {
                successBanner.style.display = 'none';
            }

            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

            const tabWlBtn = document.querySelector('[data-tab="tabWorkload"]');
            if (tabWlBtn) tabWlBtn.classList.add('active');
            const tabWlPane = document.getElementById('tabWorkload');
            if (tabWlPane) tabWlPane.classList.add('active');

            const numSecs = parseInt(mInputSections ? mInputSections.value : 12) || 12;
            const lFac = parseInt(mInputLFac ? mInputLFac.value : 1) || 1;
            const tFac = parseInt(mInputTFac ? mInputTFac.value : 3) || 3;
            const pFac = parseInt(mInputPFac ? mInputPFac.value : 3) || 3;

            if (wlSliderSections) wlSliderSections.value = numSecs;
            if (wlInputSections) wlInputSections.value = numSecs;
            if (lblValSections) lblValSections.textContent = numSecs;

            if (wlSliderLFac) wlSliderLFac.value = lFac;
            if (wlInputLFac) wlInputLFac.value = lFac;
            if (lblValLFac) lblValLFac.textContent = lFac;

            if (wlSliderTFac) wlSliderTFac.value = tFac;
            if (wlInputTFac) wlInputTFac.value = tFac;
            if (lblValTFac) lblValTFac.textContent = tFac;

            if (wlSliderPFac) wlSliderPFac.value = pFac;
            if (wlInputPFac) wlInputPFac.value = pFac;
            if (lblValPFac) lblValPFac.textContent = pFac;

            const data = await fetchAndRenderWorkload({
                courses: modalCoursesList,
                num_sections: numSecs,
                l_faculty_multiplier: lFac,
                t_faculty_multiplier: tFac,
                p_faculty_multiplier: pFac
            });

            setTimeout(() => {
                if (data || currentWorkloadData) renderWorkloadCharts(data || currentWorkloadData);
            }, 60);

            tabWlPane.scrollIntoView({ behavior: 'smooth' });
        });
    }

    // Auto-fetch default workload and preview data on initial load
    fetchAndRenderWorkload().then(() => {
        // Also fetch preview data in the background so modal is instant
        fetch('/api/preview-data').then(r => r.json()).then(res => {
            if (res.success) {
                cachedPreviewData = res;
                if (res.courses && res.courses.records && res.courses.records.length > 0) {
                    modalCoursesList = res.courses.records.map(c => ({
                        course_title: c.Subject,
                        l: c.L,
                        t: c.T,
                        p: c.P,
                        c: c.C,
                        ltpc: c['L-T-P-C']
                    }));
                }
            }
        }).catch(() => {});
    });

});

