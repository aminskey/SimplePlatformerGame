from sys import stdout

class Level():
	def __init__(self, filename):
		self.file = filename
		self.dataset = []

	def return_dataset(self, header):
		with open(self.file, "r") as f:
			file = f.readlines()
			dataset = []
			in_dataset = False

			for line in file:
				line = line.replace("\n", "")
				line = line.replace("\t", "")

				if in_dataset == True:
					dataset.append(line)

				if line == "["+header+"]{":
					in_dataset = True

				if line == "}":
					in_dataset = False


			else:
				if in_dataset:
					print('Corrupt file')
					return None


			f.close()

		dataset.pop()
		self.dataset = dataset

		return self.return_dict()

	def return_file_name(self):
		return self.file

	def return_dict(self):
		dict = {}
		for i in range(len(self.dataset)):
			dict[self.dataset[i].split()[0]] = self.dataset[i].split()[1]
		return dict

	def print_dataset(self, header):
		print("["+header+"]")
		dict = self.return_dataset(header)
		for i in range(len(dict)):
			print(self.dataset[i].split()[0]+":"+dict[self.dataset[i].split()[0]])

	def print_file(self):
		with open(self.file, "r") as f:
			print(f.read())
			f.close()
