import os
import re


def get_next_file(path, step=1, pos=None):
    return iterate_file_number(path, step, pos)


def get_previous_file(path, step=1, pos=None):
    return iterate_file_number(path, -step, pos)


def iterate_file_number(path, step, pos=None):
    directory, file_str = os.path.split(path)
    pattern = re.compile(r'\d+')

    match_iterator = pattern.finditer(file_str)

    for ind, match in enumerate(reversed(list(match_iterator))):
        if (pos is None) or (ind == pos):
            number_span = match.span()
            left_ind = number_span[0]
            right_ind = number_span[1]
            number = int(file_str[left_ind:right_ind]) + step
            new_file_str = "{left_str}{number:0{len}}{right_str}".format(
                left_str=file_str[:left_ind],
                number=number,
                len=right_ind - left_ind,
                right_str=file_str[right_ind:]
            )
            new_file_str_no_leading_zeros = "{left_str}{number}{right_str}".format(
                left_str=file_str[:left_ind],
                number=number,
                right_str=file_str[right_ind:]
            )
            new_complete_path = os.path.join(directory, new_file_str)
            if os.path.exists(new_complete_path):
                return new_complete_path
            new_complete_path = os.path.join(directory, new_file_str_no_leading_zeros)
            if os.path.exists(new_complete_path):
                return new_complete_path
