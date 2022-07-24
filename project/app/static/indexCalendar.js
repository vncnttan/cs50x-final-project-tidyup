import {Spinner} from './spinner.js';
import {Calendar} from './calendar.js';
import {events} from './events.js';

// Credit to : ylli2000.
// https://www.jqueryscript.net/time-clock/dynamic-event-calendar-bootstrap.html
document.addEventListener("DOMContentLoaded", async ()=>{
    const cal = Calendar('calendar');
    const spr = Spinner('calendar');
    await spr.renderSpinner().delay(0);
    await
    cal.bindData(events);
    cal.render();
});