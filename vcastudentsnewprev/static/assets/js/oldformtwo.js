$(document).ready(function () {
    $('.select2').select2({
        placeholder: 'Select an option', // Placeholder text
        width: '100%', // Width of the dropdown
        theme: 'bootstrap', // Apply Bootstrap theme for styling
        minimumResultsForSearch: Infinity, // Hide the search input
        dropdownCssClass: 'custom-dropdown', // Apply custom CSS class for styling
        // Additional options...
    });
});


//next part

function selectAnswerMode(mode) {
    // Speech synthesis messages
    $('.mode').html(mode);
    if (mode === 'speak') {
        speak('You have selected to answer orally.');
    } else if (mode === 'type') {
        speak('You have selected to type the answers.');
    }

    // Update UI or perform actions based on the selected mode
    if (mode === 'speak') {
        // Code for speak mode
        // You might want to show/hide relevant UI elements
        console.log('Speak mode selected');
    } else if (mode === 'type') {
        // Code for type mode
        // You might want to show/hide relevant UI elements
        console.log('Type mode selected');
    }

    // Close the answer mode modal
    closeAnswerModeModal();
    $('#selectModeButton').hide()
    // Show the "Start" button
    $('#startButton').show();
}

function speak(text, callback) {
    
    
var utterance = new SpeechSynthesisUtterance(text);

// Set up onend event to trigger the callback
utterance.onend = function () {
    if (callback) {
        callback();
    }
};

// Speak the text
speechSynthesis.speak(utterance);

// If speech synthesis is not supported, call the callback immediately
if (!speechSynthesis.speaking) {
    if (callback) {
        callback();
    }
}
}
        
