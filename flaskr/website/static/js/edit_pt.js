$(document).ready(function() {
    $('a[data-bs-toggle="tab"]').on('shown.bs.tab', function(e) {
        const activeHref = $(e.target).attr('href');
        const activeText = $(e.target).text();

        const $dropdownItem = $(`#dropdownMenu .dropdown-item[href="${activeHref}"]`);
        if ($dropdownItem.length) {
            $('#dropdownMenuLink').text(activeText);
            $('#dropdownMenu .dropdown-item').removeClass('d-none');
            $dropdownItem.addClass('d-none');
        }
    });

    const $input = $("#test-input");
    const $dropdown = $("#suggestions");

    let debounceTimer;
    let currentRequest = null;

    $input.on("input", function () {
        const text = $(this).val();
        clearTimeout(debounceTimer);

        debounceTimer = setTimeout(function () {
            if (text.length < 2) {
                $dropdown.removeClass("show");
                return;
            }

            if (currentRequest) currentRequest.abort();

            currentRequest = $.getJSON("/ac", { text: text })
                .done(function (results) {
                    renderSuggestions(results, $input, $dropdown);
                })
                .fail(function (jqXHR, textStatus) {
                    if (textStatus !== "abort") {
                        console.error("Error:", jqXHR.responseJSON || jqXHR.statusText);
                    }
                })
                .always(function () {
                    currentRequest = null;
                });
        }, 250);
    });

    $(document).on("click", function(e) {
        if (!$(e.target).closest($input).length && !$(e.target).closest($dropdown).length) {
            $dropdown.removeClass("show");
        }
    });
});

function renderSuggestions(results, $input, $dropdown) {
    $dropdown.empty();
    if (!results || results.length === 0) {
        $dropdown.removeClass("show");
        return;
    }
    console.log(results);
    results.forEach(place => {
        const $item = $('<li><a class="dropdown-item" href="#"></a></li>');
        $item.find("a").text(place.formatted).on("click", function (e) {
            e.preventDefault();
            $input.val(place.formatted);
            $dropdown.removeClass("show");
        });
        $dropdown.append($item);
    });

    $dropdown.addClass("show");
}
