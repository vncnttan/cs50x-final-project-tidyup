const StopEventPropagation = (e)=> {
    if (!e) return;
    e.cancelBubble = true;
    if (e.stopPropagation) e.stopPropagation();
};
export const Calendar = (id) => ({
    id: id,
    data: [],
    el: undefined,
    y: undefined,
    m: undefined,
    onDateClick(e) {
        if (this===e.target) {
            // the following will only run for the target, not its ancestors
            StopEventPropagation(e);
            const el = e.srcElement;
            console.log('click');
            console.log(el);
          }
    },
    onEventClick(e) {
        StopEventPropagation(e);
        const el = event.currentTarget;
        console.log('click');
        console.log(el);

        var myOffcanvas = el.nextElementSibling;
        var bsOffcanvas = new bootstrap.Offcanvas(myOffcanvas);

        bsOffcanvas.show();
    },
    bindData(events) {
        this.data = events.sort((a,b) => {
            if ( a.time < b.time ) return -1;
            if ( a.time > b.time ) return 1;
            return 0;
        });
    },
    renderEvents() {
        if (!this.data || this.data.length<=0) return;
        const lis = this.el.querySelectorAll(`.${this.id} .days .inside`);
        let y = this.el.querySelector('.month-year .year').innerText;
        let m = lis[0].querySelector('.date').getAttribute('month');
        lis.forEach((li)=>{
            let d = li.innerText;
            let divEvents = li.querySelector('.events');
            li.onclick = this.onDateClick;
            this.data.forEach((ev)=>{
                let evTime = moment(ev.time);
                var legibledate = new Date(evTime).toDateString();;
                if (evTime.year() == y && evTime.month() == m && evTime.date() == d) {
                    let frgEvent = document.createRange().createContextualFragment(`
                        <div time="${ev.time}" class="event ${ev.cls}"><i class="${ev.icon} mx-1"></i> <b> ${ev.name} </b> </div>

                        <div class="offcanvas offcanvas-start text-black text-start" tabindex="-1" id="offcanvas" aria-labelledby="offcanvasLabel">
                            <div class="offcanvas-header">
                                <h5 class="offcanvas-title " id="offcanvasLabel"> Event Details </h5>
                                <button type="button" class="btn-close text-reset" data-bs-dismiss="offcanvas" aria-label="Close"></button>
                            </div>
                            <div class="offcanvas-body">
                                <h8 class="tight">${legibledate}</h8>
                                <h1 class="tight">${ev.name} <i class="${ev.icon}"></i></h1> <br>
                                <i class="${ev.notify_icon}"></i>
                                <a data-toggle="tooltip" title="Edit notification settings using edit event" style="text-decoration: none;"> Remind this event on email </a>
                                <p> Event type : <i class="${ev.icon}"></i> ${ev.type}</p>

                                <p style="white-space: pre">Event Details : <br>${ev.details}<p><br>

                                <!-- A button to edit the event -->
                                <form action="/events/edit-short-event" method="post">
                                  <input type="hidden" value="${ev.id}" name="edit_event_id"/>
                                  <button class="btn btn-secondary" type="submit"> Edit Event </button>
                                </form>

                                <!-- A button to delete event -->
                                <div class="position-absolute bottom-0 end-0">
                                    <div class="delete_event">
                                        <form id="deleteForm ${ev.id}" action="/events/del-short-event" method="post">
                                            <input type="hidden" value="${ev.id}" name="del_event_id"/>
                                            <input type="hidden" value="${ev.name}" id="del_short_name ${ev.id}" name="del_event_name"/>
                                            <span data-bs-dismiss="offcanvas" class="text-reset">
                                                <button type="button" class="btn btn-danger m-4 delshortevbtn" data-toggle="modal" data-target="#Modal" id="delShortEvBtn ${ev.id}">
                                                    Delete this event
                                                </button>
                                            </span>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `);
                    divEvents.appendChild(frgEvent);
                    let divEventsOnThatDay = divEvents.querySelectorAll(`.event[time='${ev.time}']`);
                    let foo = this;
                    divEventsOnThatDay.forEach(function(divEvent){
                        divEvent.onclick = foo.onEventClick;
                    });

                    fn1();
                }
            });
        });
    },
    render(y, m) {
        //-------------------------------------------------------------------------------------------
        //first time when you call render() without params, it is going to default to current date.
        //this logic here is to make sure if you re-render by calling render() without any param again,
        //if the calendar is already looking at some other month, then it will get the updated data, but
        //the calendar will not jump back to current month and stay at the previous month you are looking at.
        //this is useful when server side has updated events, calendar can re-bindData() and re-render()
        //itself correctly to reflect any changes.
        if (isNaN(y) && isNaN(this.y)) {
            this.y = moment().year();
        } else if ((!isNaN(y) && isNaN(this.y)) || (!isNaN(y) && !isNaN(this.y))) {
            this.y = y>1600 ? y : moment().year(); //calendar doesn't exist before 1600! :)
        }
        if (isNaN(m) && isNaN(this.m)) {
            this.m = moment().month();
        } else if ((!isNaN(m) && isNaN(this.m)) || (!isNaN(m) && !isNaN(this.m))) {
            this.m = m>=0 ? m : moment().month(); //momentjs month starts from 0-11
        }
        //------------------------------------------------------------------------------------------

        const d = moment().year(this.y).month(this.m).date(1); //first date of month
        const now = moment();
        const frgCal = document.createRange().createContextualFragment(`
        <div class="calendar noselect p-5">
            <div class="month-year-btn d-flex justify-content-center align-items-center mb-2">
                <a class="prev-month"><i class="fas fa-caret-left fa-lg m-3"></i></a>
                <div class="month-year d-flex justify-content-center align-items-center">
                    <div class="month mb-2 mr-2">${moment().month(this.m).format('MMMM')}</div>
                    <div class="year mb-2">${this.y}</div>
                </div>
                <a class="next-month"><i class="fas fa-caret-right fa-lg m-3" aria-hidden="true"></i></a>
            </div>
            <ol class="day-names list-unstyled">
                <li><h6 class="initials">Sun</h6></li>
                <li><h6 class="initials">Mon</h6></li>
                <li><h6 class="initials">Tue</h6></li>
                <li><h6 class="initials">Wed</h6></li>
                <li><h6 class="initials">Thu</h6></li>
                <li><h6 class="initials">Fri</h6></li>
                <li><h6 class="initials">Sat</h6></li>
            </ol>
        </div>
        `);
        const isSameDate = (d1, d2) => d1.format('YYYY-MM-DD') == d2.format('YYYY-MM-DD');
        let frgWeek;
        d.day(-1); //move date to the oldest Sunday, so that it lines up with the calendar layout
        for(let i=0; i<5; i++){ //loop thru 35 boxes on the calendar month
            frgWeek = document.createRange().createContextualFragment(`
            <ol class="days list-unstyled" week="${d.week()}">
                <li class="${d.add(1,'d'),this.m != d.month()?' outside':'inside'}${isSameDate(d,now)?' today':''}"><div month="${d.month()}" class="date">${d.format('D')}</div><div class="events"></div></li>
                <li class="${d.add(1,'d'),this.m != d.month()?' outside':'inside'}${isSameDate(d,now)?' today':''}"><div month="${d.month()}" class="date">${d.format('D')}</div><div class="events"></div></li>
                <li class="${d.add(1,'d'),this.m != d.month()?' outside':'inside'}${isSameDate(d,now)?' today':''}"><div month="${d.month()}" class="date">${d.format('D')}</div><div class="events"></div></li>
                <li class="${d.add(1,'d'),this.m != d.month()?' outside':'inside'}${isSameDate(d,now)?' today':''}"><div month="${d.month()}" class="date">${d.format('D')}</div><div class="events"></div></li>
                <li class="${d.add(1,'d'),this.m != d.month()?' outside':'inside'}${isSameDate(d,now)?' today':''}"><div month="${d.month()}" class="date">${d.format('D')}</div><div class="events"></div></li>
                <li class="${d.add(1,'d'),this.m != d.month()?' outside':'inside'}${isSameDate(d,now)?' today':''}"><div month="${d.month()}" class="date">${d.format('D')}</div><div class="events"></div></li>
                <li class="${d.add(1,'d'),this.m != d.month()?' outside':'inside'}${isSameDate(d,now)?' today':''}"><div month="${d.month()}" class="date">${d.format('D')}</div><div class="events"></div></li>
            </ol>
            `);
            frgCal.querySelector('.calendar').appendChild(frgWeek);
        }

        frgCal.querySelector('.prev-month').onclick = ()=>{
            const dp = moment().year(this.y).month(this.m).date(1).subtract(1, 'month');
            this.render(dp.year(), dp.month());
        };
        frgCal.querySelector('.next-month').onclick = ()=>{
            const dn = moment().year(this.y).month(this.m).date(1).add(1, 'month');
            this.render(dn.year(), dn.month());
        };
        this.el = document.getElementById(this.id);
        this.el.innerHTML = ''; //replacing
        this.el.appendChild(frgCal);
        this.renderEvents();
    }
});