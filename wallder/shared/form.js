(() => {
  for (const form of document.querySelectorAll('[data-demo-form]')) {
    const fields = [...form.querySelectorAll('[data-validate]')];
    const result = form.querySelector('[data-form-result]');
    form.noValidate = true;

    function validate(field) {
      const error = form.querySelector('#' + field.id + '-error');
      const reason = field.required && !field.value.trim() ? 'missing' :
        field.validity.typeMismatch ? 'email' : '';
      if (reason) field.setAttribute('aria-invalid', 'true');
      else field.removeAttribute('aria-invalid');
      error.hidden = !reason;
      for (const message of error.children) message.hidden = message.dataset.error !== reason;
      return !reason;
    }

    for (const field of fields) {
      field.addEventListener('input', () => {
        if (field.hasAttribute('aria-invalid')) validate(field);
        result.hidden = true;
      });
    }

    form.addEventListener('submit', event => {
      event.preventDefault();
      const invalid = fields.filter(field => !validate(field));
      result.hidden = invalid.length > 0;
      if (invalid.length) invalid[0].focus();
      else result.focus();
    });
  }
})();
