// Darkmode
$(document).ready(function () {
    $(function () {
      // On page load, check cookie
      const theme = Cookies.get("theme") || "light";
      $("html").attr("data-bs-theme", theme);
      $("#switch-darkmode").prop("checked", theme === "dark");

      // On toggle
      $("#switch-darkmode").on("change", function () {
        const newTheme = this.checked ? "dark" : "light";
        $("html").attr("data-bs-theme", newTheme);
        Cookies.set("theme", newTheme, { expires: 365 }); // save for 1 year
      });
    });
});
