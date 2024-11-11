/**
 * Sends a message from the user to the server and displays the response from the bot.
 * 
 * This function retrieves the user's input from an input element with the ID 'user-input',
 * sends it to the server via a POST request to the '/chat' endpoint, and then displays
 * both the user's message and the bot's response in a chat box element with the ID 'chat-box'.
 * 
 * If the user's input is empty, the function returns early without sending a request.
 * 
 * The function also handles updating the chat box's scroll position to ensure the latest
 * messages are visible and clears the input field after the message is sent.
 * 
 * @function
 */
function sendMessage() {
    const inputElement = document.getElementById('user-input');
    const message = inputElement.value.trim();

    if (message === "") return;

    const chatBox = document.getElementById('chat-box');
    const userMessage = `<div class='user-message'>You: ${message}</div>`;
    chatBox.innerHTML += userMessage;

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
    })
    .then(response => response.json())
    .then(data => {
        const botMessage = `<div class='bot-message'>Bot: ${data.response}</div>`;
        chatBox.innerHTML += botMessage;
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => console.error('Error:', error));

    inputElement.value = '';
}
