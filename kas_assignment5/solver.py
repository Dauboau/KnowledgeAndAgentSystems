import sys


class Argument:
    """ An argument stores a name, label as well as the attacked and attacking arguments """
    def __init__(self, name: str) -> None:
        """ Create an argument """
        self.name = name
        self.attackers = set()
        self.is_attacking = set()
        self.label = "UNLABELED"

    def is_defeated(self) -> bool:
        """ An argument is defeated if it is attacked by an argument labeled IN """
        return "IN" in [arg.label for arg in self.attackers]


def generate_arguments_from_file(tgf_file) -> set[Argument]:
    arguments = set()
    name_argument_mapping = dict()

    with open(tgf_file, "r") as file:
        lines = file.read().splitlines()
        # read arguments
        for line in lines[:lines.index("#")]:
            new_argument = Argument(line)
            name_argument_mapping[line] = new_argument
            arguments.add(new_argument)

        # read attacks
        for attack_relation in lines[lines.index("#") + 1:]:
            attack_relation = attack_relation.split()
            argument1 = name_argument_mapping[attack_relation[0]]
            argument2 = name_argument_mapping[attack_relation[1]]
            argument1.is_attacking.add(argument2)
            argument2.attackers.add(argument1)

    return arguments


def print_in_arguments(arguments: set[Argument]) -> None:
    print(set(arg.name for arg in arguments if arg.label == "IN"))


def is_conflict_free_set(arguments: set[Argument]) -> bool:
    # The set of arguments labeled IN is conflict free, if no attacker
    # is itself labeled IN
    for argument in arguments:
        if argument.label == "IN" and argument.is_defeated():
            return False
    return True


def is_admissible_set(arguments: set[Argument]) -> bool:
    if not is_conflict_free_set(arguments):
        return False
    for argument in arguments:
        if argument.label == "IN":
            for attacker in argument.attackers:
                # If attacker is labeled OUT, check if it's defeated by an IN argument
                if attacker.label != "OUT" and not any(a.label == "IN" for a in attacker.attackers):
                    return False
    return True



def is_complete_extension(arguments: set[Argument]) -> bool:
    if not is_admissible_set(arguments):
        return False
    for argument in arguments:
        if argument.label == "UNLABELED":
            # An argument should be labeled IN if it's defended by the set
            if all(attacker.label == "OUT" for attacker in argument.attackers):
                return False
    return True



def is_stable_extension(arguments: set[Argument]) -> bool:
    if not is_conflict_free_set(arguments):
        return False
    for argument in arguments:
        if argument.label == "OUT" and not any(a.label == "IN" for a in argument.attackers):
            return False
    return True



def find_extensions(arguments: set[Argument], extension: str) -> None:
    unlabeled_arguments = [arg for arg in arguments if arg.label == "UNLABELED"]

    if not is_conflict_free_set(arguments):
        return

    if len(unlabeled_arguments) == 0:
        # All arguments got assigned a label
        # Check if current label assignment is a solution
        if extension == "CONFLICT-FREE" and is_conflict_free_set(arguments):
            print_in_arguments(arguments)
        if extension == "ADMISSIBLE" and is_admissible_set(arguments):
            print_in_arguments(arguments)
        if extension == "COMPLETE" and is_complete_extension(arguments):
            print_in_arguments(arguments)
        if extension == "STABLE" and is_stable_extension(arguments):
            print_in_arguments(arguments)
        return

    # Choose some unlabeled argument
    some_argument = unlabeled_arguments[0]

    # Consider all options with the argument labeled IN or OUT
    some_argument.label = "IN"
    find_extensions(arguments, extension)
    some_argument.label = "OUT"
    find_extensions(arguments, extension)

    # Reverse the label assignment to previous state
    some_argument.label = "UNLABELED"


def main():
    try: 
        extension = sys.argv[1].upper()
        accepted_extensions = ["CONFLICT-FREE", "ADMISSIBLE", "COMPLETE", "STABLE"]
        if extension not in accepted_extensions:
            print("Error: extension (" + extension + ") is not supported")
            print("Possible extensions: " + str(accepted_extensions))
            raise IndexError
        arguments = generate_arguments_from_file(sys.argv[2])
    except IndexError:
        print("Usage: python extension [argumentation_frame.tgf]")
        exit(-1)

    find_extensions(arguments, extension)


if __name__ == "__main__":
    main()
