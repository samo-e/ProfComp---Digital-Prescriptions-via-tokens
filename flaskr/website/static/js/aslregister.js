document.addEventListener("DOMContentLoaded", function () {
  const addBtn = document.getElementById("btn-add-manual");
  const form = document.getElementById("carer-form");
  const deleteBtn = document.getElementById("btn-delete-carer");

  if (addBtn) {
    addBtn.addEventListener("click", function () {
      form.classList.remove("d-none");
      addBtn.disabled = true;
    });
  }

  if (deleteBtn) {
    deleteBtn.addEventListener("click", function () {
      form.classList.add("d-none");
      addBtn.disabled = false;
    });
  }
});
