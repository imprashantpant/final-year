
let selectedSentences = [];
let generatedParagraph = "";

document.querySelector(".button").addEventListener("click", () => {
  const input = document.querySelector(".input-field").value;
  const splitted = input.split(/([.?!])/g);
  const sentences = [];
  //To add the punctuation associated with the sentence in the sentences array
  for (let i = 0; i < splitted.length; i += 2) {
    const sentence = splitted[i];
    const punctuation = splitted[i + 1] || "";
    sentences.push(sentence + punctuation);
  }
  let output = "";
  for (let i = 0; i < sentences.length; i++) {
    if (sentences[i] !== "") {
      output += `<button class="sentence">${sentences[i]}</button>. `;
    }
  }
  document.querySelector(".output").innerHTML = output;

  const sentenceElements = document.querySelectorAll(".sentence");
  for (let i = 0; i < sentenceElements.length; i++) {
    sentenceElements[i].addEventListener("click", () => {
      if (!selectedSentences.includes(sentenceElements[i].innerHTML)) {
        selectedSentences.push(sentenceElements[i].innerHTML);
        console.log(selectedSentences);
        generateParagraph(selectedSentences);
      }
    });
  }
});

//to generate a new paragraph from the selected sentences
function generateParagraph(selectedSentences) {
  generatedParagraph = selectedSentences.join(" ").replace(/\s+/g, " ").trim();
  console.log(generatedParagraph);
}

