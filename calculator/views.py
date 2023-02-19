from django.shortcuts import render
from django.views import View
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

class Matrix2x2(View):
    
    def get(self, request):
        return render(self.request, "draft_matrix.html")
    
    def post(self, request):
        try:
            i1 = custom_isdigit(request.POST.get('i1'))
            i2 = custom_isdigit(request.POST.get('i2'))
            i3 = custom_isdigit(request.POST.get('i3'))
            i4 = custom_isdigit(request.POST.get('i4'))
        except ValueError:
            message = "Warning: Type numbers (integer or float) into the input!"
            return render(self.request, "draft_matrix.html", {"warning" : message})
        array = np.array([[i1, i2], [i3, i4]])
        determinant = round(np.linalg.det(array), 3)
        result = {
            "det" : determinant,
            "m1": i1, "m2" : i2,
            "m3" : i3, "m4" : i4,
            "j1" : request.POST.get("i1"), "j2" : request.POST.get("i2"),
            "j3" : request.POST.get("i3"), "j4" : request.POST.get("i4"),
        }
        return render(self.request, "draft_matrix.html", context=result)
    
class Matrix3x3(View):

    def get(self, request):
        return render(self.request, "draft_3x3.html")
    
    def post(self, request):
        try:
            i1 = custom_isdigit(request.POST.get('i1'))
            i2 = custom_isdigit(request.POST.get('i2'))
            i3 = custom_isdigit(request.POST.get('i3'))
            i4 = custom_isdigit(request.POST.get('i4'))
            i5 = custom_isdigit(request.POST.get('i5'))
            i6 = custom_isdigit(request.POST.get('i6'))
            i7 = custom_isdigit(request.POST.get('i7'))
            i8 = custom_isdigit(request.POST.get('i8'))
            i9 = custom_isdigit(request.POST.get('i9'))
        except ValueError:
            message = "Warning: Type numbers (integer or float) into the input!"
            return render(self.request, "draft_3x3.html", {"warning" : message})
        array = np.array([[i1, i2, i3], [i4, i5, i6], [i7, i8, i9]])
        determinant = round(np.linalg.det(array), 3)
        is_det = True
        is_minor = False
        minor = np.zeros((2, 2))
        try:
            minor_l = int(self.request.POST.get('minor_l'))
            minor_c = int(self.request.POST.get('minor_c'))
        except ValueError:
            message = "Warning: Type non-zero integer into «Minor's line» or «Minor's column» input!"
            return render(self.request, "draft_3x3.html", {"warning" : message})
        result = {
                "is_det" : is_det,
                "det" : determinant,
                "is_minor" : is_minor,
                "m1" : i1, "m2" : i2, "m3" : i3, 
                "m4" : i4, "m5" : i5, "m6" : i6, 
                "m7" : i7, "m8" : i8, "m9" : i9,
                "j1" : request.POST.get("i1"), "j2" : request.POST.get("i2"), "j3" : request.POST.get("i3"),
                "j4" : request.POST.get("i4"), "j5" : request.POST.get("i5"), "j6" : request.POST.get("i6"), 
                "j7" : request.POST.get("i7"), "j8" : request.POST.get("i8"), "j9" : request.POST.get("i9"), 
                }
        if minor_c != 0 and minor_l != 0:
            try:
                minor = matrix_minor(array, minor_l, minor_c)
            except IndexError:
                message = "Warning: Type a number within a range of 0-3 when trying to specify minor line or column"
                return render(self.request, "draft_3x3.html", {"warning" : message})
            is_minor = True
            result = {
                "is_det" : is_det,
                "det" : determinant, 
                "minor1" : minor[0][0],
                "minor2" : minor[0][1],
                "minor3" : minor[1][0],
                "minor4" : minor[1][1], 
                "is_minor" : is_minor,
                "minor_c" : minor_c,
                "minor_l" : minor_l,
                "str_minor_c" : request.POST.get('minor_c'),
                "str_minor_l" : request.POST.get('minor_l'),
                "m1" : i1, "m2" : i2, "m3" : i3, 
                "m4" : i4, "m5" : i5, "m6" : i6, 
                "m7" : i7, "m8" : i8, "m9" : i9,
                "j1" : request.POST.get("i1"), "j2" : request.POST.get("i2"), "j3" : request.POST.get("i3"),
                "j4" : request.POST.get("i4"), "j5" : request.POST.get("i5"), "j6" : request.POST.get("i6"), 
                "j7" : request.POST.get("i7"), "j8" : request.POST.get("i8"), "j9" : request.POST.get("i9"), 
                }
        return render(self.request, "draft_3x3.html", context=result)
