$(document).on("click", function (e) {
  const modalEl = document.getElementById("imageModal");
  const modal = bootstrap.Modal.getInstance(modalEl);

  if (modal && modalEl.classList.contains("show")) {
    modal.hide();
  }
});

$(document).ready(function () {
  $("img")
    .not("#modalImage")
    .on("click", function () {
      const src = $(this).attr("src");
      $("#modalImage").attr("src", src);
      const modal = new bootstrap.Modal(document.getElementById("imageModal"));
      modal.show();
    });
});

window.addEventListener("load", function () {
  new bootstrap.ScrollSpy(document.body, {
    target: "#navbar-contents",
    offset: 10,
  });
});
