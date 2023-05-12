let selectedSentences = [];
let generatedParagraph = "";
let originalText = "";
let result_tfidf = "";
let result_tfidf_acc = 0.0;

document.querySelector(".button").addEventListener("click", () => {
  const input = document.querySelector(".input-field").value;
  originalText = input;
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
      output += `<button class="sentence test">${sentences[i]}</button>. `;
    }
  }
  document.querySelector(".output").innerHTML = output;

  const sentenceElements = document.querySelectorAll(".sentence");
  for (let i = 0; i < sentenceElements.length; i++) {
    sentenceElements[i].addEventListener("click", () => {
      if (![...sentenceElements[i].classList].includes("selected")) {
        sentenceElements[i].classList.add("selected");
      } else {
        sentenceElements[i].classList.remove("selected");
      }

      if (!selectedSentences.includes(sentenceElements[i].innerHTML)) {
        selectedSentences.push(sentenceElements[i].innerHTML);
        generateParagraph(selectedSentences);
      } else {
        item = sentenceElements[i].innerHTML;
        let itemIndex = selectedSentences.indexOf(item);
        let newSentences = [
          ...selectedSentences.slice(0, itemIndex),
          ...selectedSentences.slice(itemIndex + 1),
        ];
        selectedSentences = newSentences
        generateParagraph(selectedSentences);
      }
    });
  }
});

//to generate a new paragraph from the selected sentences
function generateParagraph(selectedSentences) {
  generatedParagraph = selectedSentences.join(" ").replace(/\s+/g, " ").trim();
  document.querySelector(".generatedOutput").innerHTML = generatedParagraph;
}

document.querySelector(".submit").addEventListener("click", () => {

  // queryObj = { originalText: originalText , summary : generatedParagraph, new_var : category_value};
  queryObj = { originalText: originalText, summary: generatedParagraph };
  makePostRequest('http://127.0.0.1:5000/test', queryObj);

});

function makePostRequest(path, queryObj) {
  axios.post(path, queryObj).then(
    (response) => {
      let result = response.data;
      result_tfidf = result.tfidf_sum;
      result_tfidf_acc = result.acc_tfids;
      console.log(result_tfidf);
      console.log(result_tfidf_acc);
    },
    (error) => {
      console.log(error);
    }
  );
}
