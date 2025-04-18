class NumberNodeBase:
    SLIDER_DISPLAY: bool = True
    NUMBER_TYPE: str = "FLOAT"  # or "INT"
    DEFAULT: float | int = 0.542
    MIN: float | int = 0
    MAX: float | int = 1.0
    STEP: float | int = 0.005

    @classmethod
    def INPUT_TYPES(cls):
        slider_config: dict[str, float | int | str] = {
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

    FUNCTION = "run"
    OUTPUT_NODE = True
    CATEGORY = "RyuuNoodles/Util"

    def run(self, number):
        return (round(number, 3),)


class FloatPlain(NumberNodeBase):
    SLIDER_DISPLAY = False
    NUMBER_TYPE = "FLOAT"
    RETURN_TYPES = (NUMBER_TYPE,)
    DEFAULT = 0.765
    MIN = 0.0
    MAX = 1.0
    STEP = 0.005
    DESCRIPTION = (
        "Allows for setting a float value and outputs the value rounded to 3 decimal places. \n"
        f"Limits: min: {MIN}, max: {MAX}, step: {STEP}"
    )


class FloatPlainLarger(NumberNodeBase):
    SLIDER_DISPLAY = False
    NUMBER_TYPE = "FLOAT"
    RETURN_TYPES = (NUMBER_TYPE,)
    DEFAULT = 3.75
    MIN = 0.0
    MAX = 24.0
    STEP = 0.05
    DESCRIPTION = (
        "Allows for setting a float value and outputs the value rounded to 3 decimal places. \n"
        f"Limits: min: {MIN}, max: {MAX}, step: {STEP}"
    )


class FloatSlider(NumberNodeBase):
    SLIDER_DISPLAY = True
    NUMBER_TYPE = "FLOAT"
    RETURN_TYPES = (NUMBER_TYPE,)
    DEFAULT = 0.345
    MIN = 0.0
    MAX = 1.0
    STEP = 0.005
    DESCRIPTION = (
        "Allows for setting a float value with a slider display and outputs the value rounded to 3 decimal places. \n"
        f"Limits: min: {MIN}, max: {MAX}, step: {STEP}"
    )


class IntSlider(NumberNodeBase):
    SLIDER_DISPLAY = True
    NUMBER_TYPE = "INT"
    RETURN_TYPES = (NUMBER_TYPE,)
    DEFAULT = 25
    MIN = 0
    MAX = 50
    STEP = 1
    DESCRIPTION = (
        "Allows for setting an int value with a slider display. \n" f"Limits: min: {MIN}, max: {MAX}, step: {STEP}"
    )
