// Select HTML elements by their IDs and assign them to variables
const daysElement = document.getElementById("days");
const hoursElement = document.getElementById("hours");
const minutesElement = document.getElementById("minutes");
const secondsElement = document.getElementById("seconds");

// Select elements for flipping sheets and assign them to variables
const dayFlip = document.getElementById("flip-sheet-day");
const hourFlip = document.getElementById("flip-sheet-hour");
const minFlip = document.getElementById("flip-sheet-min");
const secFlip = document.getElementById("flip-sheet-sec");

// Select the element in the card to display the days
const countdownDaysElement = document.getElementById("countdownDays");
// Set the target date (May 10th)
const targetDate = new Date("May 10, 2024 00:00:00").getTime();

// Function to update the countdown timer and perform transitions
const timer = () => {
	const now = new Date().getTime();
	const timeDifference = targetDate - now;

	if (timeDifference > 0) {
		const days = Math.floor(timeDifference / (1000 * 60 * 60 * 24));
		const hours = Math.floor((timeDifference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
		const minutes = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
		const seconds = Math.floor((timeDifference % (1000 * 60)) / 1000);

		// Update the countdown timer
		daysElement.innerText = days < 10 ? `0${days}` : days;
		hoursElement.innerText = hours < 10 ? `0${hours}` : hours;
		minutesElement.innerText = minutes < 10 ? `0${minutes}` : minutes;
		secondsElement.innerText = seconds < 10 ? `0${seconds}` : seconds;

		// Update the days in the card
		countdownDaysElement.innerText = `${days} days`;

		// Perform transitions
		if (seconds === 59) flip_anime(secFlip);
		if (minutes === 59 && seconds === 59) flip_anime(minFlip);
		if (hours === 23 && minutes === 59 && seconds === 59) flip_anime(hourFlip);
		if (days === 0 && hours === 23 && minutes === 59 && seconds === 59) flip_anime(dayFlip);
	} else {
		// Countdown has reached the target date
		clearInterval(stopTimer);
		clearInterval(stopAnime);
	}
};

// Set an interval to run the timer function every 1000ms (1 second)
const stopTimer = setInterval(timer, 1000);

// Function to toggle the "flip" class for seconds flip animation
const flip_anime_sec = () => {
	secFlip.classList.toggle("flip");
};

// Function to toggle the "flip" class for the provided element
const flip_anime = (obj) => {
	obj.classList.add("flip");

	setTimeout(() => {
		obj.classList.remove("flip");
	}, 1000);
};

// Set an interval to run the flip_anime_sec function every 1000ms for seconds flip animation
const stopAnime = setInterval(flip_anime_sec, 1000);
