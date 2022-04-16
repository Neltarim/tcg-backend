var localhost = '127.0.0.1:8000/'
var matchMakingURL = 'ws://' + localhost + 'match-maker/';


function connect(username) {
  var gameSocket = new WebSocket(matchMakingURL);  
  gameSocket.onopen = function open() {
    console.log('WebSockets connection created.');
    gameSocket.send(JSON.stringify({
      "event": "LOGIN",
      "message": "",
      "username": username,
      "password": "qwer1234"
    }));



    document.getElementById('disconnect').addEventListener("click", () => {
      gameSocket.send(JSON.stringify({
        "event": "DISCONNECT",
        "message": "getting out."
      }))
    })
    document.getElementById('test').addEventListener("click", () => {
      gameSocket.send(JSON.stringify({
        "event": "TEST",
        "message": "testing from front"
      }))
    })
  };

  gameSocket.onclose = function (e) {
    console.log('Socket is closed.', e.reason);
  };
  // Sending the info about the room
  gameSocket.onmessage = function (e) {
    let data = JSON.parse(e.data);
    data = data["payload"] || 'no payload';
    let message = data['message'] || 'no message';
    let event = data["event"] || 'no event';
    console.log(event, message)
  };

  if (gameSocket.readyState == WebSocket.OPEN) {
    gameSocket.onopen();
  }
}

try {
  document.getElementById('sasono').addEventListener("click", () => {
    connect('sasono');
  })
  document.getElementById('neltarim').addEventListener("click", () => {
    connect('neltarim');
  })
} catch (e) {console.log(e)}