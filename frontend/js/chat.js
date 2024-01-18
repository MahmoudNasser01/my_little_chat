// Extract room name from the URL and fetch initial chat data
const roomName = window.location.pathname.split('/').filter(Boolean).pop();
const ws = new WebSocket(`ws://localhost:8080/${roomName}/`);

ws.addEventListener('open', (event) => {
    ws.send(JSON.stringify({
        auth_token: localStorage.getItem('auth_token'),
        room_name: roomName,
        event: 'user-joined',
        data: {},
    }));
});

ws.addEventListener('close', (event) => {
    console.log('WebSocket connection closed:', event);
});

// Event handler for when a message is received from the server
ws.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    console.log('Message from server:', data);

    if (data.event === 'typing') {
        handleTypingStatus(true);
        typingTimeout = setTimeout(() => {
                let typingIndicator = document.getElementById('typing-indicator');
                typingIndicator.style.display = 'none';
                isTyping = false;
        }, 2000); // Adjust the timeout duration as needed
    } else if (data.event === 'message') {
        fetchChatData(roomName);
    }
    else if(data.event === 'user-joined'){
        fetchOnlineUsers(window.location.pathname.split('/').filter(Boolean).pop());
    }
});

fetchChatData(roomName);

function sendMessageToServer(roomName, message) {
    const messageData = {
        auth_token: localStorage.getItem('auth_token'),
        room_name: roomName,
        event: 'message',
        data: {
            content: message
        },
    };

    ws.send(JSON.stringify(messageData));
}

function fetchChatData(roomName) {
    const xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            const chatData = JSON.parse(xhr.responseText);
            updateChatMessages(chatData);
        }
    };

    xhr.open("GET", `/get-room-messages?room=${roomName}`, true);
    xhr.send();
}

function updateChatMessages(chatData) {
    const messagesContainer = document.getElementById('messages-container');
    messagesContainer.innerHTML = '';

    chatData.messages.forEach((message) => {
        const messageCard = document.createElement('div');
        messageCard.className = 'message-card';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const userImage = document.createElement('img');
        userImage.className = 'user-image';
        userImage.src = 'https://unsplash.it/600/400'; // Replace with actual user image URL
        userImage.alt = 'User Image';

        const messageDetails = document.createElement('div');
        messageDetails.className = 'message-details';

        const messageSender = document.createElement('div');
        messageSender.className = 'message-sender';
        messageSender.innerText = message.sender;

        const messageTimestamp = document.createElement('div');
        messageTimestamp.className = 'message-timestamp';
        messageTimestamp.innerText = message.timestamp;

        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.innerText = message.content;

        messageDetails.appendChild(messageSender);
        messageDetails.appendChild(messageTimestamp);

        messageContent.appendChild(userImage);
        messageContent.appendChild(messageDetails);

        messageCard.appendChild(messageContent);
        messageCard.appendChild(messageText);

        messagesContainer.appendChild(messageCard);
    });
}

function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();

    if (message !== '') {
        sendMessageToServer(roomName, message);
        messageInput.value = '';
    }
}

// Variable to track typing status
let isTyping = false;
let typingTimeout;

// Event handler for detecting typing
function handleTyping() {
    const messageInput = document.getElementById('message-input');

    messageInput.addEventListener('input', () => {
        if (messageInput.value.trim() !== '' && !isTyping) {
            isTyping = true;
            sendTypingStatus(true);
        } else if (messageInput.value.trim() === '' && isTyping) {
            isTyping = false;
            sendTypingStatus(false);
        }
    });
}
// Function to send typing status to the server
function sendTypingStatus(isTyping) {
    const typingData = {
        auth_token: localStorage.getItem('auth_token'),
        room_name: roomName,
        event: 'typing',
        data: {
            is_typing: isTyping,
        },
    };

    ws.send(JSON.stringify(typingData));


}

// Event handler for when a typing status is received from the server
function handleTypingStatus(isTyping) {
    const typingIndicator = document.getElementById('typing-indicator');
    typingIndicator.style.display = isTyping ? 'block' : 'none';
}

handleTyping();
