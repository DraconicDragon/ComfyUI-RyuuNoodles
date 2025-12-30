import time

from comfy.utils import ProgressBar  # type: ignore


class WaitNode:
    """
    Wait node that pauses for a specified number of seconds,
    updating the progress bar in 10ms intervals.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "seconds": ("INT", {"default": 10, "min": 0, "max": 60}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = "RyuuNoodles 🐲/Utils"

    def execute(self, images, seconds):
        """
        Waits for the specified number of seconds, updating the progress bar in 10ms intervals.
        Returns the input images unchanged.
        """
        if seconds == 0:
            return (images,)

        interval = 0.01  # 10ms
        total_steps = int(seconds / interval)
        pbar = ProgressBar(total_steps)

        for _ in range(total_steps):
            time.sleep(interval)
            pbar.update(1)

        return (images,)