let currentQuestionIndex = 0;
    let recognition;
    let testnumber
     function startQuestions() {
        var mode = $('.mode').html()
        $.ajax({
                    url: '/get_testnumber',  // Update the URL to the endpoint that fetches chapters
                    type: 'GET',
                    // data: { subject_id: selectedSubjectId },
                    // dataType: 'json',
                    success: function (data) {
                        // alert(data.testnumber)
                        if (data.testnumber == ""){
                            testnumber = 1
                        }else{
                            
                            testnumber = parseInt(data.testnumber)+1
                            
                        }
                        collectedData.numbertest.push(testnumber);
                        sname = $('#subjectDropdown').val();
                        cname = $('#chapterDropdown').val();
                        collectedData.subjectname.push(sname);
                        collectedData.chaptername.push(cname);


                    }})
        // Retrieve the selected subject and chapter IDs
    
        
    askQuestion(mode)
    
    }
    function askQuestion(mode) {
        // alert(mode)
       
           
            

            if (mode === 'speak') {
                if(recognition){
        recognition.stop();
    }
        // Code for speak mode
        // You might want to show/hide relevant UI elements
        speakquestion();
                
                
        } else if (mode === 'type') {
            
            // Code for type mode
            // You might want to show/hide relevant UI elements
            // alert("entered into type ")
            $('#inputtext').html('')
            displayQuestion();
            $('#inputtext').show();
            $('#submitButton').show();

        }
        
    }

    function addSubmitListener() {
        stopSpeech();
        $('#submitButton').on('click', function () {
            $('#inputtext').html('')
            if (speechSynthesis.speaking) {
            speechSynthesis.cancel();
            alert('here')
        }
            
            

            
            handleTypedAnswer();
        });
    }

    function handleTypedAnswer() {
        var mode = $('.mode').html()
        if (speechSynthesis.speaking) {
    speechSynthesis.cancel();
}
        if($('#inputtext').val() == ''){
            
            speak("You have not entered any answer")
            askQuestion(mode);
            return false
        }
        correctAnswer =   $('#answer').text();
        console.log(correctAnswer,"correctAnswer")
        var typedAnswer = $('#inputtext').val();
        
        console.log(typedAnswer,"typedAnswer")
        checkAnswer(typedAnswer,correctAnswer);
        $('#inputtext').val('');

    }


    var collectedData = {
questions: [],
correctAnswers: [],
userAnswers: [],
similarityScores: [],
attemptednumber:[],
numbertest:[],
subjectname:[],
chaptername:[]
    };

    
    function displayQuestion() {
        
        // Display the question based on your UI logic
        var questionList = $('#questionList').html(); // Assuming you have a question list
        $.getJSON('/get_question/' + questionList + '/' + currentQuestionIndex, function (data) {
            if (data.question !== '') {
                console.log(data.question,"this is question")
                $('#question').text(data.question);
                $('#answer').text(data.answer);
                
                speak(data.question);
                if(recognition){
                    recognition.stop()
                }
                
            } else {
                $('#question').text('End of questions.');
                speak('End of questions.');
                // currentQuestionIndex = 0;
                handleEndOfQuestions()
            }
        });
    }

   
    function handleEndOfQuestions() {
        $('#submitButton').hide();
        $('#startButton').hide();
        $('#inputtext').hide();



        console.log(collectedData)
        // Make an AJAX request to save the results
        $.ajax({
            url: '/save_results',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(collectedData),
            success: function (response) {  
                console.log(response,"save_results");
                // Handle success if needed
            },
            error: function (error) {
                console.error(error);
                // Handle error if needed
            },
            
        });
    }


    function speakquestion() {
        $('#startButton').hide();
    questionList = $('#questionList').html()
        $.getJSON('/get_question/' + questionList + '/' +currentQuestionIndex, function (data) {
            if (data.question !== '') {
                $('#question').text(data.question);
                $('#answer').text(data.answer);
                if(recognition){
                    recognition.stop()
                }
                // Use the speak function with the callback
                    speak(data.question, function () {
                        // Call listenForAnswer after the speech is finished
                        listenForAnswer(data.answer);
                    });
            } else {
                $('#question').text('End of questions.');
                speak('End of questions.');
                // $('#question').text("");
                currentQuestionIndex = 0;
                handleEndOfQuestions()
            }
        });
    }

    function listenForAnswer(correctAnswer) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.lang = 'en-US';
        recognition.start()

        recognition.onresult = function (event) {
            
            let userAnswer = event.results[event.results.length - 1][0].transcript.toLowerCase();
            console.log('User Answer:', userAnswer);
            console.log(correctAnswer,"correctAnswer")
            // Calculate fuzzy similarity between user's answer and correct answer
            let similarityScore = similarity(userAnswer, correctAnswer.toLowerCase());
            console.log(similarityScore,'similarity')
            if (similarityScore >= 0.7) {  // You can adjust the similarity threshold
                console.log('Correct!');
                speak("Thats Correct, you are doing Great");
                if(attempt == 1){
                    collectedData.attemptednumber.push(1);
                }else if(attempt == 2){
                    collectedData.attemptednumber.push(2);
                }else{
                    collectedData.attemptednumber.push(10);
                }
                recognition.stop();
                
                collectedData.userAnswers.push(userAnswer);
                collectedData.similarityScores.push(similarityScore);
                // alert($('#question').text())
                collectedData.questions.push($('#question').text());
                collectedData.correctAnswers.push($('#answer').text());
                currentQuestionIndex++;
                attempt = 1;
                speakquestion();
            } else {
                // Check if it's the second attempt for the same question
                if (sessionStorage.getItem('lastQuestion') === currentQuestionIndex.toString()) {
                    recognition.stop();
                    console.log('Incorrect. The correct answer is:', correctAnswer);
                    speak(`Sorry, it's incorrect. The correct answer is ${correctAnswer}`);
                    sessionStorage.removeItem('lastQuestion'); // Clear the session storage
                    collectedData.userAnswers.push(userAnswer);
                    collectedData.similarityScores.push(similarityScore);
                    attempt++;
                    collectedData.attemptednumber.push(attempt);
                    collectedData.questions.push($('#question').text());
                    collectedData.correctAnswers.push($('#answer').text());
                    currentQuestionIndex++;
                    speakquestion();
                } else {
                    console.log('Incorrect. Please try again.');
                    recognition.stop();
                    speak("Sorry, it's incorrect. Please try again.");
                    sessionStorage.setItem('lastQuestion', currentQuestionIndex.toString());
                    attempt++;
                    speakquestion();
                }
            }
        };
        

        // recognition.stop();
    }
