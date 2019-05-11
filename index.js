var messages = [], //array that hold the record of each string in chat
    lastUserMessage = "", //keeps track of the most recent input string from the user
    botName = 'Chatbot', //name of the chatbot
    talking = true, //when false the speach function doesn't work
    api_key = None;


function intiAWS() {
    //get id_token param from URL
    var idToken = window.location.href.split('=')[1].slice(0,-13);
    AWS.config.region = 'us-west-2';
    AWS.config.credentials = new AWS.CognitoIdentityCredentials({
        IdentityPoolId: 'us-west-2:0cd1ab89-62fe-4f69-af79-76629882abce',
        Logins: {
            'cognito-idp.us-west-2.amazonaws.com/us-west-2_jzs4z7cwD': idToken
        }
    });

    AWS.config.credentials.get(function (err) {
        if (err) {
            alert("You have been logged out automatically! Re-SignIn Required.");
            window.location.replace("https://aceyuanchatbotsign.auth.us-west-2.amazoncognito.com/login?response_type=token&client_id=7v30pltq6mgg3boilfm9cv3ukg&redirect_uri=https://s3-us-west-2.amazonaws.com/album-bot/index.html");
        }
    });
}

function postData(message) {
    var apigClient;
    AWS.config.credentials.refresh(function (err) {
        if (err) {
            alert(err)
        } else {
            apigClient = apigClientFactory.newClient({
                accessKey: AWS.config.credentials.accessKeyId,
                secretKey: AWS.config.credentials.secretAccessKey,
                sessionToken: AWS.config.credentials.sessionToken,
                apiKey: api_key,
                region: 'us-west-2'
            });

            var params = {
            };

            var body = {
            };

            var additionalParams = {
                // If there are any unmodeled query parameters or headers that must be
                //   sent with the request, add them here.
                queryParams: {
                    'qr': message,
                    'id': AWS.config.credentials.identityId
                }
            };

            apigClient.searchGet(params, body, additionalParams)
                .then(function (result) {
                    var jsonString = JSON.parse(result.data.body);
                    var botMessage = jsonString["messages"][0]["unstructured"]["text"];
                    //add the chatbot's name and message to the array messages
                    messages.push("<b>" + botName + ":</b> " + botMessage[0]);
                    // says the message using the text to speech function written below
                    //Speech(botMessage);
                    //outputs the last few array elements of messages to html
                    for (var i = 1; i < 8; i++) {
                        if (messages[messages.length - i])
                            document.getElementById("chatlog" + i).innerHTML = messages[messages.length - i];
                    }
                    //populate the search result module
                    if (botMessage.length > 1) {
                        botMessage.shift()
                        loadingSearchResults(botMessage);
                    }
                }).catch(function (result) {
                    // Add error callback code here.
                    alert(result);
                });
        }
    })
}
//
//
//****************************************************************
//****************************************************************
//****************************************************************
function chatbotResponse() {
    talking = true;
    postData(lastUserMessage);
}

//****************************************************************
function loadingSearchResults(images) {
    //remove history images in this images
    var node = document.getElementById("gallery");
    while (node.firstChild) {
        node.removeChild(node.firstChild);
    }
    //fill in new images
    for (var i = 0; i < images.length; i++) {
        var node = new Image(255, 200);
        node.src = images[i];
        document.getElementById("gallery").appendChild(node)
    }
    //show up modal
    $('#resultModal').modal('show');
}
//****************************************************************
//****************************************************************
//
//
//
//this runs each time enter is pressed.
//It controls the overall input and output
function newEntry() {
    //var images = ["London-Intro-4X3.jpg", "nyc-street.jpg", "London-Intro-4X3.jpg", "nyc-street.jpg"];
    
    //if the message from the user isn't empty then run 
    if (document.getElementById("chatbox").value != "") {
        //pulls the value from the chatbox ands sets it to lastUserMessage
        lastUserMessage = document.getElementById("chatbox").value;
        //sets the chat box to be clear
        document.getElementById("chatbox").value = "";
        //adds the value of the chatbox to the array messages
        messages.push(lastUserMessage);
        //Speech(lastUserMessage);  //says what the user typed outloud
        //sets the variable botMessage in response to lastUserMessage
        chatbotResponse();
    }
}

//text to Speech
//https://developers.google.com/web/updates/2014/01/Web-apps-that-talk-Introduction-to-the-Speech-Synthesis-API
function Speech(say) {
    if ('speechSynthesis' in window && talking) {
        var utterance = new SpeechSynthesisUtterance(say);
        //msg.voice = voices[10]; // Note: some voices don't support altering params
        //msg.voiceURI = 'native';
        //utterance.volume = 1; // 0 to 1
        //utterance.rate = 0.1; // 0.1 to 10
        //utterance.pitch = 1; //0 to 2
        //utterance.text = 'Hello World';
        //utterance.lang = 'en-US';
        speechSynthesis.speak(utterance);
    }
}

//runs the keypress() function when a key is pressed
document.onkeypress = keyPress;
//if the key pressed is 'enter' runs the function newEntry()
function keyPress(e) {
    var x = e || window.event;
    var key = (x.keyCode || x.which);
    if (key == 13 || key == 3) {
        //runs this function when enter is pressed
        newEntry();
    }
    if (key == 38) {
        console.log('hi')
        //document.getElementById("chatbox").value = lastUserMessage;
    }
}

//clears the placeholder text ion the chatbox
//this function is set to run when the users brings focus to the chatbox, by clicking on it
function placeHolder() {
    document.getElementById("chatbox").placeholder = "";
}

function uploadFile(e) {
    var file = e.target.files[0];
    const reader = new FileReader();
    const xhr = new XMLHttpRequest();
    const url = "https://r7dxay3a66.execute-api.us-west-2.amazonaws.com/demo/upload/my-album-photos/" + file.name;
    const extension = 'image/' + file.name.split('.').pop();
    xhr.open("PUT", url);
    xhr.setRequestHeader('x-api-key', api_key);
    xhr.setRequestHeader('Content-Type', extension);
    reader.onload = function (evt) {
        xhr.send(evt.target.result);
        console.log('upload successfully');
    };
    reader.readAsArrayBuffer(file);
    //console.log(e.target.files[0]);
}

function endrecord() {
    rec.stop();
    console.log('record end');
}

$('#voiceModal').on('shown.bs.modal', function (e) {
    var player = document.getElementById('player');

    var handleSuccess = function (stream) {
        rec = new MediaRecorder(stream);
        rec.start();
        console.log('record start');
        audioChunks = [];
        rec.ondataavailable = e => {
            audioChunks.push(e.data);
            if (rec.state == "inactive") {
                let blob = new Blob(audioChunks, { type: 'audio/mpeg-3' });
                console.log(blob);
                var blobUrl = URL.createObjectURL(blob);
                recordedAudio.src = URL.createObjectURL(blob);
                console.log(blobUrl);
                recordedAudio.autoplay = true;
                console.log('record wraped up');
            }
        }
    };

    navigator.mediaDevices.getUserMedia({ audio: true, video: false })
        .then(handleSuccess);
})

