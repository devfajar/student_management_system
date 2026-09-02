const BASE_URL = 'http://127.0.0.1:8000/api';

export function getToken() {
  return localStorage.getItem('token');
}

export function getRefreshToken() {
  return localStorage.getItem('refresh_token');
}

export function setTokens(token, refreshToken = null) {
  if (token) {
    localStorage.setItem('token', token);
  } else {
    localStorage.removeItem('token');
  }

  if (refreshToken) {
    localStorage.setItem('refresh_token', refreshToken);
  } else if (refreshToken === null && !token) {
    localStorage.removeItem('refresh_token');
  }
}

export function setToken(token) {
  setTokens(token);
}

export function clearTokens() {
  localStorage.removeItem('token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
}

// ==========================================
// Silent JWT Refresh & Request Queue System
// ==========================================
let isRefreshing = false;
let refreshSubscribers = [];

function onTokenRefreshed(newToken) {
  refreshSubscribers.forEach((callback) => callback(newToken, null));
  refreshSubscribers = [];
}

function onRefreshFailed(error) {
  refreshSubscribers.forEach((callback) => callback(null, error));
  refreshSubscribers = [];
}

function addRefreshSubscriber(callback) {
  refreshSubscribers.push(callback);
}

export async function silentRefreshToken() {
  const refresh = getRefreshToken();
  if (!refresh) {
    clearTokens();
    window.dispatchEvent(new CustomEvent('auth:expired'));
    throw new Error('No refresh token available');
  }

  try {
    const response = await fetch(`${BASE_URL}/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    });

    if (!response.ok) {
      clearTokens();
      window.dispatchEvent(new CustomEvent('auth:expired'));
      throw new Error('Refresh token invalid or expired');
    }

    const data = await response.json();
    setTokens(data.access, data.refresh || refresh);
    return data.access;
  } catch (err) {
    clearTokens();
    window.dispatchEvent(new CustomEvent('auth:expired'));
    throw err;
  }
}

export async function request(endpoint, options = {}, isRetry = false) {
  const token = getToken();
  const headers = {
    ...(options.headers || {})
  };

  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers
  });

  // Handle 401 Unauthorized for regular requests
  if (response.status === 401 && !endpoint.includes('/auth/login/') && !endpoint.includes('/auth/refresh/')) {
    if (isRetry) {
      clearTokens();
      window.dispatchEvent(new CustomEvent('auth:expired'));
      throw new Error('Session expired. Please log in again.');
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        addRefreshSubscriber(async (newToken, err) => {
          if (err) {
            reject(err);
          } else {
            try {
              const retryOpts = { ...options };
              resolve(await request(endpoint, retryOpts, true));
            } catch (retryErr) {
              reject(retryErr);
            }
          }
        });
      });
    }

    isRefreshing = true;
    try {
      const newAccessToken = await silentRefreshToken();
      isRefreshing = false;
      onTokenRefreshed(newAccessToken);
      return await request(endpoint, options, true);
    } catch (refreshErr) {
      isRefreshing = false;
      onRefreshFailed(refreshErr);
      throw new Error('Session expired. Please log in again.');
    }
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const errorMsg = data.detail || data.error || (typeof data === 'object' ? Object.entries(data).map(([k, v]) => `${k}: ${v}`).join(', ') : 'Request failed');
    throw new Error(errorMsg);
  }

  return data;
}

export async function downloadFile(endpoint, defaultFilename = 'download', isRetry = false) {
  let token = getToken();
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, { headers });
  if (response.status === 401 && !isRetry) {
    try {
      const newAccessToken = await silentRefreshToken();
      return downloadFile(endpoint, defaultFilename, true);
    } catch (err) {
      throw new Error('Session expired. Please log in again.');
    }
  }

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || err.detail || `Download failed with status ${response.status}`);
  }

  const disposition = response.headers.get('content-disposition');
  let filename = defaultFilename;
  if (disposition && disposition.includes('filename=')) {
    const match = disposition.match(/filename="?([^"]+)"?/);
    if (match && match[1]) filename = match[1];
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}



export const api = {
  // Auth & Profile
  login: (username, password) => request('/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  }),
  getMe: () => request('/auth/me/'),
  updateProfile: (profileData) => {
    if (profileData instanceof FormData) {
      return request('/auth/me/', {
        method: 'PUT',
        body: profileData
      });
    }
    return request('/auth/me/', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
  },

  // Dashboard
  getDashboardStats: () => request('/dashboard/stats/'),

  // Staff CRUD
  getStaffList: () => request('/staff/'),
  createStaff: (staffData) => request('/staff/', {
    method: 'POST',
    body: JSON.stringify(staffData)
  }),
  updateStaff: (id, staffData) => request(`/staff/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(staffData)
  }),
  deleteStaff: (id) => request(`/staff/${id}/`, {
    method: 'DELETE'
  }),

  // Student CRUD
  getStudentsList: () => request('/students/'),
  createStudent: (studentData) => request('/students/', {
    method: 'POST',
    body: studentData instanceof FormData ? studentData : JSON.stringify(studentData)
  }),
  updateStudent: (id, studentData) => request(`/students/${id}/`, {
    method: 'PUT',
    body: studentData instanceof FormData ? studentData : JSON.stringify(studentData)
  }),
  deleteStudent: (id) => request(`/students/${id}/`, {
    method: 'DELETE'
  }),

  // Course CRUD
  getCourses: () => request('/courses/'),
  createCourse: (course_name) => request('/courses/', {
    method: 'POST',
    body: JSON.stringify({ course_name })
  }),
  updateCourse: (id, course_name) => request(`/courses/${id}/`, {
    method: 'PUT',
    body: JSON.stringify({ course_name })
  }),
  deleteCourse: (id) => request(`/courses/${id}/`, {
    method: 'DELETE'
  }),

  // Subject CRUD
  getSubjects: () => request('/subjects/'),
  createSubject: (subjectData) => request('/subjects/', {
    method: 'POST',
    body: JSON.stringify(subjectData)
  }),
  updateSubject: (id, subjectData) => request(`/subjects/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(subjectData)
  }),
  deleteSubject: (id) => request(`/subjects/${id}/`, {
    method: 'DELETE'
  }),

  // Session Year CRUD
  getSessions: () => request('/sessions/'),
  createSession: (sessionData) => request('/sessions/', {
    method: 'POST',
    body: JSON.stringify(sessionData)
  }),
  deleteSession: (id) => request(`/sessions/${id}/`, {
    method: 'DELETE'
  }),

  // Student Leaves
  getStudentLeaves: () => request('/student-leaves/'),
  applyStudentLeave: (leaveData) => request('/student-leaves/', {
    method: 'POST',
    body: JSON.stringify(leaveData)
  }),
  approveStudentLeave: (id) => request(`/student-leaves/${id}/approve/`, {
    method: 'POST'
  }),
  disapproveStudentLeave: (id) => request(`/student-leaves/${id}/disapprove/`, {
    method: 'POST'
  }),

  // Staff Leaves
  getStaffLeaves: () => request('/staff-leaves/'),
  applyStaffLeave: (leaveData) => request('/staff-leaves/', {
    method: 'POST',
    body: JSON.stringify(leaveData)
  }),
  approveStaffLeave: (id) => request(`/staff-leaves/${id}/approve/`, {
    method: 'POST'
  }),
  disapproveStaffLeave: (id) => request(`/staff-leaves/${id}/disapprove/`, {
    method: 'POST'
  }),

  // Feedback
  getStudentFeedback: () => request('/student-feedback/'),
  sendStudentFeedback: (feedback) => request('/student-feedback/', {
    method: 'POST',
    body: JSON.stringify({ feedback })
  }),
  replyStudentFeedback: (id, reply) => request(`/student-feedback/${id}/reply/`, {
    method: 'POST',
    body: JSON.stringify({ feedback_reply: reply })
  }),

  getStaffFeedback: () => request('/staff-feedback/'),
  sendStaffFeedback: (feedback) => request('/staff-feedback/', {
    method: 'POST',
    body: JSON.stringify({ feedback })
  }),
  replyStaffFeedback: (id, reply) => request(`/staff-feedback/${id}/reply/`, {
    method: 'POST',
    body: JSON.stringify({ feedback_reply: reply })
  }),

  // Attendance
  getAttendanceStudents: (subject_id, session_year_id) => request(`/attendance/get-students/?subject_id=${subject_id}&session_year_id=${session_year_id}`),
  saveAttendance: (payload) => request('/attendance/save-attendance/', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  getAttendanceDates: (subject_id, session_year_id) => request(`/attendance/get-dates/?subject_id=${subject_id}&session_year_id=${session_year_id}`),
  getAttendanceReports: (attendance_id) => request(`/attendance/get-reports/?attendance_id=${attendance_id}`),
  updateAttendance: (payload) => request('/attendance/update-attendance/', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  studentViewAttendance: (subject_id, start_date, end_date) => {
    let url = '/attendance/student-view/?';
    if (subject_id) url += `subject_id=${subject_id}&`;
    if (start_date && end_date) url += `start_date=${start_date}&end_date=${end_date}`;
    return request(url);
  },

  // Results & Grading
  getResults: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/results/${query ? `?${query}` : ''}`);
  },
  deleteResult: (id) => request(`/results/${id}/`, {
    method: 'DELETE'
  }),
  getStudentsForResults: (subject_id, session_year_id) =>
    request(`/results/get-students/?subject_id=${subject_id}&session_year_id=${session_year_id}`),
  saveStudentResults: (payload) => request('/results/save-results/', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  getStudentResults: () => request('/results/my-results/'),

  // Notifications & Broadcasts
  getStudentNotifications: () => request('/notifications/student/'),
  getStaffNotifications: () => request('/notifications/staff/'),
  broadcastToStudents: (payload) => request('/notifications/broadcast-students/', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  broadcastToStaff: (payload) => request('/notifications/broadcast-staff/', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  getAdminNotificationHistory: () => request('/notifications/admin-history/'),
  deleteStudentNotification: (id) => request(`/notifications/student-notification/${id}/`, {
    method: 'DELETE'
  }),
  deleteStaffNotification: (id) => request(`/notifications/staff-notification/${id}/`, {
    method: 'DELETE'
  }),

  // Fee & Payment Tracking
  getFeeStructures: () => request('/fee-structures/'),
  createFeeStructure: (payload) => request('/fee-structures/', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  updateFeeStructure: (id, payload) => request(`/fee-structures/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(payload)
  }),
  deleteFeeStructure: (id) => request(`/fee-structures/${id}/`, {
    method: 'DELETE'
  }),
  generateFeeInvoices: (payload) => request('/fees/generate-invoices/', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  getFeeInvoices: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/fee-invoices/${query ? `?${query}` : ''}`);
  },
  collectFeePayment: (payload) => request('/fees/collect-payment/', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  getMyFeeInvoices: () => request('/fees/my-invoices/'),
  getFeeReceipt: (id) => request(`/fees/receipts/${id}/`),

  // Student Document Vault
  getStudentDocuments: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/student-documents/${query ? `?${query}` : ''}`);
  },
  uploadStudentDocument: (formData) => request('/student-documents/', {
    method: 'POST',
    body: formData
  }),
  deleteStudentDocument: (id) => request(`/student-documents/${id}/`, {
    method: 'DELETE'
  }),
  verifyStudentDocument: (id, verification_status, rejection_reason = '') => request(`/student-documents/${id}/verify/`, {
    method: 'POST',
    body: JSON.stringify({ verification_status, rejection_reason })
  }),

  // Export & Reporting Engine
  exportReportCardPdf: (studentId = null) => {
    const query = studentId ? `?student_id=${studentId}` : '';
    return downloadFile(`/reports/report-card/${query}`, 'academic_report_card.pdf');
  },
  exportAttendanceCsv: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return downloadFile(`/reports/attendance-csv/${query ? `?${query}` : ''}`, 'attendance_report.csv');
  },
  exportFeesCsv: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return downloadFile(`/reports/fees-csv/${query ? `?${query}` : ''}`, 'fee_invoices_report.csv');
  },
  exportStudentsCsv: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return downloadFile(`/reports/students-csv/${query ? `?${query}` : ''}`, 'students_roster.csv');
  }
};