var attempt = 1;
// Function to check the correctness of the answer
function checkAnswer(userAnswer, correctAnswer,recognition = "") {

var mode = $('.mode').html()
if (userAnswer  == "No answer received") { // You can adjust the similarity threshold
    speak("Time is up.Repeating the question");
    if(recognition){
        recognition.stop();
    }
    askQuestion(mode);
}
// alert(attempt)


// Calculate fuzzy similarity between user's answer and correct answer
let similarityScore = similarity(userAnswer, correctAnswer.toLowerCase());

console.log(similarityScore, 'similarity');


if (similarityScore >= 0.7) { // You can adjust the similarity threshold
    console.log('Correct!');
    speak("Thats Correct, you are doing Great");
    if(attempt == 1){
        collectedData.attemptednumber.push(1);
    }else if(attempt == 2){
        collectedData.attemptednumber.push(2);
    }else{
        collectedData.attemptednumber.push(10);
    }
    if(recognition){
        recognition.stop();
    }
    collectedData.userAnswers.push(userAnswer);
    collectedData.similarityScores.push(similarityScore);
    // alert($('#question').text())
    collectedData.questions.push($('#question').text());
    collectedData.correctAnswers.push($('#answer').text());
    currentQuestionIndex++;
    attempt = 1;
    askQuestion(mode);
    
} else {
    // Check if it's the second attempt for the same question
        // console.log('Incorrect. Please try again.');
        // speak("Sorry, it's incorrect. Please try again.");
        // if(recogniton){
        //     recognition.stop();
        // }
        // askQuestion(mode);

        if (sessionStorage.getItem('lastQuestion') === currentQuestionIndex.toString()) {
            
                    console.log('Incorrect. The correct answer is:', correctAnswer);
                    speak(`Sorry, it's incorrect. The correct answer is ${correctAnswer}`);
                    sessionStorage.removeItem('lastQuestion'); // Clear the session storage
                    sessionStorage.removeItem('attempt'); 
                    collectedData.userAnswers.push(userAnswer);
                    collectedData.similarityScores.push(similarityScore);
                    attempt++;
                    collectedData.attemptednumber.push(attempt);
                    collectedData.questions.push($('#question').text());
                    collectedData.correctAnswers.push($('#answer').text());
                    currentQuestionIndex++;
                    attempt = 1;
                    askQuestion(mode);
            } else {
                console.log('Incorrect. Please try again.');
             
                speak("Sorry, it's incorrect. Please try again.");
                sessionStorage.setItem('lastQuestion', currentQuestionIndex.toString());
                attempt++;
                askQuestion(mode);
            }
}
}

function similarity(s1, s2) {
        var longer = s1;
        var shorter = s2;
        if (s1.length < s2.length) {
            longer = s2;
            shorter = s1;
        }
        var longerLength = longer.length;
        if (longerLength == 0) {
            return 1.0;
        }


        return (longerLength - editDistance(longer, shorter)) / parseFloat(longerLength);
    }
    function editDistance(s1, s2) {
        s1 = s1.toLowerCase();
        s2 = s2.toLowerCase();

        var costs = new Array();
        for (var i = 0; i <= s1.length; i++) {
            var lastValue = i;
            for (var j = 0; j <= s2.length; j++) {
                if (i == 0)
                    costs[j] = j;
                else {
                    if (j > 0) {
                        var newValue = costs[j - 1];
                        if (s1.charAt(i - 1) != s2.charAt(j - 1))
                            newValue = Math.min(Math.min(newValue, lastValue),
                                costs[j]) + 1;
                        costs[j - 1] = lastValue;
                        lastValue = newValue;
                    }
                }
            }
            if (i > 0)
                costs[s2.length] = lastValue;
        }
        return costs[s2.length];
    }

