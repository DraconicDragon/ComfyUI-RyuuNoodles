import torch  # type: ignore

from comfy.utils import ProgressBar  # type: ignore


class RyuuTestNode:
    """
    Example node using ComfyUI's ProgressBar utility class
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "iterations": ("INT", {"default": 5, "min": 1, "max": 50}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process_with_progressbar"
    CATEGORY = "example"

    def process_with_progressbar(self, images, iterations):
        """
        Processing function using ProgressBar utility
        """
        batch_size = images.shape[0]
        total_steps = batch_size * iterations

        # Create progress bar with total number of steps
        pbar = ProgressBar(total_steps)

        processed_images = []

        # Process each image
        for i in range(batch_size):
            image = images[i]

            # Simulate multiple processing iterations per image
            for iteration in range(iterations):

                # Simulate some work
                processed_image = image * (1.0 + iteration * 0.01)  # Example processing

                # Update progress bar
                pbar.update(1)

            processed_images.append(processed_image)

        return (torch.stack(processed_images),)
