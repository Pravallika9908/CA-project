
document.addEventListener('keydown', function(event) {
    // Check if Ctrl+U was pressed
    if(event.ctrlKey && event.key === 'u') {
        // Prevent the default action (view source)
        event.preventDefault();
    }
});

document.addEventListener('contextmenu', function (e) {
    e.preventDefault();
});

function openAnswerModeModal() {
    // Show the answer mode modal
    document.getElementById('answerModeModal').style.display = 'block';
}

function closeAnswerModeModal() {
    // Hide the answer mode modal
    document.getElementById('answerModeModal').style.display = 'none';
}


    $(document).ready(function () {
        $('#subjectDropdown').change(function () {
            var selectedSubjectId = $(this).val();
// alert(selectedSubjectId)
            // Clear existing options in the chapter dropdown
            $('#chapterDropdown').empty();
            $('#chapterDropdown').append('<option value="">---Select---</option>');

            // Fetch chapters based on the selected subject
            if (selectedSubjectId !== "") {
                $.ajax({
                    url: '/fetch_chapters',  // Update the URL to the endpoint that fetches chapters
                    type: 'GET',
                    data: { subject_id: selectedSubjectId },
                    dataType: 'json',
                    success: function (data) {
                        console.log(data), // Specify the expected data type

                            // Populate the chapter dropdown with fetched chapters
                            $.each(data.chapters, function (index, chapter) {
                                console.log(data)
                                var chapterId = chapter[0];
                                var chapterName = chapter[1];
                                $('#chapterDropdown').append('<option value="' + chapterName + '">' + chapterName + '</option>')
                            });

                // Update the selected subject display
                var selectedSubjectName = $('#subjectDropdown option:selected').text();
                $('#selectedSubjectDisplay').text(selectedSubjectName);

                // Clear the selected chapter display
                $('#selectedChapterDisplay').text('None');
                    },
                    error: function (error) {
                        console.log(error);
                    }
                });
            }
        });
    
$('#chapterDropdown').change(function () {
    // Update the selected chapter display
    var selectedChapterName = $('#chapterDropdown option:selected').text();
    $('#selectedChapterDisplay').text(selectedChapterName);
    var subjectid = $('#subjectDropdown').val()

    var isChapterSelected = selectedChapterName !== '---Select---';
    
        $('#selectModeButton').toggle(isChapterSelected);
        $('#questionList').html('')
        $.ajax({
                    url: '/fetchquestions',  // Update the URL to the endpoint that fetches chapters
                    type: 'GET',
                    data: { selectedChapterName: selectedChapterName,subjectid: subjectid },
                    dataType: 'json',
                    success: function (data) {
                        questions = data.chapters;
                        // alert(questions)
                        if(questions!=""){
                            $('#questionList').html(questions)
                        }else{
                            alert("there are no questions in this chapters, we will be adding soon!!!")
                            $('#selectModeButton').hide()
                            $('#startButton').hide();
                            $('#speakModeBtn').hide();
                            $('#typeModeBtn').hide();
                            $('#textanswer').hide()

                            
                            
                        }
                        

                    },
           
                    
                })

});
});