//the next one

// Disable back button
history.pushState(null, null, document.URL);

// Prevent going back on popstate
window.addEventListener('popstate', function (event) {
    history.pushState(null, null, document.URL);
    alert("Back button is disabled.");
    event.preventDefault();
});

// Add an event listener for the logout button
$(document).on("click", "#logoutButton", function (event) {
    event.preventDefault();
    logout();
});

// Add an event listener for beforeunload to handle browser close
window.addEventListener('beforeunload', function (event) {
    // Perform asynchronous logout when the user closes the browser
    logoutAsync();
});

function logout() {
    // Clear session and redirect to the logout page
    sessionStorage.clear();
    window.location.href = "{{ url_for('logout') }}";
}

function logoutAsync() {
    // Perform any asynchronous logout actions, such as making an AJAX request
    // Example using jQuery for simplicity, you can use other methods like Fetch API
    $.ajax({
        type: 'POST',
        url: 'logout.php', // Replace with your server-side logout endpoint
        async: false, // Synchronous request for better compatibility
        success: function (data) {
            // Handle success if needed
            console.log("Logout successful");
        },
        error: function (xhr, textStatus, errorThrown) {
            // Handle error if needed
            console.error("Logout error");
        }
    });
}


    

//the next one 4
document.addEventListener('DOMContentLoaded', function () {
    // Create a new XMLHttpRequest object
    var xhr = new XMLHttpRequest();

    // Configure it to make a GET request to your /getremainingtime endpoint
    xhr.open('GET', '/getremainingtime', true);

    // Define the callback function to handle the response
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            // Parse the JSON response
            var data = JSON.parse(xhr.responseText);

            // Assuming the API response has a 'daysLeft' property
            var daysLeft = data.daysLeft;

            // Update the content of the <h1> element
            document.getElementById('timeline').innerText = 'Timeline: You have ' + daysLeft + ' days left for subscription';
        }
    };

    // Send the AJAX request
    xhr.send();
});

//the next one 5

// Function to update the countdown timer
function updateCountdown() {
    // Set the deadline to May 5, 2024, at midnight
    var deadline = moment('2024-05-05T00:00:00');

    // Calculate the remaining time
    var now = moment();
    var remainingTime = moment.duration(deadline - now);

    // Display the remaining time in a user-friendly format
    var days = Math.floor(remainingTime.asDays());
    var hours = remainingTime.hours();
    var minutes = remainingTime.minutes();
    var seconds = remainingTime.seconds();

    // Update the HTML content
    $('#countdown-timer').html('Time remaining: ' + days + ' days, ' + hours + ' hours, ' + minutes + ' minutes, ' + seconds + ' seconds');
}

// Update the countdown every second
setInterval(updateCountdown, 1000);

// Initial call to set up the countdown
updateCountdown();

//one more

