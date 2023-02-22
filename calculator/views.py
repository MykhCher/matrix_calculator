from django.shortcuts import render
from django.views import View
from .forms import MatrixChoiceForm
import numpy as np
import re

def custom_isdigit(value):
    """
    Accepts: string with float or a statement with math operands \n
    Returns: float or ValueError \n
    Custom method to check if input value is a digit- or numberlike.
    Supports next methods and operations: \n
    '+' : plus \n
    '-' : minus \n
    '*' : multiply \n
    'x * 10^2' : multiply by a power of ten \n
    """
    try:
        value = float(value)
    except ValueError:
        if ("*10^" in value) or ("* 10^" in value) or ("* 10 ^" in value):
            sv = re.split("\+|-|\*|/", value)    # result is ['3 ', ' 7', ' 10^2'] in case we have value = '3 + 7 * 10 ^ 2'
            
            value_separator = ''
            for i in sv:
                if '^' in i:
                    powered_ten = list(i.strip(' '))
                    pwd_ten_str = ''
                    for idx, elem in enumerate(powered_ten):
                        if elem == '^':
                            summed = '\^'
                        else:
                            summed = elem
                        pwd_ten_str += summed
                    i = pwd_ten_str
                value_separator += i.strip(' ') + '|'

            operator_separator = re.split(value_separator, value)
            op_sp_rmlist = []
            for idx, i in enumerate(operator_separator):
                if i == ' ':
                    op_sp_rmlist.append(idx)
                elif not i:
                    op_sp_rmlist.append(idx)
                try:
                    float(i)
                    op_sp_rmlist.append(idx)
                except ValueError:
                    pass
            for i in reversed(op_sp_rmlist):
                operator_separator.pop(i)
                
            for idx, elem in enumerate(sv):
                if "10^" in sv[(idx+1) % len(sv)] or "10 ^" in sv[(idx+1) % len(sv)]: 
                    pwd_num_idx = idx
                    pwd_num = custom_isdigit(elem)
                    power = float(sv[(idx+1) % len(sv)].split("^")[1])

            powered_number_result = pwd_num * 10 ** power
            sv.pop(pwd_num_idx+1)
            sv[pwd_num_idx] = str(powered_number_result)
            operator_separator.pop(pwd_num_idx)

            new_str = ''
            for idx_sv, elem_sv in enumerate(sv):
                for idx_ops, operator in enumerate(operator_separator):
                    if idx_sv == idx_ops:
                        new_str += elem_sv + operator
                   
            new_str += sv[-1]
            value = custom_isdigit(new_str)
      
        elif "+" in value:
            sv = value.split("+")
            added_value = 0
            for i in sv:
                next_summed = custom_isdigit(i)
                added_value += next_summed
            return added_value
        elif "-" in value:
            sv = value.split("-")
            minused_value = custom_isdigit(sv[0]) * 2
            for i in sv:
                next_minused = custom_isdigit(i)
                minused_value -= next_minused
            return minused_value
        elif "*" in value:
            sv = re.split("\+|-", value)
            for idx, elem in enumerate(sv):
                if "*" in elem:
                    mul_list = elem.split("*")
                    mul_item = 1
                    for j in mul_list:
                        mul_item *= custom_isdigit(j)
            return mul_item 
        elif "," in value:    # in case user is messed up with input of coma or dot
            stripped_value = value.split(",")
            remainder = stripped_value[1].strip(" ")
            power = len(remainder)
            final_remainder = int(remainder) / 10**(power)
            value = float(stripped_value[0]) + final_remainder
        else:
            error_message = f'could not convert {type(value)} to custom_isdigit: {value}'
            raise ValueError(error_message)
    return value

def matrix_minor(arr, i, j):
    """
    Returns a minor of given arr -> `np.array` removing i-line and j-column from the origin
    """
    mask = np.ones_like(arr, dtype=bool)
    mask[i-1, :] = False
    mask[:, j-1] = False

    minor = arr[mask].reshape(arr.shape[0] - 1, arr.shape[1] - 1)

    del mask

    return minor

class TrueMatrix(View):
    def get(self, request):
        m_width = 3
        m_width_range = range(3)
        m_height = 3
        m_height_range = range(3)
        context = {
            "m_width" : m_width_range,
            "m_truewidth" : m_width,
            "m_height" : m_height_range,
            "m_trueheight" : m_height,
            "size_form" : MatrixChoiceForm()
        }
        return render(self.request, 'truematrix.html', context)
    
    def post(self, request):
        m_width = int(self.request.POST.get("width"))
        m_width_range = range(m_width)
        m_height = int(self.request.POST.get("height"))
        m_height_range = range(m_height)
        context = {
            "m_width" : m_width_range,
            "m_truewidth" : m_width,
            "m_height" : m_height_range,
            "m_trueheight" : m_height,
            "size_form" : MatrixChoiceForm(initial={"width" : m_width, "height" : m_height})
        }
        if 'matrix00' in self.request.POST:
            context["is_solved"] = True
            matrix_elements = []
            for elem in self.request.POST:
                if 'matrix' in elem:
                    matrix_elements.append(custom_isdigit(self.request.POST.get(elem)))
            array = np.array(matrix_elements)
            array = array.reshape(m_height, m_width)
            if m_width == m_height:
                is_det = True
                determinant = np.linalg.det(array)
                context["is_det"] = is_det
                context["determinant"] = round(determinant, 4)
            context["array"] = array
            try:
                minor_l = int(self.request.POST.get('minor_l'))
                minor_c = int(self.request.POST.get('minor_c'))
            except ValueError:
                message = "Warning: Type a number within a range of 0-3 when trying to specify minor line or column"
                context = {
                    "m_width" : m_width_range,
                    "m_truewidth" : m_width,
                    "m_height" : m_height_range,
                    "m_trueheight" : m_height,
                    "size_form" : MatrixChoiceForm(),
                    "warning" : message,
                }
                return render(self.request, "truematrix.html", context)
            if minor_c != 0 and minor_l != 0:
                try:
                    minor = matrix_minor(array, minor_l, minor_c)
                except IndexError:
                    message = "Warning: Type a number within a range of 0-3 when trying to specify minor line or column"
                    context = {
                        "m_width" : m_width_range,
                        "m_truewidth" : m_width,
                        "m_height" : m_height_range,
                        "m_trueheight" : m_height,
                        "size_form" : MatrixChoiceForm(),
                        "warning" : message,
                    }
                    return render(self.request, "truematrix.html", context)
                is_minor = True
                context["str_minor_c"] = str(minor_c)
                context["str_minor_l"] = str(minor_l)
                context["is_minor"] = is_minor
                context["minor"] = minor
            
        return render(self.request, 'truematrix.html', context)