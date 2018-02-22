$(function() {
    // Находим форму на странице
    var $form = $('div#form');
    
    // Ошибки формы
    var $errorlist = $form.find('ul.nonfield.errorlist');
    var $holder = $('div[data-form="nonfield-errorlist"]');
    $errorlist.find('li').each(function() {
        $holder.append('<p>' + $(this).text() + '</p>');
    });
    
    // Обход полей формы
    $form.find('label').each(function() {
        var $label = $(this);
        var id = $label.attr('for');
        var $input = $form.find('#' + id);
        // Ищем куда вставить поле
        var $holder = $('div[data-form="' + id.slice(3) + '"]');
        
        if ($input.attr('type') === 'checkbox') {
            // Чекбокс - это особый случай
            $label.addClass('form-check-label')
            $input.addClass('form-check-input');
            $holder.append($input);
            $holder.append($label);
        } else {
            // Для остальных элементов
            $input.addClass('form-control');
            $holder.append($label);
            $holder.append($input);
        }
    });
    
    // Удаляем форму со страницы
    $form.remove();
});