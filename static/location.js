const currentLocationButton = document.querySelectorAll('.getCurrentLocation');

if (!navigator.geolocation) {
    currentLocationButton.classlist.toggle('active');
    currentLocationButton.classlist.toggle('disabled');
    currentLocationButton.disabled = true;
}

function getCurrentLocation() {
    navigator.geolocation.getCurrentPosition(pos => {
        const { latitude:lat, longitude:lng } = pos.coords;
        window.location.pathname = `/current_location/${lat}/${lng}`;
    })
}

for (const button of currentLocationButton) {
    button.onclick = getCurrentLocation;
}