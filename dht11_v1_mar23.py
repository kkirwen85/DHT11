import RPi.GPIO as GPIO
import dht11
import time
import datetime
import smtplib
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
	'https://www.googleapis.com/auth/drive']

#credentials = ServiceAccountCredentials.from_json_keyfile_name('File_Name.json', scope)
#gc = gspread.authorize(credentials)

# Open a worksheet from spreadsheet with one shot
#sh = gc.open("Spreadsheet_Name")
#wks = sh.worksheet("Tab_Name")
	

def get_google_data(current_temp, current_humidity):
	credentials = ServiceAccountCredentials.from_json_keyfile_name('File_Name.json', scope)
	gc = gspread.authorize(credentials)
	
	sh = gc.open("Spreadsheet_Name")
	wks = sh.worksheet("Tab_Name")
	
	#Get email alert values, High and Low.
	high_val = wks.cell(1,7).value
	low_val = wks.cell(2,7).value
	time_incr = float(wks.cell(1,4).value) * 30
	d = datetime.datetime.now()
	wks.insert_row([d.strftime("%A %b %d, %Y"), d.strftime("%I:%M %p"), current_temp, current_humidity], index=3)
	check_temp(current_temp, high_val, low_val)
	return (time_incr)
    
    


#Email Information	
smtpUser = 'SendFrom_Email'
smtpPass = 'SendFrom_Email_Password'

toAdd = 'SendTo_Email_Phone'
fromAdd = smtpUser

#Email Function
def send_alert(alert_type, alert_mess):
	header = ('To: ' + toAdd + '\n' + 'From: ' + fromAdd +
		'\n' + 'Subject: ' + alert_type)
	s = smtplib.SMTP('smtp.gmail.com',587)

	s.ehlo()
	s.starttls()
	s.ehlo()

	s.login(smtpUser, smtpPass)
	s.sendmail(fromAdd, toAdd, header + '\n\n' + alert_mess)

	s.quit()

#Function for checking if temperature is too high or too low
def check_temp(temp_read, high_alert, low_alert):
	if float(temp_read) > float(high_alert):
		send_alert("High Reading!", "Temperature is " + str(temp_read))
		#print("High Reading!\n")
	elif float(temp_read) < float(low_alert):
		send_alert("Low Reading!", "Temperature is " + str(temp_read))
		#print("Low Reading!\n")
	else:
		x_temp = 1
		#print("All good!\n")


# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# read data using pin 17
instance = dht11.DHT11(pin=17)


while True:
    result = instance.read()
    cur_temp = ((result.temperature * 9/5)+32)
    cur_hum = result.humidity
    
    if result.is_valid():
        #print("Last valid input: " + str(datetime.datetime.now()))
        #print("Temperature: %d C" % result.temperature)
        #print("Temperature: %d F" % ((result.temperature * 9/5)+32))
        #print("Humidity: %d %%" % result.humidity + '\n')
        time_incr = get_google_data(cur_temp, cur_hum)
        #print (str(time_incr))
                          
    time.sleep(time_incr)
    
