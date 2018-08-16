$(document).ready(function() {

  // Markdown Editor
  let element = document.getElementById('field-notes')
  if (element) {
    let editor = new SimpleMDE({element: element})
    document.querySelector('span.editor-info-block').style.display = 'none'
  }

})
