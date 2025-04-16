class NumberNodeBase:
    SLIDER_DISPLAY: bool = True
    NUMBER_TYPE: str = "FLOAT"  # or "INT"
    DEFAULT: float | int = 0.542
    MIN: float | int = 0
    MAX: float | int = 1.0
    STEP: float | int = 0.005

    DESCRIPTION = "Allows for setting a number value and outputs the value rounded to 3 decimal places."

    @classmethod
    def INPUT_TYPES(cls):
        slider_config = {
            "default": cls.DEFAULT,
            "min": cls.MIN,
            "max": cls.MAX,
            "step": cls.STEP,
        }

        if cls.SLIDER_DISPLAY:
            slider_config["display"] = "slider"

        return {
            "required": {
                "number": (
                    cls.NUMBER_TYPE,
                    slider_config,
                ),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "run"
    OUTPUT_NODE = True
    CATEGORY = "RyuuNoodles/Util"

    def run(self, number):
        return (round(number, 3),)


class FloatSlider(NumberNodeBase):
    SLIDER_DISPLAY = True
    NUMBER_TYPE = "FLOAT"
    DEFAULT = 0.542
    MIN = 0.0
    MAX = 1.0
    STEP = 0.005


class FloatPlain(NumberNodeBase):
    SLIDER_DISPLAY = False
    NUMBER_TYPE = "FLOAT"
    DEFAULT = 0.542
    MIN = 0.0
    MAX = 1.0
    STEP = 0.005


class IntSlider(NumberNodeBase):
    SLIDER_DISPLAY = True
    NUMBER_TYPE = "INT"
    DEFAULT = 25
    MIN = 0
    MAX = 50
    STEP = 1
