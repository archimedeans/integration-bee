$(document).ready(async () => {
    await startClock();
});
async function startClock() {
    var countdown;
    await $.getJSON("/countdown-json", data => {
        countdown = data
    });
    var tZero = Date.now() + countdown.timeLeft;
    var subHour;
    var subMinute;
    if (countdown.enable) {
        updateClock(tZero, subHour, subMinute, timer);
        $("#liveClockDescription").text(countdown.description);

        // Update the clock every second
        var timer = setInterval(() => {
            updateClock(tZero, subHour, subMinute, timer);
        }, 1000);
    } else {
        $("#liveClockSecondsUnit").text(countdown.description);
        $("#liveClockMinutes").hide();
        $("#liveClockHours").hide();
    }
}

// Updates the `liveClock` element
function updateClock(tZero, subHour, subMinute, timer) {
    var secondsLeft = Math.trunc((tZero - Date.now()) / 1000);
    if (secondsLeft <= 0) {
        secondsLeft = 0;
        clearInterval(timer);
    }

    if (secondsLeft < 60) {
        $("#liveClockSecondsNumber").text(secondsLeft % 60);
        $("#liveClockMinutes").hide();
        $("#liveClockHours").hide();
    } else if (secondsLeft < 3600) {
        $("#liveClockSecondsNumber").text(padTime(secondsLeft % 60));
        $("#liveClockMinutesNumber").text(Math.trunc((secondsLeft % 3600) / 60));
        $("#liveClockHours").hide();
    } else {
        $("#liveClockSecondsNumber").text(padTime(secondsLeft % 60));
        $("#liveClockMinutesNumber").text(padTime(Math.trunc((secondsLeft % 3600) / 60)));
        $("#liveClockHoursNumber").text(Math.trunc(secondsLeft / 3600));
    }
}
function padTime(i) {
    if (i < 10) {
        i = "0" + i
    };
    return i;
}
