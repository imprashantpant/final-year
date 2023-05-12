function selectSentences() {
  const container = document.getElementById('container');
  const text = container.textContent;
  const sentences = text.split(/[.?!]+/);

  const selection = window.getSelection();
  selection.removeAllRanges();

  sentences.forEach(sentence => {
    const range = document.createRange();
    range.selectNodeContents(container);
    const sentenceIndex = text.indexOf(sentence);
    range.setStart(container.firstChild, sentenceIndex);
    range.setEnd(container.firstChild, sentenceIndex + sentence.length);
    selection.addRange(range);
  });
}
