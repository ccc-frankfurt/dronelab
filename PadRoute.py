import csv


class PadRoute(object):
    def __init__(self):
        self.commands = []  # tello functions
        self.args = []  # tuple of arguments of fucntions

    def to_csv(self, delimiter=","):
        assert len(self.commands) == len(self.args)
        strings = []
        for index in range(len(self.commands)):
            string = str(self.commands[index])
            string += delimiter
            string += delimiter.join(self.args[index])
            strings.append(string)
        return "\n".join(strings)

    def from_csv(self, csv):
        strings = csv.split("\n")
        self.commands = []
        self.args = []
        for string in strings:
            command, *args = string.split(",")
            self.commands.append(command)
            self.args.append(args)

    def run(self, tello):
        for index in range(len(self.commands)):
            command = self.commands[index]
            args = self.args[index]
            func = getattr(tello, command)
            func(*args)

    def __str__(self):
        return self.to_csv(" ")


if __name__ == '__main__':
    route = PadRoute()
    route.commands = ["print", "print"]
    route.args = [["1"], ["2"]]
    class Foo:
        def print(self, x):
            print(x)
    route.run(Foo())

    print(route.to_csv())

    route.from_csv("""print,1
print,2""")
    print(route.commands)
    print(route.args)


