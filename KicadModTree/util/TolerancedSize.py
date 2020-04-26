# KicadModTree is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KicadModTree is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kicad-footprint-generator. If not, see < http://www.gnu.org/licenses/ >.
#
# (C) 2016-2018 by Thomas Pointhuber, <thomas.pointhuber@gmx.at>

from __future__ import division
import math
import re


class TolerancedSize():
    r""" Class for handling toleranced size parameters as defined by IPC

    :params:
      * *minimum* (float) --
        Minimum size of the dimension. None if not specified.
        (default: None)
      * *nominal* (float) --
        Nominal size of the dimension. None if not specified.
        (default: None)
      * *maximum* (float) --
        Maximum size of the dimension. None if not specified.
        (default: None)
      * *tolerance* (float or [float, float]) --
        Tolerance of the dimension. Tolerance is symetrical if
        only a float is given. Asymetrical tolerances use a list.
        If one of the values is negative then it is the negative tolerance.
        If both are postive then the first entry is the negative tolerance.
        None if not specified.
        (default: None)
      * *unit* (string) --
        Unit of the given dimension.
        Named options are "inch" and "mil". Everything else means mm.
        (default: None which means mm)
    """

    def __init__(self, minimum=None, nominal=None, maximum=None, tolerance=None, unit=None):
        if nominal is not None:
            self.nominal = nominal
        else:
            if minimum is None or maximum is None:
                raise KeyError("Either nominal or minimum and maximum must be given")
            self.nominal = (minimum + maximum)/2

        if minimum is not None and maximum is not None:
            self.minimum = minimum
            self.maximum = maximum
        elif tolerance is not None:
            if type(tolerance) in [int, float]:
                self.minimum = self.nominal - tolerance
                self.maximum = self.nominal + tolerance
            elif len(tolerance) == 2:
                if tolerance[0] < 0:
                    self.minimum = self.nominal + tolerance[0]
                    self.maximum = self.nominal + tolerance[1]
                elif tolerance[1] < 0:
                    self.minimum = self.nominal + tolerance[1]
                    self.maximum = self.nominal + tolerance[0]
                else:
                    self.minimum = self.nominal - tolerance[0]
                    self.maximum = self.nominal + tolerance[1]
        else:
            self.minimum = self.nominal
            self.maximum = self.nominal

        if self.maximum < self.minimum:
            raise ValueError(
                "Maximum is smaller than minimum. Tolerance ranges given wrong or parameters confused.")

        self.minimum = TolerancedSize.toMetric(self.minimum, unit)
        self.nominal = TolerancedSize.toMetric(self.nominal, unit)
        self.maximum = TolerancedSize.toMetric(self.maximum, unit)

        self.ipc_tol = self.maximum - self.minimum
        self.ipc_tol_RMS = self.ipc_tol
        self.maximum_RMS = self.maximum
        self.minimum_RMS = self.minimum

    @staticmethod
    def toMetric(value, unit):
        r""" Convert the value to metric from the given unit

        :params:
          * *value* (float) --
            The value to be converted to metric
          * *unit* (string) --
            Unit the value is in currently. Named options are "inch" and "mil". Everything else means mm.
            (default: None which means mm)
        """
        if unit == "inch":
            factor = 25.4
        elif unit == "mil":
            factor = 25.4/1000
        else:
            factor = 1
        return value * factor

    @staticmethod
    def roundToBase(value, base):
        r""" Round value to given base

        :params:
          * *value* (float) --
          * *base* (float) --
        """
        return round(value/base) * base

    @staticmethod
    def fromString(input, unit=None):
        r""" Generate new TolerancedSize instance from size string

        :params:
            * *input* (string) --
              Size string use to generate the instance. Options are:
                * <nominal>
                * <minimal> .. <nominal> .. <maximum>
                * <minimal> .. <maximum>
                * <nominal> +/- <tolerance>
                * <nominal> +<positive tolerance> -<negative tolerance>
              Whitespace is ignored. Both .. and ... can be used as separator.
              Positive and negative tolerance can be in any order.
            * *unit* (string) --
              Unit of the given dimension. Named options are "inch" and "mil". Everything else means mm.
              (default: None which means mm)
        """
        minimum = None
        nominal = None
        maximum = None
        tolerance = None

        s = re.sub(r'\s+', '', str(input))
        if type(input) in [int, float]:
            nominal = input
        elif "+/-" in s:
            tokens = s.split("+/-")
            nominal = float(tokens[0])
            tolerance = float(tokens[1])
        elif '+' in s and '-' in s:
            if s.count('+') > 1 or s.count('-') > 1:
                raise ValueError(
                    "Illegal dimension specifier: {}\n"
                    "\tToo many tolerance specifiers. Expected nom+tolp-toln"
                    .format(input)
                )
            idxp = s.find('+')
            idxn = s.find('-')

            nominal = float(s[0:min(idxp, idxn)])
            tolerance = [
                float(s[idxn: idxp if idxn < idxp else None]),
                float(s[idxp: idxn if idxn > idxp else None])]
        elif '...' in s or '..' in s:
            s = s.replace('...', '..')
            tokens = s.split('..')
            if len(tokens) > 3:
                raise ValueError(
                    "Illegal dimension specifier: {}\n"
                    "\tToo many tokens seperated by '...' (Valid options are min...max or min...nom...max)"
                    .format(input)
                )
            minimum = float(tokens[0])
            maximum = float(tokens[-1])
            if len(tokens) == 3:
                nominal = float(tokens[1])
        else:
            try:
                nominal = float(s)
            except Exception as e:
                raise ValueError(
                    "Dimension specifier not recogniced: {}\n"
                    "\t Valid options are nom, nom+/-tol, nom+tolp-toln, min...max or min...nom...max".
                    format(input)
                ) from e

        return TolerancedSize(
            minimum=minimum,
            nominal=nominal,
            maximum=maximum,
            tolerance=tolerance,
            unit=unit
        )

    @staticmethod
    def fromYaml(yaml, base_name=None, unit=None):
        r""" Create instance from parsed yaml (=dict)

        :params:
            * *yaml* (dict or string) --
              The parsed yaml document as dict,
              extracted sub dict or the size string.
            * *base_name* (string) --
              Name of the parameter (dict key)
              This key is used to get the size string or sub dict for extracting the dimension parameters or None if
              the yaml already represents the leave notes of the format. (default: None)
            * *unit* (string) --
              Unit of the given dimension. Named options are "inch" and "mil". Everything else means mm.
              (default: None which means mm)

        :yaml format:
            * *String-based* ({base_name:size_string}) --
              Size string use to generate the instance. Options are:
                * <nominal>
                * <minimal> .. <nominal> .. <maximum>
                * <minimal> .. <maximum>
                * <nominal> +/- <tolerance>
                * <nominal> +<positive tolerance> -<negative tolerance>
              Whitespace is ignored. Both .. and ... can be used as separator.
              Positive and negative tolerance can be in any order.
            * *Dict-based* ({base_name:size_dict})
              The size dict supports the keys minimum, nominal, maximum and tolerance

        """
        if base_name is not None:
            if base_name+"_min" in yaml or base_name+"_max" in yaml or base_name+"_tol" in yaml:
                return TolerancedSize(
                    minimum=yaml.get(base_name+"_min"),
                    nominal=yaml.get(base_name),
                    maximum=yaml.get(base_name+"_max"),
                    tolerance=yaml.get(base_name+"_tol")
                )
            return TolerancedSize.fromYaml(yaml.get(base_name), unit=unit)

        elif type(yaml) is dict:
            return TolerancedSize(
                minimum=yaml.get("minimum"),
                nominal=yaml.get("nominal"),
                maximum=yaml.get("maximum"),
                tolerance=yaml.get("tolerance"),
                unit=unit
            )
        else:
            return TolerancedSize.fromString(yaml, unit)

    def updateRMS(self, tolerances):
        r"""Update root mean square values with given tolerance chain

        :params:
            * *tolerance* (itterable of floats) --
        """
        square_sum = 0
        for t in tolerances:
            square_sum += t**2

        self.ipc_tol_RMS = math.sqrt(square_sum)
        if self.ipc_tol_RMS > self.ipc_tol:
            if (TolerancedSize.roundToBase(self.ipc_tol_RMS, 1e-6) >
                    TolerancedSize.roundToBase(self.ipc_tol, 1e-6)):
                raise ValueError(
                    "RMS tolerance larger than normal tolerance."
                    "Did you give the wrong tolerances?\n"
                    "tol(RMS): {} tol: {}"
                    .format(self.ipc_tol_RMS, self.ipc_tol)
                )
            # the discrepancy most likely comes from floating point errors. Ignore it.
            self.ipc_tol_RMS = self.ipc_tol

        self.maximum_RMS = self.maximum - (self.ipc_tol - self.ipc_tol_RMS)/2
        self.minimum_RMS = self.minimum + (self.ipc_tol - self.ipc_tol_RMS)/2

    def __add__(self, other):
        if type(other) in [int, float]:
            result = TolerancedSize(
                minimum=self.minimum + other,
                maximum=self.maximum + other
            )
            return result

        result = TolerancedSize(
            minimum=self.minimum + other.minimum,
            maximum=self.maximum + other.maximum
        )
        result.updateRMS([self.ipc_tol_RMS, other.ipc_tol_RMS])
        return result

    def __sub__(self, other):
        if type(other) in [int, float]:
            result = TolerancedSize(
                minimum=self.minimum - other,
                maximum=self.maximum - other
            )
            return result

        result = TolerancedSize(
            minimum=self.minimum - other.maximum,
            maximum=self.maximum - other.minimum
        )
        result.updateRMS([self.ipc_tol_RMS, other.ipc_tol_RMS])
        return result

    def __mul__(self, other):
        if type(other) not in [int, float]:
            raise NotImplementedError(
                "Multiplication is only implemented against float or int"
            )
        result = TolerancedSize(
            minimum=self.minimum*other,
            maximum=self.maximum*other
        )
        result.updateRMS([self.ipc_tol_RMS*math.sqrt(other)])
        return result

    def __div__(self, other):
        return self.__truediv__(other)

    def __truediv__(self, other):
        if type(other) not in [int, float]:
            raise NotImplementedError(
                "Division is only implemented against float or int"
            )
        result = TolerancedSize(
            minimum=self.minimum/other,
            maximum=self.maximum/other
        )
        result.updateRMS([self.ipc_tol_RMS/math.sqrt(other)])
        return result

    def __floordiv__(self, other):
        if type(other) not in [int, float]:
            raise NotImplementedError(
                "Integer division is only implemented against float or int"
            )
        result = TolerancedSize(
            minimum=self.minimum//other,
            maximum=self.maximum//other
        )
        result.updateRMS([self.ipc_tol_RMS//math.sqrt(other)])
        return result

    def __str__(self):
        return 'nom: {}, min: {}, max: {}  | min_rms: {}, max_rms: {}'\
            .format(self.nominal, self.minimum, self.maximum, self.minimum_RMS, self.maximum_RMS)
