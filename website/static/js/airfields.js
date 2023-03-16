var filterActive;

function filterCategory(category) {
    if (filterActive != category) {
        
        // reset results list
        $('.filter-cat-results .f-cat').removeClass('active');
        
        // elements to be filtered
        $('.filter-cat-results .f-cat')
            .filter('[data-cat="' + category + '"]')
            .addClass('active');
        
        // reset active filter
        filterActive = category;
    }
}



$('.filtering select').change(function() {
    if ($(this).val() == 'cat-all') {
        $('.filter-cat-results .f-cat').addClass('active');
        filterActive = 'cat-all';
    } else {
        filterCategory($(this).val());
    }
});
