from Tkinter import *
import subprocess
import time
import thread
import tkFont
import sys

args = sys.argv

#~ if len(args) == 1:
	#~ args = ["haveInternet.pyw", "-ip", "192.168.0.8", "-time_between_pings", "1"] #could put default arguments here. Mostly for testing

class Win(Tk):
	#~ def __init__(self, time_between_pings = 4, interval = 60, notify_interval = 20, display_ping = True, ip_to_ping = "8.8.8.8", do_log):
	def __init__(self, time_between_pings, interval, notify_interval, display_ping, ip_to_ping, do_log, dim = 100):
		self.display_ping = display_ping
		self.time_between_pings = time_between_pings #in seconds
		self.notify_interval = notify_interval #time you have to not have internet in order to be notified when it comes back
		self.interval = interval #log collection interval
		self.ip_to_ping = ip_to_ping
		self.do_log = do_log
		Tk.__init__(self, None)
		self.attributes('-topmost', 1) #Make it stay on top
		self.overrideredirect(1) #make the window not have borders/title bar
		
		#create the canvas. This will take up the whole window. Default to "no internet" look
		#if there is in fact internet, it changes to green very quickly
		w, h = dim, dim
		self.f = Canvas(self, bg = "red", width = w, height = h)
		self.f.pack()
		consolas = tkFont.Font(family="Consolas", size="-%s" % (str(h - 10)))
		self.canvas_text_id = self.f.create_text(w/2, h/2,
												font = consolas)
		self.f.itemconfigure(self.canvas_text_id, text=":(")
		
		
		#this array holds the times of the last times the window was clicked
		#This is used later to show if the window is clicked three times in .5 seconds,
		#	then the window will close and the program will exit
		self.times_last_clicked = [0, 0, 0]
		
		#bind mouse events for movement and window closing
		self.bind("<ButtonPress-1>", self.on_click)
		self.bind("<B1-Motion>", self.on_motion)
		
		#create file and file header for log. Includes the timestamp in seconds
		self.log_name = "internet_connectivity%s.csv" % str(time.time()).split(".")[0]
		if self.do_log:
			self.output_log = open(self.log_name, "w")
			self.output_log.write("interval, cumulative packet success ratio, avg ping time cumulative, interval packet success ratio, avg ping time interval")
			self.output_log.close()
		#this is for the interval. If [interval] seconds have passed since
		#	the last the time log was written to, this gets reset and the log
		#	is written to. Interval values in the self.logInfo dict are reset
		#	as well
		self.last_time_written_to_log = time.time()
		
		#this is the dictionary where the logging info is kept
		#pingcount variables are set to .1 initially to avoid
		#	a division by zero error when calculating stats.
		#	it's accounted for by flooring the pingcount when it's added to
		self.logInfo = {}
		self.logInfo["interval-success"] = 0.0
		self.logInfo["interval-pingtime"] = 0.0
		self.logInfo["interval-pingcount"] = .1
		self.logInfo["cumulative-success"] = 0.0
		self.logInfo["cumulative-pingtime"] = 0.0
		self.logInfo["cumulative-pingcount"] = .1
		
		#time_last_had_internet is used to decide when to notify
		#	the user. If time.time() - time_last_had... then print \x07 (bell character)
		self.time_last_had_internet = time.time()
		
		self.do_loop = True
		
		#start processes
		#self.loop()
		thread.start_new_thread(self.loop, ())
		self.mainloop()
	
	def on_click(self, event):
		self.x_mouse_start = self.winfo_pointerx() - self.winfo_rootx()
		self.y_mouse_start = self.winfo_pointery() - self.winfo_rooty()
		#destroy the window when it's clicked three times in half a second
		self.times_last_clicked = self.times_last_clicked[1:] + [time.time()]
		if self.times_last_clicked[-1] - self.times_last_clicked[0] < .5:
			self.do_loop = False
			self.destroy()
	
	def on_motion(self, event):
		#with self.overrideredirect(1), the window loses it's movement capabilities
		#this function reinstates it
		x = self.winfo_pointerx() - self.x_mouse_start
		y = self.winfo_pointery() - self.y_mouse_start
		size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
		self.geometry("%dx%d+%d+%d" % (size + (x, y)))
	
	def loop(self):
		while self.do_loop:
			start_time = time.time()
			try:
				ping_output = subprocess.check_output("ping %s -n 1" % (self.ip_to_ping), shell=True)
				#print ping_output
				if "Uncreachable" not in ping_output:
					time_index = ping_output.index("time=")
					ms_index = ping_output.index("ms", time_index)
					ping_time = float(ping_output[time_index+5:ms_index]) / 1000.0
					lost_index = ping_output.index("Lost = ")
					was_lost = bool(int(ping_output[lost_index + 7:lost_index+8]))
			except:
				ping_time = time.time() - start_time
				was_lost = True
			
			w = self.winfo_width()
			h = self.winfo_height()
			if not was_lost:
				if time.time() - self.time_last_had_internet > self.notify_interval:
					print "\x07" #ba-ding
				self.f.config(bg = "green") # :)
				#find the maximum font where the ping will fit in the window
				if self.display_ping:
					ping_to_display = str(int(round(ping_time*1000)))#.split(".")[0]
					font_size_h_limit = abs(h-10)
					font_size_w_limit = (abs(w-10) / len(ping_to_display)) * 2
					consolas = tkFont.Font(family="Consolas", size="-%s" % (str(min([font_size_h_limit, font_size_w_limit]))))
					self.f.itemconfigure(self.canvas_text_id, font=consolas)
					self.f.itemconfigure(self.canvas_text_id, text=ping_to_display)
				else:
					consolas = tkFont.Font(family="Consolas", size="-%s" % (str(h-10)))
					self.f.itemconfigure(self.canvas_text_id, font=consolas)
					self.f.itemconfigure(self.canvas_text_id, text=":)")
				self.logInfo["cumulative-success"] += 1.0
				self.logInfo["cumulative-success"] -= self.logInfo["cumulative-success"]%1
				self.logInfo["cumulative-pingtime"] += ping_time
				self.logInfo["interval-success"] += 1.0
				self.logInfo["interval-success"] -= self.logInfo["interval-success"]%1
				self.logInfo["interval-pingtime"] += ping_time
				
				self.time_last_had_internet = time.time()
			else:
				consolas = tkFont.Font(family="Consolas", size="-%s" % (str(h-10)))
				self.f.itemconfigure(self.canvas_text_id, font=consolas)
				self.f.config(bg = "red") # :(
				self.f.itemconfigure(self.canvas_text_id, text=":(")
			
			self.logInfo["cumulative-pingcount"] += 1.0
			self.logInfo["cumulative-pingcount"] -= self.logInfo["cumulative-pingcount"]%1
			self.logInfo["interval-pingcount"] += 1.0
			self.logInfo["interval-pingcount"] -= self.logInfo["interval-pingcount"]%1
			
			if time.time() - self.last_time_written_to_log >= self.interval and self.do_log:
				with open(self.log_name, "a") as logFile:
					if self.logInfo["cumulative-success"] != 0:
						avg_pingtime_cumulative = self.logInfo["cumulative-pingtime"] / self.logInfo["cumulative-success"]
					else:
						avg_pingtime_cumulative = 0
					if self.logInfo["interval-success"] != 0:
						avg_pingtime_interval = self.logInfo["interval-pingtime"] / self.logInfo["interval-success"]
					else:
						avg_pingtime_interval = 0
					logFile.write("\n%s, %s, %s, %s, %s" % (time.time() - self.last_time_written_to_log, 
														self.logInfo["cumulative-success"] / self.logInfo["cumulative-pingcount"],
														avg_pingtime_cumulative,
														self.logInfo["interval-success"] / self.logInfo["interval-pingcount"],
														avg_pingtime_interval))
				self.logInfo["interval-success"] = 0.1
				self.logInfo["interval-pingtime"] = 0.0
				self.logInfo["interval-pingcount"] = .1
				self.last_time_written_to_log = time.time()
			time.sleep(self.time_between_pings)

def main(*args):
	x = Win(*args)
	return 0


if __name__ == "__main__":
	#~ default_IP = "8.8.8.8"
	default_IP = "192.168.0.8"
	#~ time_between_pings = 4, interval = 60, notify_interval = 20, display_ping = True, ip_to_ping = "8.8.8.8")
	hlp = """
Usage: haveInternet [-ip <ip = 8.8.8.8>] [-help] [-log] [-no_display_ping]"""
	if "/help" in args or "-help" in args or "/?" in args or "-?" in args:
		print hlp
	else:
		log = "-log" in args
		if not '-ip' in args:
			ip = default_IP
		else:
			ip = args[args.index("-ip") + 1]
		if not "-time_between_pings" in args:
			time_between_pings = 1
		else:
			time_between_pings = int(args[args.index("-time_between_pings") + 1])
		if not "-notify_interval" in args:
			notify_interval = 20
		else:
			notify_interval = int(args[args.index("-notify_interval") + 1])
		display_ping = "-no_display_ping" not in args
		if "-log_interval" in args:
			interval = int(args[args.index("-log_interval") + 1])
		else:
			interval = 60
		main(time_between_pings, interval, notify_interval, display_ping, ip, log, 50)
		
