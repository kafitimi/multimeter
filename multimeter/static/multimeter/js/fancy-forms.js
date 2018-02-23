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
        var $host = $('div[data-form="' + id.slice(3) + '"]');
        
        if ($input.attr('type') === 'checkbox') {
            // Чекбокс - это особый случай
            $label.addClass('form-check-label')
            $input.addClass('form-check-input');
            $host.prepend($label);
            $host.prepend($input);
        } else {
            // Для остальных элементов
            $input.addClass('form-control');
            $host.prepend($input);
            $host.prepend($label);
        }
    });
    
    // Обход скрытых элементов
    $form.find('input[type="hidden"]').each(function() {
        var id = $(this).attr('id');
        var $input = $form.find('#' + id);
        var $host = $('div[data-form="' + id.slice(3) + '"]');
        
        $input.addClass('form-control');
        $host.prepend($input);
    });
    
    // Удаляем форму со страницы
    $form.remove();
});