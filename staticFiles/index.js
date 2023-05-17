let selectedSentences = [];
let generatedParagraph = "";
let originalText = "";
let result_tfidf = "";
let result_tfidf_acc = 0.0;
let result_bm25 = "";
let result_bm25_acc = 0.0;
let category = "Yoga";
let error = "";
let thresholdValue = 1.0;









document.querySelector(".categorySelection").addEventListener("change", () => {
  const selectedValue = document.querySelector(".categorySelection").value;
  category = selectedValue;
  console.log(category)
})



// Select all radio buttons by their name attribute
const radioButtons = document.querySelectorAll('input[name="size"]');

// Variable to store the selected value


// Create an event listener for each radio button
radioButtons.forEach(radioButton => {
  radioButton.addEventListener('change', function () {
    if (this.checked) {
      thresholdValue = this.value;
      // console.log(thresholdValue);
      // Perform any desired actions with the selected value
    }
  });
});


document.querySelector(".button").addEventListener("click", () => {
  const input = document.querySelector(".input-field").value;
  originalText = input;
  const splitted = input.split(/([।?])/g);
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

function tfidfsummary(result_tfidf) {
  document.querySelector(".tfidfsummary").innerHTML = result_tfidf;
}

function BM25summary(result_bm25) {
  document.querySelector(".BM25Summary").innerHTML = result_bm25;
}

function accuracyResult(result_tfidf_acc) {
  document.querySelector(".accuracyValue").innerHTML = result_tfidf_acc;

}

function accuracyResultBM25(result_bm25_acc) {
  document.querySelector(".accuracyValueBM25").innerHTML = result_bm25_acc;

}


function showTFIDF(countTFIDF) {
  document.querySelector(".countTFIDF").innerHTML = countTFIDF;
}

function showBM25(countBM25) {
  document.querySelector(".countBM25").innerHTML = countBM25;
}

function showOriginal(countOriginal) {
  document.querySelector(".countOriginal").innerHTML = countOriginal;
}




document.querySelector(".submit").addEventListener("click", () => {

  // queryObj = { originalText: originalText , summary : generatedParagraph, new_var : category_value};
  queryObj = { originalText: originalText, summary: generatedParagraph, category: category, thresholdValue: thresholdValue };
  makePostRequest('http://127.0.0.1:5000/test', queryObj);

});

function countWords(paragraph) {
  // Replace all instances of "danda" (।) with an empty string
  const cleanedParagraph = paragraph.replace(/।/g, '');
  // Split the cleaned paragraph into an array of words
  const words = cleanedParagraph.split(' ');
  // Filter out any empty words
  const filteredWords = words.filter(word => word.trim() !== '');
  // Return the count of words
  return filteredWords.length;
}


function makePostRequest(path, queryObj) {
  axios.post(path, queryObj).then(
    (response) => {
      let result = response.data;
      result_tfidf = result.tfidf_sum;
      result_tfidf_acc = result.tfidf_acc;
      result_bm25 = result.bm25_sum;
      result_bm25_acc = result.bm25_acc;
      error = result.error;
      console.log(result_tfidf);
      console.log(result_tfidf_acc);
      console.log(result_bm25);
      console.log(result_bm25_acc);
      console.log(error);
      tfidfsummary(result_tfidf);
      accuracyResult(result_tfidf_acc);
      BM25summary(result_bm25);
      accuracyResultBM25(result_bm25_acc);
      countTFIDF = countWords(result_tfidf);
      countBM25 = countWords(result_bm25);
      countOriginal = countWords(originalText);

      showTFIDF(countTFIDF);
      showBM25(countBM25);
      showOriginal(countOriginal);

    },
    (error) => {
      console.log(error);
    }
  );
}
