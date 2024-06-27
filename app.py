from flask import Flask, render_template, request
import datetime

app = Flask(__name__)

# Define peak hours (e.g., 8 AM to 6 PM)
PEAK_HOURS = range(8, 18)

# Define extra charges for specific slots
SLOT_EXTRA_CHARGE = {
    '1': 10,  # extra charge for slot 1
    '3': 15  # extra charge for slot 3
}

def calculate_duration(entry_time, exit_time):
    if exit_time < entry_time:
        exit_time += datetime.timedelta(days=1)  # Handle overnight parking
    duration_seconds = (exit_time - entry_time).total_seconds()
    duration_hours = duration_seconds / 3600
    return duration_hours

def calculate_peak_duration(entry_time, exit_time, peak_hours):
    peak_duration = 0
    current_time = entry_time
    while current_time < exit_time:
        if current_time.hour in peak_hours:
            peak_duration += 1
        current_time += datetime.timedelta(hours=1)
    return peak_duration

def calculate_parking_cost(duration, peak_duration, parking_slot, base_rate, peak_hour_multiplier, slot_extra_charge):
    peak_hour_rate = base_rate * peak_hour_multiplier
    off_peak_hour_rate = base_rate

    peak_cost = peak_duration * peak_hour_rate
    off_peak_cost = (duration - peak_duration) * off_peak_hour_rate

    location_multiplier = 1.2 if parking_slot.lower() == "prime" else 1.0
    total_cost = (peak_cost + off_peak_cost) * location_multiplier

    extra_charge = slot_extra_charge.get(parking_slot, 0)
    total_cost += extra_charge

    return round(total_cost, 2), round(peak_cost, 2), extra_charge

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_price', methods=['POST'])
def calculate_price_route():
    number_plate = request.form['number_plate']
    parking_slot = request.form['parking_slot']
    entry_time_str = request.form['entry_time']
    exit_time_str = request.form['exit_time']

    entry_time = datetime.datetime.strptime(entry_time_str, '%H:%M')
    exit_time = datetime.datetime.strptime(exit_time_str, '%H:%M')

    duration = calculate_duration(entry_time, exit_time)
    peak_duration = calculate_peak_duration(entry_time, exit_time, PEAK_HOURS)

    base_rate = 5
    peak_hour_multiplier = 1.5

    total_cost, peak_cost, extra_charge = calculate_parking_cost(
        duration, peak_duration, parking_slot, base_rate, peak_hour_multiplier, SLOT_EXTRA_CHARGE
    )

    return render_template('bill.html', number_plate=number_plate, parking_slot=parking_slot,
                           entry_time_str=entry_time_str, exit_time_str=exit_time_str,
                           duration=duration, peak_cost=peak_cost, extra_charge=extra_charge,
                           total_cost=total_cost)

if __name__ == '__main__':
    app.run(debug=True)