var isInteractiveMode = false;

    function toggleInteractive() {
        var kastamElements = $('.kastam');

        // Toggle visibility of elements with class 'kastam'
        kastamElements.toggle();
        if (speechSynthesis.speaking) {
                speechSynthesis.cancel();
            }

        // Toggle the mode and update button text
        isInteractiveMode = !isInteractiveMode;
        updateButtonText();
    }

    function updateButtonText() {
        var button = $('#interactive');

        // Update button text based on the current mode
        if (isInteractiveMode) {
            button.text('Stop Interactive Mode');
            speak('Interactive Mode activated.');
            // InteractiveMode()
            $('#dropdownContainer').show()
        } else {
            button.text('Start Interactive Mode');
            window.location.reload()
           
        }
    }

    // function InteractiveMode(){
    //     navigator.mediaDevices.getUserMedia({ audio: true })
    //       .then(function(stream) {
    //         console.log('Microphone access granted!');
    //         $('#dropdownContainer').show()
    //       })
    //       .catch(function(err) {
    //         console.error('Error accessing microphone:', err);
    //         alert("Unable to find Mic input")

    //       });
    // }


    document.addEventListener('DOMContentLoaded', function () {
  const dropdownContainer = document.getElementById('dropdownContainer');
  const timeIntervalSelect = document.getElementById('timeInterval');
  let intervalId;
  let timeoutId;

  document.getElementById('submitBtn').addEventListener('click', function () {

    
    const selectedInterval = timeIntervalSelect.value;
    const currentTime = new Date().toLocaleTimeString();
    if(selectedInterval == 30){
        xyz = " 30 minutes"
    }else if(selectedInterval == 60){
        xyz = " 1 hour"
    }else if(selectedInterval == 90){
        xyz = " 1 and half hour"
    }else if(selectedInterval == 120){
        xyz = " 2 hour"
    }else{
        xyz = " 1 hour"
    }
    $('#selected-timer').html("You have selected "+xyz+ " interval")

    // Assuming you have an API endpoint in app.py to handle the time and interval
    fetch('/interactive', {
      method: 'POST',
      body: JSON.stringify({
        currentTime: currentTime,
        timeInterval: selectedInterval,
      }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('API Response:', data.results[0].question);
        if (data.results[0].question !== '') {
          console.log(data.results[0], "this is question");
          speak("Hey!! I am about to shoot you a question");

          var userResponse = confirm("Are you ready?");
            if (!userResponse) {
                speak("Okay, let me know when you are ready.");
                return false;

            }else{
                if (speechSynthesis.speaking) {
    speechSynthesis.cancel();
  }
            
            speak("Great! Let's proceed.");

            // var displayText = "Question:" + data.results[0].question + " (Number of Times answered wrong previously: " + data.results[0].attempt_no + ")";

            $('#question_inter').text(data.results[0].question);
            $('#attemptno').html("Number of Times answered wrongly previously:"+data.results[0].attempt_no)

          $('#answer_inter').text(data.results[0].correct_answer);

          speak(data.results[0].question);
          if (recognition) {
            recognition.stop();
          }
          $('#inputtext_inter').show();
          $('#submitButton_inter').show();

          clearTimeout(timeoutId);

          // Set a timeout for 2 minutes to submit an empty answer
        //   timeoutId = setTimeout(function () {
        //     speak("It seems like you need to study this")
        //     handleTypedAnswer_inter()
        //   }, 0.5 * 60 * 1000); // 2 minutes in milliseconds
            }
        } else {
          $('#question_inter').text('End of questions.');
          speak('End of questions.');
          handleEndOfQuestions();
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });

    dropdownContainer.style.display = 'none';

    // Start the interval only when the user submits the form
    intervalId = setInterval(function () {
      const currentTime = new Date().toLocaleTimeString();

      // Make API call at the specified interval
      fetch('/interactive', {
        method: 'POST',
        body: JSON.stringify({
          currentTime: currentTime,
          timeInterval: selectedInterval,
        }),
      })
        .then(response => response.json())
        .then(data => {
          //   console.log('API Response:', data);
          if (data.results[0].question !== '') {
            console.log(data.results[0].question, "this is question");
            speak("Hey!! I am about to shoot you a question");
            var userResponse = confirm("Are you ready?");
            if (!userResponse) {
                speak("Okay, let me know when you are ready.");
                return false;

            }else{
                if (speechSynthesis.speaking) {
    speechSynthesis.cancel();
  }
            speak("Great! Let's proceed.");

            // var displayText = "Question " + data.results[0].question + " (Attempt No: " + data.results[0].attemptno + ")";

            // $('#question_inter').text(displayText);
            $('#question_inter').text(data.results[0].question);
            $('#attemptno').html("Number of Times answered wrongly previously:"+data.results[0].attempt_no)
            $('#answer_inter').text(data.results[0].answer);

            speak(data.results[0].question);
            if (recognition) {
              recognition.stop();
            }
            $('#inputtext_inter').show();
            $('#submitButton_inter').show();

            clearTimeout(timeoutId);

            // Set a timeout for 2 minutes to submit an empty answer
            // timeoutId = setTimeout(function () {
            //   speak("It seems like you need to study this")
            //   handleTypedAnswer_inter()
              
            // }, 0.5 * 60 * 1000); // 0.5 minutes in milliseconds
            }
          } else {
            $('#question_inter').text('End of questions.');
            speak('End of questions.');
            handleEndOfQuestions();
          }
        })
        .catch(error => {
          console.error('Error:', error);
        });
    }, selectedInterval * 60 * 1000); // Convert minutes to milliseconds
  });

  // Stop the interval and clear the timeout when the user leaves the page or closes the browser
  window.addEventListener('beforeunload', function () {
    clearInterval(intervalId);
    clearTimeout(timeoutId);
  });
});

function addSubmitListener_inter() {
  $('#submitButton_inter').on('click', function () {
    clearTimeout(timeoutId); // Clear the timeout when the user manually submits an answer
    $('#inputtext_inter').html('');
    handleTypedAnswer_inter();
  });
}

function handleTypedAnswer_inter() {
  if (speechSynthesis.speaking) {
    speechSynthesis.cancel();
  }
  correctAnswer = $('#answer_inter').text();
    

  if ($('#inputtext_inter').val() == '') {
    // alert('handleTypedAnswer_inter')
    speak("You have not entered any answer");
    checkAnswer_inter("Unanswered", correctAnswer);
  }
  
  console.log(correctAnswer, "correctAnswer");
  var typedAnswer = $('#inputtext_inter').val();

  console.log(typedAnswer, "typedAnswer");
  checkAnswer_inter(typedAnswer, correctAnswer);
  
  $('#inputtext_inter').val('');
}

function checkAnswer_inter(userAnswer, correctAnswer) {
  // Calculate fuzzy similarity between user's answer and correct answer
  let similarityScore = similarity(userAnswer, correctAnswer.toLowerCase());
  var collectedDataInteractive = {
    questions: [$('#question_inter').text()],
    correctAnswers: [$('#answer_inter').text()],
    userAnswers: [userAnswer],
    similarityScores: [similarityScore],
        };
  console.log(similarityScore, 'similarity');

  if (similarityScore >= 0.7) {
    // You can adjust the similarity threshold
    console.log('Correct!');
    speak("Thats Correct, you are doing Great");
  } else {
    console.log('Incorrect. The correct answer is:', correctAnswer);
    speak(`Sorry, it's incorrect. The correct answer is ${correctAnswer}`);
    $('#question_inter').show();
    $('#answer_inter').show();


  }
  save_interactive(collectedDataInteractive)
  $('#question_inter').text('');
//   $('#question_inter').hide();
  $('#answer_inter').val('');
//   $('#answer_inter').hide();
  $('#submitButton_inter').hide();
  $('#inputtext_inter').hide();
  $('#attemptno').hide()
}


function save_interactive(collectedDataInteractive){
    $.ajax({
                url: '/save_interactive',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(collectedDataInteractive),
                success: function (response) {  
                    console.log(response,"save_results");
                    // Handle success if needed
                },
                error: function (error) {
                    console.error(error);
                    // Handle error if needed
                },
                
            });
}

// the dark mode one

 // Get the dark mode toggle element
 const darkModeToggle = document.getElementById('darkModeToggle');

 // Check if user has a preference for dark mode
 const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

 // Set initial theme based on user preference or default to light mode
 if (prefersDarkMode) {
     document.body.classList.add('dark-mode');
     darkModeToggle.checked = true;
 }

 // Toggle between light and dark mode when the toggle is clicked
 darkModeToggle.addEventListener('change', () => {
     document.body.classList.toggle('dark-mode');
 });



