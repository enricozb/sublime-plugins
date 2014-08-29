import glob
import os
import sublime
import sublime_plugin

class F5(sublime_plugin.TextCommand):
	def java(self, run):
		cmd = 'javac "%(path)s"'
		cmd = cmd + ' && java "%(base)s"' if run else cmd


	def cpp(self, run):
		cmd = 'g++ "%(path)s" -Wall -o "%(base)s"'
		cmd = cmd + ' && "%(path)s"' if run else cmd

		return ('make', {'cmd': cmd})
	
	def py(self, run):
		cmd = 'python -u "%(path)s"'

		return ('make', {'cmd': cmd})

	def pde(self, run):
		# place inside proper dir
		return (('build'), {})

	def run(self, run):
		self.path = None
		self.classpath = None

		{path : self.view.file_name(),
		 base : os.path.splitext(os.path.basename(path))[0],
		 ext : os.path.splitext(os.path.basename(path))[1].strip('.'),
		}
		
		self.view.window().run_command(*getattr(self, ext, lambda arg: 0)(run))
