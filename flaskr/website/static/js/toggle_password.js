$(function () {
  $("#password-view-toggle").click(function () {
    const $password = $("#password");
    const $icon = $(this).find("i");
    const isPassword = $password.attr("type") === "password";

    $password.attr("type", isPassword ? "text" : "password");
    $icon.toggleClass("bi-eye bi-eye-slash");
  });
});
