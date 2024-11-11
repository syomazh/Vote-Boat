document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
    document.getElementById('searchButton').addEventListener('click', function() {
        let candidate = document.getElementById('searchNameInput').value;
        let topic = document.getElementById('searchTopicInput').value;


        const oceanPhrases = [
            "Casting a net for information",
            "Navigating the seas of knowledge",
            "Sailing through data",
            "Diving deep for details",
            "Charting the course for facts",
            "Fishing for insights",
            "Anchoring in truth",
            "Plumbing the depths for answers",
            "Setting sail for the truth",
            "Harpooning the facts",
            "Exploring uncharted waters of information",
            "Surfing the waves of data",
            "Docking at the harbor of knowledge",
            "Reeling in the truth",
            "Steering through the currents of data"
          ];
        const randomIndex = Math.floor(Math.random() * oceanPhrases.length);
        const randomPhrase1= oceanPhrases[randomIndex];
        const randomIndex2 = Math.floor(Math.random() * oceanPhrases.length-2);
        const randomPhrase2= oceanPhrases[(randomIndex2+randomIndex)%oceanPhrases.length];
          

        document.getElementById('bio').innerHTML = '<strong style="font-size: 1.1em;"></strong><br><span style="font-size: 0.8em;"></span>';
        document.getElementById('voting-history').innerHTML = '<strong style="font-size: 1.1em;">'+randomPhrase1+"..."+'</strong><br><span style="font-size: 0.8em;"></span>';
        document.getElementById('links').innerHTML = '<br><strong style="font-size: 1.1em;">'+randomPhrase2+ "..."+'</strong><br><span style="font-size: 0.9em;"></span>';

        if (candidate === "" || topic === "") return;
        // Show the loading GIF
        document.getElementById('loading').style.display = 'block';

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: candidate,
                topic: topic
            })
        })
        .then(response => response.json())
        .then(data => {

            // Hide the loading GIF when done loading
            document.getElementById('loading').style.display = 'none';

            // Populate the frontend with the returned data
            document.getElementById('bio').innerHTML = '<strong style="font-size: 1.1em;">Bio:</strong><br><span style="font-size: 0.8em;">' + data.bio + '</span>';
            document.getElementById('voting-history').innerHTML = '<strong style="font-size: 1.1em;">Voting history:</strong><br><span style="font-size: 0.8em;">' + data.vote + '</span>';
            // document.getElementById('info').innerHTML = '<strong style="font-size: 1.1em;">Quick info:</strong><br><span style="font-size: 0.9em;">' + data.info + '</span>';
            document.getElementById('links').innerHTML = '<strong style="font-size: 1.1em;">Extra links:</strong><br><span style="font-size: 0.9em;">' + data.links + '</span>';
        })
        .catch(error => console.error('Error:', error));
    });
});