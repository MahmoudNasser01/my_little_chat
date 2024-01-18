function fetchOnlineUsers(roomName) {
    const xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            const usersData = JSON.parse(xhr.responseText);
            updateActiveUsers(usersData.onlineUsers);
        }
    };

    xhr.open("GET", `/get-online-users?room=${roomName}`, true);
    xhr.send();
}

function updateActiveUsers(usersData) {
    var activeUsersList = document.getElementById("active-users-list");

    try {
        // Ensure that usersData is an array
        if (!Array.isArray(usersData)) {
            throw new Error("Invalid data format");
        }

        // Clear previous content
        activeUsersList.innerHTML = "";

        usersData.forEach((user) => {
            // Create a new list item for each user
            var userCircle = document.createElement("div");
            userCircle.className = "user-circle";

            // Check if user.image exists, otherwise use a placeholder
            var imageUrl = user.image || 'https://unsplash.it/600/400';
            userCircle.innerHTML = `<img src="${imageUrl}" alt="${user.username}"><div class="user-name">${user.username}</div>`;

            activeUsersList.appendChild(userCircle);
        });

    } catch (error) {
        console.error("Error fetching active users:", error.message);
    }
}

fetchOnlineUsers(window.location.pathname.split('/').filter(Boolean).pop());
