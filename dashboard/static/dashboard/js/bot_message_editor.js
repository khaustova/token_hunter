(function(window, document, undefined) {

    window.onload = init;
  
    function init(){
        let mdTextarea = document.getElementsByClassName("md-editor__textarea")[0];

        document.getElementById("bold-button").addEventListener("click", function() {
            styleText(mdTextarea, "<b>", "</b>")
        })

        document.getElementById("italic-button").addEventListener("click", function() {
            styleText(mdTextarea, "<i>", "</i>")
        })

        document.getElementById("underline-button").addEventListener("click", function() {
            styleText(mdTextarea, "<u>", "</u>")
        })

        document.getElementById("spoiler-button").addEventListener("click", function() {
            styleText(mdTextarea, "<s>", "</s>")
        })

        document.getElementById("link-button").addEventListener("click", function() {
            makeElement(mdTextarea, `<a href="Ссылка">Название ссылки</a>`)
        })

        document.getElementById("code-button").addEventListener("click", function() {
            styleText(mdTextarea, "<code>", "</code>")
        })

        document.getElementById("lt-button").addEventListener("click", function() {
            makeElement(mdTextarea, `&lt;`)
        })

        document.getElementById("gt-button").addEventListener("click", function() {
            makeElement(mdTextarea, `&gt;`)
        })

        document.getElementById("amp-button").addEventListener("click", function() {
            makeElement(mdTextarea, `&amp;`)
        })

        let previewButton = document.getElementById('preview-button');
        let previewField = document.getElementById("preview-field")
        let previewInfo = document.getElementsByClassName("md-editor__preview_info")[0]
        let toolBar = document.getElementsByClassName("toolbar-list")[0]

        previewButton.addEventListener("click", function() {
            previewField.innerHTML = mdTextarea.value.replace(/\n/g, '<br>\n');
            previewField.classList.toggle("show")
            mdTextarea.classList.toggle("hide")
            toolBar.classList.toggle("hide")
            previewInfo.classList.toggle("show")
            if (previewField.classList.contains("show")) {
                previewButton.innerHTML = '<span class="material-symbols-outlined">visibility_off</span>'
            }
            else {
                previewButton.innerHTML = '<span class="material-symbols-outlined">visibility</span>'
            }
            
        })
    }

  })(window, document, undefined);


function styleText(textatrea, commandStart, commandEnd) {
    if (textatrea.selectionStart == textatrea.selectionEnd) {
        textatrea.setRangeText(`${commandStart}${commandEnd}`, textatrea.selectionStart, textatrea.selectionEnd, "end");
        textatrea.focus();
        return;
    }
    
    let selected = textatrea.value.slice(textatrea.selectionStart, textatrea.selectionEnd);
    textatrea.setRangeText(`${commandStart}${selected}${commandEnd}`);
}

function makeElement(textatrea, element) {
    textatrea.setRangeText(`${element}`, textatrea.selectionStart, textatrea.selectionEnd, "end");
    textatrea.focus();
}