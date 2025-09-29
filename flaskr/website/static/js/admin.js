// --- Assignment logic ---
document.addEventListener('DOMContentLoaded', function() {
	document.querySelectorAll('.assign-student-form').forEach(function(form) {
		form.addEventListener('submit', function(e) {
			e.preventDefault();
			var formData = new FormData(form);
			var button = form.querySelector('button[type="submit"]');
			var studentName = form.closest('li').querySelector('span.student-name').textContent;
			var studentId = form.querySelector('input[name="student_id"]').value;
			var teacherId = form.querySelector('input[name="teacher_id"]').value;
			var csrf = form.querySelector('input[name="csrf_token"]').value;
			console.log('[Assign] Submitting assignment for:', studentName, 'studentId:', studentId, 'teacherId:', teacherId);
			fetch(form.action, {
				method: 'POST',
				body: formData,
				headers: { 'X-Requested-With': 'XMLHttpRequest' }
			})
			.then(response => {
				console.log('[Assign] AJAX response status:', response.status);
				return response.json();
			})
			.then(data => {
				console.log('[Assign] AJAX response data:', data);
				if (data.success && data.student) {
					button.disabled = true;
					button.style.opacity = '0.5';
					var assignedList = document.getElementById('assigned-students-list');
					if (assignedList) {
						var noStudents = assignedList.querySelector('li');
						if (noStudents && noStudents.textContent.includes('No students assigned')) {
							assignedList.removeChild(noStudents);
							console.log('[Assign] Removed "No students assigned." placeholder');
						}
						var li = document.createElement('li');
						li.innerHTML = `
							${data.student.name} (${data.student.email})
							<form class="unassign-student-form" method="post" action="/admin/unassign_student" style="display:inline;">
								<input type="hidden" name="csrf_token" value="${data.csrf_token}">
								<input type="hidden" name="teacher_id" value="${data.student.teacher_id}">
								<input type="hidden" name="student_id" value="${data.student.id}">
								<button type="submit">Unassign</button>
							</form>
						`;
						assignedList.appendChild(li);
						console.log('[Assign] Added student to assigned list:', data.student.name);
						attachUnassignHandler(li.querySelector('.unassign-student-form'));
					} else {
						console.log('[Assign] assigned-students-list not found');
					}
				} else {
					console.log('[Assign] Assignment failed or not successful:', data);
				}
			})
			.catch(error => {
				console.error('[Assign] AJAX error:', error);
			});
		});
		});
	});

	// --- Unassign logic ---
	function attachUnassignHandler(form) {
		if (!form) return;
		form.addEventListener('submit', function(e) {
			e.preventDefault();
			var formData = new FormData(form);
			var li = form.closest('li');
			var studentId = form.querySelector('input[name="student_id"]').value;
			console.log('[Unassign] Submitting unassign for studentId:', studentId);
			fetch(form.action, {
				method: 'POST',
				body: formData,
				headers: { 'X-Requested-With': 'XMLHttpRequest' }
			})
			.then(response => {
				console.log('[Unassign] AJAX response status:', response.status);
				return response.json();
			})
			.then(data => {
				console.log('[Unassign] AJAX response data:', data);
				if (data.success && li) {
					li.remove();
					var assignedList = document.getElementById('assigned-students-list');
					if (assignedList && assignedList.children.length === 0) {
						var placeholder = document.createElement('li');
						placeholder.textContent = 'No students assigned.';
						assignedList.appendChild(placeholder);
						console.log('[Unassign] Added "No students assigned." placeholder');
					}
					var assignForms = document.querySelectorAll('.assign-student-form');
					assignForms.forEach(function(assignForm) {
						var assignStudentId = assignForm.querySelector('input[name="student_id"]').value;
						if (assignStudentId === studentId) {
							var assignButton = assignForm.querySelector('button[type="submit"]');
							assignButton.disabled = false;
							assignButton.style.opacity = '1';
							var assignLi = assignForm.closest('li');
							if (assignLi) assignLi.style.opacity = '1';
						}
					});
				} else {
					console.log('[Unassign] Unassign failed or not successful:', data);
				}
			})
			.catch(error => {
				console.error('[Unassign] AJAX error:', error);
			});
		});
	}

	// Attach AJAX unassign handler to all existing forms
	document.querySelectorAll('.unassign-student-form').forEach(attachUnassignHandler);
});
