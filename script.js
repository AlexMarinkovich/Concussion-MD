var recording
navigator.mediaDevices.getUserMedia({video: true, audio: false})
    .then(stream => {
    // get video from webcam
    const video = document.getElementById('webcam-video')
    video.srcObject = stream
    video.play() 
    recording = new MediaRecorder(stream)

    // when recording stops, gets recording data
    recording.ondataavailable = event => {sendToPython(event.data)}
    })
    .catch(error => {console.error(error)})


function startRecording(event) {
    document.getElementById("start-button").innerHTML = "Started!"
    event.preventDefault()
    recording.start()
    setTimeout(function() {stopRecording(event)}, 5000)
}

function stopRecording(event) {
    event.preventDefault(); 
    recording.stop()
}

// send video data to python server
function sendToPython(recordedBlob) {
    // get base64data from recordedBlob
    var reader = new FileReader()
    reader.readAsDataURL(recordedBlob)
    reader.onloadend = function() {
        const base64data = reader.result;
        fetch('https://alexmarinkovich.pythonanywhere.com/processvideo', {
            method: 'POST',
            mode: 'no-cors',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({videodata: base64data})
        })} 
    document.getElementById("UnsucessfulText").style.display = "block" 
    }

setTimeout(function() {
    fetch('https://alexmarinkovich.pythonanywhere.com/getresult')
    .then(response => response.json())
    .then(data => {
        console.log(data)
        if (data == "") {return}
        else if (data == "-1") {document.getElementById("UnsucessfulText").style.display = "block"}
        else {document.getElementById("SucessfulText").style.display = "block"} // take this out later
        })
    .catch(error => {console.log(error)})
    }, 1000);