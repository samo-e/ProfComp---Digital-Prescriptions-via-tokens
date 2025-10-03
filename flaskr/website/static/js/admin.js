// --- Assignment logic ---
(function() {
  console.log('[DEBUG] Admin.js initializing...');
  
  function ready(fn) {
    if (document.readyState !== 'loading') { fn(); }
    else { document.addEventListener('DOMContentLoaded', fn, { once: true }); }
  }

  ready(function() {
    console.log('[DEBUG] DOM ready, setting up handlers');
    
    // Clean up any existing handlers first
    if (window.__unassignHandler) {
      console.log('[DEBUG] Removing existing unassign handler');
      document.removeEventListener('submit', window.__unassignHandler);
      window.__unassignHandler = null;
    }
    
    // Guard map to prevent duplicate submissions per form
    const submitting = new WeakSet();

    console.log('[DEBUG] Setting up assign form handlers');
    document.querySelectorAll('.assign-student-form').forEach(function(form) {
      form.addEventListener('submit', function(e) {
        e.preventDefault();
        if (submitting.has(form)) {
          return; // already handling this form
        }
        submitting.add(form);

        const formData = new FormData(form);
        const button = form.querySelector('button[type="submit"]');
        const originalText = button ? button.textContent : '';
        const li = form.closest('li');
        const studentNameEl = li ? li.querySelector('span.student-name') : null;
        const studentName = studentNameEl ? studentNameEl.textContent : '';
        const studentId = form.querySelector('input[name="student_id"]').value;
        const teacherId = form.querySelector('input[name="teacher_id"]').value;

        if (button) {
          button.disabled = true;
          button.textContent = 'Assigning...';
        }

        fetch(form.action, {
          method: 'POST',
          body: formData,
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(r => r.json())
        .then(data => {
          if (data && data.success && data.student) {
            // Update assign button and source item
            if (button) {
              button.textContent = 'Assigned';
              button.disabled = true;
              button.style.opacity = '0.5';
            }
            if (li) {
              li.style.opacity = '0.5';
            }

            // Update assigned list live
            const assignedList = document.getElementById('assigned-students-list');
            if (assignedList) {
              const firstLi = assignedList.querySelector('li');
              if (firstLi && firstLi.textContent.includes('No students assigned')) {
                assignedList.removeChild(firstLi);
              }
              const newLi = document.createElement('li');
              newLi.innerHTML = `
                ${data.student.name} (${data.student.email})
                <form class="unassign-student-form" method="post" action="/admin/unassign_student" style="display:inline;">
                  <input type="hidden" name="csrf_token" value="${data.csrf_token}">
                  <input type="hidden" name="teacher_id" value="${data.student.teacher_id}">
                  <input type="hidden" name="student_id" value="${data.student.id}">
                  <button type="submit">Unassign</button>
                </form>
              `;
              assignedList.appendChild(newLi);
              // No need to call attachUnassignHandler - event delegation handles it
            }
          } else {
            // Failure: restore button
            if (button) {
              button.disabled = false;
              button.textContent = originalText || 'Assign';
            }
          }
        })
        .catch(err => {
          console.error('[Assign] AJAX error:', err);
          if (button) {
            button.disabled = false;
            button.textContent = originalText || 'Assign';
          }
        })
        .finally(() => {
          submitting.delete(form);
        });
      }, { once: false });
    });

    // --- Unassign logic using event delegation ---
    console.log('[DEBUG] Setting up unassign event delegation');
    const unassignSubmitting = new WeakSet();
    
    // Create a single delegated event handler
    window.__unassignHandler = function(e) {
      const form = e.target.closest('.unassign-student-form');
      if (!form) return;
      
      console.log('[DEBUG] Unassign handler triggered for student ID:', form.querySelector('input[name="student_id"]').value);
      e.preventDefault();
      
      // Prevent multiple submissions
      if (unassignSubmitting.has(form)) {
        console.log('[DEBUG] Unassign already in progress for this form, ignoring');
        return;
      }
      unassignSubmitting.add(form);
      
      const formData = new FormData(form);
      const li = form.closest('li');
      const button = form.querySelector('button[type="submit"]');
      const originalText = button ? button.textContent : '';
      const studentId = form.querySelector('input[name="student_id"]').value;
      
      // Show loading state
      if (button) {
        button.disabled = true;
        button.textContent = 'Unassigning...';
      }
      
      fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(r => r.json())
      .then(data => {
        if (data && data.success) {
          if (li) li.remove();
          const assignedList = document.getElementById('assigned-students-list');
          if (assignedList && assignedList.children.length === 0) {
            const placeholder = document.createElement('li');
            placeholder.textContent = 'No students assigned.';
            assignedList.appendChild(placeholder);
          }
          // Re-enable the corresponding assign button in modal if present
          document.querySelectorAll('.assign-student-form').forEach(function(assignForm) {
            const assignStudentId = assignForm.querySelector('input[name="student_id"]').value;
            if (assignStudentId === studentId) {
              const assignButton = assignForm.querySelector('button[type="submit"]');
              if (assignButton) {
                assignButton.disabled = false;
                assignButton.textContent = 'Assign';
                assignButton.style.opacity = '1';
              }
              const assignLi = assignForm.closest('li');
              if (assignLi) {
                assignLi.style.opacity = '1';
              }
            }
          });
        } else {
          // Restore button on failure
          if (button) {
            button.disabled = false;
            button.textContent = originalText || 'Unassign';
          }
        }
      })
      .catch(err => {
        console.error('[Unassign] AJAX error:', err);
        // Restore button on error
        if (button) {
          button.disabled = false;
          button.textContent = originalText || 'Unassign';
        }
      })
      .finally(() => {
        console.log('[DEBUG] Unassign request completed, removing from submitting set');
        unassignSubmitting.delete(form);
      });
    };
    
    // Attach the single delegated listener
    console.log('[DEBUG] Attaching document-level unassign handler');
    document.addEventListener('submit', window.__unassignHandler);

    // No longer need to attach individual handlers - using event delegation above

    // --- Modal search filter ---
    console.log('[DEBUG] Setting up search filter');
    const searchInput = document.getElementById('student-search');
    
    const studentsList = document.getElementById('students-list');
    if (searchInput && studentsList) {
      console.log('[DEBUG] Search filter elements found, attaching listener');
      const filter = () => {
        const q = searchInput.value.trim().toLowerCase();
        studentsList.querySelectorAll('li').forEach(li => {
          const nameEl = li.querySelector('.student-name');
          const text = nameEl ? nameEl.textContent.toLowerCase() : li.textContent.toLowerCase();
          li.style.display = text.includes(q) ? '' : 'none';
        });
      };
      searchInput.addEventListener('input', filter, { passive: true });
      console.log('[DEBUG] Search input listener attached');
      // Prevent Enter key from triggering any default form submission in the modal context
      searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          e.stopPropagation();
        }
      });
    }
    
    console.log('[DEBUG] Admin.js initialization complete');
  });
})();

