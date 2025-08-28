// tabs-dropdown.js
$(document).ready(function() {
    // Listen to all tab changes (including top-level tabs)
    $('a[data-bs-toggle="tab"]').on('shown.bs.tab', function(e) {
        const activeHref = $(e.target).attr('href');
        const activeText = $(e.target).text();

        const $dropdownItem = $(`#dropdownMenu .dropdown-item[href="${activeHref}"]`);
        if ($dropdownItem.length) {
            // Update dropdown toggle text
            $('#dropdownMenuLink').text(activeText);

            // Show all dropdown items
            $('#dropdownMenu .dropdown-item').removeClass('d-none');

            // Hide the selected item
            $dropdownItem.addClass('d-none');
        }
    });
});
