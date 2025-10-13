// Darkmode
$(function () {
  load_dark_mode();
});

(function () {
  load_dark_mode();
})();

function load_dark_mode() {
  // On page load, check cookie
  const theme = Cookies.get("theme") || "light";
  $("html").attr("data-bs-theme", theme);
  $("#switch-darkmode").prop("checked", theme === "dark");

  // On toggle
  $("#switch-darkmode").on("change", function () {
    const newTheme = this.checked ? "dark" : "light";
    $("html").attr("data-bs-theme", newTheme);
    Cookies.set("theme", newTheme, { expires: 365 });

    const buttons = document.querySelectorAll(".btn-dark, .btn-light");

    buttons.forEach((btn) => {
      if (btn.classList.contains("btn-dark")) {
        btn.classList.remove("btn-dark");
        btn.classList.add("btn-light");
      } else if (btn.classList.contains("btn-light")) {
        btn.classList.remove("btn-light");
        btn.classList.add("btn-dark");
      }
    });
  });
}
